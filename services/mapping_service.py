"""
Mapping Service — Stage 1 of the migration pipeline.

Responsibility:
    - Parse the uploaded source file (CSV or Excel)
    - Apply field mapping rules to each row
    - Persist a MigrationRecord per row (source_data + transformed_data)
    - Advance the job status from PENDING → MAPPING → VALIDATING

Redundancy resolution (FieldMapping vs FieldMappingDetail):
    FieldMappingDetail rows are the authoritative source for field-to-field rules
    (source_field, destination_field, transformation_rule, field_order).

    FieldMapping.mapping_rules (JSON) is treated as optional global config for
    the job, e.g. {"skip_empty_rows": true, "encoding": "utf-8"}.
    It is NOT used for individual field rules — that is FieldMappingDetail's job.
"""

from datetime import datetime
from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

import models
from models.migration_job import JobStatus
from models.migration_record import MigrationRecord, MigrationRecordStatus
from services.file_readers import get_file_reader


# ---------------------------------------------------------------------------
# Transformation helpers
# ---------------------------------------------------------------------------

def _apply_transformation(value, rule: str | None):
    """Apply a transformation rule string to a single field value."""
    if not rule:
        return value
    rule = rule.strip().lower()

    if rule == "uppercase":
        return str(value).upper() if value is not None else value
    if rule == "lowercase":
        return str(value).lower() if value is not None else value
    if rule == "strip":
        return str(value).strip() if value is not None else value
    if rule.startswith("date_format:"):
        fmt = rule.split(":", 1)[1]
        try:
            return datetime.strptime(str(value), fmt).isoformat()
        except (ValueError, TypeError):
            return value

    # Unknown rule — pass value through unchanged
    return value


def _transform_row(raw_row: dict, details: List[models.FieldMappingDetail]) -> dict:
    """Map and transform a single source row into a destination row."""
    transformed = {}
    for detail in sorted(details, key=lambda d: d.field_order):
        source_val = raw_row.get(detail.source_field)
        transformed[detail.destination_field] = _apply_transformation(
            source_val, detail.transformation_rule
        )
    return transformed


# ---------------------------------------------------------------------------
# Main service entry point
# ---------------------------------------------------------------------------

def run(job_id: int, db: Session, storage_backend: str = "local") -> dict:
    """
    Execute the mapping stage for a migration job.

    Args:
        job_id:           ID of the MigrationJob to process.
        db:               Active SQLAlchemy session.
        storage_backend:  "local" (default) or "cloud".

    Returns:
        dict with records_created count and final job status.
    """

    # 1. Load and validate job state
    job = db.query(models.MigrationJob).filter(models.MigrationJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Migration job not found")
    if job.status != JobStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Job must be PENDING to start mapping. Current status: {job.status.value}"
        )

    # 2. Advance status to MAPPING
    job.status = JobStatus.MAPPING
    job.started_at = datetime.utcnow()
    db.commit()

    try:
        # 3. Load the uploaded source file
        uploaded_file = (
            db.query(models.UploadedFile)
            .filter(
                models.UploadedFile.migration_job_id == job_id,
                models.UploadedFile.is_deleted == False
            )
            .first()
        )
        if not uploaded_file:
            raise HTTPException(status_code=404, detail="No uploaded file found for this job")

        # 4. Load field mapping — FieldMappingDetail is authoritative for field rules.
        #    FieldMapping.mapping_rules holds optional global config (not field rules).
        field_mapping = (
            db.query(models.FieldMapping)
            .filter(models.FieldMapping.migration_job_id == job_id)
            .first()
        )
        if not field_mapping:
            raise HTTPException(status_code=400, detail="No field mapping defined for this job")

        details = field_mapping.field_mapping_details
        if not details:
            raise HTTPException(status_code=400, detail="Field mapping has no field mapping details")

        # Read optional global config from mapping_rules JSON
        global_config = field_mapping.mapping_rules or {}
        skip_empty_rows = global_config.get("skip_empty_rows", False)

        # 5. Parse file rows and create MigrationRecords
        reader = get_file_reader(storage_backend)
        records_created = 0

        for index, raw_row in enumerate(reader.read_rows(uploaded_file.file_path, uploaded_file.file_type)):
            if skip_empty_rows and all(v in (None, "") for v in raw_row.values()):
                continue

            transformed_row = _transform_row(raw_row, details)

            record = MigrationRecord(
                migration_job_id=job_id,
                source_record_id=index + 1,
                source_data=raw_row,
                transformed_data=transformed_row,
                status=MigrationRecordStatus.PENDING,
                migrated_at=datetime.utcnow()
            )
            db.add(record)
            records_created += 1

        # 6. Update job counters and advance to VALIDATING
        job.total_records = records_created
        job.status = JobStatus.VALIDATING
        db.commit()

        return {"records_created": records_created, "status": job.status.value}

    except HTTPException:
        job.status = JobStatus.FAILED
        job.error_message = "Mapping stage failed — see logs"
        db.commit()
        raise
    except Exception as e:
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Mapping failed: {str(e)}")