import datetime
import enum

from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Enum
from sqlalchemy.orm import Relationship

from database import Base


class MigrationReportType(enum.Enum):
    SUMMARY = 'summary'
    DETAILED = 'detailed'
    VALIDATION = 'validation'


class MigrationReportFormat(enum.Enum):
    PDF = 'pdf'
    CSV = 'csv'
    JSON = 'json'


class MigrationReport(Base):
    __tablename__ = 'migration_reports'

    id = Column(Integer, primary_key=True, index=True)
    migration_job_id = Column(Integer, ForeignKey('migration_jobs.id'), index=True)

    report_file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False, default=0)

    report_type = Column(Enum(MigrationReportType), index=True)
    format = Column(Enum(MigrationReportFormat), nullable=False)

    datetime = Column(DateTime, default=datetime.datetime.utcnow)

    # migration_job = Relationship('MigrationJob', back_populates='migration_reports', uselist=False)
