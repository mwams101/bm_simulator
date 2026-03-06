from ast import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
from db.session import get_db
from modules.security.auth import require_admin
from schemas.uploaded_files import UploadedFilesBase

router = APIRouter(
    prefix="/uploaded-files",
    tags=["uploaded files"]
)

@router.get("/", response_model=List[UploadedFilesBase])
async def get_uploaded_files(
        db: Session = Depends(get_db()),
        current_user: models.User = Depends(require_admin)
):
    uploaded_files = db.query(UploadedFilesBase).all()
    return uploaded_files

@router.get("/{id}", response_model=UploadedFilesBase)
async def get_uploaded_file_by_id(
        uploaded_file_id: int,
        db: Session = Depends(get_db()),
        current_user: models.User = Depends(require_admin)
):
    uploaded_file = db.query(UploadedFilesBase).get(uploaded_file_id)
    return uploaded_file

@router.post("/", response_model=UploadedFilesBase)
async def create_uploaded_file(
        uploaded_file: UploadedFilesBase,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    pass

