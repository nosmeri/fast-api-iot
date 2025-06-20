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


@pytest.fixture(scope="session", autouse=True)
def test_user():
    response = client.post("/register", json={"username": "test", "password": "test"})
    assert response.status_code == 201, "회원가입 실패"
    return response.cookies.get("session")
