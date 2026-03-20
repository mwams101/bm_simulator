from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AuditLogsBase(BaseModel):
    id: int
    user_id: int
    migration_job_id: Optional[int] = None
    action_type: str
    action_description: str
    ip_address: Optional[str] = None
    request_data: Optional[str] = None
    response_data: Optional[str] = None
    timestamp: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AuditLogsCreate(BaseModel):
    user_id: int
    migration_job_id: Optional[int] = None
    action_type: str
    action_description: str
    ip_address: Optional[str] = None
    request_data: Optional[str] = None
    response_data: Optional[str] = None