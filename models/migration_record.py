import enum
from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, Enum, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Relationship

from database import Base


class MigrationRecordStatus(enum.Enum):
    SUCCESS = 'success'
    FAILED = 'failed'
    SKIPPED = 'skipped'


class MigrationRecord(Base):
    __tablename__ = 'migration_records'

    id = Column(Integer, primary_key=True, index=True)
    migration_job_id = Column(Integer, ForeignKey('migration_jobs.id'), nullable=False)
    source_record_id = Column(Integer, nullable=False)

    source_data = Column(JSON, nullable=False)
    transformed_data = Column(JSON, nullable=False)

    status = Column(Enum(MigrationRecordStatus), nullable=False)
    error_message = Column(String, nullable=True)
    migrated_at = Column(DateTime, default=datetime.utcnow)

    # migration_job = Relationship('MigrationJob', back_populates='migration_records')
