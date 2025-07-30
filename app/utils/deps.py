from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from config.db import get_db
from schemas.user import UserResponse
from services import jwt_service


# 액세스 토큰 쿠키에서 추출
def get_access_token(request: Request) -> str | None:
    return request.cookies.get("access_token")


# 리프레시 토큰 쿠키에서 추출
def get_refresh_token(request: Request) -> str | None:
    return request.cookies.get("refresh_token")


# 토큰 검증 및 사용자 정보 반환
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


# 토큰 갱신을 처리하는 내부 함수
def _handle_token_refresh(
    request: Request, db: Session, refresh_token: str
) -> UserResponse | None:
    """토큰 갱신을 처리하는 내부 함수"""
    if not refresh_token:
        return None

    result = jwt_service.refresh_access_token(db, refresh_token)
    if result:
        new_access_token, new_refresh_token = result
        # request.state에 새로운 토큰들을 저장
        request.state.new_access_token = new_access_token
        request.state.new_refresh_token = new_refresh_token

        # 새로운 access token으로 사용자 정보 반환
        return decode_token(new_access_token)

    return None


# 현재 사용자 정보 조회(선택적)
def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db),
    access_token: str = Depends(get_access_token),
    refresh_token: str = Depends(get_refresh_token),
) -> UserResponse | None:
    if not access_token and not refresh_token:
        return None

    try:
        if access_token:
            return decode_token(access_token)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
    except HTTPException:
        # Access token이 만료되었고 refresh token이 있는 경우
        return _handle_token_refresh(request, db, refresh_token)


# 현재 사용자 정보 조회(필수)
def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    access_token: str = Depends(get_access_token),
    refresh_token: str = Depends(get_refresh_token),
) -> UserResponse:
    if not access_token and not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please login",
        )

    try:
        if access_token:
            return decode_token(access_token)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
    except HTTPException:
        # Access token이 만료되었고 refresh token이 있는 경우
        refreshed_user = _handle_token_refresh(request, db, refresh_token)
        if refreshed_user:
            return refreshed_user

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired and no valid refresh token",
        )


# 관리자 권한 확인
def require_admin(user: UserResponse = Depends(get_current_user)) -> UserResponse:
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are not admin"
        )
    return user
