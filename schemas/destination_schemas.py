from datetime import datetime

from pydantic import BaseModel


class DestinationSchemaBase(BaseModel):
    id: int
    created_by: int
    schema_name: str
    description: str
    created_at: datetime
    updated_at: datetime


class DestinationSchemaCreate(BaseModel):
    schema_name: str
    description: str

