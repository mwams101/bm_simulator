from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
from db.session import get_db
from modules.security.auth import require_admin
from schemas.field_mapping import FieldMappingBase

router = APIRouter(
    prefix="/field-mappings",
    tags=["field-mappings"]
)

@router.get("/", response_model=List[FieldMappingBase])
def get_field_mappings(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin())
):
    field_mappings = db.query(models.FieldMapping).all()
    return field_mappings