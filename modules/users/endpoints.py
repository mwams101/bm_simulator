from typing import List

from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session

import models
from db.session import get_db
from schemas.users import UserCreate, UserBase, UserUpdate

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/", response_model=List[UserBase])
async def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users


@router.get("/{user_id}", response_model=UserBase)
async def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    model_user = models.User
    user = db.query(model_user).filter(model_user.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.delete("/{user_id}")
async def delete_by_user_id(user_id: int, db: Session = Depends(get_db)):
    model_user = models.User
    user = db.query(model_user).filter(model_user.user_id == user_id).first()

    if not user:
        return HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted"}