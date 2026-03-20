from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

import models
from db.session import get_db
from modules.security.auth import require_admin
from schemas.notifications import NotificationsBase, NotificationsCreate, NotificationsUpdate

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"]
)


@router.get("/", response_model=List[NotificationsBase])
async def get_notifications(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    return db.query(models.Notification).all()


@router.get("/{notification_id}", response_model=NotificationsBase)
async def get_notification_by_id(
        notification_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    notification = db.query(models.Notification).filter(
        models.Notification.id == notification_id
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    return notification


@router.get("/by-user/{user_id}", response_model=List[NotificationsBase])
async def get_notifications_by_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    return db.query(models.Notification).filter(
        models.Notification.user_id == user_id
    ).all()


@router.post("/", response_model=NotificationsBase)
async def create_notification(
        notification: NotificationsCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    new_notification = models.Notification(
        user_id=notification.user_id,
        migration_job_id=notification.migration_job_id,
        notification_type=notification.notification_type,
        recipient=notification.recipient,
        subject=notification.subject,
        message=notification.message,
        status=notification.status
    )

    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)

    return new_notification


@router.put("/{notification_id}", response_model=NotificationsBase)
async def update_notification(
        notification_id: int,
        notification: NotificationsUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    existing = db.query(models.Notification).filter(
        models.Notification.id == notification_id
    ).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Notification not found")

    existing.status = notification.status
    existing.sent_at = notification.sent_at

    db.commit()
    db.refresh(existing)

    return existing


@router.delete("/{notification_id}")
async def delete_notification(
        notification_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    notification = db.query(models.Notification).filter(
        models.Notification.id == notification_id
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    db.delete(notification)
    db.commit()

    return {"message": "Notification successfully deleted"}