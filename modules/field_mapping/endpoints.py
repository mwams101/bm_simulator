from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
from db.session import get_db
from modules.security.auth import require_admin
from schemas.field_mappings import FieldMappingBase, FieldMappingCreate

router = APIRouter(
    prefix="/field-mappings",
    tags=["field-mappings"]
)

@router.get("/", response_model=List[FieldMappingBase])
async def get_field_mappings(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin())
):
    field_mappings = db.query(models.FieldMapping).all()
    return field_mappings

@router.get("/{id}", response_model=FieldMappingBase)
async def get_field_mapping_by_id(
        field_mapping_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin())
):
    field_mapping = db.query(models.FieldMapping).filter(field_mapping_id == models.FieldMapping.id).first()
    return field_mapping

@router.post("/", response_model=FieldMappingBase)
async def create_field_mapping(
        field_mapping: FieldMappingCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin())
):
    existing_field_mapping = db.query(models.FieldMapping).filter(field_mapping.id == field_mapping.id).first()
    if existing_field_mapping:
        raise HTTPException(status_code=400, detail="Field mapping with this id already exists")

    new_field_mapping = models.FieldMapping(
        migration_job_id=field_mapping.migration_job_id,
        mapping_template_id=field_mapping.mapping_template_id,
        mapping_rules=field_mapping.mapping_rules
    )

    db.add(new_field_mapping)
    db.commit()
    db.refresh(new_field_mapping)
    return new_field_mapping

@router.put("/{id}", response_model=FieldMappingBase)
async def update_field_mapping(
        field_mapping_id: int,
        field_mapping: FieldMappingBase,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin())
):
    field_mapping = db.query(models.FieldMapping).filter(field_mapping_id == models.FieldMapping.id).first()
    if not field_mapping:
        raise HTTPException(status_code=404, detail="Field mapping with this id not found")

    field_mapping.mapping_rules = field_mapping.mapping_rules
    db.commit()
    db.refresh(field_mapping)
    return field_mapping

@router.delete("/{id}")
async def delete_field_mapping_by_id(
        field_mapping_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin())
):
    field_mapping = db.query(models.FieldMapping).filter(field_mapping_id == models.FieldMapping.id).first()
    if not field_mapping:
        raise HTTPException(status_code=404, detail="Field mapping with this id not found")

    db.delete(field_mapping)
    db.commit()
    return {"message": "Field mapping deleted successfully"}
