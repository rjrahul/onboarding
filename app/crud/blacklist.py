from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, select, text
from app.models.blacklist import BlacklistModel
from app.schemas.blacklist import BlacklistCreate
from app.schemas.customer import CustomerCreate

def create_blacklist_entry(db: Session, blacklist_entry: BlacklistCreate):
    db_blacklist = BlacklistModel(
        name=blacklist_entry.name,
        email=blacklist_entry.email,
        phone=blacklist_entry.phone,
        date_of_birth=blacklist_entry.date_of_birth,
    )
    db.add(db_blacklist)
    db.commit()
    db.refresh(db_blacklist)
    return db_blacklist

def search_blacklist_by_customer_data(db: Session, customer_data: CustomerCreate):
    query = db.query(BlacklistModel)

    name_and_email_condition = and_(BlacklistModel.name == customer_data.name, BlacklistModel.email == customer_data.email)
    name_and_phone_condition = text('1=0')  # Default to false
    name_and_date_of_birth_condition = text('1=0')  # Default to false

    if customer_data.phone:
        name_and_phone_condition = and_(BlacklistModel.name == customer_data.name, BlacklistModel.phone == customer_data.phone)

    if customer_data.date_of_birth:
        name_and_date_of_birth_condition = and_(BlacklistModel.name == customer_data.name, BlacklistModel.date_of_birth == customer_data.date_of_birth)

    query = query.filter(or_(name_and_email_condition, name_and_phone_condition, name_and_date_of_birth_condition))

    return query.first()