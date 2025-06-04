from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import services.jwt_service as jwt_manager
import routers.auth as auth_router
from sqlalchemy import create_engine

from models.user import Base
from config.db import SQLALCHEMY_DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router.router)

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def mainPage(request: Request):
    tkn = request.cookies.get("session")
    data = {
            "request": request,
            "message": "Hello World!",
            }
    if jwt_manager.check_token(tkn):
        data.update({
            "user": {
                "username": jwt_manager.decode_access_token(tkn)["sub"],
                "is_admin": bool(jwt_manager.decode_access_token(tkn).get("is_admin", False))
            }
        })
    
    return templates.TemplateResponse("index.html", data)
    
class Post(BaseModel):
	title: str
	content: str

@app.post("/posts")
def createContents(post : Post):
	title = post.title
	content = post.content
	return {
        "Title": title,
        "Content": content,
		"status": "success"
    }

@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request):
    tkn=request.cookies.get("session")
    if not jwt_manager.check_token(tkn):
        return "Please login"
    if not jwt_manager.decode_access_token(tkn).get("is_admin",False):
        return "You are not admin"

    data= {
        "request": request,
        "user": {
            "username": jwt_manager.decode_access_token(tkn)["sub"],
            "is_admin": bool(jwt_manager.decode_access_token(tkn).get("is_admin",False))
        }
    }

    return templates.TemplateResponse("admin.html", data)