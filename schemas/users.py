from pydantic import BaseModel


class UserBase(BaseModel):
    user_name: str
    email: str
    role: str


class UserCreate(UserBase):
    password: str
