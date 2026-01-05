from pydantic import BaseModel


class SchemaFieldBase(BaseModel):
    destination_schema_id: int
    name: str
    data_type: str
    is_required: bool
    is_unique: bool
    validation_rule: str
    max_length: int
    default_value: str
    field_order: int
