from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.hybrid import hybrid_property
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

    user = Relationship('User', back_populates='destination_schemas')
    schema_fields = Relationship('SchemaField', back_populates='destination_schema')

    @hybrid_property
    def created_by_name(self):
        return self.user.user_name if self.user else ""

