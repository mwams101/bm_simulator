from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

import models
from db.session import get_db
from modules.security.auth import require_admin
from schemas.uploaded_files import UploadedFilesBase
from services.file_storage import get_file_storage

router = APIRouter(
    prefix="/uploaded-files",
    tags=["uploaded files"]
)


@router.get("/", response_model=List[UploadedFilesBase])
async def get_uploaded_files(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    return db.query(models.UploadedFile).all()


@router.get("/{uploaded_file_id}", response_model=UploadedFilesBase)
async def get_uploaded_file_by_id(
        uploaded_file_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    uploaded_file = db.query(models.UploadedFile).filter(
        models.UploadedFile.id == uploaded_file_id
    ).first()
    if not uploaded_file:
        raise HTTPException(status_code=404, detail="Uploaded file not found")
    return uploaded_file


@router.post("/upload/{job_id}", response_model=UploadedFilesBase)
async def upload_file(
        job_id: int,
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    job = db.query(models.MigrationJob).filter(models.MigrationJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Migration job not found")

    storage = get_file_storage()
    saved = storage.save(job_id, file)

    new_uploaded_file = models.UploadedFile(
        migration_job_id=job_id,
        original_filename=saved["original_filename"],
        uploaded_filename=saved["uploaded_filename"],
        file_path=saved["file_path"],
        file_type=saved["file_type"],
        file_size=saved["file_size"],
        upload_timestamp=datetime.utcnow(),
        expiry_timestamp=datetime.utcnow() + timedelta(days=30),
        is_deleted=False
    )

    db.add(new_uploaded_file)
    db.commit()
    db.refresh(new_uploaded_file)
    return new_uploaded_file


@router.delete("/{uploaded_file_id}")
async def delete_uploaded_file(
        uploaded_file_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    uploaded_file = db.query(models.UploadedFile).filter(
        models.UploadedFile.id == uploaded_file_id
    ).first()
    if not uploaded_file:
        raise HTTPException(status_code=404, detail="Uploaded file not found")
    if uploaded_file.is_deleted:
        raise HTTPException(status_code=400, detail="File is already deleted")

    storage = get_file_storage()
    storage.delete(uploaded_file.file_path)

    uploaded_file.is_deleted = True
    db.commit()
    return {"message": "Uploaded file successfully deleted"}