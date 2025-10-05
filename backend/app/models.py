from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=4, max_length=72)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserProfile(User):
    posts_count: int = 0
    likes_count: int = 0


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class CommentBase(BaseModel):
    text: str


class CommentCreate(CommentBase):
    post_id: int


class Comment(CommentBase):
    id: int
    post_id: int
    author_id: int
    author: User
    created_at: datetime
    
    class Config:
        from_attributes = True


class RoutePoint(BaseModel):
    lat: float
    lng: float


class Photo(BaseModel):
    id: int
    url: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class PostBase(BaseModel):
    title: str
    description: Optional[str] = None


class PostCreate(PostBase):
    photos: List[str] = Field(default_factory=list)


class Post(PostBase):
    id: int
    author_id: int
    author: User
    likes_count: int
    liked: bool = False
    comments: List[Comment] = Field(default_factory=list)
    photos: List[Photo] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Group(BaseModel):
    id: int
    name: str
    members: List[User] = Field(default_factory=list)



