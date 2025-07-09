from typing import Any

from models.user import User
from schemas.user import UserResponse
from sqlalchemy.orm import Session


# 모든 사용자 조회
def get_all_users(db: Session) -> list[UserResponse]:
    users = db.query(User).all()
    return [UserResponse.model_validate(user) for user in users]


# 사용자 업데이트
def db_update(db: Session, userid: str, update_data: dict[str, Any]) -> UserResponse:
    user = db.query(User).filter(User.id == userid).first()
    if user:
        for key, value in update_data.items():
            setattr(user, key, value)
        db.commit()
        db.refresh(user)
        return UserResponse.model_validate(user)
    else:
        raise ValueError("User not found")


# 사용자 삭제
def db_delete(db: Session, userid: str) -> UserResponse:
    user = db.query(User).filter(User.id == userid).first()
    if user:
        db.delete(user)
        db.commit()
        db.refresh(user)
        return UserResponse.model_validate(user)
    else:
        raise ValueError("User not found")
