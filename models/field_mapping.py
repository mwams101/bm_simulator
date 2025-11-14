from datetime import datetime

from pydantic import Json
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from database import Base


class FieldMapping(Base):
    __tablename__ = 'field_mapping'

    id = Column(Integer, primary_key=True, index=True)
    migration_job_id = Column(Integer, ForeignKey('migration_job.id'), nullable=False)
    mapping_template_id = Column(Integer, ForeignKey('mapping_template.id'), nullable=True)

    mapping_rules = Column(Json, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    migration_job = relationship('MigrationJob', back_populates='field_mappings', uselist=False)
    mapping_template = relationship('MappingTemplate', back_populates='field_mappings')