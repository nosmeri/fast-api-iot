from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from services import jwt_service, auth_service
from models.user import UserCreate, UserLogin, UserResponse
from config.db import get_db
from sqlalchemy.orm import Session

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    
    if jwt_service.check_token(request.cookies.get("session")):
        return "You are already logged in."
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=JSONResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    username = user.username
    password = user.password
    try:
        user: UserResponse = auth_service.authenticate_user(db, username, password)
    except ValueError as e:
        return JSONResponse(status_code=403, content={"status": "error", "message": str(e)})
    if not user:
        return JSONResponse(status_code=403, content={"status": "error", "message": "Invalid username or password"})
    
    data = {
        "sub": user.username,
        "is_admin": user.is_admin}
    token = jwt_service.create_access_token(data=data)
    response = JSONResponse(status_code=200, content={"status": "success", "message": "Login successful"})
    response.set_cookie(key="session", value=token)
    return response

@router.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    
    if jwt_service.check_token(request.cookies.get("session")):
        return "You are already logged in."
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register", response_class=JSONResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        new_user = auth_service.create_user(db, user)
    except ValueError as e:
        return JSONResponse(status_code=403, content={
            "status": "error",
            "message": str(e)})
    
    data = {
        "sub": new_user.username,
        "is_admin": new_user.is_admin}
    token = jwt_service.create_access_token(data=data)
    response = JSONResponse(status_code=201, content={
            "status": "success",
            "message": "User created successfully",})
    response.set_cookie(key="session", value=token)
    return response

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("session")
    return response