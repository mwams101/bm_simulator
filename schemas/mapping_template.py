from datetime import datetime

from pydantic import BaseModel


class MappingTemplateBase(BaseModel):
    user_id: int
    template_name: str
    description: str
    created_at: datetime
    is_active: bool

class MappingTemplateUpdate(MappingTemplateBase):
    template_name: str
    description: str
    is_active: bool



