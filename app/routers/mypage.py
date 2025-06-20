from fastapi import APIRouter, Request, HTTPException, Depends
from utils.path import templates
from utils.deps import get_current_user
from models.user import UserResponse

router = APIRouter()

@router.get("/")
def mypage(request: Request, user: UserResponse = Depends(get_current_user)):
    data = {
        "user": {
            "username": user.username,
            "is_admin": user.is_admin
        }
    }
    
    return templates.TemplateResponse(request, "mypage.html", data)