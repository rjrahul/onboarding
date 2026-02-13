from typing import List, Optional
from pydantic import BaseModel, ConfigDict, field_validator, Field
from app.schemas.validators import is_customer_less_than_18

class BlacklistBase(BaseModel):
    name: str
    phone: str
    date_of_birth: str
    email: str

class Blacklist(BlacklistBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class BlacklistCreate(BlacklistBase):
    pass
