from sqlalchemy.orm import Session
from app.models.customer import CustomerModel, AddressModel
from app.schemas.customer import CustomerCreate, CustomerUpdate

def get_customers(db: Session):
    return db.query(CustomerModel).all()

def get_customer_by_id(db: Session, customer_id: int):
    return db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()

def create_customer(db: Session, customer: CustomerCreate):
    db_customer = CustomerModel(
        name=customer.name,
        email=customer.email,
        phone=customer.phone,
        date_of_birth=customer.date_of_birth,
        national_id=customer.national_id,
        addresses=[
            AddressModel(
                street=addr.street,
                city=addr.city,
                state=addr.state,
                zip_code=addr.zip_code,
                country=addr.country
            )
            for addr in customer.addresses
        ] if customer.addresses else []
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

def update_customer(db: Session, db_customer: CustomerModel, updates: CustomerUpdate):
    update_data = updates.model_dump(exclude_unset=True)
    
    # Handle addresses separately if they exist in the update
    if 'addresses' in update_data:
        addresses_data = update_data.pop('addresses')
        # Clear existing addresses
        db_customer.addresses.clear()
        # Add new addresses as SQLAlchemy models
        if addresses_data:
            for addr_data in addresses_data:
                db_address = AddressModel(
                    street=addr_data.street,
                    city=addr_data.city,
                    state=addr_data.state,
                    zip_code=addr_data.zip_code,
                    country=addr_data.country
                )
                db_customer.addresses.append(db_address)
    
    # Update other fields
    for field, value in update_data.items():
        setattr(db_customer, field, value)
    
    db.commit()
    db.refresh(db_customer)
    return db_customer

def delete_customer(db: Session, db_customer: CustomerModel):
    db.delete(db_customer)
    db.commit()
