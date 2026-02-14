import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.core.database import get_db, Base
from app.models.blacklist import BlacklistModel

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_api.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close() # type: ignore

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(autouse=True)
def clean_blacklist():
    db = TestingSessionLocal()
    try:
        db.query(BlacklistModel).delete()
        db.commit()
    finally:
        db.close()

def test_blacklist_create_success_and_error(setup_database):
    """
    Covers one success (valid creation) and one error (missing required field) for Blacklist API.
    Ensures DB isolation, response validation, and clear assertion.
    """
    # Success test
    success_data = {
        "name": "Alice Smith",
        "email": "alice@example.com",
        "phone": "07123459988",
        "date_of_birth": "1989-07-26"
    }
    resp_succ = client.post("/blacklist/", json=success_data)
    assert resp_succ.status_code == 200, f"Expected 200, got {resp_succ.status_code}"
    body_succ = resp_succ.json()
    assert all(body_succ[k] == success_data[k] for k in ["name", "email", "phone", "date_of_birth"]), "Response body mismatch"
    assert "id" in body_succ and isinstance(body_succ["id"], int)

    # Error test: missing required field
    error_data = {
        "email": "bob@example.com",
        "phone": "07123451111",
        "date_of_birth": "1991-12-04"
        # 'name' missing
    }
    resp_err = client.post("/blacklist/", json=error_data)
    assert resp_err.status_code == 422, f"Expected 422, got {resp_err.status_code}"
    assert "detail" in resp_err.json()

if __name__ == "__main__":
    pytest.main(["-v", __file__])
