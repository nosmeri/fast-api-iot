import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture(scope="module")
def test_user():
    # 1️⃣ 먼저 회원가입 시도
    response = client.post("/register", json={
        "username": "test",
        "password": "test"
    })
    assert response.status_code == 201, "회원가입 실패"
    return {"username": "test", "password": "test"}

def test_login_success(test_user):
    response = client.post("/login", json=test_user)
    print(response.json())
    assert response.status_code == 200, "로그인 실패"

def test_login_fail():
    response = client.post("/login", json={"username": "bad", "password": "bad"})
    assert response.status_code == 400, "잘못된 로그인 요청이 실패하지 않았습니다"