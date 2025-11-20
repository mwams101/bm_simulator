from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status, HTTPException

from db.session import get_db
from models import User
from modules.security.authenticate import authenticate_user, create_access_token, get_current_active_user
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

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserBase)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_active_user)):
    return {"message": f"Hello {current_user.user_name}, you have access to this protected route!"}


@router.get("/")
async def root():
    return {"message": "Welcome to FastAPI Authentication Example"}
