from fastapi import FastAPI, Request, Response, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
import jwt_manager

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def printHello(request: Request):
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

@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    
    if jwt_manager.check_token(request.cookies.get("session")):
        return "You are already logged in."
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "password":
        data = {
            "sub": username,
            "is_admin": True}
        token = jwt_manager.create_access_token(data=data)
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(key="session", value=token, httponly=True, secure=True)
        return response
        
    else:
        return {"status": "error", "message": "Invalid credentials"}
    

@app.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("session")
    return response

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