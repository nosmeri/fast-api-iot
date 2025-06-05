from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
import services.jwt_service as jwt_manager
from config.db import get_db
from sqlalchemy.orm import Session
import services.admin_service as admin_service
from models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def admin(request: Request, db: Session = Depends(get_db)):
    tkn=request.cookies.get("session")
    if not jwt_manager.check_token(tkn):
        return "Please login"
    if not jwt_manager.decode_access_token(tkn).get("is_admin",False):
        return "You are not admin"

    users = admin_service.get_all_users(db)
    data= {
        "request": request,
        "user": {
            "username": jwt_manager.decode_access_token(tkn)["sub"],
            "is_admin": bool(jwt_manager.decode_access_token(tkn).get("is_admin",False))
        },
        "users": users
    }

    return templates.TemplateResponse("admin.html", data)

@router.post("/modify", response_class=JSONResponse)
def admin_modify_member(request: Request, userid: int, attr: str, type: str, value: str, db: Session = Depends(get_db)):
    tkn = request.cookies.get("session")
    if not jwt_manager.check_token(tkn):
        return "Please login"
    if not jwt_manager.decode_access_token(tkn).get("is_admin",False):
        return "You are not admin"
    if type not in ["bool", "int", "str"]:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Invalid type specified. Use 'bool', 'int', or 'str'."})
    if attr not in map(lambda x: x.name, User.__table__.columns):
        return JSONResponse(status_code=400, content={"status": "error", "message": f"Invalid attribute '{attr}' specified."})
    update_data = {}
    if type == "bool":
        update_data[attr] = value.lower() == "true"
    elif type == "int":
        try:
            update_data[attr] = int(value)
        except ValueError:
            return JSONResponse(status_code=400, content={"status": "error", "message": "Invalid integer value."})
    elif type == "str":
        update_data[attr] = value
    admin_service.db_update(db, userid, update_data)
    return {"status": "success", "message": f"User {userid} updated successfully with {attr} = {value}"}
    
@router.delete("/delete")
def admin_delete_member(request: Request, userid: int, db: Session = Depends(get_db)):
    tkn = request.cookies.get("session")
    if not jwt_manager.check_token(tkn):
        return "Please login"
    if not jwt_manager.decode_access_token(tkn).get("is_admin",False):
        return "You are not admin"

    admin_service.db_delete(db, userid)
    return {"status": "success", "message": f"User {userid} deleted successfully"}