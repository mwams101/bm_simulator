from pydantic import BaseModel


class FieldMappingDetails(BaseModel):
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
