from fastapi import HTTPException, status
from models.user import User
from passlib.context import CryptContext
from schemas.user import UserCreate, UserResponse, user_to_response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from utils.validators import validate_password, validate_user_credentials

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 비밀번호 해시화
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# 비밀번호 검증
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# 사용자 생성 (비동기식)
async def create_user_async(db: AsyncSession, user: UserCreate) -> User:
    existing_user = await get_user_by_username_async(db, user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )

    # 통합 유효성 검사
    is_valid, errors = validate_user_credentials(user.username, user.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="; ".join(errors)
        )

    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user


# 비밀번호 변경 (비동기식)
async def change_password_async(
    db: AsyncSession, id: str, current_password: str, new_password: str
) -> User:
    user = await get_user_by_id_async(db, id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
        )

    # 현재 비밀번호 확인
    if not verify_password(current_password, user.password):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    # 새 비밀번호 유효성 검사
    is_valid, errors = validate_password(new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="; ".join(errors)
        )

    user.password = get_password_hash(new_password)  # type: ignore
    await db.commit()
    await db.refresh(user)

    return user


# 사용자 조회(username) - 비동기식
async def get_user_by_username_async(db: AsyncSession, username: str) -> User | None:
    stmt = select(User).filter(User.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# 사용자 조회(id) - 비동기식
async def get_user_by_id_async(db: AsyncSession, user_id: str) -> User | None:
    stmt = select(User).filter(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# 사용자 인증 (비동기식)
async def authenticate_user_async(
    db: AsyncSession, username: str, password: str
) -> UserResponse | None:
    user = await get_user_by_username_async(db, username)
    if not user or not verify_password(password, user.password):  # type: ignore
        return None
    return user_to_response(user)


# 사용자 삭제 (비동기식)
async def delete_user_async(db: AsyncSession, user_id: str) -> UserResponse:
    user = await get_user_by_id_async(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
        )
    await db.delete(user)
    await db.commit()
    return user_to_response(user)
