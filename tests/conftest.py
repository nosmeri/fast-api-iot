import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def test_user():
    response = client.post("/register", json={"username": "test", "password": "test"})
    assert response.status_code == 201, "회원가입 실패"
    return response.cookies.get("session")
