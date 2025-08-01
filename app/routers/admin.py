from typing import Any

import services.admin_service as admin_service
from config.db import get_async_db
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from schemas.admin import ModifyUser
from schemas.user import UserResponse
from sqlalchemy.ext.asyncio import AsyncSession
from utils.deps import require_admin_async
from utils.path import templates

router = APIRouter(dependencies=[Depends(require_admin_async)])


@router.get("/")
async def admin_page(
    request: Request,
    user: UserResponse = Depends(require_admin_async),
) -> HTMLResponse:
    data: dict[str, Any] = {
        "user": {"username": user.username, "is_admin": user.is_admin},
    }

    return templates.TemplateResponse(request, "admin.html", data)


@router.get("/user")
async def get_users(
    db: AsyncSession = Depends(get_async_db),
) -> dict:
    users: list[UserResponse] = await admin_service.get_all_users(db)
    return {"users": [u.model_dump() for u in users]}


# 사용자 수정
@router.put("/user")
async def admin_modify_user(
    request: Request,
    modify_user: ModifyUser,
    db: AsyncSession = Depends(get_async_db),
) -> dict[str, str]:
    # 업데이트 데이터 생성
    update_data: dict[str, Any] = {modify_user.attr: modify_user.value}

    # 데이터베이스 업데이트
    await admin_service.db_update(db, modify_user.userid, update_data)
    return {
        "status": "success",
        "message": f"User {modify_user.userid} updated successfully with {modify_user.attr} = {modify_user.value}",
    }


# 사용자 삭제
@router.delete("/user")
async def admin_delete_member(
    request: Request, userid: str, db: AsyncSession = Depends(get_async_db)
) -> dict[str, str]:
    await admin_service.db_delete(db, userid)
    return {"status": "success", "message": f"User {userid} deleted successfully"}
