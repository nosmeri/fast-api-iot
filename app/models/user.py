from datetime import datetime
from uuid import uuid4

from config.db import Base
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Boolean, Column, DateTime, Integer, String, func


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    # id = Column(Integer, primary_key=True, autoincrement=True)
    password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(UserCreate):
    pass


class ChangePassword(BaseModel):
    currentPassword: str
    newPassword: str


class UserResponse(BaseModel):
    id: str
    username: str
    is_admin: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
