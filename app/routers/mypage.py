from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from schemas.user import UserResponse
from utils.deps import get_current_user_async
from utils.path import templates

router = APIRouter()


# 마이페이지
@router.get("/")
async def mypage(
    request: Request, user: UserResponse = Depends(get_current_user_async)
) -> HTMLResponse:
    return templates.TemplateResponse(request, "mypage.html")
