from datetime import datetime
from pydantic import BaseModel, ConfigDict


# 사용자 생성 스키마
class UserCreate(BaseModel):
    username: str
    password: str


# 사용자 로그인 스키마
class UserLogin(UserCreate):
    pass


# 비밀번호 변경 스키마
class ChangePassword(BaseModel):
    currentPassword: str
    newPassword: str


# 사용자 응답 스키마
class UserResponse(BaseModel):
    id: str
    username: str
    is_admin: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
