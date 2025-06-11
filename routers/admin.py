from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
import services.jwt_service as jwt_manager
from config.db import get_db
from sqlalchemy.orm import Session
import services.admin_service as admin_service
from models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/")
def admin(request: Request, db: Session = Depends(get_db)):
    tkn=request.cookies.get("session")
    if not jwt_manager.check_token(tkn):
        raise HTTPException(status_code=401, detail="Please login")
    decoded_token=jwt_manager.decode_access_token(tkn)
    if not decoded_token.get("is_admin",False):
        raise HTTPException(status_code=403, detail="You are not admin")

    users = admin_service.get_all_users(db)
    data= {
        "request": request,
        "user": {
            "username": decoded_token["sub"],
            "is_admin": bool(decoded_token.get("is_admin",False))
        },
        "users": users
    }

    return templates.TemplateResponse("admin.html", data)

@router.post("/modify")
def admin_modify_member(request: Request, userid: int, attr: str, type: str, value: str, db: Session = Depends(get_db)):
    tkn = request.cookies.get("session")
    if not jwt_manager.check_token(tkn):
        raise HTTPException(status_code=401, detail="Please login")
    if not jwt_manager.decode_access_token(tkn).get("is_admin",False):
        raise HTTPException(status_code=403, detail="You are not admin")
    if type not in ["bool", "int", "str"]:
        raise HTTPException(status_code=400, detail="Invalid type specified. Must be 'bool', 'int', or 'str'.")
    if attr not in map(lambda x: x.name, User.__table__.columns):
        raise HTTPException(status_code=400, detail=f"Invalid attribute '{attr}' specified. Must be one of {list(map(lambda x: x.name, User.__table__.columns))}.")
    update_data = {}
    if type == "bool":
        update_data[attr] = value.lower() == "true"
    elif type == "int":
        try:
            update_data[attr] = int(value)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid value '{value}' for type 'int'. Must be a valid integer.")
    elif type == "str":
        update_data[attr] = value
    admin_service.db_update(db, userid, update_data)
    return {"status": "success", "message": f"User {userid} updated successfully with {attr} = {value}"}
    
@router.delete("/delete")
def admin_delete_member(request: Request, userid: int, db: Session = Depends(get_db)):
    tkn = request.cookies.get("session")
    if not jwt_manager.check_token(tkn):
        raise HTTPException(status_code=401, detail="Please login")
    if not jwt_manager.decode_access_token(tkn).get("is_admin",False):
        raise HTTPException(status_code=403, detail="You are not admin")

    admin_service.db_delete(db, userid)
    return {"status": "success", "message": f"User {userid} deleted successfully"}