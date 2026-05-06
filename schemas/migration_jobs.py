from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MigrationJobsBase(BaseModel):
    id: int
    user_id: int
    destination_schema_id: Optional[int] = None
    name: str
    status: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_records: int
    successful_records: int
    failed_records: int
    error_message: Optional[str] = None

    model_config = {"from_attributes": True}


class MigrationJobsCreate(BaseModel):
    name: str
    destination_schema_id: Optional[int] = None
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_records: int
    successful_records: int
    failed_records: int
    error_message: Optional[str] = None


class MigrationJobsUpdate(BaseModel):
    name: str
    destination_schema_id: Optional[int] = None
    status: str
    total_records: int
    successful_records: int
    failed_records: int
    error_message: Optional[str] = None