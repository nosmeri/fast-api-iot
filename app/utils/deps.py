from config.db import get_async_db
from fastapi import Depends, HTTPException, Request, status
from models.enums import UserRole
from schemas.user import UserResponse
from services import jwt_service
from sqlalchemy.ext.asyncio import AsyncSession


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
    payload["id"] = payload["sub"]

    return UserResponse(**payload)


# 토큰 갱신을 처리하는 내부 함수 (비동기식)
async def _handle_token_refresh_async(
    request: Request, db: AsyncSession, refresh_token: str
) -> UserResponse | None:
    """토큰 갱신을 처리하는 내부 함수 (비동기)"""
    if not refresh_token:
        return None

    result = await jwt_service.refresh_access_token_async(db, refresh_token)
    if result:
        new_access_token, new_refresh_token = result
        # request.state에 새로운 토큰들을 저장
        request.state.new_access_token = new_access_token
        request.state.new_refresh_token = new_refresh_token

        # 새로운 access token으로 사용자 정보 반환
        return decode_token(new_access_token)

    return None


# 현재 사용자 정보 조회(선택적) - 비동기식
async def get_current_user_optional_async(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
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
        return await _handle_token_refresh_async(request, db, refresh_token)


# 현재 사용자 정보 조회(필수) - 비동기식
async def get_current_user_async(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
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
        refreshed_user = await _handle_token_refresh_async(request, db, refresh_token)
        if refreshed_user:
            return refreshed_user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired and no valid refresh token",
        )


# 관리자 권한 확인 - 비동기식
async def require_manager_async(
    user: UserResponse = Depends(get_current_user_async),
) -> UserResponse:
    if user.role != UserRole.ADMIN and user.role != UserRole.MANAGER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are not manager"
        )
    return user


# 관리자 권한 확인 - 비동기식
async def require_admin_async(
    user: UserResponse = Depends(get_current_user_async),
) -> UserResponse:
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are not admin"
        )
    return user
