from models.user import User, UserCreate, UserResponse
from passlib.context import CryptContext
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_user(db: Session, user: UserCreate) -> User:
    existing_user = get_user_by_username(db, user.username)
    if existing_user:
        raise ValueError("Username already exists")

    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def change_password(db: Session, id: str, new_password: str) -> User:
    user = get_user_by_id(db, id)
    if not user:
        raise ValueError("User not found")

    user.password = get_password_hash(new_password)  # type: ignore
    db.commit()
    db.refresh(user)

    return user


def get_user_by_username(db: Session, username: str) -> User:
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: str) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def authenticate_user(db: Session, username: str, password: str) -> UserResponse | None:
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.password):  # type: ignore
        return None
    return user
