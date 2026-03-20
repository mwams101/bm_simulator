from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

import models
from db.session import get_db
from modules.security.auth import require_admin
from schemas.duplicate_detections import DuplicateDetectionsBase, DuplicateDetectionsCreate, DuplicateDetectionsUpdate

router = APIRouter(
    prefix="/duplicate-detections",
    tags=["duplicate-detections"]
)


@router.get("/", response_model=List[DuplicateDetectionsBase])
async def get_duplicate_detections(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    return db.query(models.DuplicateDetection).all()


@router.get("/{duplicate_detection_id}", response_model=DuplicateDetectionsBase)
async def get_duplicate_detection_by_id(
        duplicate_detection_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    duplicate_detection = db.query(models.DuplicateDetection).filter(
        models.DuplicateDetection.id == duplicate_detection_id
    ).first()

    if not duplicate_detection:
        raise HTTPException(status_code=404, detail="Duplicate detection not found")

    return duplicate_detection


@router.get("/by-job/{migration_job_id}", response_model=List[DuplicateDetectionsBase])
async def get_duplicate_detections_by_job(
        migration_job_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    return db.query(models.DuplicateDetection).filter(
        models.DuplicateDetection.migration_job_id == migration_job_id
    ).all()


@router.post("/", response_model=DuplicateDetectionsBase)
async def create_duplicate_detection(
        duplicate_detection: DuplicateDetectionsCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    migration_job = db.query(models.MigrationJob).filter(
        models.MigrationJob.id == duplicate_detection.migration_job_id
    ).first()

    if not migration_job:
        raise HTTPException(status_code=404, detail="Migration job not found")

    new_duplicate_detection = models.DuplicateDetection(
        migration_job_id=duplicate_detection.migration_job_id,
        duplicate_key_hash=duplicate_detection.duplicate_key_hash,
        record_count=duplicate_detection.record_count,
        record_ids=duplicate_detection.record_ids,
        resolution=duplicate_detection.resolution
    )

    db.add(new_duplicate_detection)
    db.commit()
    db.refresh(new_duplicate_detection)

    return new_duplicate_detection


@router.put("/{duplicate_detection_id}", response_model=DuplicateDetectionsBase)
async def update_duplicate_detection(
        duplicate_detection_id: int,
        duplicate_detection: DuplicateDetectionsUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    existing = db.query(models.DuplicateDetection).filter(
        models.DuplicateDetection.id == duplicate_detection_id
    ).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Duplicate detection not found")

    existing.resolution = duplicate_detection.resolution

    db.commit()
    db.refresh(existing)

    return existing


@router.delete("/{duplicate_detection_id}")
async def delete_duplicate_detection(
        duplicate_detection_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    duplicate_detection = db.query(models.DuplicateDetection).filter(
        models.DuplicateDetection.id == duplicate_detection_id
    ).first()

    if not duplicate_detection:
        raise HTTPException(status_code=404, detail="Duplicate detection not found")

    db.delete(duplicate_detection)
    db.commit()

    return {"message": "Duplicate detection successfully deleted"}