from datetime import datetime

from pydantic import BaseModel


class MigrationJobsBase(BaseModel):
    id: int
    name: str
    status: str
    created_at: datetime
    started_at: datetime
    completed_at: datetime
    total_records: int
    successful_records: int
    failed_records: int
    error_message: str

class MigrationJobsCreate(BaseModel):
    name: str
    status: str
    started_at: datetime
    completed_at: datetime
    total_records: int
    successful_records: int
    failed_records: int
    error_message: str

class MigrationJobsUpdate(BaseModel):
    name: str
    status: str
    total_records: int
    successful_records: int
    failed_records: int
    error_message: str


