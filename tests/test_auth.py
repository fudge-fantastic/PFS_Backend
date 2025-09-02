import pytest
from fastapi.testclient import TestClient
from tests.conftest import client, sample_user

def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Welcome to PixelForge E-Commerce Backend"
    assert data["version"] == "1.0.0"
    assert "supported_categories" in data

def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_user_registration(client, sample_user):
    """Test user registration."""
    response = client.post("/auth/register", json=sample_user)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] == True
    assert data["message"] == "User registered successfully"
    assert "access_token" in data["data"]
    assert data["data"]["user"]["email"] == sample_user["email"]

def test_duplicate_user_registration(client, sample_user):
    """Test duplicate user registration should fail."""
    # First registration
    client.post("/auth/register", json=sample_user)
    
    # Second registration with same email
    response = client.post("/auth/register", json=sample_user)
    assert response.status_code == 400
    data = response.json()
    assert "already registered" in data["detail"].lower()

def test_user_login(client, sample_user):
    """Test user login."""
    # Register user first
    client.post("/auth/register", json=sample_user)
    
    # Login
    login_data = {
        "email": sample_user["email"],
        "password": sample_user["password"]
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["message"] == "Login successful"
    assert "access_token" in data["data"]

def test_invalid_login(client):
    """Test login with invalid credentials."""
    login_data = {
        "email": "nonexistent@test.com",
        "password": "wrongpassword"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 401
    data = response.json()
    assert "incorrect email or password" in data["detail"].lower()

def test_get_current_user(client, sample_user):
    """Test getting current user details."""
    # Register and login
    register_response = client.post("/auth/register", json=sample_user)
    token = register_response.json()["data"]["access_token"]
    
    # Get current user
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["data"]["email"] == sample_user["email"]

def test_unauthorized_access(client):
    """Test accessing protected endpoint without token."""
    response = client.get("/users/me")
    assert response.status_code == 401

def test_invalid_token(client):
    """Test accessing protected endpoint with invalid token."""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 401
