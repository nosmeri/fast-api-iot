from models.user import User, UserCreate, UserResponse
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from utils.validators import validate_user_credentials

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 비밀번호 해시화
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# 비밀번호 검증
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# 사용자 생성
def create_user(db: Session, user: UserCreate) -> User:
    existing_user = get_user_by_username(db, user.username)
    if existing_user:
        raise ValueError("Username already exists")

    # 통합 유효성 검사
    is_valid, errors = validate_user_credentials(user.username, user.password)
    if not is_valid:
        raise ValueError("; ".join(errors))

    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


# 비밀번호 변경
def change_password(db: Session, id: str, new_password: str) -> User:
    user = get_user_by_id(db, id)
    if not user:
        raise ValueError("User not found")

    user.password = get_password_hash(new_password)  # type: ignore
    db.commit()
    db.refresh(user)

    return user


# 사용자 조회(username)
def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


# 사용자 조회(id)
def get_user_by_id(db: Session, user_id: str) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


# 사용자 인증
def authenticate_user(db: Session, username: str, password: str) -> UserResponse | None:
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.password):  # type: ignore
        return None
    return UserResponse.model_validate(user)
