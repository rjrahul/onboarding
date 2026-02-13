from fastapi import FastAPI
from app.core.database import Base, engine
from app.api.v1.customer import router as customer_router

app = FastAPI(title="Onboard Customer")

Base.metadata.create_all(bind=engine)

app.include_router(customer_router)
