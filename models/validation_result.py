from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship

from database import Base


class ValidationResult(Base):
    __tablename__ = "validation_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    migration_job_id = Column(Integer, ForeignKey("migration_job.id"), nullable=False)
    record_number = Column(Integer, ForeignKey("record_number.id"), nullable=False)
    validation_type = Column(postgresql.ENUM("missing_field", "invalid_format", "duplicate", "data_Type_mismatch"))
    field_name = Column(String, nullable=False)
    error_message = Column(String, nullable=False)
    original_value = Column(String, nullable=False)
    suggested_value = Column(String, nullable=False)
    severity = Column(postgresql.ENUM("error", "warning", "info"))
    validated_at = Column(DateTime(timezone=True),  nullable=False)

    migration_job = relationship("MigrationJob", back_populates="validation_results")