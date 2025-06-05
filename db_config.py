from config.db import get_db
from sqlalchemy.orm import Session
from models.user import User

def db_update(db: Session, username: str, update_data: dict):

    db.query(User).filter(User.username == username).update(update_data)
    db.commit()

def db_delete(db: Session, username: str):
    db.query(User).filter(User.username == username).delete()
    db.commit()

username="admin"
update_data = {
    "is_admin": True
}
db=next(get_db())

db_delete(db, "kes")
