from sqlalchemy import Column, Integer, ForeignKey, String, Boolean
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

    destination_schema = Relationship('DestinationSchema', back_populates='schema_fields')
