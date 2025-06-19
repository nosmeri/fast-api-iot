import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_login_success():
    response = client.post("/auth/login", json={"username": "test", "password": "test"})
    assert response.status_code == 200

def test_login_fail():
    response = client.post("/auth/login", json={"username": "bad", "password": "bad"})
    assert response.status_code == 401