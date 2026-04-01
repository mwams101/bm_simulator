import enum
from datetime import datetime

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

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    total_records = Column(Integer, default=0)
    successful_records = Column(Integer, default=0)
    failed_records = Column(Integer, default=0)
    error_message = Column(String, nullable=True)

    user = relationship("User", back_populates="migration_jobs")
    uploaded_files = relationship("UploadedFile", back_populates="migration_job")
    field_mappings = relationship("FieldMapping", back_populates="migration_job")
    migration_records = relationship("MigrationRecord", back_populates="migration_job")
    validation_results = relationship("ValidationResult", back_populates="migration_job")
    duplicate_detections = relationship("DuplicateDetection", back_populates="migration_job")
    migration_reports = relationship("MigrationReport", back_populates="migration_job")
    notifications = relationship("Notification", back_populates="migration_job")
    audit_logs = relationship("AuditLog", back_populates="migration_job")
    new_bank_customers = relationship("NewBankCustomer", back_populates="migration_job")
    new_bank_accounts = relationship("NewBankAccount", back_populates="migration_job")