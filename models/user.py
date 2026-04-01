import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, TIMESTAMP, Enum
from sqlalchemy.orm import relationship

from database import Base


class UserRole(enum.Enum):
    ADMIN = 'admin'
    USER = 'user'


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)

    user_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String, index=True)

    role = Column(Enum(UserRole), default=UserRole.USER)

    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    last_login = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    migration_jobs = relationship("MigrationJob", back_populates="user")
    mapping_templates = relationship("MappingTemplate", back_populates="user")
    destination_schemas = relationship("DestinationSchema", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
