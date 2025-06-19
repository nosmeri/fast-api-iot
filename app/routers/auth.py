from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from services import jwt_service, auth_service
from models.user import UserCreate, UserLogin, UserResponse, ChangePassword
from config.db import get_db
from sqlalchemy.orm import Session
from utils.path import templates
from utils.deps import get_current_user_optional, get_current_user

router = APIRouter()

@router.get("/login")
def login_form(request: Request, user: UserResponse = Depends(get_current_user_optional)):
    if user:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    username = user.username
    password = user.password
    try:
        user: UserResponse = auth_service.authenticate_user(db, username, password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    data = {
        "id": user.id,
        "username": user.username,
        "is_admin": user.is_admin}
    token = jwt_service.create_access_token(data=data)
    response = JSONResponse(status_code=200, content={"status": "success", "message": "Login successful"})
    response.set_cookie(key="session", value=token, httponly=True)
    return response

@router.get("/register")
def register_form(request: Request, user: UserResponse = Depends(get_current_user_optional)):
    
    if user:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        new_user = auth_service.create_user(db, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    data = {
        "id": new_user.id,
        "username": new_user.username,
        "is_admin": new_user.is_admin}
    token = jwt_service.create_access_token(data=data)
    response = JSONResponse(status_code=201, content={
            "status": "success",
            "message": "User created successfully",})
    response.set_cookie(key="session", value=token, httponly=True)
    return response

@router.get("/changepw")
def change_password_form(request: Request, user: UserResponse = Depends(get_current_user)):
    data = {
        "request": request,
        "user": {
            "username": user.username,
            "is_admin": user.is_admin
        }
    }
    
    return templates.TemplateResponse("changepw.html", data)

@router.post("/changepw")
def change_password(request: Request, change_password: ChangePassword, db: Session = Depends(get_db), user: UserResponse = Depends(get_current_user)):
    if not auth_service.authenticate_user(db, user.username, change_password.currentPassword):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    try:
        updated_user = auth_service.change_password(db, user.id, change_password.newPassword)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return JSONResponse(status_code=200, content={
        "status": "success",
        "message": "Password changed successfully"
    })

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("session")
    return response