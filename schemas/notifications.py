from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NotificationsBase(BaseModel):
    id: int
    user_id: int
    migration_job_id: Optional[int] = None
    notification_type: str
    recipient: str
    subject: str
    message: str
    status: str
    created_at: datetime
    sent_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class NotificationsCreate(BaseModel):
    user_id: int
    migration_job_id: Optional[int] = None
    notification_type: str
    recipient: str
    subject: str
    message: str
    status: str


class NotificationsUpdate(BaseModel):
    status: str
    sent_at: Optional[datetime] = None