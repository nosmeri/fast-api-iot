from fastapi import Depends, HTTPException, status, Request
from services import jwt_service
from models.user import UserResponse

def get_raw_token(request: Request) -> str:
    return request.cookies.get("session")

def decode_token(token: str) -> UserResponse:
    payload = jwt_service.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return UserResponse(**payload)

def get_current_user_optional(token: str = Depends(get_raw_token)) -> UserResponse | None:
    if not token:
        return None
    try:
        return decode_token(token)
    except HTTPException:
        return None

def get_current_user(token: str = Depends(get_raw_token)) -> UserResponse:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please login",
        )
    return decode_token(token)

def require_admin(user: UserResponse = Depends(get_current_user)) -> UserResponse:
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not admin"
        )
    return user