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
    return UserResponse(**payload)


def try_refresh_token(
    db: Session, refresh_token: str, response: Response
) -> UserResponse | None:
    """Refresh token을 사용해서 새로운 access token과 refresh token을 발급받고 사용자 정보를 반환합니다."""
    result = jwt_service.refresh_access_token(db, refresh_token)
    if not result:
        return None

    new_access_token, new_refresh_token = result

    # 새로운 access token을 쿠키에 설정
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=True,
        samesite="strict",
    )

    # 새로운 refresh token을 쿠키에 설정
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
    )

    # 새로운 access token으로 사용자 정보 반환
    payload = jwt_service.verify_token(new_access_token)
    if not payload:
        return None

    return UserResponse(**payload)


def get_current_user_optional(
    request: Request,
    response: Response,
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
            return try_refresh_token(db, refresh_token, response)
        return None

    return None


def get_current_user(
    request: Request,
    response: Response,
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
            refreshed_user = try_refresh_token(db, refresh_token, response)
            if refreshed_user:
                return refreshed_user

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
