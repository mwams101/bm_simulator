from pydantic import BaseModel


class FieldMappingDetailsBase(BaseModel):
    id: int
    field_mapping_id: int
    source_field: str
    destination_field: str
    field_order: int
    transformation_rule: str

class FieldMappingDetailsCreate(BaseModel):
    field_mapping_id: int
    source_field: str
    destination_field: str
    field_order: int
    transformation_rule: str

model_config = {"from_attributes": True}