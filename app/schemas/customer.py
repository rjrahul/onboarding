from typing import List, Optional
from pydantic import BaseModel, ConfigDict, field_validator, Field
from app.schemas.validators import is_customer_less_than_18

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
    name: str = Field(min_length=1, max_length=40)
    phone: Optional[str] = Field(default=None, pattern=r"^07\d{9}$")
    date_of_birth: Optional[str] = Field(
        default=None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Date of birth in YYYY-MM-DD format (must be 18+)"
    )

    @field_validator('date_of_birth')
    @classmethod
    def validate_date_of_birth(cls, value):
        return is_customer_less_than_18(value)

    addresses: Optional[List[AddressBase]] = []
    national_id: Optional[str] = None

class CustomerCreateBase(CustomerBase):
    email: str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$", max_length=40)

class Customer(CustomerCreateBase):
    id: int
    addresses: Optional[List[Address]] = [] # type: ignore

    model_config = ConfigDict(from_attributes=True)

class CustomerCreate(CustomerCreateBase):
    pass

class CustomerUpdate(CustomerBase):
    pass
