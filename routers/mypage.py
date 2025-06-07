from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from services import jwt_service

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def mypage(request: Request):
    tkn = request.cookies.get("session")
    if not tkn or not jwt_service.check_token(tkn):
        return "You are not logged in. Please log in first."
    
    user_data = jwt_service.decode_access_token(tkn)
    data = {
        "request": request,
        "user": {
            "username": user_data["sub"],
            "is_admin": user_data.get("is_admin", False)
        }
    }
    
    return templates.TemplateResponse("mypage.html", data)