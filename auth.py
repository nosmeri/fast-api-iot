from jose import jwt
from datetime import datetime, timedelta
from typing import Optional

SECRET_KEY = "63ad42229557af3539c82e947648fa9ced38b6c3a4b0fac9073ae7b56c5652ba2043985760a9711cadb57874101f7002c6b9dbd799312d817bc006c3411077c2"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire.timestamp()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
def decode_access_token(token: str) -> dict:
    try:
        decoded_jwt = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_jwt
    except jwt.JWTError:
        return {}
def verify_access_token(token: str) -> bool:
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return True
    except jwt.JWTError:
        return False
def get_token_expiration(token: str) -> Optional[datetime]:
    try:
        decoded_jwt = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return datetime.fromtimestamp(decoded_jwt.get("exp", 0))
    except jwt.JWTError:
        return None
def is_token_expired(token: str) -> bool:
    expiration = get_token_expiration(token)
    print(datetime.fromtimestamp(datetime.now().timestamp()))
    print(expiration)
    if expiration:
        return datetime.now() > expiration
    return True
def check_token(token: str) -> bool:
    if not token:
        return False
    if is_token_expired(token):
        return False
    return verify_access_token(token)