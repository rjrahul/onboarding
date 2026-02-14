import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.core.database import get_db, Base
from app.models.customer import CustomerModel, AddressModel

# Test database setup
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
    """Setup test database for the entire test module"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(autouse=True)
def clean_database():
    """Clean database before each test to ensure isolation"""
    db = TestingSessionLocal()
    try:
        db.query(CustomerModel).delete()
        db.query(AddressModel).delete()
        db.commit()
    finally:
        db.close()

class TestCustomerFinal:
    def test_fail_risk_assessment_customer_data(self, setup_database):
        """FAIL TEST: Should fail risk assessment when customer data risk is high (simulate risk score > 30)"""
        from unittest.mock import patch, AsyncMock
        from app.exceptions.HighRiskError import HighRiskError
        import os
        os.environ["FRAUD_API_URL"] = "http://test-fake-url"

        # Customer that would otherwise succeed
        customer_data = {
            "name": "Risky Customer",
            "email": "risk@example.com",
            "phone": "07123456789",
            "date_of_birth": "1990-01-01",
            "addresses": []
        }

        # Patch:
        # - fraud API returns low risk
        # - assess_customer_risk raises HighRiskError (score > 30)
        with patch("app.services.risk_assessment.compute_risk_score_based_on_fraud_api", new=AsyncMock(return_value={"category": "LOW", "score": 0})), \
             patch("app.services.risk_assessment.assess_customer_risk", new=AsyncMock(side_effect=HighRiskError("Customer risk score is very high"))):
            response = client.post("/customers/", json=customer_data)
        assert response.status_code in (400, 403, 422)
        body = response.json()
        assert "detail" in body
        assert "customer failed risk assessment" in body["detail"].lower()

    def test_success_create_customer_with_address_and_auto_generated_ids(self, setup_database):
        """SUCCESS TEST: Create customer with address and verify auto-generated IDs are returned, and perform actual risk score check."""
        from unittest.mock import patch, AsyncMock
        import os
        os.environ["FRAUD_API_URL"] = "http://test-fake-url"
        customer_data = {
            "name": "Rahul",
            "email": "rahul@gmail.com",
            "phone": "07123456789",
            "date_of_birth": "1990-01-01",
            "addresses": [
                {
                    "street": "Street 1",
                    "city": "city 1",
                    "state": "state 1",
                    "zip_code": "201021",
                    "country": "India"
                }
            ]
        }

        # Patch fraud API call: compute_risk_score_based_on_fraud_api to avoid external call
        with patch("app.services.risk_assessment.compute_risk_score_based_on_fraud_api", new=AsyncMock(return_value={"category": "LOW", "score": 5})):
            with patch("app.services.risk_assessment.assess_customer_risk", new=AsyncMock(return_value=5)):
                response = client.post("/customers/", json=customer_data)

        assert response.status_code == 200
        created_customer = response.json()
        # Validate customer data and auto-generated ID
        assert created_customer["name"] == "Rahul"
        assert created_customer["email"] == "rahul@gmail.com"
        assert created_customer["phone"] == "07123456789"
        assert created_customer["date_of_birth"] == "1990-01-01"
        assert "id" in created_customer
        assert created_customer["id"] is not None
        assert isinstance(created_customer["id"], int)
        # Validate address data and auto-generated address ID
        assert len(created_customer["addresses"]) == 1
        address = created_customer["addresses"][0]
        assert "id" in address
        assert address["id"] is not None
        assert isinstance(address["id"], int)
        assert address["street"] == "Street 1"
        assert address["city"] == "city 1"
        assert address["state"] == "state 1"
        assert address["zip_code"] == "201021"
        assert address["country"] == "India"
        # Now check for a risk_score in the response if included, or assume risk_score is what would be returned by assess_customer_risk:
        if "risk_score" in created_customer:
            assert created_customer["risk_score"] == 5

    def test_error_create_customer_with_duplicate_email(self, setup_database):
        """EMAIL UNIQUENESS: Should not allow creation of two customers with the same email address"""
        from unittest.mock import patch, AsyncMock, MagicMock
        from app.exceptions.HighRiskError import HighRiskError
        import os
        os.environ["FRAUD_API_URL"] = "http://test-fake-url"

        customer_data = {
            "name": "DupEmail",
            "email": "unique@gmail.com",
            "phone": "07123450002",
            "date_of_birth": "1995-07-20",
            "addresses": [
                {
                    "street": "1 Dup St",
                    "city": "Dup City",
                    "state": "Dup State",
                    "zip_code": "202022",
                    "country": "CountryDup"
                }
            ]
        }
        # First creation should succeed
        with patch("app.services.risk_assessment.compute_risk_score_based_on_fraud_api", new=AsyncMock(return_value={"category": "LOW", "score": 5})):
            response1 = client.post("/customers/", json=customer_data)
        assert response1.status_code == 200
        # Second creation with same email should fail
        new_name_data = dict(customer_data)
        new_name_data["name"] = "AnotherCustomer"  # To ensure only email uniqueness is tested
        with patch("app.services.risk_assessment.compute_risk_score_based_on_fraud_api", new=AsyncMock(return_value={"category": "LOW", "score": 5})):
            response2 = client.post("/customers/", json=new_name_data)
        assert response2.status_code == 409 or response2.status_code == 422, f"Expected 409 Conflict or 422, got: {response2.status_code}"
        error_resp = response2.json()
        assert "detail" in error_resp
        assert any("exist" in str(error).lower() or "unique" in str(error).lower() or "duplicate" in str(error).lower() for error in ([error_resp["detail"]] if isinstance(error_resp["detail"], str) else error_resp["detail"]))

    def test_error_create_customer_with_invalid_required_fields(self, setup_database):
        """ERROR TEST: Attempt to create customer with missing required fields"""
        invalid_customer_data = {
            "name": "Invalid Customer"
            # Missing required email field
        }
        
        response = client.post("/customers/", json=invalid_customer_data)
        assert response.status_code == 422  # Validation error
        
        error_response = response.json()
        assert "detail" in error_response
        # Verify the error is related to missing email field
        assert any("email" in str(error).lower() for error in error_response["detail"])
    
    def test_regex_validation_phone_and_date_patterns(self, setup_database):
        """REGEX TEST: Validate phone and date_of_birth regex pattern enforcement"""
        
        # Test 1: Invalid phone format (should fail)
        invalid_phone_data = {
            "name": "Invalid Phone Customer",
            "email": "invalidphone@example.com",
            "phone": "+1234567890",  # Invalid format - doesn't match ^07\d{9}$
            "addresses": []
        }
        
        response = client.post("/customers/", json=invalid_phone_data)
        assert response.status_code == 422
        error_response = response.json()
        assert "detail" in error_response
        # Verify the error is related to phone validation
        assert any("phone" in str(error).lower() for error in error_response["detail"])
        
        # Test 2: Invalid date format (should fail)
        invalid_date_data = {
            "name": "Invalid Date Customer",
            "email": "invaliddate@example.com",
            "date_of_birth": "01-01-1990",  # Invalid format - doesn't match ^\d{4}-\d{2}-\d{2}$
            "addresses": []
        }
        
        response = client.post("/customers/", json=invalid_date_data)
        assert response.status_code == 422
        error_response = response.json()
        assert "detail" in error_response
        # Verify the error is related to date_of_birth validation
        assert any("date_of_birth" in str(error).lower() for error in error_response["detail"])
        
        # Test 3: Valid phone and date formats (should succeed)
        from unittest.mock import patch, AsyncMock, MagicMock
        from app.exceptions.HighRiskError import HighRiskError
        import os
        os.environ["FRAUD_API_URL"] = "http://test-fake-url"

        valid_data = {
            "name": "Valid Customer",
            "email": "valid@example.com",
            "phone": "07987654321",  # Valid format - matches ^07\d{9}$
            "date_of_birth": "1985-12-25",  # Valid format - matches ^\d{4}-\d{2}-\d{2}$
            "addresses": []
        }
        
        # Patch the fraud API and assess_customer_risk to simulate success
        with patch("app.services.risk_assessment.compute_risk_score_based_on_fraud_api", new=AsyncMock(return_value={"category": "LOW", "score": 0})):
            response = client.post("/customers/", json=valid_data)
        assert response.status_code == 200
        
        created_customer = response.json()
        
        assert created_customer["name"] == "Valid Customer"
        assert created_customer["email"] == "valid@example.com"
        assert created_customer["phone"] == "07987654321"
        assert created_customer["date_of_birth"] == "1985-12-25"
        assert "id" in created_customer
        assert created_customer["addresses"] == []

    def test_error_date_of_birth_less_than_18(self, setup_database):
        """DOB LESS THAN 18: Should trigger validation error if customer is a minor"""
        underage_data = {
            "name": "Young Customer",
            "email": "young@example.com",
            "phone": "07123456780",
            "date_of_birth": "2010-01-01",
            "addresses": []
        }

        response = client.post("/customers/", json=underage_data)
        assert response.status_code == 422
        error_response = response.json()
        assert "detail" in error_response
        # Check that error message contains reference to 18 years/date_of_birth
        assert any("18" in str(error) or "date_of_birth" in str(error).lower() for error in error_response["detail"])

    def test_fail_risk_assessment_on_blacklist(self, setup_database):
        """FAIL TEST: Should fail risk assessment and prevent customer creation if on blacklist."""
        from unittest.mock import patch, AsyncMock, MagicMock
        from app.exceptions.HighRiskError import HighRiskError
        import os
        os.environ["FRAUD_API_URL"] = "http://test-fake-url"
        customer_data = {
            "name": "Blacklisted",
            "email": "blacklisted@example.com",
            "phone": "07111111111",
            "date_of_birth": "1988-12-12",
            "addresses": []
        }
        # Patch the fraud API and assess_customer_risk to simulate blacklist
        with patch("app.services.risk_assessment.compute_risk_score_based_on_fraud_api", new=AsyncMock(return_value={"category": "LOW", "score": 0})), \
             patch("app.services.risk_assessment.assess_customer_risk", new=AsyncMock(side_effect=HighRiskError("Customer is on the blacklist"))):
            response = client.post("/customers/", json=customer_data)
        # Expect 400 or 422 or custom error handling
        assert response.status_code in (400, 403, 422)
        body = response.json()
        assert "detail" in body
        assert "customer failed risk assessment" in body["detail"].lower()

if __name__ == "__main__":
    pytest.main(["-v", __file__])
