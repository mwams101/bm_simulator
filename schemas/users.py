from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    user_name: str
    email: str
    role: str


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class UserTokenData(UserBase):
    user_name: str | None = None


class LoginSchema(BaseModel):
    username: str
    password: str
