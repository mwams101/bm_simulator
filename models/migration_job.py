import enum

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, String
from sqlalchemy.orm import relationship

from database import Base


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    MAPPING = "mapping"
    VALIDATING = "validating"
    PREVIEWING = "previewing"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


class MigrationJob(Base):
    __tablename__ = 'migration_jobs'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    name = Column(String, nullable=False)
    status = Column(Enum(JobStatus), nullable=False, default=JobStatus.PENDING)

    created_at = Column(DateTime, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    total_records = Column(Integer, default=0)
    successful_records = Column(Integer, default=0)
    failed_records = Column(Integer, default=0)
    error_message = Column(String, nullable=True)

    # user = relationship("User", back_populates="migration_jobs")
    # uploaded_file = relationship("UploadedFile", back_populates="migration_jobs")
    # validation_result = relationship("ValidationResult", back_populates="migration_jobs")