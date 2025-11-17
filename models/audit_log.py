from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, String, TIMESTAMP
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship

from database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    migration_job_id = Column(Integer, ForeignKey('job.id'), nullable=False)
    action_type = Column(postgresql.ENUM("login", "logout", "upload", "map", "validate","execute","download","delete"))
    action_description = Column(String, nullable=False)
    ip_address = Column(String, nullable=False)
    request_data = Column(String, nullable=False)
    response_data = Column(String, nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)


    user = relationship("User", back_populates="audit_log")
    migration_job = relationship("MigrationJob", back_populates="audit_log")