from jose import jwt
from datetime import datetime, timedelta
from config.settings import settings

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now() + timedelta(hours=settings.JWT_EXPIRES_IN_HOURS)
    to_encode.update({"exp": int(expire.timestamp())})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt
def decode_access_token(token: str) -> dict:
    try:
        decoded_jwt = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return decoded_jwt
    except jwt.JWTError:
        return {}
def verify_access_token(token: str) -> bool:
    try:
        jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return True
    except jwt.JWTError:
        return False
def get_token_expiration(token: str) -> datetime | None:
    try:
        decoded_jwt = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return datetime.fromtimestamp(decoded_jwt.get("exp", 0))
    except jwt.JWTError:
        return None
def is_token_expired(token: str) -> bool:
    expiration = get_token_expiration(token)
    if expiration:
        return datetime.now() > expiration
    return True
def check_token(token: str) -> bool:
    if not token:
        return False
    if not verify_access_token(token):
        return False
    return not is_token_expired(token)