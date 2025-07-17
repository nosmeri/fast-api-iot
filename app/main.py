import time

import aiofiles
import routers.admin as admin_router
import routers.auth as auth_router
import routers.mypage as mypage_router
from config.settings import settings
from fastapi import Depends, FastAPI, Request, UploadFile
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from schemas.user import UserResponse
from utils.deps import get_current_user_optional, require_admin
from utils.error_handlers import (forbidden_error, internal_server_error,
                                  not_found_error, unauthorized_error)
from utils.logger import main_logger
from utils.path import BASE_DIR, UPLOAD_DIR, templates

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


# HTTP 요청 로깅 미들웨어
# - 모든 HTTP 요청과 응답을 로깅 (health check 제외)
# - 요청 시간, 메서드, URL, 상태 코드, 응답 시간 등을 기록
@app.middleware("http")
async def logging_middleware(request: Request, call_next) -> Response:
    # health check 경로는 로깅하지 않음
    if request.url.path == "/health":
        return await call_next(request)

    # 요청 시작 시간 기록
    start_time = time.time()

    # 요청 정보 로깅
    main_logger.info(
        f"요청 시작 - {request.method} {request.url.path} "
        f"클라이언트: {request.client.host if request.client else 'Unknown'} "
        f"User-Agent: {request.headers.get('user-agent', 'Unknown')}"
    )

    try:
        # 다음 미들웨어 또는 엔드포인트 실행
        response = await call_next(request)

        # 응답 시간 계산
        process_time = time.time() - start_time

        # 성공 응답 로깅
        main_logger.info(
            f"요청 완료 - {request.method} {request.url.path} "
            f"상태: {response.status_code} "
            f"처리시간: {process_time:.3f}초"
        )

        return response

    except Exception as e:
        # 에러 발생 시 로깅
        process_time = time.time() - start_time
        main_logger.error(
            f"요청 실패 - {request.method} {request.url.path} "
            f"에러: {str(e)} "
            f"처리시간: {process_time:.3f}초"
        )
        raise e


# 토큰 갱신 미들웨어
# - 액세스 토큰과 리프레시 토큰을 쿠키에 설정
@app.middleware("http")
async def token_refresh_middleware(request: Request, call_next) -> Response:
    response = await call_next(request)

    # request.state에 새로운 토큰이 있으면 쿠키에 설정
    if hasattr(request.state, "new_access_token") and request.state.new_access_token:
        main_logger.info(f"액세스 토큰 갱신 - {request.method} {request.url.path}")
        response.set_cookie(
            key="access_token",
            value=request.state.new_access_token,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=int(settings.JWT_ACCESS_EXPIRES_IN_HOURS * 3600),  # 시간 → 초
        )

    if hasattr(request.state, "new_refresh_token") and request.state.new_refresh_token:
        main_logger.info(f"리프레시 토큰 갱신 - {request.method} {request.url.path}")
        response.set_cookie(
            key="refresh_token",
            value=request.state.new_refresh_token,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=int(settings.JWT_REFRESH_EXPIRES_IN_DAYS * 24 * 3600),  # 일 → 초
        )

    return response


# 라우터 포함
app.include_router(auth_router.router, prefix="")
app.include_router(admin_router.router, prefix="/admin")
app.include_router(mypage_router.router, prefix="/mypage")

# 정적 파일 서비스 마운트
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


# 메인 페이지 엔드포인트
@app.get("/")
async def mainPage(
    request: Request, user: UserResponse | None = Depends(get_current_user_optional)
) -> HTMLResponse:
    data: dict = {}
    if user:
        data.update(
            {"user": {"username": user.username, "is_admin": bool(user.is_admin)}}
        )

    return templates.TemplateResponse(request, "index.html", data)

@app.get("/introduction")
async def introduction(request: Request, user: UserResponse | None = Depends(get_current_user_optional)) -> HTMLResponse:
    data: dict = {}
    if user:
        data.update(
            {"user": {"username": user.username, "is_admin": bool(user.is_admin)}}
        )

    return templates.TemplateResponse(request, "introduction.html", data)


# 파일 업로드 엔드포인트
# - "/upload": 파일 업로드 엔드포인트
# - file: 업로드할 파일 객체
# - UPLOAD_DIR: 파일 저장 디렉토리
# - dest: 파일 저장 경로
# - async with aiofiles.open(dest, "wb") as buffer: 비동기 파일 저장
@app.post("/upload")
async def upload_file(file: UploadFile) -> dict:
    if not file.filename:
        return {"error": "No filename provided"}

    dest = UPLOAD_DIR / file.filename

    # 비동기 파일 쓰기
    async with aiofiles.open(dest, "wb") as buffer:
        content = await file.read()
        await buffer.write(content)

    return {"stored": dest.name, "size": dest.stat().st_size}


# 상태 확인 엔드포인트
# - "/health": 상태 확인 엔드포인트
# - include_in_schema=False: 문서에 포함되지 않음
@app.get("/health", include_in_schema=False)
async def health_check() -> dict:
    return {"status": "ok"}


# 통합 예외처리
# - 401: 인증 실패
# - 403: 권한 없음
# - 404: 페이지 없음
# - 500: 서버 오류
@app.exception_handler(401)
async def unauthorized(request: Request, exc) -> HTMLResponse:
    return unauthorized_error(request, exc)


@app.exception_handler(403)
async def forbidden(request: Request, exc) -> HTMLResponse:
    return forbidden_error(request, exc)


@app.exception_handler(404)
async def not_found(request: Request, exc) -> HTMLResponse:
    return not_found_error(request, exc)


@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc) -> HTMLResponse:
    return internal_server_error(request, exc)


# 문서 엔드포인트
# - "/docs": Swagger UI 문서
# - dependencies=[Depends(require_admin)]: 관리자 권한 필요
# - include_in_schema=False: 문서에 포함되지 않음
@app.get("/docs", dependencies=[Depends(require_admin)], include_in_schema=False)
async def custom_swagger_ui() -> HTMLResponse:
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")


# 문서 엔드포인트
# - "/redoc": ReDoc 문서
# - dependencies=[Depends(require_admin)]: 관리자 권한 필요
# - include_in_schema=False: 문서에 포함되지 않음
@app.get("/redoc", dependencies=[Depends(require_admin)], include_in_schema=False)
async def custom_redoc() -> HTMLResponse:
    return get_redoc_html(openapi_url="/openapi.json", title="ReDoc")


# 문서 엔드포인트
# - "/openapi.json": OpenAPI 스키마
# - dependencies=[Depends(require_admin)]: 관리자 권한 필요
# - include_in_schema=False: 문서에 포함되지 않음
@app.get(
    "/openapi.json", dependencies=[Depends(require_admin)], include_in_schema=False
)
async def custom_openapi() -> JSONResponse:
    return JSONResponse(
        get_openapi(title=app.title, version=app.version, routes=app.routes)
    )
