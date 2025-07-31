import uuid
from contextlib import contextmanager

import pytest
from config.db import SessionLocal  # type: ignore
from config.settings import settings  # type: ignore
from fastapi.testclient import TestClient
from main import app  # type: ignore
from models import Base  # type: ignore
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

client = TestClient(app)


@contextmanager
def create_user_and_login(password="test1234!"):
    username = f"user-{uuid.uuid4().hex[:8]}"
    client.post("/register", json={"username": username, "password": password})
    response = client.post("/login", json={"username": username, "password": password})
    access_token = response.cookies.get("access_token")
    refresh_token = response.cookies.get("refresh_token")
    assert (
        access_token is not None
    ), "access_token이 None입니다. 로그인 응답을 확인하세요."
    assert (
        refresh_token is not None
    ), "refresh_token이 None입니다. 로그인 응답을 확인하세요."
    client.cookies.update(response.cookies)
    try:
        yield username, password, access_token, refresh_token
    finally:
        client.cookies.delete("access_token")
        client.cookies.delete("refresh_token")


@contextmanager
def db_session() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URL)
    Base.metadata.create_all(bind=engine)  # 테이블 생성
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def admin_user():
    response = client.post(
        "/register", json={"username": "admin", "password": "admin1234!"}
    )
    assert response.status_code == 201, "회원가입 실패"
    # DB에서 is_admin True로 변경
    from config.db import SessionLocal  # type: ignore
    from models.user import User  # type: ignore

    db = SessionLocal()
    user = db.query(User).filter_by(username="admin").first()
    assert user is not None, "admin 유저가 DB에 없음"
    user.is_admin = True
    db.commit()
    db.close()
    return (response.cookies.get("access_token"), response.cookies.get("refresh_token"))
