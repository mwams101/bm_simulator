from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DuplicateDetectionsBase(BaseModel):
    id: int
    migration_job_id: int
    duplicate_key_hash: str
    record_count: int
    record_ids: str
    resolution: str
    detected_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class DuplicateDetectionsCreate(BaseModel):
    migration_job_id: int
    duplicate_key_hash: str
    record_count: int
    record_ids: str
    resolution: str


class DuplicateDetectionsUpdate(BaseModel):
    resolution: str