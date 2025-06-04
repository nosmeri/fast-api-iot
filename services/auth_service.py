from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models.user import User, UserResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_user(db: Session, user: User) -> User:
    existing_user = get_user_by_username(db, user.username)
    if existing_user:
        raise ValueError("Username already exists")

    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

def get_user_by_username(db: Session, username: str) -> User:
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str) -> UserResponse | None:
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.password):
        return None
    return user