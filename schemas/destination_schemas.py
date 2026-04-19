from datetime import datetime

from pydantic import BaseModel


class DestinationSchemaBase(BaseModel):
    id: int
    created_by: int
    created_by_name: str = ""
    schema_name: str
    description: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class DestinationSchemaCreate(BaseModel):
    schema_name: str
    description: str