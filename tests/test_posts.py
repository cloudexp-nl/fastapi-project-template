import pytest
from fastapi.testclient import TestClient
from src.main import app
from typing import List, Dict
import math
from sqlalchemy import text

def create_bulk_posts(client: TestClient, token: str, count: int) -> List[Dict]:
    """Create a specified number of posts and return their data."""
    created_posts = []
    for i in range(count):
        response = client.post(
            "/api/v1/posts/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": f"Test Post {i+1}",
                "content": f"Test Content for post {i+1}"
            }
        )
        assert response.status_code == 200, f"Failed to create post {i+1}"
        created_posts.append(response.json())
    return created_posts

def get_all_posts_paginated(client: TestClient, page_size: int = 10) -> List[Dict]:
    """Fetch all posts using pagination."""
    all_posts = []
    page = 1
    while True:
        response = client.get(f"/api/v1/posts/?page={page}&size={page_size}")
        assert response.status_code == 200
        data = response.json()
        
        # Assuming the API returns a structure like {"items": [...], "total": n}
        posts = data["items"]
        total = data["total"]
        
        all_posts.extend(posts)
        
        # Break if we've got all posts
        if len(all_posts) >= total:
            break
        
        page += 1
    
    return all_posts

@pytest.mark.db
def test_bulk_posts_creation_and_pagination(client, test_user_token, capsys, db_session):
    # Test parameters
    TOTAL_POSTS = 105
    PAGE_SIZE = 10
    
    with capsys.disabled():
        print(f"\nCreating {TOTAL_POSTS} posts...")
    created_posts = create_bulk_posts(client, test_user_token, TOTAL_POSTS)
    assert len(created_posts) == TOTAL_POSTS
    
    with capsys.disabled():
        print("Fetching all posts using pagination...")
    fetched_posts = get_all_posts_paginated(client, PAGE_SIZE)
    
    # Get total posts from API
    response = client.get("/api/v1/posts/")
    total_from_api = response.json()["total"]
    
    # Get total posts directly from database
    result = db_session.execute(text("SELECT COUNT(*) FROM posts"))
    total_in_db = result.scalar()
    
    # Verify counts match between API and database
    assert total_from_api == total_in_db, \
        f"API total ({total_from_api}) doesn't match database total ({total_in_db})"
    
    assert len(fetched_posts) == TOTAL_POSTS == total_in_db, \
        f"Mismatch in counts: fetched={len(fetched_posts)}, expected={TOTAL_POSTS}, db={total_in_db}"
    
    # Create sets of post IDs for comparison
    created_ids = {post["id"] for post in created_posts}
    fetched_ids = {post["id"] for post in fetched_posts}
    
    # Get all IDs directly from database for complete verification
    db_ids_result = db_session.execute(text("SELECT id FROM posts ORDER BY id"))
    db_ids = {row[0] for row in db_ids_result}
    
    # Verify all sets of IDs match
    assert created_ids == fetched_ids == db_ids, \
        f"""ID mismatch:
        Created IDs count: {len(created_ids)}
        Fetched IDs count: {len(fetched_ids)}
        DB IDs count: {len(db_ids)}
        """
    
    expected_pages = math.ceil(TOTAL_POSTS / PAGE_SIZE)
    full_pages = TOTAL_POSTS // PAGE_SIZE
    remaining_posts = TOTAL_POSTS % PAGE_SIZE
    
    with capsys.disabled():
        print(f"\nPagination Summary:")
        print(f"Total posts created: {TOTAL_POSTS}")
        print(f"Total posts fetched: {len(fetched_posts)}")
        print(f"Total posts in DB (SQL): {total_in_db}")
        print(f"Total posts from API: {total_from_api}")
        print(f"Page size: {PAGE_SIZE}")
        print(f"\nPages breakdown:")
        print(f"- Full pages (with {PAGE_SIZE} posts each): {full_pages}")
        print(f"- Last page (with {remaining_posts} posts): 1")
        print(f"- Total pages needed: {expected_pages} ({full_pages} full + 1 partial)")
        
        print("\nID Verification:")
        print(f"Created IDs count: {len(created_ids)}")
        print(f"Fetched IDs count: {len(fetched_ids)}")
        print(f"DB IDs count: {len(db_ids)}")
        print(f"All posts successfully verified!")

@pytest.mark.db
def test_create_and_get_posts(client, test_user_token):
    # Create first post
    first_post = client.post(
        "/api/v1/posts/",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={
            "title": "First Test Post",
            "content": "First Test Content"
        }
    )
    assert first_post.status_code == 200
    first_created = first_post.json()
    assert first_created["title"] == "First Test Post"
    assert first_created["content"] == "First Test Content"
    
    # Create second post
    second_post = client.post(
        "/api/v1/posts/",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={
            "title": "Second Test Post",
            "content": "Second Test Content"
        }
    )
    assert second_post.status_code == 200
    second_created = second_post.json()
    assert second_created["title"] == "Second Test Post"
    assert second_created["content"] == "Second Test Content"
    
    # Get all posts
    get_response = client.get("/api/v1/posts/")
    assert get_response.status_code == 200
    response_data = get_response.json()
    
    # Verify pagination data
    assert "items" in response_data
    assert "total" in response_data
    assert response_data["total"] == 2
    
    # Get posts from items
    posts = response_data["items"]
    assert isinstance(posts, list)
    assert len(posts) == 2, f"Expected 2 posts, but got {len(posts)}"
    
    # Find both posts in the list
    posts_by_id = {post["id"]: post for post in posts}
    
    # Verify first post
    assert first_created["id"] in posts_by_id
    first_found = posts_by_id[first_created["id"]]
    assert first_found["title"] == "First Test Post"
    assert first_found["content"] == "First Test Content"
    
    # Verify second post
    assert second_created["id"] in posts_by_id
    second_found = posts_by_id[second_created["id"]]
    assert second_found["title"] == "Second Test Post"
    assert second_found["content"] == "Second Test Content"

