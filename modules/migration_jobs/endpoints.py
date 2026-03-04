from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql.visitors import replacement_traverse

import models
from db.session import get_db
from modules.security.auth import require_admin
from schemas.migration_jobs import MigrationJobsBase, MigrationJobsCreate, MigrationJobsUpdate

router = APIRouter(
    prefix="/migration-jobs",
    tags=["migration-jobs"]
)

@router.get("/", response_model=List[MigrationJobsBase])
async def get_migration_jobs(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin())
):

    migration_jobs = db.query(models.MigrationJob).all()
    return migration_jobs

@router.get("/{id}", response_model=MigrationJobsBase)
async def get_migration_job_by_id(
        migration_job_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin())
):
    migration_job = db.query(models.MigrationJob).filter(migration_job_id == models.MigrationJob.id).first()
    return migration_job

@router.post("/", response_model=MigrationJobsCreate)
async def create_migration_job(
        migration_job: MigrationJobsBase,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin())
):

    existing_migration_job = db.query(models.MigrationJob).filter(migration_job.name == migration_job.name).first()

    if existing_migration_job:
        raise HTTPException(status_code=400, detail="Migration job with the same name already exists")

    new_migration_job = models.MigrationJob(
        user_id=current_user.id,
        name=migration_job.name,
        status=migration_job.status,
        started_at=migration_job.started_at,
        completed_at=migration_job.completed_at,
        total_records=migration_job.total_records,
        successful_records=migration_job.successful_records,
        failed_records=migration_job.failed_records,
        error_message=migration_job.error_message
    )

    db.add(new_migration_job)
    db.commit()
    db.refresh(new_migration_job)

    return new_migration_job


@router.put("/{migration_job_id}", response_model=MigrationJobsBase)
async def update_migration_job(
        migration_job_id: int,
        migration_job: MigrationJobsUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin())
):
    existing_migration_job = db.query(models.MigrationJob).filter(migration_job_id == migration_job.id).first()

    if not existing_migration_job:
        raise HTTPException(status_code=404, detail="Migration job with the given id does not exist")

    existing_migration_job.name = migration_job.name
    existing_migration_job.status = migration_job.status
    existing_migration_job.total_records = migration_job.total_records
    existing_migration_job.successful_records = migration_job.successful_records
    existing_migration_job.failed_records = migration_job.failed_records
    existing_migration_job.error_message = migration_job.error_message

    db.commit()
    db.refresh(existing_migration_job)
    return existing_migration_job


@router.delete("/{migration_job_id}")
async def delete_migration_job_by_id(
        migration_job_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin())
):
    migration_job = db.query(models.MigrationJob).filter(migration_job_id == models.MigrationJob.id).first()

    if not migration_job:
        raise HTTPException(status_code=404, detail="Migration job with the given id does not exist")

    db.delete(migration_job)
    db.commit()
    return {"message": "Migration job successfully deleted"}

