from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects import postgresql

from database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String, unique=True, index=True)
    role = Column(postgresql.ENUM('admin', 'user', name='role', create_type=False) )
    created_at = Column(postgresql.TIMESTAMP, index=True)
    last_login = Column(postgresql.TIMESTAMP, index=True)