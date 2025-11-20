import enum
from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, String, TIMESTAMP, Enum
from sqlalchemy.orm import relationship

from database import Base


class AuditLogActionType(str, enum.Enum):
    LOGIN = 'login'
    LOGOUT = 'logout'
    UPLOAD = 'upload'
    MAP = 'map'
    VALIDATE = 'validate'
    EXECUTE = 'execute'
    DOWNLOAD = 'download'
    DELETE = 'delete'


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    migration_job_id = Column(Integer, ForeignKey('migration_jobs.id'), nullable=False)

    action_type = Column(Enum(AuditLogActionType), nullable=False)

    action_description = Column(String, nullable=False)
    ip_address = Column(String, nullable=False)
    request_data = Column(String, nullable=False)
    response_data = Column(String, nullable=False)

    timestamp = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    # user = relationship("User", back_populates="audit_logs")
    # migration_job = relationship("MigrationJob", back_populates="audit_logs")
