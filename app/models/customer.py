from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class AddressModel(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    street = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    zip_code = Column(String, nullable=False)
    country = Column(String, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    
class CustomerModel(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    date_of_birth = Column(String, nullable=True)
    addresses = relationship(AddressModel, backref="customer", cascade="all, delete-orphan")
    national_id = Column(String, nullable=True)
