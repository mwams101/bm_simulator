from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

import models
from db.session import get_db
from schemas.users import UserCreate


router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.post("/")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user