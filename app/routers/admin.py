from fastapi import APIRouter, Request, Depends, HTTPException, status
from config.db import get_db
from sqlalchemy.orm import Session
import services.admin_service as admin_service
from models.user import User, UserResponse
from utils.path import templates
from utils.deps import require_admin

router = APIRouter(dependencies=[Depends(require_admin)])

@router.get("/")
def admin(request: Request, db: Session = Depends(get_db), user: UserResponse = Depends(require_admin)):

    users = admin_service.get_all_users(db)
    data= {
        "request": request,
        "user": {
            "username": user.username,
            "is_admin": user.is_admin
        },
        "users": users
    }

    return templates.TemplateResponse("admin.html", data)

@router.put("/user")
def admin_modify_member(request: Request, userid: int, attr: str, type: str, value: str, db: Session = Depends(get_db)):
    if type not in ["bool", "int", "str"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid type specified. Must be 'bool', 'int', or 'str'.")
    if attr not in map(lambda x: x.name, User.__table__.columns):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid attribute '{attr}' specified. Must be one of {list(map(lambda x: x.name, User.__table__.columns))}.")
    update_data = {}
    if type == "bool":
        update_data[attr] = value.lower() == "true"
    elif type == "int":
        try:
            update_data[attr] = int(value)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid value '{value}' for type 'int'. Must be a valid integer.")
    elif type == "str":
        update_data[attr] = value
    admin_service.db_update(db, userid, update_data)
    return {"status": "success", "message": f"User {userid} updated successfully with {attr} = {value}"}
    
@router.delete("/user")
def admin_delete_member(request: Request, userid: int, db: Session = Depends(get_db)):
    admin_service.db_delete(db, userid)
    return {"status": "success", "message": f"User {userid} deleted successfully"}