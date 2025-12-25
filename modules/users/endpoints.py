from typing import List

from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session

import models
from db.session import get_db
from modules.security.auth import (
    get_password_hash,
    get_current_active_user,
    require_admin
)
from schemas.users import UserCreate, UserBase

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


# ADMIN ONLY - List all users
@router.get("/", response_model=List[UserBase])
async def get_users(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    """Only admins can list all users"""
    users = db.query(models.User).all()
    return users


# AUTHENTICATED USERS - Get own profile
@router.get("/me", response_model=UserBase)
async def get_my_profile(
        current_user: models.User = Depends(get_current_active_user)
):
    """Any authenticated user can get their own profile"""
    return current_user


# ADMIN OR OWNER - Get user by ID
@router.get("/{user_id}", response_model=UserBase)
async def get_user_by_id(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user)
):
    """Users can view their own profile, admins can view any profile"""
    model_user = models.User
    user = db.query(model_user).filter(model_user.user_id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if user is admin or viewing their own profile
    if current_user.role != "admin" and current_user.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only view your own profile"
        )

    return user


# PUBLIC - Create new user (registration)
@router.post("/", response_model=UserBase)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(
        models.User.user_name == user.user_name
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    existing_email = db.query(models.User).filter(
        models.User.email == user.email
    ).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    if user.role == "admin":
        raise HTTPException(
            status_code=403,
            detail="Cannot self-assign admin role"
        )

    # Truncate to 72 bytes (not characters) before hashing
    safe_password = user.password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    hashed_password = get_password_hash(safe_password)

    new_user = models.User(
        user_name=user.user_name,
        email=user.email,
        password=hashed_password,
        role=user.role if user.role else "user"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ADMIN ONLY - Delete user
@router.delete("/{user_id}")
async def delete_by_user_id(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    model_user = models.User
    user = db.query(model_user).filter(model_user.user_id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.user_id == current_user.user_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete your own account"
        )

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


# ADMIN OR OWNER - Update user
@router.put("/{user_id}", response_model=UserBase)
async def update_user(
        user_id: int,
        user_update: UserCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user)
):
    """Users can update their own profile, admins can update any profile"""
    user = db.query(models.User).filter(models.User.user_id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check permissions
    if current_user.role != "admin" and current_user.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own profile"
        )

    # Non-admins cannot change their role
    if current_user.role != "admin" and user_update.role != user.role:
        raise HTTPException(
            status_code=403,
            detail="You cannot change your own role"
        )

    # Update fields
    user.user_name = user_update.user_name
    user.email = user_update.email
    if user_update.password:
        safe_password = user_update.password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
        user.password = get_password_hash(safe_password)
    user.role = user_update.role

    db.commit()
    db.refresh(user)

    return user