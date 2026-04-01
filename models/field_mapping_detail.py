from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import Relationship

from database import Base


class FieldMappingDetail(Base):
    __tablename__ = 'field_mapping_details'

    id = Column(Integer, primary_key=True, index=True)
    field_mapping_id = Column(Integer, ForeignKey('field_mappings.id'),nullable=False)

    source_field = Column(String, nullable=False)
    destination_field = Column(String, nullable=False)
    transformation_rule = Column(String, nullable=True)
    field_order = Column(Integer, nullable=False)

    field_mapping = Relationship("FieldMapping", back_populates='field_mapping_details')
