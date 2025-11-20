import enum

from sqlalchemy import Column, Integer, DateTime, Boolean, String, ForeignKey, Enum
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship

from database import Base


class UploadFileType(enum.Enum):
    CSV = 'csv'
    EXCEL = 'excel'


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    migration_job_id = Column(Integer, ForeignKey("migration_jobs.id"), nullable=False)

    original_filename = Column(String, index=True, nullable=False)
    uploaded_filename = Column(String, index=True, nullable=False)
    file_path = Column(String, index=True, nullable=False)
    file_type = Column(Enum(UploadFileType), index=True, nullable=False)
    file_size = Column(Integer, index=True, nullable=False)

    upload_timestamp = Column(DateTime, index=True, nullable=False)
    expiry_timestamp = Column(DateTime, index=True, nullable=False)

    is_deleted = Column(Boolean, nullable=False, default=False)

    # migration_job = relationship("MigrationJob", back_populates="uploaded_files")
