from typing import List

from fastapi import APIRouter, Depends, HTTPException
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


@router.get("/{id}", response_model=SchemaFieldBase)
async def get_schema_field_by_id(
        schema_field_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    schema_field = db.query(models.SchemaField).filter(schema_field_id == models.SchemaField.id).first()
    return schema_field


@router.post("/", response_model=SchemaFieldBase)
async def create_schema_field(
        schema_field: SchemaFieldBase,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    existing_schema_field = db.query(models.SchemaField).filter(
        models.SchemaField.name == schema_field.name
    ).first()

    if existing_schema_field:
        raise HTTPException(status_code=400, detail="Schema Field name already exists")

    new_schema_field = models.SchemaField(
        destination_schema_id=schema_field.id,
        name=schema_field.name,
        data_type=schema_field.data_type,
        is_required=schema_field.is_required,
        is_unique=schema_field.is_unique,
        validation_rule=schema_field.validation_rule,
        max_length=schema_field.max_length,
        default_value=schema_field.default_value,
        field_order=schema_field.field_order,
    )

    db.add(new_schema_field)
    db.commit()
    db.refresh(new_schema_field)

    return new_schema_field


@router.delete("/{id}")
async def delete_schema_field_by_id(
        schema_field_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    schema_field = db.query(models.SchemaField).filter(models.SchemaField.id == schema_field_id).first()

    if not schema_field:
        raise HTTPException(status_code=404, detail="Schema field with this id not found")

    db.delete(schema_field)
    db.commit()
    return {"message": "Destination Schema successfully deleted"}
