from models.user import User, UserCreate, UserResponse
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from models.refresh_tocken import RefreshToken

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 비밀번호 해시화
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# 비밀번호 검증
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# 사용자명 유효성 검사
def validate_username(username: str) -> bool:
    import re

    # 하이픈으로 시작하지 않고, 연속된 하이픈이 없으며, 하이픈으로 끝나지 않는 영숫자와 하이픈만 허용
    regex = r"^(?!-)(?!.*--)[A-Za-z0-9-]+(?<!-)$"
    return bool(re.match(regex, username))


# 비밀번호 유효성 검사
def validate_password(password: str) -> bool:
    # 최소 8자 이상
    if len(password) < 8:
        return False

    # 숫자 포함 여부
    has_number = any(char.isdigit() for char in password)
    # 알파벳 포함 여부
    has_alphabet = any(char.isalpha() for char in password)
    # 특수문자 포함 여부
    special_chars = '!@#$%^&*(),.?":{}|<>'
    has_special_char = any(char in special_chars for char in password)

    return has_number and has_alphabet and has_special_char


# 사용자 생성
def create_user(db: Session, user: UserCreate) -> User:
    existing_user = get_user_by_username(db, user.username)
    if existing_user:
        raise ValueError("Username already exists")

    if not validate_username(user.username) or not validate_password(user.password):
        raise ValueError("Invalid username or password")

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
