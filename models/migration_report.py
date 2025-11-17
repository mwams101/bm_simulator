import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Relationship

from database import Base


class MigrationReport(Base):
    __tablename__ = 'migration_reports'

    id = Column(Integer, primary_key=True, index=True)
    migration_job_id = Column(Integer, ForeignKey('migration_jobs.id'), index=True)
    report_type = Column(ENUM('summary, detailed, validation', name='report_type', create_type=False), index=True)
    report_file_path = Column(String, nullable=False)
    format = Column(ENUM('pdf, csv, json'), nullable=False)
    datetime = Column(DateTime, default=datetime.datetime.utcnow)
    file_size = Column(Integer, nullable=False)

    migration_job = Relationship('MigrationJob', back_populates='migration_reports', uselist=False)
