from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class MappingTemplate(Base):
    __tablename__ = "mapping_templates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    template_name = Column(String, index=True, nullable=False)
    description = Column(String, index=True, nullable=False)
    created_at = Column(DateTime, index=True, nullable=False)
    is_active = Column(Boolean, index=True, nullable=False)

    user = relationship("User", back_populates="mapping_templates")
