from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import Relationship

from database import Base


class DestinationSchema(Base):
    __tablename__ = 'destination_schemas'

    id = Column(Integer, primary_key=True, index=True)

    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)

    schema_name = Column(String, nullable=False)
    description = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = Relationship('User', back_populates='destination_schemas', uselist=False)
    schema_field = Relationship('SchemaField', back_populates='destination_schemas')

