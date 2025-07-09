from typing import Any

from config.db import get_db
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from schemas.user import ChangePassword, UserCreate, UserLogin, UserResponse
from services import auth_service, jwt_service
from sqlalchemy.orm import Session
from utils.deps import (get_current_user, get_current_user_optional,
                        get_refresh_token)
from utils.path import templates
from utils.validators import get_validation_rules

router = APIRouter()


# 유효성 검사 규칙 제공 API
@router.get("/validation-rules")
def get_validation_rules_api():
    return get_validation_rules()


# 로그인 페이지
@router.get("/login")
def login_form(
    request: Request, user: UserResponse | None = Depends(get_current_user_optional)
):
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(request, "login.html")


# 로그인
@router.post("/login")
def login(
    request: Request, user_login: UserLogin, db: Session = Depends(get_db)
) -> JSONResponse:
    username = user_login.username
    password = user_login.password
    try:
        user = auth_service.authenticate_user(db, username, password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username or password",
        )

    access_token = jwt_service.create_access_token(
        user_id=user.id, username=user.username, is_admin=user.is_admin
    )
    refresh_tocken = jwt_service.create_refresh_token(user_id=user.id, db=db)

    request.state.new_access_token = access_token
    request.state.new_refresh_token = refresh_tocken

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "success", "message": "Login successful"},
    )


# 회원가입 페이지
@router.get("/register")
def register_form(
    request: Request, user: UserResponse | None = Depends(get_current_user_optional)
):
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(request, "register.html")


# 회원가입
@router.post("/register")
def register(
    request: Request, user: UserCreate, db: Session = Depends(get_db)
) -> JSONResponse:
    try:
        new_user = auth_service.create_user(db, user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    access_token = jwt_service.create_access_token(
        user_id=new_user.id, username=new_user.username, is_admin=new_user.is_admin
    )
    refresh_tocken = jwt_service.create_refresh_token(user_id=new_user.id, db=db)

    request.state.new_access_token = access_token
    request.state.new_refresh_token = refresh_tocken

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "status": "success",
            "message": "User created successfully",
        },
    )


# 비밀번호 변경 페이지
@router.get("/changepw")
def change_password_form(
    request: Request, user: UserResponse = Depends(get_current_user)
):
    data: dict[str, Any] = {
        "user": {"username": user.username, "is_admin": user.is_admin}
    }

    return templates.TemplateResponse(request, "changepw.html", data)


# 비밀번호 변경
@router.put("/changepw")
def change_password(
    request: Request,
    change_password: ChangePassword,
    db: Session = Depends(get_db),
    user: UserResponse = Depends(get_current_user),
) -> JSONResponse:
    if not auth_service.authenticate_user(
        db, user.username, change_password.currentPassword
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    try:
        updated_user = auth_service.change_password(
            db, user.id, change_password.newPassword
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "success", "message": "Password changed successfully"},
    )


# 로그아웃
@router.post("/logout")
def logout(
    request: Request,
    db: Session = Depends(get_db),
    refresh_token: str = Depends(get_refresh_token),
) -> JSONResponse:
    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "success", "message": "Logout successful"},
    )
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    request.state.new_access_token = None
    request.state.new_refresh_token = None

    jwt_service.revoke_refresh_token(db, refresh_token)
    return response


@router.delete("/delete_account")
def delete_user(
    request: Request,
    db: Session = Depends(get_db),
    user: UserResponse = Depends(get_current_user),
) -> JSONResponse:
    try:
        auth_service.delete_user(db, user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "success", "message": "User deleted successfully"},
    )
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    request.state.new_access_token = None
    request.state.new_refresh_token = None

    return response
