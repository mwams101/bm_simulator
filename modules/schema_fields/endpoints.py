from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
from db.session import get_db
from modules.security.auth import require_admin
from schemas.schema_fields import SchemaFieldBase

router = APIRouter(
    prefix="/schema-fields",
    tags=["schema-fields"]
)


@router.get("/", response_model=List[SchemaFieldBase])
async def get_schema_fields(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    schema_fields = db.query(models.SchemaField).all()
    return schema_fields
