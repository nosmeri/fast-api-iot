import pytest
from config.settings import settings
from fastapi.testclient import TestClient
from main import app
from models import Base
from sqlalchemy import create_engine

client = TestClient(app)


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
    from config.db import SessionLocal
    from models.user import User
    db = SessionLocal()
    user = db.query(User).filter_by(username="admin").first()
    assert user is not None, "admin 유저가 DB에 없음"
    user.is_admin = True
    db.commit()
    db.close()
    return (response.cookies.get("access_token"), response.cookies.get("refresh_token"))
