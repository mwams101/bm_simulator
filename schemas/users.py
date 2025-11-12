from pydantic import BaseModel


class UserCreate(BaseModel):
    user_name: str
    email: str
    password: str
    role: str