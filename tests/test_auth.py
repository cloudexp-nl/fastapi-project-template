import pytest
from fastapi.testclient import TestClient
from src.main import app

@pytest.mark.db
def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "new@example.com",
            "username": "newuser",
            "password": "Test123!@#"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "new@example.com"
    assert data["username"] == "newuser"

@pytest.mark.db
def test_create_post(client, test_user_token):
    response = client.post(
        "/api/v1/posts/",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={
            "title": "Test Post",
            "content": "Test Content"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Post"
    assert data["content"] == "Test Content" 