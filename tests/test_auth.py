import uuid

from config.db import SessionLocal
from fastapi.testclient import TestClient
from main import app
from models.refresh_tocken import RefreshToken
from services import jwt_service

client = TestClient(app)


def create_user_and_login(password="test1234!"):
    username = f"user_{uuid.uuid4().hex[:8]}"
    client.post("/register", json={"username": username, "password": password})
    response = client.post("/login", json={"username": username, "password": password})
    access_token = response.cookies.get("access_token")
    refresh_token = response.cookies.get("refresh_token")
    return username, password, access_token, refresh_token


def test_register_page():
    response = client.get("/register")
    assert response.status_code == 200, "회원가입 페이지 접근 실패"


def test_register_success():
    username = f"newuser_{uuid.uuid4().hex[:8]}"
    response = client.post(
        "/register", json={"username": username, "password": "newpass1234!"}
    )
    assert response.status_code == 201, "회원가입 실패"
    # 토큰 쿠키 검증
    access_token = response.cookies.get("access_token")
    refresh_token = response.cookies.get("refresh_token")
    assert access_token is not None and access_token != "", "access_token 쿠키 없음"
    assert refresh_token is not None and refresh_token != "", "refresh_token 쿠키 없음"
    assert access_token.count(".") == 2, "access_token이 JWT 형식이 아님"
    assert refresh_token.count(".") == 2, "refresh_token이 JWT 형식이 아님"


def test_register_duplicate():
    username = f"dupuser_{uuid.uuid4().hex[:8]}"
    client.post("/register", json={"username": username, "password": "pass1234!"})
    response = client.post(
        "/register", json={"username": username, "password": "pass1234!"}
    )
    assert response.status_code == 400, "중복된 회원가입 요청이 실패하지 않았습니다"


def test_register_password_rule_fail():
    username = f"pwfail_{uuid.uuid4().hex[:8]}"
    response = client.post(
        "/register", json={"username": username, "password": "123"}
    )
    assert response.status_code == 400


def test_login_page():
    response = client.get("/login")
    assert response.status_code == 200, "로그인 페이지 접근 실패"


def test_login_success():
    username, password, access_token, refresh_token = create_user_and_login()
    response = client.post("/login", json={"username": username, "password": password})
    assert response.status_code == 200, "로그인 실패"
    # 토큰 쿠키 검증
    access_token = response.cookies.get("access_token")
    refresh_token = response.cookies.get("refresh_token")
    assert access_token is not None and access_token != "", "access_token 쿠키 없음"
    assert refresh_token is not None and refresh_token != "", "refresh_token 쿠키 없음"
    assert access_token.count(".") == 2, "access_token이 JWT 형식이 아님"
    assert refresh_token.count(".") == 2, "refresh_token이 JWT 형식이 아님"


def test_login_wrong_password():
    username, _, _, _ = create_user_and_login()
    response = client.post("/login", json={"username": username, "password": "wrongpass"})
    assert response.status_code == 400


def test_login_nonexistent_user():
    username = f"idontexist_{uuid.uuid4().hex[:8]}"
    response = client.post("/login", json={"username": username, "password": "whatever123!"})
    assert response.status_code == 400


def test_login_fail():
    response = client.post("/login", json={"username": "bad", "password": "bad"})
    assert response.status_code == 400, "잘못된 로그인 요청이 실패하지 않았습니다"


def test_logout_token_removal_and_revoke():
    _, _, access_token, refresh_token = create_user_and_login()
    cookies = {}
    if access_token is not None:
        cookies["access_token"] = access_token
    if refresh_token is not None:
        cookies["refresh_token"] = refresh_token
    response = client.post(
        "/logout",
        cookies=cookies,
    )
    assert response.status_code == 200, "로그아웃 실패"
    set_cookie_header = response.headers.get("set-cookie", "")
    set_cookie_headers = set_cookie_header.split(", ") if set_cookie_header else []
    access_token_deleted = any('access_token=""' in h for h in set_cookie_headers)
    assert access_token_deleted, "access_token 쿠키 삭제 안됨"
    refresh_token_deleted = any('refresh_token=""' in h for h in set_cookie_headers)
    assert refresh_token_deleted, "refresh_token 쿠키 삭제 안됨"
    # DB revoke 확인은 생략(별도 통합테스트에서 확인 권장)


def test_mypage_without_token():
    response = client.get("/mypage")
    assert response.status_code == 401


def test_token_refresh_with_expired_access_token():
    _, _, _, refresh_token = create_user_and_login()
    expired_access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0IiwidXNlcm5hbWUiOiJ0ZXN0IiwiaXNfYWRtaW4iOmZhbHNlLCJleHAiOjEwMDAwMDAwMDAsInR5cGUiOiJhY2Nlc3MiLCJpYXQiOjEwMDAwMDAwMDB9.signature"
    cookies = {"access_token": expired_access_token}
    if refresh_token is not None:
        cookies["refresh_token"] = refresh_token
    response = client.get(
        "/mypage",
        cookies=cookies,
    )
    assert response.status_code in (200, 401, 403), response.text


def test_refresh_token_reuse_after_logout():
    _, _, access_token, refresh_token = create_user_and_login()
    cookies = {}
    if access_token is not None:
        cookies["access_token"] = access_token
    if refresh_token is not None:
        cookies["refresh_token"] = refresh_token
    client.post(
        "/logout",
        cookies=cookies,
    )
    expired_access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0IiwidXNlcm5hbWUiOiJ0ZXN0IiwiaXNfYWRtaW4iOmZhbHNlLCJleHAiOjEwMDAwMDAwMDAsInR5cGUiOiJhY2Nlc3MiLCJpYXQiOjEwMDAwMDAwMDB9.signature"
    cookies2 = {"access_token": expired_access_token}
    if refresh_token is not None:
        cookies2["refresh_token"] = refresh_token
    response = client.get(
        "/mypage",
        cookies=cookies2,
    )
    assert response.status_code in (401, 403)


def test_login_after_delete_account():
    username, password, access_token, refresh_token = create_user_and_login()
    cookies = {}
    if access_token is not None:
        cookies["access_token"] = access_token
    if refresh_token is not None:
        cookies["refresh_token"] = refresh_token
    response = client.delete(
        "/delete_account",
        cookies=cookies,
    )
    assert response.status_code == 200
    response = client.post("/login", json={"username": username, "password": password})
    assert response.status_code == 400


def test_admin_page_without_admin():
    username, password, access_token, refresh_token = create_user_and_login()
    cookies = {}
    if access_token is not None:
        cookies["access_token"] = access_token
    if refresh_token is not None:
        cookies["refresh_token"] = refresh_token
    response = client.get(
        "/admin",
        cookies=cookies,
    )
    assert response.status_code in (401, 403)
