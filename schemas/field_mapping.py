from typing import Dict, Any

from pydantic import BaseModel


class FieldMappingBase(BaseModel):
    migration_job_id: int
    mapping_template_id: int
    mapping_rules: Dict[str, Any]