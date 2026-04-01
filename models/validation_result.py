import enum

from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Enum
from sqlalchemy.orm import relationship

from database import Base


class ValidationResultType(enum.Enum):
    MISSING_FIELD = 'missing_field'
    INVALID_FIELD = 'invalid_field'
    DUPLICATE_FIELD = 'duplicate_field'
    DATA_TYPE_MISMATCH = 'data_type_mismatch'


class ValidationResultSeverity(enum.Enum):
    ERROR = 'error'
    WARNING = 'warning'
    INFO = 'info'


class ValidationResult(Base):
    __tablename__ = "validation_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    migration_job_id = Column(Integer, ForeignKey("migration_jobs.id"), nullable=False)

    record_number = Column(Integer, ForeignKey("migration_records.id"), nullable=False)
    validation_type = Column(Enum(ValidationResultType), nullable=False)
    field_name = Column(String, nullable=False)
    error_message = Column(String, nullable=False)
    original_value = Column(String, nullable=False)
    suggested_value = Column(String, nullable=False)
    severity = Column(Enum(ValidationResultSeverity), nullable=False)

    validated_at = Column(DateTime(timezone=True), nullable=False)

    migration_job = relationship("MigrationJob", back_populates="validation_results")
