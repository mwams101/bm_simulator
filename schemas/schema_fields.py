from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SchemaFieldBase(BaseModel):
    id: int
    destination_schema_id: int
    name: str
    data_type: str
    is_required: bool
    is_unique: bool
    validation_rule: str
    max_length: int
    default_value: str
    field_order: int
    created_at: datetime
    updated_at: datetime


class SchemaFieldCreate(BaseModel):
    destination_schema_id: int
    name: str
    data_type: str
    is_required: bool
    is_unique: bool
    validation_rule: Optional[str] = None
    max_length: int
    default_value: Optional[str] = None
    field_order: int
