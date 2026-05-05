"""
Report Service — Stage 4 (final) of the migration pipeline.

Responsibility:
    - Triggered after a job reaches COMPLETED or FAILED status
    - Generates a JSON report file summarising the migration outcome
    - Persists a MigrationReport row pointing to that file
    - Creates an in-app Notification for the job owner
    - Writes an AuditLog entry recording the report action

Report content (JSON):
    {
      "job":         { id, name, status, started_at, completed_at },
      "counts":      { total_records, successful_records, failed_records },
      "validation":  { total_issues, errors, warnings, by_type: {...} },
      "duplicates":  { groups_detected },
      "failed_records": [ { record_id, error_message }, ... ]   (capped at 100)
    }

The file is written to  REPORT_DIR/<job_id>/<timestamp>_<report_type>.json
(configurable via the REPORT_DIR env-var; defaults to "reports").
"""

import json
import os
from collections import defaultdict
from datetime import datetime
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

import models
from models.audit_log import AuditLog, AuditLogActionType
from models.migration_job import JobStatus
from models.migration_record import MigrationRecordStatus
from models.migration_report import MigrationReport, MigrationReportType, MigrationReportFormat
from models.notification import Notification, NotificationStatus, NotificationType
from models.validation_result import ValidationResultSeverity

REPORT_DIR = os.getenv("REPORT_DIR", "reports")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _build_report_payload(job: models.MigrationJob, db: Session, report_type: MigrationReportType) -> dict:
    """Assemble the dict that will be serialised to JSON."""

    # --- Validation summary ---
    validation_results = (
        db.query(models.ValidationResult)
        .filter(models.ValidationResult.migration_job_id == job.id)
        .all()
    )
    errors = sum(1 for v in validation_results if v.severity == ValidationResultSeverity.ERROR)
    warnings = sum(1 for v in validation_results if v.severity == ValidationResultSeverity.WARNING)
    by_type: dict[str, int] = defaultdict(int)
    for vr in validation_results:
        by_type[vr.validation_type.value] += 1

    # --- Duplicate groups ---
    dup_count = (
        db.query(models.DuplicateDetection)
        .filter(models.DuplicateDetection.migration_job_id == job.id)
        .count()
    )

    payload: dict = {
        "job": {
            "id": job.id,
            "name": job.name,
            "status": job.status.value,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        },
        "counts": {
            "total_records": job.total_records or 0,
            "successful_records": job.successful_records or 0,
            "failed_records": job.failed_records or 0,
        },
        "validation": {
            "total_issues": len(validation_results),
            "errors": errors,
            "warnings": warnings,
            "by_type": dict(by_type),
        },
        "duplicates": {
            "groups_detected": dup_count,
        },
    }

    if report_type in (MigrationReportType.DETAILED, MigrationReportType.VALIDATION):
        failed_records = (
            db.query(models.MigrationRecord)
            .filter(
                models.MigrationRecord.migration_job_id == job.id,
                models.MigrationRecord.status == MigrationRecordStatus.FAILED,
            )
            .limit(100)
            .all()
        )
        payload["failed_records"] = [
            {"record_id": r.id, "error_message": r.error_message or ""}
            for r in failed_records
        ]

    return payload


def _write_report_file(job_id: int, report_type: MigrationReportType, payload: dict) -> tuple[str, int]:
    """Write JSON to disk. Returns (file_path, file_size_bytes)."""
    job_dir = os.path.join(REPORT_DIR, str(job_id))
    _ensure_dir(job_dir)

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{ts}_{report_type.value}.json"
    file_path = os.path.join(job_dir, filename)

    content = json.dumps(payload, indent=2, default=str)
    with open(file_path, "w", encoding="utf-8") as fh:
        fh.write(content)

    return file_path, len(content.encode("utf-8"))


# ---------------------------------------------------------------------------
# Main service entry point
# ---------------------------------------------------------------------------

def run(
    job_id: int,
    db: Session,
    report_type: MigrationReportType = MigrationReportType.SUMMARY,
    report_format: MigrationReportFormat = MigrationReportFormat.JSON,
) -> dict:
    """
    Generate a post-execution report for a migration job.

    Args:
        job_id:        ID of the MigrationJob.
        db:            Active SQLAlchemy session.
        report_type:   SUMMARY | DETAILED | VALIDATION
        report_format: JSON (only JSON is implemented; PDF/CSV are stubs)

    Returns:
        dict with report_id, file_path, file_size, report_type, status.
    """

    # 1. Load job — must be COMPLETED or FAILED
    job = db.query(models.MigrationJob).filter(models.MigrationJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Migration job not found")
    if job.status not in (JobStatus.COMPLETED, JobStatus.FAILED):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Report can only be generated for COMPLETED or FAILED jobs. "
                f"Current status: {job.status.value}"
            ),
        )

    if report_format != MigrationReportFormat.JSON:
        raise HTTPException(
            status_code=400,
            detail=f"Report format '{report_format.value}' is not yet implemented. Use 'json'.",
        )

    try:
        now = datetime.utcnow()

        # 2. Build and persist the report file
        payload = _build_report_payload(job, db, report_type)
        file_path, file_size = _write_report_file(job_id, report_type, payload)

        # 3. Persist MigrationReport row
        report = MigrationReport(
            migration_job_id=job_id,
            report_file_path=file_path,
            file_size=file_size,
            report_type=report_type,
            format=report_format,
            datetime=now,
        )
        db.add(report)
        db.flush()  # get report.id

        # 4. Notify the job owner (in-app)
        status_label = job.status.value.upper()
        notification = Notification(
            user_id=job.user_id,
            migration_job_id=job_id,
            notification_type=NotificationType.IN_APP,
            recipient=str(job.user_id),
            subject=f"Migration report ready — Job #{job_id} ({status_label})",
            message=(
                f"The {report_type.value} report for migration job '{job.name}' is ready. "
                f"Successful: {job.successful_records or 0}, "
                f"Failed: {job.failed_records or 0}. "
                f"Report ID: {report.id}."
            ),
            status=NotificationStatus.SENT,
            created_at=now,
            sent_at=now,
        )
        db.add(notification)

        # 5. Audit log
        audit = AuditLog(
            user_id=job.user_id,
            migration_job_id=job_id,
            action_type=AuditLogActionType.DOWNLOAD,
            action_description=(
                f"Generated {report_type.value} report (ID {report.id}) "
                f"for job '{job.name}' (status: {status_label}). "
                f"File: {file_path}, size: {file_size} bytes."
            ),
            timestamp=now,
        )
        db.add(audit)

        db.commit()

        return {
            "report_id": report.id,
            "report_type": report_type.value,
            "format": report_format.value,
            "file_path": file_path,
            "file_size_bytes": file_size,
            "job_status": job.status.value,
            "successful_records": job.successful_records or 0,
            "failed_records": job.failed_records or 0,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")