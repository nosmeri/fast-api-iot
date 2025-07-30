from typing import Any

import services.admin_service as admin_service
from config.db import get_db
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from models.user import User
from schemas.user import UserResponse
from sqlalchemy.orm import Session
from utils.deps import require_admin
from utils.path import templates

router = APIRouter(dependencies=[Depends(require_admin)])


# 관리자 페이지
@router.get("/")
async def admin(
    request: Request,
    db: Session = Depends(get_db),
    user: UserResponse = Depends(require_admin),
) -> HTMLResponse:
    users: list[UserResponse] = admin_service.get_all_users(db)
    data: dict[str, Any] = {
        "user": {"username": user.username, "is_admin": user.is_admin},
        "users": users,
    }

    return templates.TemplateResponse(request, "admin.html", data)


# 사용자 수정
@router.put("/user")
async def admin_modify_member(
    request: Request,
    userid: str,
    attr: str,
    type: str,
    value: str,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    if type not in ["bool", "int", "str"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid type specified. Must be 'bool', 'int', or 'str'.",
        )

    # 민감한 필드 보호
    protected_fields = {"password"}
    if attr in protected_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Attribute '{attr}' is protected and cannot be modified through this endpoint.",
        )

    # 컬럼명 리스트를 미리 계산
    column_names = [col.name for col in User.__table__.columns]
    if attr not in column_names:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid attribute '{attr}' specified. Must be one of {column_names}.",
        )

    # 업데이트 데이터 생성
    update_data: dict[str, Any] = {}
    if type == "bool":
        update_data[attr] = value.lower() == "true"
    elif type == "int":
        try:
            update_data[attr] = int(value)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid value '{value}' for type 'int'. Must be a valid integer.",
            )
    elif type == "str":
        update_data[attr] = value

    # 데이터베이스 업데이트
    admin_service.db_update(db, userid, update_data)
    return {
        "status": "success",
        "message": f"User {userid} updated successfully with {attr} = {value}",
    }


# 사용자 삭제
@router.delete("/user")
async def admin_delete_member(
    request: Request, userid: str, db: Session = Depends(get_db)
) -> dict[str, str]:
    admin_service.db_delete(db, userid)
    return {"status": "success", "message": f"User {userid} deleted successfully"}
