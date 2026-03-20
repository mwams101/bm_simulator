from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class NewBankAccountsBase(BaseModel):
    id: int
    customer_id: int
    migration_job_id: Optional[int] = None
    account_number: int
    account_type: str
    balance: float
    currency: str
    account_open_date: date
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NewBankAccountsCreate(BaseModel):
    customer_id: int
    migration_job_id: Optional[int] = None
    account_number: int
    account_type: str
    balance: float
    currency: str
    account_open_date: date
    status: str
    created_at: datetime
    updated_at: datetime


class NewBankAccountsUpdate(BaseModel):
    balance: float
    status: str
    updated_at: datetime