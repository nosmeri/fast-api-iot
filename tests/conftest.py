import uuid
from contextlib import asynccontextmanager

import pytest_asyncio
from config.db import AsyncSessionLocal  # type: ignore
from config.settings import settings  # type: ignore
from httpx import ASGITransport, AsyncClient
from main import app  # type: ignore
from models import Base  # type: ignore
from sqlalchemy.ext.asyncio import create_async_engine


@pytest_asyncio.fixture(autouse=True, scope="session")
async def setup_database():
    # async engine 생성
    async_database_url = settings.SQLALCHEMY_DATABASE_URL.replace(
        "postgresql://", "postgresql+asyncpg://"
    )
    async_engine = create_async_engine(async_database_url, future=True)
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(autouse=True, scope="session")
async def async_client(setup_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def create_user_and_login(async_client, password="test1234!"):
    username = f"user-{uuid.uuid4().hex[:8]}"
    await async_client.post(
        "/register", json={"username": username, "password": password}
    )
    response = await async_client.post(
        "/login", json={"username": username, "password": password}
    )
    access_token = response.cookies.get("access_token")
    refresh_token = response.cookies.get("refresh_token")
    assert (
        access_token is not None
    ), "access_token이 None입니다. 로그인 응답을 확인하세요."
    assert (
        refresh_token is not None
    ), "refresh_token이 None입니다. 로그인 응답을 확인하세요."
    async_client.cookies.set("access_token", access_token)
    async_client.cookies.set("refresh_token", refresh_token)
    try:
        yield username, password, access_token, refresh_token
    finally:
        async_client.cookies.delete("access_token")
        async_client.cookies.delete("refresh_token")


@asynccontextmanager
async def get_async_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest_asyncio.fixture(autouse=True, scope="session")
async def admin_user(async_client):
    response = await async_client.post(
        "/register", json={"username": "admin", "password": "admin1234!"}
    )
    assert response.status_code == 201, "회원가입 실패"
    # DB에서 role ADMIN으로 변경
    from models.user import User  # type: ignore
    from sqlalchemy import select

    async with get_async_db() as db:
        stmt = select(User).filter(User.username == "admin")

        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        assert user is not None, "admin 유저가 DB에 없음"
        user.role = "ADMIN"
        await db.commit()
        await db.refresh(user)
        return (
            response.cookies.get("access_token"),
            response.cookies.get("refresh_token"),
        )
