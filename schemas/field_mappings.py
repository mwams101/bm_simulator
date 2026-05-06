from datetime import datetime
from typing import Dict, Any, Optional

from pydantic import BaseModel


class FieldMappingBase(BaseModel):
    id: int
    migration_job_id: int
    mapping_template_id: Optional[int] = None
    mapping_rules: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class FieldMappingCreate(BaseModel):
    migration_job_id: int
    mapping_template_id: int
    mapping_rules: Dict[str, Any]

