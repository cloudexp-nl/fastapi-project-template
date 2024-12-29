from fastapi.testclient import TestClient
import pytest
from src.main import app

@pytest.mark.db
def test_api_flow(client, db_session):
    """Test the complete API flow using TestClient"""
    
    # Register user
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "Test123!@#"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    
    # Login and get token
    token_response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "testuser",
            "password": "Test123!@#"
        }
    )
    assert token_response.status_code == 200
    token = token_response.json()["access_token"]
    
    # Create a post
    post_data = {
        "title": "Test Post",
        "content": "This is a test post"
    }
    post_response = client.post(
        "/api/v1/posts/",
        headers={"Authorization": f"Bearer {token}"},
        json=post_data
    )
    assert post_response.status_code == 200
    created_post = post_response.json()
    assert created_post["title"] == post_data["title"]
    
    # Get posts and verify
    posts_response = client.get("/api/v1/posts/")
    assert posts_response.status_code == 200
    posts_data = posts_response.json()
    
    # Verify pagination data
    assert "items" in posts_data
    assert "total" in posts_data
    assert posts_data["total"] >= 1
    
    # Verify post in items
    posts = posts_data["items"]
    assert len(posts) >= 1
    assert posts[0]["title"] == post_data["title"]
    assert posts[0]["content"] == post_data["content"] 