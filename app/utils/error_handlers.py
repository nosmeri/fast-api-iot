from fastapi import Request, status
from fastapi.responses import HTMLResponse

from utils.logger import main_logger
from utils.path import templates


# 공통 에러 응답
def error_response(
    request: Request,
    error_code: int,
    error_title: str,
    error_message: str,
    status_code: int | None = None,
) -> HTMLResponse:
    if status_code is None:
        status_code = error_code

    main_logger.error(f"{error_code} {error_title} {error_message}")

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "error_code": error_code,
            "error_title": error_title,
            "error_message": error_message,
        },
        status_code=status_code,
    )


# 401 인증 실패 에러 응답
def unauthorized_error(request: Request, exc) -> HTMLResponse:
    """401 인증 실패 에러 응답"""
    return error_response(
        request,
        401,
        "인증 실패",
        "로그인이 필요합니다. 로그인 후 다시 시도해주세요.",
        status_code=status.HTTP_401_UNAUTHORIZED,
    )


# 403 권한 없음 에러 응답
def forbidden_error(request: Request, exc) -> HTMLResponse:
    """403 권한 없음 에러 응답"""
    return error_response(
        request,
        403,
        "접근 권한 없음",
        "이 페이지에 접근할 권한이 없습니다. 관리자에게 문의하세요.",
        status_code=status.HTTP_403_FORBIDDEN,
    )


# 404 페이지 없음 에러 응답
def not_found_error(request: Request, exc) -> HTMLResponse:
    """404 페이지 없음 에러 응답"""
    return error_response(
        request,
        404,
        "페이지를 찾을 수 없습니다",
        "요청하신 페이지가 존재하지 않습니다.",
        status_code=status.HTTP_404_NOT_FOUND,
    )


# 500 서버 오류 응답
def internal_server_error(request: Request, exc) -> HTMLResponse:
    """500 서버 오류 응답"""
    return error_response(
        request,
        500,
        "서버 오류",
        "서버에서 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
