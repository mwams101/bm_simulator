from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class NewBankCustomersBase(BaseModel):
    id: int
    migration_job_id: Optional[int] = None
    first_name: str
    last_name: str
    date_of_birth: date
    email: str
    phone_masked: str
    address_line_1: str
    address_line_2: str
    city: str
    state: str
    postal_code: str
    country: str
    customer_type: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NewBankCustomersCreate(BaseModel):
    migration_job_id: Optional[int] = None
    first_name: str
    last_name: str
    date_of_birth: date
    email: str
    phone_masked: str
    address_line_1: str
    address_line_2: str
    city: str
    state: str
    postal_code: str
    country: str
    customer_type: str
    status: str
    created_at: datetime
    updated_at: datetime


class NewBankCustomersUpdate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_masked: str
    address_line_1: str
    address_line_2: str
    city: str
    state: str
    postal_code: str
    country: str
    status: str
    updated_at: datetime