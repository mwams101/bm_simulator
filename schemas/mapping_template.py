from datetime import datetime

from pydantic import BaseModel


class MappingTemplateBase(BaseModel):
    id: int
    user_id: int
    template_name: str
    description: str
    created_at: datetime
    is_active: bool



class MappingTemplateCreate(BaseModel):
    template_name: str
    description: str
    is_active: bool



