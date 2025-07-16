from fastapi.testclient import TestClient
from main import app
from app.config.db import SessionLocal
from app.services import jwt_service
from app.models.refresh_tocken import RefreshToken

client = TestClient(app)


def test_register_page():
    response = client.get("/register")
    assert response.status_code == 200, "회원가입 페이지 접근 실패"


def test_register_success():
    response = client.post(
        "/register", json={"username": "newuser", "password": "newpass1234!"}
    )
    assert response.status_code == 201, "회원가입 실패"


def test_register_duplicate():
    client.post("/register", json={"username": "dupuser", "password": "pass1234!"})
    response = client.post(
        "/register", json={"username": "dupuser", "password": "pass1234!"}
    )
    assert response.status_code == 400, "중복된 회원가입 요청이 실패하지 않았습니다"


def test_login_page():
    response = client.get("/login")
    assert response.status_code == 200, "로그인 페이지 접근 실패"


def test_login_success():
    response = client.post("/login", json={"username": "test", "password": "test1234!"})
    assert response.status_code == 200, "로그인 실패"


def test_login_fail():
    response = client.post("/login", json={"username": "bad", "password": "bad"})
    assert response.status_code == 400, "잘못된 로그인 요청이 실패하지 않았습니다"


def test_logout_token_removal_and_revoke(test_user):
    access_token, refresh_token = test_user
    # 로그아웃 요청
    response = client.post(
        "/logout",
        cookies={"access_token": access_token, "refresh_token": refresh_token},
    )
    assert response.status_code == 200, "로그아웃 실패"

    # 1. 쿠키가 삭제되었는지 확인
    set_cookie_header = response.headers.get("set-cookie", "")
    # 여러 Set-Cookie가 있을 경우 분리
    set_cookie_headers = set_cookie_header.split("\n") if "\n" in set_cookie_header else set_cookie_header.split(",")
    assert any("access_token=;" in h for h in set_cookie_headers), "access_token 쿠키 삭제 안됨"
    assert any("refresh_token=;" in h for h in set_cookie_headers), "refresh_token 쿠키 삭제 안됨"

    # 2. refresh 토큰이 DB에서 revoke 되었는지 확인
    db = SessionLocal()
    db_token = jwt_service.get_refresh_token(db, refresh_token)
    assert db_token is not None, "DB에 refresh 토큰이 없음"
    assert db_token.revoked is True, "refresh 토큰이 revoke 처리되지 않음"
    db.close()

