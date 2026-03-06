from datetime import datetime
from typing import Dict, Any

from pydantic import BaseModel


class FieldMappingBase(BaseModel):
    id: int
    migration_job_id: int
    mapping_template_id: int
    mapping_rules: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class FieldMappingCreate(BaseModel):
    migration_job_id: int
    mapping_template_id: int
    mapping_rules: Dict[str, Any]