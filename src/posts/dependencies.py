from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.auth.dependencies import get_current_user
from . import models
from .constants import UNAUTHORIZED_MSG

async def get_post_by_id(
    post_id: int,
    db: Session = Depends(get_db)
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

async def verify_post_owner(
    post: models.Post = Depends(get_post_by_id),
    current_user = Depends(get_current_user)
):
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=UNAUTHORIZED_MSG
        )
    return post 