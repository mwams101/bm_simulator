from datetime import datetime
from tokenize import String

from sqlalchemy import Integer, Column, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Relationship

from database import Base


class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    migration_job_id = Column(Integer, ForeignKey('migration_jobs.id'))
    notification_type = Column(ENUM('email', 'sms', 'in_app', name='notification_type'), nullable=False)
    recipient = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    message = Column(String, nullable=False)
    status = Column(ENUM('pending', 'sent', 'failed', name='status'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = Relationship('User', back_populates='notifications', uselist=False)
    migration_job = Relationship('MigrationJob', back_populates='notifications')
