from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status, HTTPException

import models
from db.session import get_db
from models import User
from modules.security.auth import authenticate_user, create_access_token, get_current_active_user
from modules.security.configuration import ACCESS_TOKEN_EXPIRE_MINUTES
from schemas.users import UserBase, LoginSchema

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post('/login')
async def login(payload: LoginSchema, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.username, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user_name},
        expires_delta=access_token_expires
    )

    login_in_audit = models.AuditLog(
        user_id=user.id,
        action_type="LOGIN",
        action_description="login"
    )

    db.add(login_in_audit)
    db.commit()
    db.refresh(login_in_audit)

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserBase)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_active_user)):
    return {"message": f"Hello {current_user.user_name}, you have access to this protected route!"}


@router.post("/logout")
async def logout():
    return {"message": "Logged out successfully"}
