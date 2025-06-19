from fastapi import FastAPI, Request, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import routers.auth as auth_router
import routers.admin as admin_router
import routers.mypage as mypage_router
from config.settings import settings
from utils.path import BASE_DIR, templates
from utils.deps import get_current_user_optional, require_admin
from models.user import UserResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi

from config.db import Base, engine
from models import *

Base.metadata.create_all(bind=engine)

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None,)

app.include_router(auth_router.router, prefix="")
app.include_router(admin_router.router, prefix="/admin")
app.include_router(mypage_router.router, prefix="/mypage")

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

@app.get("/")
def mainPage(request: Request, user: UserResponse = Depends(get_current_user_optional)):
    data = {
            "request": request,
            "message": "Hello World!",
            }
    if user:
        data.update({
            "user": {
                "username": user.username,
                "is_admin": bool(user.is_admin)
            }
        })
    
    return templates.TemplateResponse("index.html", data)

@app.get("/health", include_in_schema=False)
def health_check():
    return {"status": "ok"}

@app.exception_handler(401)
async def unauthorized(request: Request, exc):
    return templates.TemplateResponse("401.html", {"request": request}, status_code=status.HTTP_401_UNAUTHORIZED)
@app.exception_handler(403)
async def forbidden(request: Request, exc):
    return templates.TemplateResponse("403.html", {"request": request}, status_code=status.HTTP_403_FORBIDDEN)
@app.exception_handler(404)
async def not_found(request: Request, exc):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=status.HTTP_404_NOT_FOUND)
@app.exception_handler(500)
async def internal_server_error(request: Request, exc):
    return templates.TemplateResponse("500.html", {"request": request}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.get("/docs", dependencies=[Depends(require_admin)], include_in_schema=False)
def custom_swagger_ui():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")

@app.get("/redoc", dependencies=[Depends(require_admin)], include_in_schema=False)
def custom_redoc():
    return get_redoc_html(openapi_url="/openapi.json", title="ReDoc")

@app.get("/openapi.json", dependencies=[Depends(require_admin)], include_in_schema=False)
def custom_openapi():
    return JSONResponse(get_openapi(title=app.title, version=app.version, routes=app.routes))