from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
from db.session import get_db
from modules.security.auth import require_admin
from schemas.schema_fields import SchemaFieldBase, SchemaFieldCreate

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
        schema_field: SchemaFieldCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    existing_schema_field = db.query(models.SchemaField).filter(
        models.SchemaField.name == schema_field.name
    ).first()

    if existing_schema_field:
        raise HTTPException(status_code=400, detail="Schema Field name already exists")

    new_schema_field = models.SchemaField(
        destination_schema_id=schema_field.destination_schema_id,
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

@router.put("/{schema_field_id}", response_model=SchemaFieldBase)
async def update_schema_field(
        schema_field_id: int,
        schema_field_update: SchemaFieldCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    schema_field = db.query(models.SchemaField).filter(models.SchemaField.id == schema_field_id).first()

    if not schema_field:
        raise HTTPException(status_code=404, detail='Schema field with the given id does not exist')

    schema_field.destination_schema_id = schema_field_update.destination_schema_id
    schema_field.name = schema_field_update.name
    schema_field.data_type = schema_field_update.data_type
    schema_field.is_required = schema_field_update.is_required
    schema_field.is_unique = schema_field_update.is_unique
    schema_field.validation_rule = schema_field_update.validation_rule
    schema_field.max_length = schema_field_update.max_length
    schema_field.default_value = schema_field_update.default_value
    schema_field.field_order = schema_field_update.field_order

    db.commit()
    db.refresh(schema_field)

    return schema_field

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
