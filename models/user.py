from datetime import datetime

from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, autoincrement=True,  primary_key=True, index=True)
    user_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String, index=True)
    role = Column(postgresql.ENUM('admin', 'user', name='role', create_type=False) )
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    last_login = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    mapping_template = relationship("MappingTemplate", back_populates="users")