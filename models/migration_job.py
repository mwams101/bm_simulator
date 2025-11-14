from tokenize import String

from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship

from database import Base


class MigrationJob(Base):
    __tablename__ = 'migration_job'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    job_name = Column(String, nullable=False)
    status = Column(postgresql.ENUM(
        'pending', 'mapping', 'validating', 'previewing', 'executing', 'completed', 'failed'
        , name='status', create_type=False
    ))
    created_at = Column(DateTime, nullable=False)
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    total_records = Column(Integer, nullable=False)
    successful_records = Column(Integer, nullable=False)
    failed_records = Column(Integer, nullable=False)
    error_message = Column(String, nullable=False)

    user = relationship("User", back_populates="migration_jobs")

    uploaded_file = relationship("UploadedFile", back_populates="migration_jobs")
