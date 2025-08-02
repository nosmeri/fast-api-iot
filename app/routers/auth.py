
from config.db import get_async_db
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from schemas.user import ChangePassword, UserCreate, UserLogin, UserResponse
from services import auth_service, jwt_service
from sqlalchemy.ext.asyncio import AsyncSession
from utils.deps import (
    get_current_user_async,
    get_current_user_optional_async,
    get_refresh_token,
)
from utils.path import templates
from utils.validators import get_validation_rules

router = APIRouter()


# 유효성 검사 규칙 제공 API
@router.get("/validation-rules")
async def get_validation_rules_api() -> dict:
    return get_validation_rules()


# 로그인 페이지
@router.get("/login")
async def login_form(
    request: Request,
    user: UserResponse | None = Depends(get_current_user_optional_async),
) -> HTMLResponse:
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(request, "login.html")


# 로그인 (비동기)
@router.post("/login")
async def login(
    request: Request, user_login: UserLogin, db: AsyncSession = Depends(get_async_db)
) -> JSONResponse:
    username = user_login.username
    password = user_login.password
    try:
        user = await auth_service.authenticate_user_async(db, username, password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username or password",
        )

    access_token = jwt_service.create_access_token(
        user_id=user.id, username=user.username, role=user.role
    )
    refresh_token = await jwt_service.create_refresh_token_async(user_id=user.id, db=db)

    request.state.new_access_token = access_token
    request.state.new_refresh_token = refresh_token

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "success", "message": "Login successful"},
    )


# 회원가입 페이지
@router.get("/register")
async def register_form(
    request: Request,
    user: UserResponse | None = Depends(get_current_user_optional_async),
) -> HTMLResponse:
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(request, "register.html")


# 회원가입 (비동기)
@router.post("/register")
async def register(
    request: Request, user: UserCreate, db: AsyncSession = Depends(get_async_db)
) -> JSONResponse:
    try:
        new_user = await auth_service.create_user_async(db, user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    access_token = jwt_service.create_access_token(
        user_id=new_user.id,
        username=new_user.username,
        role=new_user.role,
    )
    refresh_token = await jwt_service.create_refresh_token_async(
        user_id=new_user.id, db=db
    )

    request.state.new_access_token = access_token
    request.state.new_refresh_token = refresh_token

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "status": "success",
            "message": "User created successfully",
        },
    )


# 비밀번호 변경 페이지
@router.get("/changepw")
async def change_password_form(
    request: Request, user: UserResponse = Depends(get_current_user_async)
) -> HTMLResponse:
    return templates.TemplateResponse(request, "changepw.html")


# 비밀번호 변경 (비동기)
@router.put("/changepw")
async def change_password(
    request: Request,
    change_password: ChangePassword,
    db: AsyncSession = Depends(get_async_db),
    user: UserResponse = Depends(get_current_user_async),
) -> JSONResponse:
    try:
        await auth_service.change_password_async(
            db, user.id, change_password.current_password, change_password.new_password
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "success", "message": "Password changed successfully"},
    )


# 로그아웃 (비동기)
@router.post("/logout")
async def logout(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
    refresh_token: str = Depends(get_refresh_token),
) -> JSONResponse:
    await jwt_service.revoke_refresh_token_async(db, refresh_token)

    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "success", "message": "Logout successful"},
    )
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    request.state.new_access_token = None
    request.state.new_refresh_token = None

    return response


# 계정 삭제 (비동기)
@router.delete("/delete_account")
async def delete_user(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
    user: UserResponse = Depends(get_current_user_async),
) -> JSONResponse:
    try:
        await auth_service.delete_user_async(db, user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "success", "message": "Account deleted successfully"},
    )
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    request.state.new_access_token = None
    request.state.new_refresh_token = None

    return response
