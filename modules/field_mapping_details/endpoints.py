from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
from db.session import get_db
from modules.security.auth import require_admin
from schemas.field_mappings import FieldMappingCreate
from schemas.field_mapping_details import FieldMappingDetails

router = APIRouter(
    prefix="/field-mapping-details",
    tags=["field-mapping-details"]
)


@router.get("/", response_model=List[FieldMappingDetails])
async def get_field_mappings_details(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    field_mappings_details = db.query(models.FieldMappingDetail).all()
    return


@router.get("/{id}", response_model=FieldMappingDetails)
async def get_field_mappings_details_by_id(
        field_mapping_details_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    field_mappings_details = db.query(models.FieldMappingDetail).filter(
        field_mapping_details_id == models.FieldMappingDetail.id).first()
    return field_mappings_details


@router.post("/", response_model=FieldMappingDetails)
async def create_field_mappings_details(
        field_mapping_details: FieldMappingCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    existing_field_mapping_details = db.query(models.FieldMappingDetail).filter(
        field_mapping_details.id == field_mapping_details.id).first()

    if existing_field_mapping_details:
        raise HTTPException(status_code=400, detail="Field mapping details with this id already exists")

    new_field_mapping_details = FieldMappingDetails(
        field_mapping_id=field_mapping_details.field_mapping_id,
        source_field=field_mapping_details.source_field,
        destination_field=field_mapping_details.destination_field,
        transformation_rule=field_mapping_details.transformation_rule,
        field_order=field_mapping_details.field_order,
    )

    db.add(new_field_mapping_details)
    db.commit()
    db.refresh(new_field_mapping_details)

    return new_field_mapping_details


@router.put("/{id}", response_model=FieldMappingDetails)
async def update_field_mappings_details(
        field_mapping_details_id: int,
        field_mapping_update: FieldMappingCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)

):
    field_mapping_details = db.query(models.FieldMappingDetail).filter(
        models.FieldMappingDetail.id == field_mapping_details_id).first()

    if not field_mapping_details:
        raise HTTPException(status_code=404, detail="Field mapping details with this id not found")

    field_mapping_details.field_mapping_id = field_mapping_update.field_mapping_id
    field_mapping_details.source_field = field_mapping_update.source_field
    field_mapping_details.destination_field = field_mapping_update.destination_field
    field_mapping_details.transformation_rule = field_mapping_update.transformation_rule
    field_mapping_details.field_order = field_mapping_update.field_order

    db.commit()
    db.refresh(field_mapping_details)
    return field_mapping_details

@router.delete("/{id}")
async def delete_field_mappings_details(
        field_mapping_details_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    field_mapping_details = db.query(models.FieldMappingDetail).filter(
        field_mapping_details_id == models.FieldMappingDetail.id).first()

    if not field_mapping_details:
        raise HTTPException(status_code=404, detail="Field mapping details with this id not found")

    db.delete(field_mapping_details)
    db.commit()
    return {"message": "Field mapping details successfully deleted"}
