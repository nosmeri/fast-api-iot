from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, String, Boolean, Integer
from config.db import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    is_admin = Column(Boolean, default=False)

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class ChangePassword(BaseModel):
    currentPassword: str
    newPassword: str


class UserResponse(BaseModel):
    id: int
    username: str
    is_admin: bool = False
    model_config = ConfigDict(from_attributes=True)