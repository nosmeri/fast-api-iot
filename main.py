from fastapi import FastAPI, Request, Response, Form
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
import jwt_manager

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def printHello(request: Request):
	return templates.TemplateResponse("index.html", {"request": request, "message": "Hello World!"})
    
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
def login(response: Response, username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "password":
        data = {"sub": username}
        token = jwt_manager.create_access_token(data=data)
        response.set_cookie(key="session", value=token)
        return {"status": "success", "message": "Login successful"}
    else:
        return {"status": "error", "message": "Invalid credentials"}
    
@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request):
    tkn=request.cookies.get("session")
    if not jwt_manager.check_token(tkn):
        return "Please login"
    if jwt_manager.decode_access_token(request.cookies.get("session"))["sub"]!="admin":
        return "You are not admin"

    return "<h1>admin page</h1>"