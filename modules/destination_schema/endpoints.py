from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
from db.session import get_db
from modules.security.auth import require_admin
from schemas.destination_schemas import DestinationSchemaBase, DestinationSchemaCreate

router = APIRouter(
    prefix="/destination-schemas",
    tags=["destination-schemas"],
)


@router.get("/", response_model=List[DestinationSchemaBase])
async def get_destination_schemas(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    destination_schemas = db.query(models.DestinationSchema).all()
    return destination_schemas


@router.post("/", response_model=DestinationSchemaBase)
async def create_destination_schema(
        destination_schema: DestinationSchemaCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    existing_destination_schema = db.query(models.DestinationSchema).filter(
        models.DestinationSchema.schema_name == destination_schema.schema_name
    ).first()

    if existing_destination_schema:
        raise HTTPException(status_code=400, detail="destination Schema name already exists")

    new_destination_schema = models.DestinationSchema(
        created_by=current_user.id,
        schema_name=destination_schema.schema_name,
        description=destination_schema.description
    )

    db.add(new_destination_schema)
    db.commit()
    db.refresh(new_destination_schema)

    return new_destination_schema


@router.put("/{destination_schema_id}", response_model=DestinationSchemaBase)
async def update_destination_schema(
        destination_schema_id: int,
        destination_schema_update: DestinationSchemaCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    destination_schema = db.query(models.DestinationSchema).filter(
        models.DestinationSchema.id == destination_schema_id).first()

    if not destination_schema:
        raise HTTPException(status_code=404, detail="Destination schema with the given id does not exist")

    destination_schema.schema_name = destination_schema_update.schema_name
    destination_schema.description = destination_schema_update.description

    db.commit()
    db.refresh(destination_schema)

    return destination_schema


@router.delete("/{destination_schema_id}")
async def delete_by_destination_schema_id(
        destination_schema_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    model_destination_schema = models.DestinationSchema
    destination_schema = db.query(model_destination_schema).filter(
        model_destination_schema.id == destination_schema_id).first()

    if not destination_schema:
        raise HTTPException(status_code=404, detail="destination schema with this id not found")

    db.delete(destination_schema)
    db.commit()
    return {"message": "Destination Schema successfully deleted"}
