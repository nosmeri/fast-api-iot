from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_register_page():
    response = client.get("/register")
    assert response.status_code == 200, "회원가입 페이지 접근 실패"


def test_register_success():
    response = client.post(
        "/register", json={"username": "newuser", "password": "newpass1234!"}
    )
    assert response.status_code == 201, "회원가입 실패"


def test_register_duplicate():
    client.post("/register", json={"username": "dupuser", "password": "pass1234!"})
    response = client.post(
        "/register", json={"username": "dupuser", "password": "pass1234!"}
    )
    assert response.status_code == 400, "중복된 회원가입 요청이 실패하지 않았습니다"


def test_login_page():
    response = client.get("/login")
    assert response.status_code == 200, "로그인 페이지 접근 실패"


def test_login_success():
    response = client.post("/login", json={"username": "test", "password": "test1234!"})
    assert response.status_code == 200, "로그인 실패"


def test_login_fail():
    response = client.post("/login", json={"username": "bad", "password": "bad"})
    assert response.status_code == 400, "잘못된 로그인 요청이 실패하지 않았습니다"
