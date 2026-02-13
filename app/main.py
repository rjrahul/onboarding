from fastapi import FastAPI
from dotenv import load_dotenv
from app.core.database import Base, engine
from app.api.v1.customer import router as customer_router
from app.api.v1.blacklist import router as blacklist_router
from app.api.v1.fraud_detection import router as fraud_router

load_dotenv()

app = FastAPI(title="Onboard Customer")

Base.metadata.create_all(bind=engine)

app.include_router(customer_router)
app.include_router(blacklist_router)
app.include_router(fraud_router)
