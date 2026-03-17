from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

import models
from db.session import get_db
from modules.security.auth import require_admin
from schemas.migration_records import MigrationRecordsBase, MigrationRecordsCreate, MigrationRecordsUpdate

router = APIRouter(
    prefix="/migration-records",
    tags=["migration-records"]
)


@router.get("/", response_model=List[MigrationRecordsBase])
async def get_migration_records(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    return db.query(models.MigrationRecord).all()


@router.get("/{migration_record_id}", response_model=MigrationRecordsBase)
async def get_migration_record_by_id(
        migration_record_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    migration_record = db.query(models.MigrationRecord).filter(
        models.MigrationRecord.id == migration_record_id
    ).first()

    if not migration_record:
        raise HTTPException(status_code=404, detail="Migration record not found")

    return migration_record


@router.get("/by-job/{migration_job_id}", response_model=List[MigrationRecordsBase])
async def get_migration_records_by_job(
        migration_job_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    return db.query(models.MigrationRecord).filter(
        models.MigrationRecord.migration_job_id == migration_job_id
    ).all()


@router.post("/", response_model=MigrationRecordsBase)
async def create_migration_record(
        migration_record: MigrationRecordsCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    migration_job = db.query(models.MigrationJob).filter(
        models.MigrationJob.id == migration_record.migration_job_id
    ).first()

    if not migration_job:
        raise HTTPException(status_code=404, detail="Migration job not found")

    new_migration_record = models.MigrationRecord(
        migration_job_id=migration_record.migration_job_id,
        source_record_id=migration_record.source_record_id,
        source_data=migration_record.source_data,
        transformed_data=migration_record.transformed_data,
        status=migration_record.status,
        error_message=migration_record.error_message
    )

    db.add(new_migration_record)
    db.commit()
    db.refresh(new_migration_record)

    return new_migration_record


@router.put("/{migration_record_id}", response_model=MigrationRecordsBase)
async def update_migration_record(
        migration_record_id: int,
        migration_record: MigrationRecordsUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    existing = db.query(models.MigrationRecord).filter(
        models.MigrationRecord.id == migration_record_id
    ).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Migration record not found")

    existing.status = migration_record.status
    existing.transformed_data = migration_record.transformed_data
    existing.error_message = migration_record.error_message

    db.commit()
    db.refresh(existing)

    return existing


@router.delete("/{migration_record_id}")
async def delete_migration_record(
        migration_record_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    migration_record = db.query(models.MigrationRecord).filter(
        models.MigrationRecord.id == migration_record_id
    ).first()

    if not migration_record:
        raise HTTPException(status_code=404, detail="Migration record not found")

    db.delete(migration_record)
    db.commit()

    return {"message": "Migration record successfully deleted"}