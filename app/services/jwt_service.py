from datetime import datetime, timedelta, timezone

from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy.orm import Session

from config.settings import settings
from models.refresh_tocken import RefreshToken


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


# 액세스 토큰 생성
def create_access_token(user_id: str, username: str, is_admin: bool) -> str:
    to_encode = {
        "sub": user_id,
        "username": username,
        "is_admin": is_admin,
        "exp": _utc_now() + timedelta(hours=settings.JWT_ACCESS_EXPIRES_IN_HOURS),
        "type": "access",
    }
    return jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


# 토큰 검증
def verify_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except ExpiredSignatureError:
        return None
    except JWTError:
        return None


# 리프레시 토큰 생성
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


# 리프레시 토큰 조회
def get_refresh_token(db: Session, token: str) -> RefreshToken | None:
    return (
        db.query(RefreshToken)
        .filter(RefreshToken.token == token)
        .with_for_update()
        .first()
    )


# 리프레시 토큰 취소
def revoke_refresh_token(db: Session, token: str) -> RefreshToken | None:
    refresh_token = db.query(RefreshToken).filter(RefreshToken.token == token).with_for_update().first()
    if not refresh_token:
        return None
    refresh_token.revoked = True
    db.commit()
    db.refresh(refresh_token)
    return refresh_token


# 리프레시 토큰 갱신
# 리프레시 토큰을 사용해서 새로운 액세스 토큰과 리프레시 토큰을 발급
def refresh_access_token(db: Session, refresh_token_str: str) -> tuple[str, str] | None:
    # Refresh token 검증
    payload = verify_token(refresh_token_str)
    if not payload or payload.get("type") != "refresh":
        return None

    # 데이터베이스에서 refresh token 확인 (동시 접근 방지)
    db_refresh_token = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_token_str
    ).with_for_update().first()
    
    if not db_refresh_token or db_refresh_token.revoked:
        return None

    # 만료 확인
    if db_refresh_token.expires_at < _utc_now():
        return None

    # 기존 refresh token revoke (원자적 처리)
    db_refresh_token.revoked = True
    db.commit()
    db.refresh(db_refresh_token)

    user = db_refresh_token.user
    if not user:
        return None

    # 새로운 access token과 refresh token 생성
    new_access_token = create_access_token(user.id, user.username, user.is_admin)
    new_refresh_token = create_refresh_token(user.id, db)

    return new_access_token, new_refresh_token
