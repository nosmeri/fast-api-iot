from jose import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
EXPIRES_IN_HOURS = float(os.getenv("JWT_EXPIRES_IN_HOURS"))

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now() + timedelta(hours=EXPIRES_IN_HOURS)
    to_encode.update({"exp": int(expire.timestamp())})
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
def get_token_expiration(token: str) -> datetime | None:
    try:
        decoded_jwt = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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