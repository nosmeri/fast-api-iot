from config.db import SessionLocal
from fastapi.testclient import TestClient
from main import app
from models.refresh_tocken import RefreshToken
from services import jwt_service

client = TestClient(app)


def test_register_page():
    response = client.get("/register")
    assert response.status_code == 200, "회원가입 페이지 접근 실패"


def test_register_success():
    response = client.post(
        "/register", json={"username": "newuser", "password": "newpass1234!"}
    )
    assert response.status_code == 201, "회원가입 실패"
    # 토큰 쿠키 검증
    access_token = response.cookies.get("access_token")
    refresh_token = response.cookies.get("refresh_token")
    assert access_token is not None and access_token != "", "access_token 쿠키 없음"
    assert refresh_token is not None and refresh_token != "", "refresh_token 쿠키 없음"
    # JWT 형식인지 간단히 확인
    assert access_token.count(".") == 2, "access_token이 JWT 형식이 아님"
    assert refresh_token.count(".") == 2, "refresh_token이 JWT 형식이 아님"


def test_register_duplicate():
    client.post("/register", json={"username": "dupuser", "password": "pass1234!"})
    response = client.post(
        "/register", json={"username": "dupuser", "password": "pass1234!"}
    )
    assert response.status_code == 400, "중복된 회원가입 요청이 실패하지 않았습니다"


def test_register_password_rule_fail():
    # 너무 짧은 비밀번호
    response = client.post(
        "/register", json={"username": "pwfail", "password": "123"}
    )
    assert response.status_code == 400


def test_login_page():
    response = client.get("/login")
    assert response.status_code == 200, "로그인 페이지 접근 실패"


def test_login_success():
    response = client.post("/login", json={"username": "test", "password": "test1234!"})
    assert response.status_code == 200, "로그인 실패"
    # 토큰 쿠키 검증
    access_token = response.cookies.get("access_token")
    refresh_token = response.cookies.get("refresh_token")
    assert access_token is not None and access_token != "", "access_token 쿠키 없음"
    assert refresh_token is not None and refresh_token != "", "refresh_token 쿠키 없음"
    # JWT 형식인지 간단히 확인
    assert access_token.count(".") == 2, "access_token이 JWT 형식이 아님"
    assert refresh_token.count(".") == 2, "refresh_token이 JWT 형식이 아님"


def test_login_wrong_password():
    # 존재하는 아이디, 틀린 비밀번호
    client.post("/register", json={"username": "wrongpw", "password": "rightpass123!"})
    response = client.post("/login", json={"username": "wrongpw", "password": "wrongpass"})
    assert response.status_code == 400


def test_login_nonexistent_user():
    response = client.post("/login", json={"username": "idontexist", "password": "whatever123!"})
    assert response.status_code == 400


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

    # 여러 Set-Cookie가 있을 경우 분리 (쉼표로 구분)
    set_cookie_headers = set_cookie_header.split(", ") if set_cookie_header else []

    # access_token 쿠키 삭제 확인 (쿠키 이름이 포함되어 있는지 확인)
    access_token_deleted = any('access_token=""' in h for h in set_cookie_headers)
    assert access_token_deleted, "access_token 쿠키 삭제 안됨"

    # refresh_token 쿠키 삭제 확인 (쿠키 이름이 포함되어 있는지 확인)
    refresh_token_deleted = any('refresh_token=""' in h for h in set_cookie_headers)
    assert refresh_token_deleted, "refresh_token 쿠키 삭제 안됨"

    # 2. refresh 토큰이 DB에서 revoke 되었는지 확인
    db = SessionLocal()
    db_token = jwt_service.get_refresh_token(db, refresh_token)
    assert db_token is not None, "DB에 refresh 토큰이 없음"
    assert db_token.revoked is True, "refresh 토큰이 revoke 처리되지 않음"
    db.close()


def test_mypage_without_token():
    response = client.get("/mypage")
    assert response.status_code == 401


def test_token_refresh_with_expired_access_token(test_user):
    # access_token을 일부러 만료시킨 값으로 대체 (임의의 만료 토큰)
    expired_access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0IiwidXNlcm5hbWUiOiJ0ZXN0IiwiaXNfYWRtaW4iOmZhbHNlLCJleHAiOjEwMDAwMDAwMDAsInR5cGUiOiJhY2Nlc3MiLCJpYXQiOjEwMDAwMDAwMDB9.signature"
    _, refresh_token = test_user
    response = client.get(
        "/mypage",
        cookies={"access_token": expired_access_token, "refresh_token": refresh_token},
    )
    # 자동 갱신되면 200, 실패하면 401/403 (정책에 따라 다름)
    assert response.status_code == 200, response.json()["detail"]


def test_refresh_token_reuse_after_logout(test_user):
    access_token, refresh_token = test_user
    # 로그아웃
    client.post(
        "/logout",
        cookies={"access_token": access_token, "refresh_token": refresh_token},
    )
    # 로그아웃 후 refresh_token 재사용 시도 (토큰 갱신 시도)
    expired_access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0IiwidXNlcm5hbWUiOiJ0ZXN0IiwiaXNfYWRtaW4iOmZhbHNlLCJleHAiOjEwMDAwMDAwMDAsInR5cGUiOiJhY2Nlc3MiLCJpYXQiOjEwMDAwMDAwMDB9.signature"
    response = client.get(
        "/mypage",
        cookies={"access_token": expired_access_token, "refresh_token": refresh_token},
    )
    assert response.status_code==401


def test_login_after_delete_account():
    # 회원가입
    response = client.post("/register", json={"username": "deluser", "password": "deluser123!"})
    assert response.status_code == 201
    # 로그인
    response = client.post("/login", json={"username": "deluser", "password": "deluser123!"})
    assert response.status_code == 200
    access_token = response.cookies.get("access_token")
    refresh_token = response.cookies.get("refresh_token")
    cookies = {}
    if access_token:
        cookies["access_token"] = access_token
    if refresh_token:
        cookies["refresh_token"] = refresh_token
    # 회원탈퇴
    response = client.delete(
        "/delete_account",
        cookies=cookies,
    )
    assert response.status_code == 200
    # 탈퇴 후 로그인 시도
    response = client.post("/login", json={"username": "deluser", "password": "deluser123!"})
    assert response.status_code == 400


def test_admin_page_without_admin():
    # 일반 유저로 로그인
    response = client.post("/register", json={"username": "notadmin", "password": "notadmin123!"})
    assert response.status_code == 201
    access_token = response.cookies.get("access_token")
    refresh_token = response.cookies.get("refresh_token")
    cookies = {}
    if access_token:
        cookies["access_token"] = access_token
    if refresh_token:
        cookies["refresh_token"] = refresh_token
    # 관리자 페이지 접근 시도
    response = client.get(
        "/admin",
        cookies=cookies,
    )
    assert response.status_code in (401, 403)
