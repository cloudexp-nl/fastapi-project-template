import pytest
import requests
import json
import os
from dotenv import load_dotenv
from urllib3.exceptions import ConnectionError
from requests.exceptions import ConnectionError as RequestsConnectionError

# Get base URL from environment variable or use default
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_URL = f"{BASE_URL}/api/v1"

print(f"\nUsing API URL: {BASE_URL} (from {'environment' if 'API_BASE_URL' in os.environ else 'default'})")

def print_response(response, action):
    """Helper function to print formatted response"""
    print(f"\n{action}:")
    print(f"Status Code: {response.status_code}")
    try:
        print("Response:", json.dumps(response.json(), indent=2))
    except:
        print("Response:", response.text)

def test_api():
    try:
        # Test root endpoint
        print("\nTesting API connectivity...")
        print(f"Connecting to: {BASE_URL}")  # Print connection attempt
        response = requests.get(BASE_URL)
        print_response(response, "Root endpoint")
        assert response.status_code == 200
        
        # Register user with unique identifier
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "email": f"test{unique_id}@example.com",
            "username": f"testuser{unique_id}",
            "password": "Test123!@#"
        }
        
        print("\nRegistering new user...")
        response = requests.post(
            f"{API_URL}/auth/register",
            json=user_data
        )
        print_response(response, "User registration")
        assert response.status_code == 200
        user = response.json()
        
        # Get token
        print("\nGetting authentication token...")
        token_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        response = requests.post(
            f"{API_URL}/auth/token",
            data=token_data
        )
        print_response(response, "Token request")
        assert response.status_code == 200
        token = response.json()["access_token"]
        
        # Create posts
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Create multiple posts
        posts = []
        for i in range(3):
            print(f"\nCreating post {i+1}...")
            post_data = {
                "title": f"Test Post {i+1}",
                "content": f"This is test content for post {i+1}"
            }
            response = requests.post(
                f"{API_URL}/posts/",
                headers=headers,
                json=post_data
            )
            print_response(response, f"Create post {i+1}")
            assert response.status_code == 200
            posts.append(response.json())
        
        # Get posts with pagination
        print("\nTesting pagination...")
        response = requests.get(f"{API_URL}/posts/?page=1&size=2")
        print_response(response, "Page 1 (size 2)")
        assert response.status_code == 200
        page1 = response.json()
        assert len(page1["items"]) == 2
        
        response = requests.get(f"{API_URL}/posts/?page=2&size=2")
        print_response(response, "Page 2 (size 2)")
        assert response.status_code == 200
        page2 = response.json()
        
        # Verify pagination
        total_posts = page1["total"]
        print(f"\nTotal posts in database: {total_posts}")
        assert total_posts >= len(posts), "Not all posts were saved"
        
        # Get specific post
        first_post_id = posts[0]["id"]
        print(f"\nGetting specific post (ID: {first_post_id})...")
        response = requests.get(f"{API_URL}/posts/{first_post_id}")
        print_response(response, "Get specific post")
        assert response.status_code == 200
        assert response.json()["id"] == first_post_id
        
        print("\n✅ All tests passed successfully!")
        
    except (ConnectionError, RequestsConnectionError) as e:
        pytest.skip(f"API server is not running at {BASE_URL}. Error: {str(e)}")
    except AssertionError as e:
        print(f"\n❌ Test failed: {str(e)}")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        raise

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 