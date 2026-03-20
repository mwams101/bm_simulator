from datetime import datetime
from pydantic import BaseModel


class ValidationResultsBase(BaseModel):
    id: int
    migration_job_id: int
    record_number: int
    validation_type: str
    field_name: str
    error_message: str
    original_value: str
    suggested_value: str
    severity: str
    validated_at: datetime

    model_config = {"from_attributes": True}


class ValidationResultsCreate(BaseModel):
    migration_job_id: int
    record_number: int
    validation_type: str
    field_name: str
    error_message: str
    original_value: str
    suggested_value: str
    severity: str
    validated_at: datetime


class ValidationResultsUpdate(BaseModel):
    validation_type: str
    field_name: str
    error_message: str
    original_value: str
    suggested_value: str
    severity: str