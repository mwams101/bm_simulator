"""
Validation Service — Stage 2 of the migration pipeline.

Responsibility:
    - Validate each PENDING MigrationRecord's transformed_data against the
      DestinationSchema's SchemaField rules
    - Detect duplicates across records on fields marked is_unique=True
    - Write ValidationResult per issue found (per record, per field)
    - Write DuplicateDetection for each group of duplicate values
    - Update each MigrationRecord status: SUCCESS or FAILED
    - Advance the job status from VALIDATING → PREVIEWING

Validation checks (in order per field):
    1. MISSING_FIELD   — required field is None or empty            → ERROR
    2. DATA_TYPE_MISMATCH — value doesn't match declared data_type  → ERROR
    3. MAX_LENGTH      — string value exceeds max_length            → WARNING
    4. VALIDATION_RULE — value fails the regex validation_rule      → WARNING
    5. DUPLICATE_FIELD — value is not unique across the batch       → ERROR
"""

import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime
from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

import models
from models.duplicate_detection import DetectionResolution, DuplicateDetection
from models.migration_job import JobStatus
from models.migration_record import MigrationRecordStatus
from models.validation_result import ValidationResult, ValidationResultType, ValidationResultSeverity


# ---------------------------------------------------------------------------
# Data type validators
# ---------------------------------------------------------------------------

def _is_float(value) -> bool:
    try:
        float(str(value))
        return True
    except (ValueError, TypeError):
        return False


