from typing import List, Optional, Annotated
from pydantic import BaseModel, ConfigDict, AfterValidator, ValidationError, Field
from datetime import datetime, date

def is_customer_less_than_18(value: str) -> str:
    if value is None:
        return value
    
    born = datetime.strptime(value, "%Y-%m-%d").date()
    today = date.today()
    age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    if age < 18:
        raise ValueError(f'Customer is less than 18 years')
    return value  

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
    date_of_birth = Annotated[Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$"), AfterValidator(is_customer_less_than_18)]
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
