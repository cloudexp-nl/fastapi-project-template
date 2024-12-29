from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import List

class PostBase(BaseModel):
    title: str
    content: str

    model_config = ConfigDict(from_attributes=True)

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    created_at: datetime
    updated_at: datetime
    author_id: int 

class PostPage(BaseModel):
    items: List[Post]
    total: int
    page: int
    size: int
    pages: int
    
    model_config = ConfigDict(from_attributes=True) 