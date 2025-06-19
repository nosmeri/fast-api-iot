import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture(scope="module")
def test_user():
    # 1️⃣ 먼저 회원가입 시도
    response = client.post("/auth/register", json={
        "username": "test",
        "password": "test"
    })
    assert response.status_code in [200, 201, 400]  # 400이면 이미 존재할 수도 있음
    return {"username": "test", "password": "test"}

def test_login_success():
    response = client.post("/auth/login", json={"username": "test", "password": "test"})
    assert response.status_code == 200

def test_login_fail():
    response = client.post("/auth/login", json={"username": "bad", "password": "bad"})
    assert response.status_code == 401