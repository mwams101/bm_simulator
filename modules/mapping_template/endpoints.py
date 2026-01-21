from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
from db.session import get_db
from modules.security.auth import require_admin
from schemas.mapping_template import MappingTemplateBase, MappingTemplateCreate

router = APIRouter(
    prefix="/mapping-templates",
    tags=["mapping-templates"]
)

@router.get("/", response_model=List[MappingTemplateBase])
async def get_mapping_templates(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):

    mapping_templates = db.query(models.MappingTemplate).all()
    return mapping_templates

@router.get("/{id}", response_model=MappingTemplateBase)
async def get_mapping_template_by_id(
        mapping_template_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    mapping_template = db.query(models.MappingTemplate).filter(mapping_template_id == models.MappingTemplate.id).first()
    return mapping_template

@router.post("/", response_model=MappingTemplateBase)
async def create_mapping_template(
        mapping_template: MappingTemplateCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    existing_mapping_template = (db.query(models.MappingTemplate).filter
                                 (models.MappingTemplate.template_name == mapping_template.template_name).first())

    if existing_mapping_template:
        raise HTTPException(status_code=400, detail="Mapping template with the same name already exists")

    new_mapping_template = models.MappingTemplate(
        user_id=current_user.id,
        template_name=mapping_template.template_name,
        description=mapping_template.description,
        is_active=mapping_template.is_active
    )

    db.add(new_mapping_template)
    db.commit()
    db.refresh(new_mapping_template)

@router.put('/{mapping_template_id}', response_model=MappingTemplateBase)
async def update_mapping_template(
        mapping_template_id: int,
        mapping_template: MappingTemplateCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    mapping_template_update = db.query(models.MappingTemplate).filter(models.MappingTemplate.id == mapping_template_id).first()

    if not mapping_template:
        raise HTTPException(status_code=404, detail="Mapping template with this id not found")

    mapping_template.template_name = mapping_template_update.template_name
    mapping_template.description = mapping_template_update.description
    mapping_template.is_active = mapping_template_update.is_active


    db.commit()
    db.refresh(mapping_template)
    return mapping_template

@router.delete("/{mapping_template_id}")
async def delete_mapping_template_by_id(
        mapping_template_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    mapping_template = db.query(models.MappingTemplate).filter(models.MappingTemplate.id == mapping_template_id).first()

    if not mapping_template:
        raise HTTPException(status_code=404, detail="Mapping template with this id not found")

    db.delete(mapping_template)
    db.commit()
    return {"message": "Mapping template successfully deleted"}