def _is_date(value) -> bool:
    try:
        datetime.strptime(str(value), "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False


DATA_TYPE_VALIDATORS = {
    "string":  lambda v: isinstance(v, str),
    "str":     lambda v: isinstance(v, str),
    "integer": lambda v: str(v).lstrip("-").isdigit(),
    "int":     lambda v: str(v).lstrip("-").isdigit(),
    "float":   _is_float,
    "decimal": _is_float,
    "boolean": lambda v: str(v).lower() in ("true", "false", "1", "0"),
    "bool":    lambda v: str(v).lower() in ("true", "false", "1", "0"),
    "date":    _is_date,
    "email":   lambda v: bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", str(v))),
}


# ---------------------------------------------------------------------------
# Per-field check functions — return an error string or None
# ---------------------------------------------------------------------------

def _check_required(field: models.SchemaField, value) -> str | None:
    if field.is_required and value in (None, ""):
        return f"Required field '{field.name}' is missing or empty"
    return None


def _check_data_type(field: models.SchemaField, value) -> str | None:
    if value in (None, ""):
        return None
    validator = DATA_TYPE_VALIDATORS.get(field.data_type.lower())
    if validator and not validator(value):
        return f"Expected type '{field.data_type}' for field '{field.name}', got '{value}'"
    return None


def _check_max_length(field: models.SchemaField, value) -> str | None:
    if field.max_length and value not in (None, "") and len(str(value)) > field.max_length:
        return f"Field '{field.name}' exceeds max length of {field.max_length} characters"
    return None


def _check_validation_rule(field: models.SchemaField, value) -> str | None:
    if field.validation_rule and value not in (None, ""):
        try:
            if not re.fullmatch(field.validation_rule, str(value)):
                return f"Field '{field.name}' failed validation rule '{field.validation_rule}'"
        except re.error:
            pass  # Malformed regex — skip silently
    return None


# ---------------------------------------------------------------------------
# Main service entry point
# ---------------------------------------------------------------------------

def run(job_id: int, db: Session) -> dict:
    """
    Execute the validation stage for a migration job.

    Args:
        job_id: ID of the MigrationJob to process.
        db:     Active SQLAlchemy session.

    Returns:
        dict with total, successful, failed record counts and final job status.
    """

    # 1. Load and validate job state
    job = db.query(models.MigrationJob).filter(models.MigrationJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Migration job not found")
    if job.status != JobStatus.VALIDATING:
        raise HTTPException(
            status_code=400,
            detail=f"Job must be in VALIDATING status. Current status: {job.status.value}"
        )
    if not job.destination_schema_id:
        raise HTTPException(
            status_code=400,
            detail="Job has no destination schema linked. Set destination_schema_id on the job first."
        )

    try:
        # 2. Load PENDING migration records
        records: List[models.MigrationRecord] = (
            db.query(models.MigrationRecord)
            .filter(
                models.MigrationRecord.migration_job_id == job_id,
                models.MigrationRecord.status == MigrationRecordStatus.PENDING
            )
            .all()
        )
        if not records:
            raise HTTPException(status_code=400, detail="No pending migration records found for this job")

        # 3. Load destination schema and its fields
        destination_schema = (
            db.query(models.DestinationSchema)
            .filter(models.DestinationSchema.id == job.destination_schema_id)
            .first()
        )
        if not destination_schema or not destination_schema.schema_fields:
            raise HTTPException(status_code=400, detail="Destination schema not found or has no fields defined")

        schema_fields: List[models.SchemaField] = destination_schema.schema_fields
        field_map = {sf.name: sf for sf in schema_fields}
        unique_fields = [sf for sf in schema_fields if sf.is_unique]

        now = datetime.utcnow()
        successful = 0
        failed = 0

        # Track unique field values across records: { field_name: { value: [record_id, ...] } }
        unique_value_tracker: dict[str, dict[str, list[int]]] = defaultdict(lambda: defaultdict(list))

        # 4. Validate each record against schema field rules
        for record in records:
            data: dict = record.transformed_data or {}
            record_has_error = False

            for field_name, schema_field in field_map.items():
                value = data.get(field_name)

                checks = [
                    (_check_required(schema_field, value),       ValidationResultType.MISSING_FIELD,      ValidationResultSeverity.ERROR),
                    (_check_data_type(schema_field, value),      ValidationResultType.DATA_TYPE_MISMATCH, ValidationResultSeverity.ERROR),
                    (_check_max_length(schema_field, value),     ValidationResultType.INVALID_FIELD,      ValidationResultSeverity.WARNING),
                    (_check_validation_rule(schema_field, value), ValidationResultType.INVALID_FIELD,     ValidationResultSeverity.WARNING),
                ]

                for error_msg, v_type, severity in checks:
                    if error_msg:
                        db.add(ValidationResult(
                            migration_job_id=job_id,
                            record_number=record.id,
                            validation_type=v_type,
                            field_name=field_name,
                            error_message=error_msg,
                            original_value=str(value) if value is not None else "",
                            suggested_value=schema_field.default_value or "",
                            severity=severity,
                            validated_at=now,
                        ))
                        if severity == ValidationResultSeverity.ERROR:
                            record_has_error = True

            # Track values on unique fields for duplicate detection pass
            for sf in unique_fields:
                val = data.get(sf.name)
                if val is not None:
                    unique_value_tracker[sf.name][str(val)].append(record.id)

            record.status = MigrationRecordStatus.FAILED if record_has_error else MigrationRecordStatus.SUCCESS
            if record_has_error:
                failed += 1
            else:
                successful += 1

        # 5. Duplicate detection pass
        # Build a lookup for quick record access
        record_by_id = {r.id: r for r in records}

        for field_name, value_map in unique_value_tracker.items():
            for value, record_ids in value_map.items():
                if len(record_ids) <= 1:
                    continue

                key_hash = hashlib.md5(f"{field_name}:{value}".encode()).hexdigest()
                db.add(DuplicateDetection(
                    migration_job_id=job_id,
                    duplicate_key_hash=key_hash,
                    record_count=len(record_ids),
                    record_ids=json.dumps(record_ids),
                    resolution=DetectionResolution.MANUAL_REVIEW,
                    detected_at=now,
                ))

                for record_id in record_ids:
                    db.add(ValidationResult(
                        migration_job_id=job_id,
                        record_number=record_id,
                        validation_type=ValidationResultType.DUPLICATE_FIELD,
                        field_name=field_name,
                        error_message=f"Duplicate value '{value}' found in unique field '{field_name}'",
                        original_value=value,
                        suggested_value="",
                        severity=ValidationResultSeverity.ERROR,
                        validated_at=now,
                    ))

                    # Flip any records we previously counted as successful
                    affected = record_by_id.get(record_id)
                    if affected and affected.status != MigrationRecordStatus.FAILED:
                        affected.status = MigrationRecordStatus.FAILED
                        successful -= 1
                        failed += 1

        # 6. Update job counters and advance to PREVIEWING
        job.successful_records = successful
        job.failed_records = failed
        job.status = JobStatus.PREVIEWING
        db.commit()

        return {
            "total_records": len(records),
            "successful_records": successful,
            "failed_records": failed,
            "status": job.status.value,
        }

    except HTTPException:
        job.status = JobStatus.FAILED
        job.error_message = "Validation stage failed — see logs"
        db.commit()
        raise
    except Exception as e:
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")