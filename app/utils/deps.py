from fastapi import Depends, HTTPException, Request, Response, status
from models.user import UserResponse
from services import jwt_service
from sqlalchemy.orm import Session
from config.db import get_db


def get_raw_token(request: Request) -> str | None:
    return request.cookies.get("access_token")


def get_refresh_token(request: Request) -> str | None:
    return request.cookies.get("refresh_token")


def decode_token(token: str) -> UserResponse:
    payload = jwt_service.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    # JWT 토큰의 'sub' 필드를 'id'로 변환
    user_data = {
        "id": payload.get("sub"),  # sub -> id로 변환
        "username": payload.get("username"),
        "is_admin": payload.get("is_admin", False),
    }

    return UserResponse(**user_data)


def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db),
    token: str = Depends(get_raw_token),
    refresh_token: str = Depends(get_refresh_token),
) -> UserResponse | None:
    if not token and not refresh_token:
        return None

    try:
        if token:
            return decode_token(token)
    except HTTPException:
        # Access token이 만료되었고 refresh token이 있는 경우
        if refresh_token:
            result = jwt_service.refresh_access_token(db, refresh_token)
            if result:
                new_access_token, new_refresh_token = result
                # request.state에 새로운 토큰들을 저장
                request.state.new_access_token = new_access_token
                request.state.new_refresh_token = new_refresh_token

                # 새로운 access token으로 사용자 정보 반환
                return decode_token(new_access_token)

    return None


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    token: str = Depends(get_raw_token),
    refresh_token: str = Depends(get_refresh_token),
) -> UserResponse:
    if not token and not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please login",
        )

    try:
        if token:
            return decode_token(token)
    except HTTPException:
        # Access token이 만료되었고 refresh token이 있는 경우
        if refresh_token:
            result = jwt_service.refresh_access_token(db, refresh_token)
            if result:
                new_access_token, new_refresh_token = result
                # request.state에 새로운 토큰들을 저장
                request.state.new_access_token = new_access_token
                request.state.new_refresh_token = new_refresh_token

                # 새로운 access token으로 사용자 정보 반환
                return decode_token(new_access_token)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired and no valid refresh token",
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
    )


def require_admin(user: UserResponse = Depends(get_current_user)) -> UserResponse:
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are not admin"
        )
    return user
