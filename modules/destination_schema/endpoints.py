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
        raise HTTPException(status_code=400, detail="Schema name already exists")

    new_destination_schema = models.DestinationSchema(
        created_by=current_user.id,
        schema_name=destination_schema.schema_name,
        description=destination_schema.description
    )

    db.add(new_destination_schema)
    db.commit()
    db.refresh(new_destination_schema)

    return new_destination_schema