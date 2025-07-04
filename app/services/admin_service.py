from models.user import User, UserResponse
from sqlalchemy.orm import Session


def get_all_users(db: Session) -> list[UserResponse]:
    users = db.query(User).all()
    return [UserResponse.model_validate(user) for user in users]


def db_update(db: Session, userid: str, update_data: dict) -> None:
    db.query(User).filter(User.id == userid).update(update_data)
    db.commit()


def db_delete(db: Session, userid: str) -> None:
    db.query(User).filter(User.id == userid).delete()
    db.commit()
