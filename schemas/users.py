from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    user_id: int
    user_name: str
    email: str
    role: str
    last_login: Optional[datetime]


class UserCreate(BaseModel):
    user_name: str
    email: str
    role: str
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class UserTokenData(UserBase):
    user_name: str | None = None


class LoginSchema(BaseModel):
    username: str
    password: str

model_config = {"from_attributes": True}
