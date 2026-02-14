import logging
import time
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.customer import CustomerCreate, CustomerUpdate, Customer as CustomerOut
from app.services import customer as service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.get("/", response_model=list[CustomerOut])
async def list_customers(db: Session = Depends(get_db)):
    logger.info("Attempting to list all customers.")
    customers = service.get_all_customers(db)
    logger.info(f"Successfully retrieved {len(customers)} customers.")
    return customers

@router.get("/{customer_id}", response_model=CustomerOut)
async def get_customer(customer_id: int, db: Session = Depends(get_db)):
    return service.get_customer_by_id(db, customer_id)

@router.post("/", response_model=CustomerOut)
async def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    start_time = time.perf_counter()

    create_response = await service.create_new_customer(db, customer)

    process_time = time.perf_counter() - start_time

    logger.info(f"Customer creation took {process_time:.2f} seconds.")

    return create_response

@router.put("/{customer_id}", response_model=CustomerOut)
async def update_customer(customer_id: int, customer: CustomerUpdate, db: Session = Depends(get_db)):
    return service.update_existing_customer(db, customer_id, customer)

@router.delete("/{customer_id}", status_code=204)
async def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    service.delete_customer_by_id(db, customer_id)
    return JSONResponse (
        status_code=204,
        content={"message" : "Customer deleted successfully !"}
    )
