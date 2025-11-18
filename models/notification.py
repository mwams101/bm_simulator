import enum
from datetime import datetime

from sqlalchemy import Integer, Column, ForeignKey, DateTime, String, Enum
from sqlalchemy.orm import Relationship

from database import Base


class NotificationStatus(enum.Enum):
    PENDING = 'pending'
    SENT = 'sent'
    FAILED = 'failed'


class NotificationType(enum.Enum):
    EMAIL = 'email'
    SMS = 'sms'
    IN_APP = 'in_app'


class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    migration_job_id = Column(Integer, ForeignKey('migration_jobs.id'))

    notification_type = Column(Enum(NotificationType), nullable=False)
    recipient = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    message = Column(String, nullable=False)
    status = Column(Enum(NotificationStatus), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = Relationship('User', back_populates='notifications', uselist=False)
    migration_job = Relationship('MigrationJob', back_populates='notifications')
