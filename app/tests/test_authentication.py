import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_login_get():
    response = client.get("/login")
    assert response.status_code == 200  # expects login form rendered

def test_register_get():
    response = client.get("/register")
    assert response.status_code == 200  # expects register form rendered

def test_changepw_get_unauthorized():
    response = client.get("/changepw")
    assert response.status_code == 401  # Unauthorized access expected

def test_login_post_invalid_credentials():
    payload = {"username": "nonexistent", "password": "wrongpassword"}
    response = client.post("/login", json=payload)
    assert response.status_code == 400  # Invalid credentials should return error

def test_login_post_valid_credentials():
    payload = {"username": "existinguser", "password": "password123"}
    response = client.post("/login", json=payload)
    assert response.status_code == 200  # Successful login should return 200
    assert "session" in response.cookies  # Check if session cookie is set

def test_register_post_existing_user():
    payload = {"username": "existinguser", "password": "password123"}
    response = client.post("/register", json=payload)
    assert response.status_code == 400  # Existing user should return error