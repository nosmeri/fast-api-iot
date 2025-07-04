import services.admin_service as admin_service
from config.db import get_db
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from models.user import User, UserResponse
from sqlalchemy.orm import Session
from typing import Dict, Any
from utils.deps import require_admin
from utils.path import templates

router = APIRouter(dependencies=[Depends(require_admin)])


@router.get("/")
def admin(
    request: Request,
    db: Session = Depends(get_db),
    user: UserResponse = Depends(require_admin),
) -> HTMLResponse:
    users = admin_service.get_all_users(db)
    data: Dict[str, Any] = {
        "user": {"username": user.username, "is_admin": user.is_admin},
        "users": users,
    }

    return templates.TemplateResponse(request, "admin.html", data)


@router.put("/user")
def admin_modify_member(
    request: Request,
    userid: str,
    attr: str,
    type: str,
    value: str,
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    if type not in ["bool", "int", "str"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid type specified. Must be 'bool', 'int', or 'str'.",
        )

    # 민감한 필드 보호
    protected_fields = {"password"}
    if attr in protected_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Attribute '{attr}' is protected and cannot be modified through this endpoint.",
        )

    # 컬럼명 리스트를 미리 계산
    column_names = [col.name for col in User.__table__.columns]
    if attr not in column_names:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid attribute '{attr}' specified. Must be one of {column_names}.",
        )

    update_data: Dict[str, Any] = {}
    if type == "bool":
        update_data[attr] = value.lower() == "true"
    elif type == "int":
        try:
            update_data[attr] = int(value)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid value '{value}' for type 'int'. Must be a valid integer.",
            )
    elif type == "str":
        update_data[attr] = value

    admin_service.db_update(db, userid, update_data)
    return {
        "status": "success",
        "message": f"User {userid} updated successfully with {attr} = {value}",
    }


@router.delete("/user")
def admin_delete_member(
    request: Request, userid: str, db: Session = Depends(get_db)
) -> Dict[str, str]:
    admin_service.db_delete(db, userid)
    return {"status": "success", "message": f"User {userid} deleted successfully"}
