from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from models.user import UserResponse
from typing import Dict, Any
from utils.deps import get_current_user
from utils.path import templates

router = APIRouter()


@router.get("/")
def mypage(
    request: Request, user: UserResponse = Depends(get_current_user)
) -> HTMLResponse:
    data: Dict[str, Any] = {
        "user": {"username": user.username, "is_admin": user.is_admin}
    }

    return templates.TemplateResponse(request, "mypage.html", data)
