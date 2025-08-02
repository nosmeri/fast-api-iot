from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from config.settings import settings
from jose import ExpiredSignatureError, JWTError, jwt
from models.enums import UserRole
from models.refresh_token import RefreshToken
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


# 액세스 토큰 생성
def create_access_token(
    user_id: str, username: str, role: UserRole
) -> str:
    to_encode = {
        "sub": user_id,
        "username": username,
        "role": role,
        "exp": _utc_now() + timedelta(hours=settings.JWT_ACCESS_EXPIRES_IN_HOURS),
        "type": "access",
    }
    return jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


# 토큰 검증
def verify_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except ExpiredSignatureError:
        return None
    except JWTError:
        return None


# 리프레시 토큰 생성 (비동기식)
async def create_refresh_token_async(user_id: str, db: AsyncSession):
    exp = _utc_now() + timedelta(days=settings.JWT_REFRESH_EXPIRES_IN_DAYS)
    payload = {
        "sub": user_id,
        "exp": exp,
        "type": "refresh",
        "jti": str(uuid4()),
    }
    token = jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )

    db_token = RefreshToken(user_id=user_id, token=token, expires_at=exp)
    db.add(db_token)
    await db.commit()
    return token


# 리프레시 토큰 조회 (비동기식)
async def get_refresh_token_async(db: AsyncSession, token: str) -> RefreshToken | None:
    stmt = (
        select(RefreshToken)
        .filter(RefreshToken.token == token)
        .with_for_update()
        .options(selectinload(RefreshToken.user))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# 리프레시 토큰 취소 (비동기식)
async def revoke_refresh_token_async(
    db: AsyncSession, token: str
) -> RefreshToken | None:
    stmt = select(RefreshToken).filter(RefreshToken.token == token).with_for_update()
    result = await db.execute(stmt)
    refresh_token = result.scalar_one_or_none()

    if not refresh_token:
        return None
    refresh_token.revoked = True
    await db.commit()
    await db.refresh(refresh_token)
    return refresh_token


# 리프레시 토큰 갱신 (비동기식)
# 리프레시 토큰을 사용해서 새로운 액세스 토큰과 리프레시 토큰을 발급
async def refresh_access_token_async(
    db: AsyncSession, refresh_token_str: str
) -> tuple[str, str] | None:
    # Refresh token 검증
    payload = verify_token(refresh_token_str)
    if not payload or payload.get("type") != "refresh":
        return None

    # 데이터베이스에서 refresh token 확인 (동시 접근 방지)
    db_refresh_token = await get_refresh_token_async(db, refresh_token_str)

    if not db_refresh_token or db_refresh_token.revoked:
        return None

    # 만료 확인
    if db_refresh_token.expires_at < _utc_now():
        return None

    # 기존 refresh token revoke (원자적 처리)
    db_refresh_token.revoked = True
    await db.commit()
    await db.refresh(db_refresh_token)

    user = db_refresh_token.user
    if not user:
        return None

    # 새로운 access token과 refresh token 생성
    new_access_token = create_access_token(
        user.id, user.username, user.role
    )
    new_refresh_token = await create_refresh_token_async(user.id, db)

    return new_access_token, new_refresh_token
