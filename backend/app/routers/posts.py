from typing import List
from fastapi import APIRouter, HTTPException
from ..models import Post, CreatePostRequest
from ..data import POSTS, sample_route


router = APIRouter()


@router.get("/", response_model=List[Post])
def list_posts():
    return POSTS


@router.get("/{post_id}", response_model=Post)
def get_post(post_id: int):
    for post in POSTS:
        if post.id == post_id:
            return post
    raise HTTPException(status_code=404, detail="Post not found")


@router.post("/", response_model=Post)
def create_post(payload: CreatePostRequest):
    new_id = max((p.id for p in POSTS), default=0) + 1
    post = Post(
        id=new_id,
        title=payload.title,
        author="Вы",
        description=payload.description,
        likes=0,
        liked=False,
        comments=[],
        route=sample_route(),
        photos=[],
    )
    POSTS.insert(0, post)
    return post


@router.post("/{post_id}/like", response_model=Post)
def like_post(post_id: int):
    for post in POSTS:
        if post.id == post_id:
            post.likes += 1
            post.liked = True
            return post
    raise HTTPException(status_code=404, detail="Post not found")



