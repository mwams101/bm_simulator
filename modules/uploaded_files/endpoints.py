from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
from db.session import get_db
from modules.security.auth import require_admin
from schemas.uploaded_files import UploadedFilesBase, UploadedFileCreate

router = APIRouter(
    prefix="/uploaded-files",
    tags=["uploaded files"]
)

@router.get("/", response_model=List[UploadedFilesBase])
async def get_uploaded_files(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    uploaded_files = db.query(models.UploadedFile).all()
    return uploaded_files

@router.get("/{uploaded_file_id}", response_model=UploadedFilesBase)
async def get_uploaded_file_by_id(
        uploaded_file_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    uploaded_file = db.query(models.UploadedFile).filter(models.UploadedFile.id == uploaded_file_id).first()
    if not uploaded_file:
        raise HTTPException(status_code=404, detail="Uploaded file not found")
    return uploaded_file

@router.post("/", response_model=UploadedFilesBase)
async def create_uploaded_file(
        uploaded_file: UploadedFileCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    from datetime import datetime, timedelta

    new_uploaded_file = models.UploadedFile(
        migration_job_id=uploaded_file.migration_job_id,
        original_filename=uploaded_file.original_filename,
        uploaded_filename=uploaded_file.uploaded_filename,
        file_path=uploaded_file.file_path,
        file_type=uploaded_file.file_type,
        file_size=uploaded_file.file_size,
        upload_timestamp=datetime.utcnow(),
        expiry_timestamp=datetime.utcnow() + timedelta(days=30),
        is_deleted=False
    )

    db.add(new_uploaded_file)
    db.commit()
    db.refresh(new_uploaded_file)
    return new_uploaded_file

@router.put("/{uploaded_file_id}", response_model=UploadedFilesBase)
async def update_uploaded_file(
        uploaded_file_id: int,
        uploaded_file_update: UploadedFileCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    uploaded_file = db.query(models.UploadedFile).filter(models.UploadedFile.id == uploaded_file_id).first()

    if not uploaded_file:
        raise HTTPException(status_code=404, detail="Uploaded file not found")

    uploaded_file.migration_job_id = uploaded_file_update.migration_job_id
    uploaded_file.original_filename = uploaded_file_update.original_filename
    uploaded_file.uploaded_filename = uploaded_file_update.uploaded_filename
    uploaded_file.file_path = uploaded_file_update.file_path
    uploaded_file.file_type = uploaded_file_update.file_type
    uploaded_file.file_size = uploaded_file_update.file_size

    db.commit()
    db.refresh(uploaded_file)
    return uploaded_file

@router.delete("/{uploaded_file_id}")
async def delete_uploaded_file(
        uploaded_file_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    uploaded_file = db.query(models.UploadedFile).filter(models.UploadedFile.id == uploaded_file_id).first()

    if not uploaded_file:
        raise HTTPException(status_code=404, detail="Uploaded file not found")

    db.delete(uploaded_file)
    db.commit()
    return {"message": "Uploaded file successfully deleted"}