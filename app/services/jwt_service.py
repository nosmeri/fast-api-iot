from datetime import datetime, timedelta, timezone

from config.settings import settings
from jose import ExpiredSignatureError, JWTError, jwt
from models.refresh_tocken import RefreshToken
from sqlalchemy.orm import Session


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(user_id: str, is_admin: bool, username: str) -> str:
    to_encode = {
        "sub": user_id,
        "is_admin": is_admin,
        "username": username,
        "exp": _utc_now() + timedelta(hours=settings.JWT_EXPIRES_IN_HOURS),
        "type": "access",
    }
    return jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def verify_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except ExpiredSignatureError:
        return None
    except JWTError:
        return None


def create_refresh_token(user_id: str, db: Session):
    exp = _utc_now() + timedelta(days=settings.JWT_REFRESH_EXPIRES_IN_DAYS)
    payload = {"sub": user_id, "exp": exp, "type": "refresh"}
    token = jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )

    db_token = RefreshToken(user_id=user_id, token=token, expires_at=exp)
    db.add(db_token)
    db.commit()
    return token


def get_refresh_token(db: Session, token: str) -> RefreshToken | None:
    return db.query(RefreshToken).filter(RefreshToken.token == token).first()


def revoke_refresh_token(db: Session, token: str) -> RefreshToken | None:
    refresh_token = get_refresh_token(db, token)
    if not refresh_token:
        return None
    refresh_token.revoked = True
    db.commit()
    db.refresh(refresh_token)
    return refresh_token


def refresh_access_token(db: Session, refresh_token_str: str) -> tuple[str, str] | None:
    """Refresh token을 사용해서 새로운 access token과 refresh token을 발급받습니다."""
    # Refresh token 검증
    payload = verify_token(refresh_token_str)
    if not payload or payload.get("type") != "refresh":
        return None

    # 데이터베이스에서 refresh token 확인
    db_refresh_token = get_refresh_token(db, refresh_token_str)
    if not db_refresh_token or db_refresh_token.revoked:
        return None

    # 만료 확인
    if db_refresh_token.expires_at < _utc_now():
        return None

    # 기존 refresh token revoke
    db_refresh_token.revoked = True
    db.commit()

    user = db_refresh_token.user
    if not user:
        return None

    # 새로운 access token과 refresh token 생성
    new_access_token = create_access_token(user.id, user.is_admin, user.username)
    new_refresh_token = create_refresh_token(user.id, db)

    return new_access_token, new_refresh_token
