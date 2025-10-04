from typing import List, Optional
from pydantic import BaseModel, Field


class User(BaseModel):
    id: int
    name: str
    email: str


class Comment(BaseModel):
    id: int
    post_id: int
    text: str
    author: str


class RoutePoint(BaseModel):
    lat: float
    lng: float


class Post(BaseModel):
    id: int
    title: str
    author: str
    description: Optional[str] = None
    likes: int = 0
    liked: bool = False
    comments: List[Comment] = Field(default_factory=list)
    route: List[RoutePoint] = Field(default_factory=list)
    photos: List[str] = Field(default_factory=list)


class AuthRequest(BaseModel):
    email: str = ""
    password: str = ""
    name: Optional[str] = None


class AuthResponse(BaseModel):
    token: str
    user: User


class CreatePostRequest(BaseModel):
    title: str
    description: Optional[str] = None


class CreateCommentRequest(BaseModel):
    post_id: int
    text: str


class Group(BaseModel):
    id: int
    name: str
    members: List[User] = Field(default_factory=list)



