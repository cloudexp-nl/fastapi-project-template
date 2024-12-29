from typing import List
from . import models

def filter_user_posts(posts: List[models.Post], user_id: int) -> List[models.Post]:
    """Filter posts by user_id"""
    return [post for post in posts if post.author_id == user_id]

def sort_posts_by_date(posts: List[models.Post], ascending: bool = False) -> List[models.Post]:
    """Sort posts by created_at date"""
    return sorted(posts, key=lambda x: x.created_at, reverse=not ascending) 