from typing import List, Optional, Annotated
from pydantic import BaseModel, ConfigDict, AfterValidator, ValidationError, Field

class AddressBase(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str
    country: str

class Address(AddressBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class CustomerBase(BaseModel):
    name: str
    email: str
    phone: Optional[str] = Field(default=None, pattern=r"^07\d{9}$")
    date_of_birth: Optional[str] = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    addresses: Optional[List[AddressBase]] = []
    national_id: Optional[str] = None

class Customer(CustomerBase):
    id: int
    addresses: Optional[List[Address]] = []

    model_config = ConfigDict(from_attributes=True)

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(CustomerBase):
    pass
