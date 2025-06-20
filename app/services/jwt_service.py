from datetime import datetime, timedelta, timezone

from config.settings import settings
from jose import ExpiredSignatureError, JWTError, jwt


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(payload: dict) -> str:
    to_encode = payload.copy()
    exp = _utc_now() + timedelta(hours=settings.JWT_EXPIRES_IN_HOURS)
    to_encode["exp"] = exp
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
