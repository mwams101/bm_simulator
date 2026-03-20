from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

import models
from db.session import get_db
from modules.security.auth import require_admin
from schemas.validation_results import ValidationResultsBase, ValidationResultsCreate, ValidationResultsUpdate

router = APIRouter(
    prefix="/validation-results",
    tags=["validation-results"]
)


@router.get("/", response_model=List[ValidationResultsBase])
async def get_validation_results(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    return db.query(models.ValidationResult).all()


@router.get("/{validation_result_id}", response_model=ValidationResultsBase)
async def get_validation_result_by_id(
        validation_result_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    validation_result = db.query(models.ValidationResult).filter(
        models.ValidationResult.id == validation_result_id
    ).first()

    if not validation_result:
        raise HTTPException(status_code=404, detail="Validation result not found")

    return validation_result


@router.get("/by-job/{migration_job_id}", response_model=List[ValidationResultsBase])
async def get_validation_results_by_job(
        migration_job_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    return db.query(models.ValidationResult).filter(
        models.ValidationResult.migration_job_id == migration_job_id
    ).all()


@router.post("/", response_model=ValidationResultsBase)
async def create_validation_result(
        validation_result: ValidationResultsCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    migration_job = db.query(models.MigrationJob).filter(
        models.MigrationJob.id == validation_result.migration_job_id
    ).first()

    if not migration_job:
        raise HTTPException(status_code=404, detail="Migration job not found")

    new_validation_result = models.ValidationResult(
        migration_job_id=validation_result.migration_job_id,
        record_number=validation_result.record_number,
        validation_type=validation_result.validation_type,
        field_name=validation_result.field_name,
        error_message=validation_result.error_message,
        original_value=validation_result.original_value,
        suggested_value=validation_result.suggested_value,
        severity=validation_result.severity,
        validated_at=validation_result.validated_at
    )

    db.add(new_validation_result)
    db.commit()
    db.refresh(new_validation_result)

    return new_validation_result


@router.put("/{validation_result_id}", response_model=ValidationResultsBase)
async def update_validation_result(
        validation_result_id: int,
        validation_result: ValidationResultsUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    existing = db.query(models.ValidationResult).filter(
        models.ValidationResult.id == validation_result_id
    ).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Validation result not found")

    existing.validation_type = validation_result.validation_type
    existing.field_name = validation_result.field_name
    existing.error_message = validation_result.error_message
    existing.original_value = validation_result.original_value
    existing.suggested_value = validation_result.suggested_value
    existing.severity = validation_result.severity

    db.commit()
    db.refresh(existing)

    return existing


@router.delete("/{validation_result_id}")
async def delete_validation_result(
        validation_result_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    validation_result = db.query(models.ValidationResult).filter(
        models.ValidationResult.id == validation_result_id
    ).first()

    if not validation_result:
        raise HTTPException(status_code=404, detail="Validation result not found")

    db.delete(validation_result)
    db.commit()

    return {"message": "Validation result successfully deleted"}