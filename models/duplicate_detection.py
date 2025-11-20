import enum
from datetime import datetime

from sqlalchemy import Integer, Column, ForeignKey, DateTime, String, Enum
from sqlalchemy.orm import Relationship

from database import Base


class DetectionResolution(str, enum.Enum):
    SKIP = "skip"
    MERGE = "merge"
    MANUAL_REVIEW = "manual_review"


class DuplicateDetection(Base):
    __tablename__ = 'duplicate_detections'

    id = Column(Integer, primary_key=True, index=True)
    migration_job_id = Column(Integer, ForeignKey('migration_jobs.id'), nullable=False)

    duplicate_key_hash = Column(String, nullable=False)
    record_count = Column(Integer, nullable=False)
    record_ids = Column(String, nullable=False)
    resolution = Column(Enum(DetectionResolution), nullable=False)

    detected_at = Column(DateTime, default=datetime.utcnow)

    # migration_job = Relationship('MigrationJob', back_populates='duplicate_detections')
