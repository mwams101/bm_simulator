import json
import os
from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

import models
from db.session import get_db
from models.migration_report import MigrationReportType, MigrationReportFormat
from modules.security.auth import require_admin
from schemas.migration_reports import MigrationReportsBase, MigrationReportsCreate, MigrationReportsUpdate
from services import report_service

router = APIRouter(
    prefix="/migration-reports",
    tags=["migration-reports"]
)


@router.get("/", response_model=List[MigrationReportsBase])
async def get_migration_reports(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    return db.query(models.MigrationReport).all()


@router.get("/{migration_report_id}", response_model=MigrationReportsBase)
async def get_migration_report_by_id(
        migration_report_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    migration_report = db.query(models.MigrationReport).filter(
        models.MigrationReport.id == migration_report_id
    ).first()

    if not migration_report:
        raise HTTPException(status_code=404, detail="Migration report not found")

    return migration_report


@router.get("/by-job/{migration_job_id}", response_model=List[MigrationReportsBase])
async def get_migration_reports_by_job(
        migration_job_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    return db.query(models.MigrationReport).filter(
        models.MigrationReport.migration_job_id == migration_job_id
    ).all()


@router.post("/", response_model=MigrationReportsBase)
async def create_migration_report(
        migration_report: MigrationReportsCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    migration_job = db.query(models.MigrationJob).filter(
        models.MigrationJob.id == migration_report.migration_job_id
    ).first()

    if not migration_job:
        raise HTTPException(status_code=404, detail="Migration job not found")

    new_migration_report = models.MigrationReport(
        migration_job_id=migration_report.migration_job_id,
        report_file_path=migration_report.report_file_path,
        file_size=migration_report.file_size,
        report_type=migration_report.report_type,
        format=migration_report.format
    )

    db.add(new_migration_report)
    db.commit()
    db.refresh(new_migration_report)

    return new_migration_report


@router.put("/{migration_report_id}", response_model=MigrationReportsBase)
async def update_migration_report(
        migration_report_id: int,
        migration_report: MigrationReportsUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    existing = db.query(models.MigrationReport).filter(
        models.MigrationReport.id == migration_report_id
    ).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Migration report not found")

    existing.report_file_path = migration_report.report_file_path
    existing.file_size = migration_report.file_size
    existing.report_type = migration_report.report_type
    existing.format = migration_report.format

    db.commit()
    db.refresh(existing)

    return existing


@router.post("/generate/{migration_job_id}")
async def generate_migration_report(
        migration_job_id: int,
        report_type: str = "summary",
        report_format: str = "json",
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    try:
        rt = MigrationReportType(report_type.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid report_type '{report_type}'. Use: summary, detailed, validation")
    try:
        rf = MigrationReportFormat(report_format.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid report_format '{report_format}'. Use: json")

    return report_service.run(migration_job_id, db, rt, rf)


@router.get("/{migration_report_id}/content")
async def get_migration_report_content(
        migration_report_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    report = db.query(models.MigrationReport).filter(
        models.MigrationReport.id == migration_report_id
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="Migration report not found")

    file_path = report.report_file_path
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Report file not found on disk: {file_path}")

    with open(file_path, "r", encoding="utf-8") as fh:
        return json.load(fh)


@router.delete("/{migration_report_id}")
async def delete_migration_report(
        migration_report_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    migration_report = db.query(models.MigrationReport).filter(
        models.MigrationReport.id == migration_report_id
    ).first()

    if not migration_report:
        raise HTTPException(status_code=404, detail="Migration report not found")

    db.delete(migration_report)
    db.commit()

    return {"message": "Migration report successfully deleted"}