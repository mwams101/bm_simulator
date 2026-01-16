from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, DateTime
from sqlalchemy.orm import Relationship

from database import Base


class SchemaField(Base):
    __tablename__ = 'schema_fields'

    id = Column(Integer, primary_key=True, index=True)
    destination_schema_id = Column(Integer, ForeignKey('destination_schemas.id'), nullable=False)

    name = Column(String, nullable=False)
    data_type = Column(String, nullable=False)
    is_required = Column(Boolean, nullable=False)
    is_unique = Column(Boolean, nullable=False)
    validation_rule = Column(String, nullable=False)
    max_length = Column(Integer, nullable=True)
    default_value = Column(String, nullable=True)
    field_order = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    destination_schemas = Relationship('DestinationSchema', back_populates='schema_fields')
