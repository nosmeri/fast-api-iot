import uuid

import pytest
from main import app  # type: ignore


@pytest.mark.asyncio
async def test_register_page(async_client):
    response = await async_client.get("/register")
    assert response.status_code == 200, "회원가입 페이지 접근 실패"


@pytest.mark.asyncio
async def test_register_success(async_client):
    username = f"newuser-{uuid.uuid4().hex[:8]}"
    response = await async_client.post(
        "/register", json={"username": username, "password": "newpass1234!"}
    )
    assert response.status_code == 201, "회원가입 실패"
    access_token = response.cookies.get("access_token")
    refresh_token = response.cookies.get("refresh_token")
    assert access_token.count(".") == 2
    assert refresh_token.count(".") == 2


@pytest.mark.asyncio
async def test_register_duplicate(async_client):
    username = f"dupuser-{uuid.uuid4().hex[:8]}"
    await async_client.post(
        "/register", json={"username": username, "password": "pass1234!"}
    )
    response = await async_client.post(
        "/register", json={"username": username, "password": "pass1234!"}
    )
    assert response.status_code == 400, "중복된 회원가입 요청이 실패하지 않았습니다"


@pytest.mark.asyncio
async def test_register_password_rule_fail(async_client):
    username = f"pwfail-{uuid.uuid4().hex[:8]}"
    response = await async_client.post(
        "/register", json={"username": username, "password": "123"}
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_page(async_client):
    response = await async_client.get("/login")
    assert response.status_code == 200, "로그인 페이지 접근 실패"


@pytest.mark.asyncio
async def test_login_success(async_client, create_user_and_login):
    username, password, access_token, refresh_token = create_user_and_login
    response = await async_client.post(
        "/login", json={"username": username, "password": password}
    )
    assert response.status_code == 200, "로그인 실패"
    assert access_token.count(".") == 2
    assert refresh_token.count(".") == 2


@pytest.mark.asyncio
async def test_login_wrong_password(async_client, create_user_and_login):
    username, _, _, _ = create_user_and_login
    response = await async_client.post(
        "/login", json={"username": username, "password": "wrongpass"}
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_nonexistent_user(async_client):
    username = f"idontexist-{uuid.uuid4().hex[:8]}"
    response = await async_client.post(
        "/login", json={"username": username, "password": "whatever123!"}
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_fail(async_client):
    response = await async_client.post(
        "/login", json={"username": "bad", "password": "bad"}
    )
    assert response.status_code == 400, "잘못된 로그인 요청이 실패하지 않았습니다"


@pytest.mark.asyncio
async def test_logout_token_removal_and_revoke(async_client, create_user_and_login):
    username, _, _, _ = create_user_and_login
    response = await async_client.post("/logout")
    assert response.status_code == 200, "로그아웃 실패"
    set_cookie_header = response.headers.get("set-cookie", "")
    set_cookie_headers = set_cookie_header.split(", ") if set_cookie_header else []
    access_token_deleted = any('access_token=""' in h for h in set_cookie_headers)
    assert access_token_deleted, "access_token 쿠키 삭제 안됨"
    refresh_token_deleted = any('refresh_token=""' in h for h in set_cookie_headers)
    assert refresh_token_deleted, "refresh_token 쿠키 삭제 안됨"


@pytest.mark.asyncio
async def test_mypage_without_token(async_client):
    response = await async_client.get("/mypage/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_token_refresh_with_expired_access_token(
    async_client, create_user_and_login
):
    username, _, _, _ = create_user_and_login
    expired_access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0IiwidXNlcm5hbWUiOiJ0ZXN0IiwiaXNfYWRtaW4iOmZhbHNlLCJleHAiOjEwMDAwMDAwMDAsInR5cGUiOiJhY2Nlc3MiLCJpYXQiOjEwMDAwMDAwMDB9.signature"
    async_client.cookies.set("access_token", expired_access_token)
    response = await async_client.get("/mypage/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_refresh_token_reuse_after_logout(async_client, create_user_and_login):
    username, _, _, refresh_token = create_user_and_login
    response = await async_client.post("/logout")

    expired_access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0IiwidXNlcm5hbWUiOiJ0ZXN0IiwiaXNfYWRtaW4iOmZhbHNlLCJleHAiOjEwMDAwMDAwMDAsInR5cGUiOiJhY2Nlc3MiLCJpYXQiOjEwMDAwMDAwMDB9.signature"

    # 로그아웃 후에도 강제로 쿠키를 설정해서 테스트
    async_client.cookies.set("access_token", expired_access_token)
    async_client.cookies.set("refresh_token", refresh_token)
    response = await async_client.get("/mypage/")
    # refresh token이 revoke되었으므로 401이어야 함
    assert (
        response.status_code == 401
    ), f"로그아웃 후 refresh token이 여전히 유효함. 응답: {response.text}"


@pytest.mark.asyncio
async def test_login_after_delete_account(async_client, create_user_and_login):
    username, password, _, _ = create_user_and_login
    response = await async_client.delete("/delete_account")
    assert response.status_code == 200
    response = await async_client.post(
        "/login", json={"username": username, "password": password}
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_admin_page_without_admin(async_client, create_user_and_login):
    username, _, _, _ = create_user_and_login
    response = await async_client.get("/admin/")
    assert response.status_code == 403
