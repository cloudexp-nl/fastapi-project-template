from sqlalchemy.orm import Session
from . import models, schemas
from .constants import DEFAULT_POSTS_LIMIT, MAX_POSTS_LIMIT

def get_post(db: Session, post_id: int):
    return db.query(models.Post).filter(models.Post.id == post_id).first()

def get_posts(db: Session, skip: int = 0, limit: int = DEFAULT_POSTS_LIMIT):
    if limit > MAX_POSTS_LIMIT:
        limit = MAX_POSTS_LIMIT
    return db.query(models.Post).offset(skip).limit(limit).all()

def create_post(db: Session, post: schemas.PostCreate, user_id: int):
    db_post = models.Post(**post.model_dump(), author_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post 