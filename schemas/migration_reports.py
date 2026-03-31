from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MigrationReportsBase(BaseModel):
    id: int
    migration_job_id: int
    report_file_path: str
    file_size: int
    report_type: str
    format: str
    datetime: Optional[datetime] = None

    model_config = {"from_attributes": True}


class MigrationReportsCreate(BaseModel):
    migration_job_id: int
    report_file_path: str
    file_size: int
    report_type: str
    format: str


class MigrationReportsUpdate(BaseModel):
    report_file_path: str
    file_size: int
    report_type: str
    format: str
