from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.auth.dependencies import get_current_user
from src.auth.schemas import User
from . import schemas, service, models

router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("/", response_model=schemas.Post)
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return service.create_post(db=db, post=post, user_id=current_user.id)

@router.get("/", response_model=schemas.PostPage)
def get_posts(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * size
    total = db.query(models.Post).count()
    posts = db.query(models.Post)\
        .offset(skip)\
        .limit(size)\
        .all()
    
    return {
        "items": posts,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }

@router.get("/{post_id}", response_model=schemas.Post)
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = service.get_post(db, post_id=post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post 