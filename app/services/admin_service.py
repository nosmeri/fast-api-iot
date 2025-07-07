from models.user import User, UserResponse
from sqlalchemy.orm import Session
from typing import Any


def get_all_users(db: Session) -> list[UserResponse]:
    users = db.query(User).all()
    return [UserResponse.model_validate(user) for user in users]


def db_update(db: Session, userid: str, update_data: dict[str, Any]) -> None:
    user = db.query(User).filter(User.id == userid).first()
    if user:
        for key, value in update_data.items():
            setattr(user, key, value)
        db.commit()


def db_delete(db: Session, userid: str) -> None:
    user = db.query(User).filter(User.id == userid).first()
    if user:
        db.delete(user)
        db.commit()
