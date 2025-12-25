from pydantic import BaseModel


class DestinationSchemaBase(BaseModel):
    created_by: int
    schema_name: str
    description: str


class DestinationSchemaCreate(BaseModel):
    schema_name: str
    description: str
