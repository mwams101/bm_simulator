from datetime import datetime

from pydantic import BaseModel


class UploadedFilesBase(BaseModel):
    id: int
    migration_job_id: int
    original_filename: str
    uploaded_filename: str
    file_path: str
    file_type: str
    file_size: int
    upload_timestamp: datetime
    expiry_timestamp: datetime
    is_deleted: bool

class UploadedFileCreate(BaseModel):
    migration_job_id: int
    original_filename: str
    uploaded_filename: str
    file_path: str
    file_type: str