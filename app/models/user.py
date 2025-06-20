from config.db import Base
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Boolean, Column, Integer, String


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)


class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(UserCreate):
    pass


class ChangePassword(BaseModel):
    currentPassword: str
    newPassword: str


class UserResponse(BaseModel):
    id: int
    username: str
    is_admin: bool = False
    model_config = ConfigDict(from_attributes=True)
