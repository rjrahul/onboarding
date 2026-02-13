from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.crud import customer as crud

def get_all_customers(db: Session):
    return crud.get_customers(db)

def get_customer_by_id(db: Session, customer_id: int):
    customer = crud.get_customer_by_id(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

def create_new_customer(db: Session, customer_data: CustomerCreate):
    return crud.create_customer(db, customer_data)

def update_existing_customer(db: Session, customer_id: int, updates: CustomerUpdate):
    customer = crud.get_customer_by_id(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return crud.update_customer(db, customer, updates)

def delete_customer_by_id(db: Session, customer_id: int):
    customer = crud.get_customer_by_id(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    crud.delete_customer(db, customer)
