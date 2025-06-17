from sqlalchemy.orm import Session
from models.user import User, UserResponse

def get_all_users(db: Session) -> list[UserResponse]:
    users = db.query(User).all()
    return [UserResponse.from_orm(user) for user in users]

def db_update(db: Session, userid: int, update_data: dict) -> None:
    db.query(User).filter(User.id == userid).update(update_data)
    db.commit()

def db_delete(db: Session, userid: int) -> None:
    db.query(User).filter(User.id == userid).delete()
    db.commit()