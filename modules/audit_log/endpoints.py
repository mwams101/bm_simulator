from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

import models
from db.session import get_db
from modules.security.auth import require_admin
from schemas.audit_logs import AuditLogsBase, AuditLogsCreate

router = APIRouter(
    prefix="/audit-logs",
    tags=["audit-logs"]
)


@router.get("/", response_model=List[AuditLogsBase])
async def get_audit_logs(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    return db.query(models.AuditLog).all()


@router.get("/{audit_log_id}", response_model=AuditLogsBase)
async def get_audit_log_by_id(
        audit_log_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    audit_log = db.query(models.AuditLog).filter(
        models.AuditLog.id == audit_log_id
    ).first()

    if not audit_log:
        raise HTTPException(status_code=404, detail="Audit log not found")

    return audit_log


@router.get("/by-user/{user_id}", response_model=List[AuditLogsBase])
async def get_audit_logs_by_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    return db.query(models.AuditLog).filter(
        models.AuditLog.user_id == user_id
    ).all()


@router.post("/", response_model=AuditLogsBase)
async def create_audit_log(
        audit_log: AuditLogsCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    new_audit_log = models.AuditLog(
        user_id=audit_log.user_id,
        migration_job_id=audit_log.migration_job_id,
        action_type=audit_log.action_type,
        action_description=audit_log.action_description,
        ip_address=audit_log.ip_address,
        request_data=audit_log.request_data,
        response_data=audit_log.response_data
    )

    db.add(new_audit_log)
    db.commit()
    db.refresh(new_audit_log)

    return new_audit_log


@router.delete("/{audit_log_id}")
async def delete_audit_log(
        audit_log_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    audit_log = db.query(models.AuditLog).filter(
        models.AuditLog.id == audit_log_id
    ).first()

    if not audit_log:
        raise HTTPException(status_code=404, detail="Audit log not found")

    db.delete(audit_log)
    db.commit()

    return {"message": "Audit log successfully deleted"}