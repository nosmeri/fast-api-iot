import routers.admin as admin_router
import routers.auth as auth_router
import routers.mypage as mypage_router
from fastapi import Depends, FastAPI, Request, status, UploadFile
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from models import *
from models.user import UserResponse
from utils.deps import get_current_user_optional, require_admin
from utils.path import BASE_DIR, UPLOAD_DIR, templates
import shutil

# FastAPI 애플리케이션 인스턴스 생성
# - docs_url=None: Swagger UI 문서 비활성화
# - redoc_url=None: ReDoc 문서 비활성화
# - openapi_url=None: OpenAPI 스키마 엔드포인트 비활성화
app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

# 라우터 포함
# - auth_router: 인증 관련 라우터
# - admin_router: 관리자 관련 라우터
# - mypage_router: 마이페이지 관련 라우터
app.include_router(auth_router.router, prefix="")
app.include_router(admin_router.router, prefix="/admin")
app.include_router(mypage_router.router, prefix="/mypage")

# 정적 파일 서비스 마운트
# - "/static": 정적 파일 디렉토리 마운트
# - BASE_DIR / "static": 정적 파일 디렉토리 경로
# - name="static": 마운트 이름
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


# 메인 페이지 엔드포인트
# - "/": 메인 페이지
# - request: FastAPI Request 객체
# - user: 현재 사용자 정보 (선택적 의존성 주입)
# - templates.TemplateResponse: 템플릿 응답 반환
@app.get("/")
def mainPage(request: Request, user: UserResponse = Depends(get_current_user_optional)):
    data: dict = {
        "message": "Hello World!",
    }
    if user:
        data.update(
            {"user": {"username": user.username, "is_admin": bool(user.is_admin)}}
        )

    return templates.TemplateResponse(request, "index.html", data)


# 파일 업로드 엔드포인트
# - "/upload": 파일 업로드 엔드포인트
# - file: 업로드할 파일 객체
# - UPLOAD_DIR: 파일 저장 디렉토리
# - dest: 파일 저장 경로
# - with dest.open("wb") as buffer: 파일 저장
@app.post("/upload")
def upload_file(file: UploadFile):
    if not file.filename:
        return {"error": "No filename provided"}
    dest = UPLOAD_DIR / file.filename
    with dest.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"stored": dest.name, "size": dest.stat().st_size}


@app.get("/health", include_in_schema=False)
def health_check():
    return {"status": "ok"}


@app.exception_handler(401)
async def unauthorized(request: Request, exc):
    return templates.TemplateResponse(
        request, "401.html", status_code=status.HTTP_401_UNAUTHORIZED
    )


@app.exception_handler(403)
async def forbidden(request: Request, exc):
    return templates.TemplateResponse(
        request, "403.html", status_code=status.HTTP_403_FORBIDDEN
    )


@app.exception_handler(404)
async def not_found(request: Request, exc):
    return templates.TemplateResponse(
        request, "404.html", status_code=status.HTTP_404_NOT_FOUND
    )


@app.exception_handler(500)
async def internal_server_error(request: Request, exc):
    return templates.TemplateResponse(
        request, "500.html", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


@app.get("/docs", dependencies=[Depends(require_admin)], include_in_schema=False)
def custom_swagger_ui():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")


@app.get("/redoc", dependencies=[Depends(require_admin)], include_in_schema=False)
def custom_redoc():
    return get_redoc_html(openapi_url="/openapi.json", title="ReDoc")


@app.get(
    "/openapi.json", dependencies=[Depends(require_admin)], include_in_schema=False
)
def custom_openapi():
    return JSONResponse(
        get_openapi(title=app.title, version=app.version, routes=app.routes)
    )
