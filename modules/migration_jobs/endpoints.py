from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.params import Depends
from sqlalchemy.orm import Session

import models
from db.session import get_db
from modules.security.auth import require_admin
from schemas.migration_jobs import MigrationJobsBase, MigrationJobsCreate, MigrationJobsUpdate
from models.migration_report import MigrationReportType, MigrationReportFormat
from services import mapping_service, validation_service, execution_service, report_service

router = APIRouter(
    prefix="/migration-jobs",
    tags=["migration-jobs"]
)


@router.get("/", response_model=List[MigrationJobsBase])
async def get_migration_jobs(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    migration_jobs = db.query(models.MigrationJob).all()
    return migration_jobs


@router.get("/{migration_job_id}", response_model=MigrationJobsBase)
async def get_migration_job_by_id(
        migration_job_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    migration_job = db.query(models.MigrationJob).filter(models.MigrationJob.id == migration_job_id).first()
    return migration_job


@router.post("/", response_model=MigrationJobsBase)
async def create_migration_job(
        migration_job: MigrationJobsCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    existing_migration_job = db.query(models.MigrationJob).filter(
        models.MigrationJob.name == migration_job.name).first()

    if existing_migration_job:
        raise HTTPException(status_code=400, detail="Migration job with the same name already exists")

    new_migration_job = models.MigrationJob(
        user_id=current_user.id,
        destination_schema_id=migration_job.destination_schema_id,
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
        current_user: models.User = Depends(require_admin)
):
    existing_migration_job = db.query(models.MigrationJob).filter(models.MigrationJob.id == migration_job_id).first()

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


@router.post("/{migration_job_id}/start-mapping")
async def start_mapping(
        migration_job_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    return mapping_service.run(job_id=migration_job_id, db=db)


@router.post("/{migration_job_id}/start-validation")
async def start_validation(
        migration_job_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    return validation_service.run(job_id=migration_job_id, db=db)


@router.post("/{migration_job_id}/start-execution")
async def start_execution(
        migration_job_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    return execution_service.run(job_id=migration_job_id, db=db)


@router.post("/{migration_job_id}/generate-report")
async def generate_report(
        migration_job_id: int,
        report_type: MigrationReportType = Query(default=MigrationReportType.SUMMARY),
        report_format: MigrationReportFormat = Query(default=MigrationReportFormat.JSON),
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    return report_service.run(
        job_id=migration_job_id,
        db=db,
        report_type=report_type,
        report_format=report_format,
    )


@router.delete("/{migration_job_id}")
async def delete_migration_job_by_id(
        migration_job_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    migration_job = db.query(models.MigrationJob).filter(models.MigrationJob.id == migration_job_id).first()

    if not migration_job:
        raise HTTPException(status_code=404, detail="Migration job with the given id does not exist")

    db.delete(migration_job)
    db.commit()
    return {"message": "Migration job successfully deleted"}
