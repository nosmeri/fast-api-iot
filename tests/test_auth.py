import uuid
from weakref import ref
from contextlib import contextmanager

from config.db import SessionLocal
from fastapi.testclient import TestClient
from main import app
from models.refresh_tocken import RefreshToken
from services import jwt_service

client = TestClient(app)


@contextmanager
def create_user_and_login(password="test1234!"):
    username = f"user-{uuid.uuid4().hex[:8]}"
    client.post("/register", json={"username": username, "password": password})
    response = client.post("/login", json={"username": username, "password": password})
    access_token = response.cookies.get("access_token")
    refresh_token = response.cookies.get("refresh_token")
    assert access_token is not None, "access_token이 None입니다. 로그인 응답을 확인하세요."
    assert refresh_token is not None, "refresh_token이 None입니다. 로그인 응답을 확인하세요."
    client.cookies.set("access_token", access_token)
    client.cookies.set("refresh_token", refresh_token)
    try:
        yield username, password, access_token, refresh_token
    finally:
        client.cookies.delete("access_token")
        client.cookies.delete("refresh_token")


def test_register_page():
    response = client.get("/register")
    assert response.status_code == 200, "회원가입 페이지 접근 실패"


def test_register_success():
    username = f"newuser-{uuid.uuid4().hex[:8]}"
    response = client.post(
        "/register", json={"username": username, "password": "newpass1234!"}
    )
    assert response.status_code == 201, "회원가입 실패"
    access_token = response.cookies.get("access_token")
    refresh_token = response.cookies.get("refresh_token")
    assert access_token.count(".") == 2  # type: ignore
    assert refresh_token.count(".") == 2  # type: ignore


def test_register_duplicate():
    username = f"dupuser-{uuid.uuid4().hex[:8]}"
    client.post("/register", json={"username": username, "password": "pass1234!"})
    response = client.post(
        "/register", json={"username": username, "password": "pass1234!"}
    )
    assert response.status_code == 400, "중복된 회원가입 요청이 실패하지 않았습니다"


def test_register_password_rule_fail():
    username = f"pwfail-{uuid.uuid4().hex[:8]}"
    response = client.post(
        "/register", json={"username": username, "password": "123"}
    )
    assert response.status_code == 400


def test_login_page():
    response = client.get("/login")
    assert response.status_code == 200, "로그인 페이지 접근 실패"


def test_login_success():
    with create_user_and_login() as (username, password, access_token, refresh_token):
        response = client.post("/login", json={"username": username, "password": password})
        assert response.status_code == 200, "로그인 실패"
        assert access_token.count(".") == 2  # type: ignore
        assert refresh_token.count(".") == 2  # type: ignore


def test_login_wrong_password():
    with create_user_and_login() as (username, _, _, _):
        response = client.post("/login", json={"username": username, "password": "wrongpass"})
        assert response.status_code == 400


def test_login_nonexistent_user():
    username = f"idontexist-{uuid.uuid4().hex[:8]}"
    response = client.post("/login", json={"username": username, "password": "whatever123!"})
    assert response.status_code == 400


def test_login_fail():
    response = client.post("/login", json={"username": "bad", "password": "bad"})
    assert response.status_code == 400, "잘못된 로그인 요청이 실패하지 않았습니다"


def test_logout_token_removal_and_revoke():
    with create_user_and_login() as (_, _, access_token, refresh_token):
        response = client.post("/logout")
        assert response.status_code == 200, "로그아웃 실패"
        set_cookie_header = response.headers.get("set-cookie", "")
        set_cookie_headers = set_cookie_header.split(", ") if set_cookie_header else []
        access_token_deleted = any('access_token=""' in h for h in set_cookie_headers)
        assert access_token_deleted, "access_token 쿠키 삭제 안됨"
        refresh_token_deleted = any('refresh_token=""' in h for h in set_cookie_headers)
        assert refresh_token_deleted, "refresh_token 쿠키 삭제 안됨"


def test_mypage_without_token():
    response = client.get("/mypage")
    assert response.status_code == 401


def test_token_refresh_with_expired_access_token():
    with create_user_and_login() as (_, _, _, refresh_token):
        expired_access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0IiwidXNlcm5hbWUiOiJ0ZXN0IiwiaXNfYWRtaW4iOmZhbHNlLCJleHAiOjEwMDAwMDAwMDAsInR5cGUiOiJhY2Nlc3MiLCJpYXQiOjEwMDAwMDAwMDB9.signature"
        client.cookies.set("access_token", expired_access_token)
        response = client.get("/mypage")
        assert response.status_code==200


def test_refresh_token_reuse_after_logout():
    with create_user_and_login() as (_, _, access_token, refresh_token):
        response = client.post("/logout")

        expired_access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0IiwidXNlcm5hbWUiOiJ0ZXN0IiwiaXNfYWRtaW4iOmZhbHNlLCJleHAiOjEwMDAwMDAwMDAsInR5cGUiOiJhY2Nlc3MiLCJpYXQiOjEwMDAwMDAwMDB9.signature"

        # 로그아웃 후에도 강제로 쿠키를 설정해서 테스트
        client.cookies.set("access_token", expired_access_token)
        client.cookies.set("refresh_token", refresh_token)
        response = client.get("/mypage")
        # refresh token이 revoke되었으므로 401이어야 함
        assert response.status_code == 401, f"로그아웃 후 refresh token이 여전히 유효함. 응답: {response.text}"


def test_login_after_delete_account():
    with create_user_and_login() as (username, password, access_token, refresh_token):
        response = client.delete("/delete_account")
        assert response.status_code == 200
        response = client.post("/login", json={"username": username, "password": password})
        assert response.status_code == 400


def test_admin_page_without_admin():
    with create_user_and_login() as (username, password, access_token, refresh_token):
        response = client.get("/admin")
        assert response.status_code==403
