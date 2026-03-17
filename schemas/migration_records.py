from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class MigrationRecordsBase(BaseModel):
    id: int
    migration_job_id: int
    source_record_id: int
    source_data: Any
    transformed_data: Any
    status: str
    error_message: Optional[str] = None
    migrated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class MigrationRecordsCreate(BaseModel):
    migration_job_id: int
    source_record_id: int
    source_data: Any
    transformed_data: Any
    status: str
    error_message: Optional[str] = None


class MigrationRecordsUpdate(BaseModel):
    status: str
    transformed_data: Any
    error_message: Optional[str] = None
