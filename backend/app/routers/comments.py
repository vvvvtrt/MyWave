from typing import List
from fastapi import APIRouter, HTTPException
from ..models import Comment, CreateCommentRequest
from ..data import POSTS


router = APIRouter()


@router.get("/by-post/{post_id}", response_model=List[Comment])
def list_comments(post_id: int):
    for post in POSTS:
        if post.id == post_id:
            return post.comments
    raise HTTPException(status_code=404, detail="Post not found")


@router.post("/", response_model=Comment)
def add_comment(payload: CreateCommentRequest):
    for post in POSTS:
        if post.id == payload.post_id:
            new_comment = Comment(
                id=max([c.id for c in post.comments], default=0) + 1,
                post_id=post.id,
                text=payload.text,
                author="Вы",
            )
            post.comments.append(new_comment)
            return new_comment
    raise HTTPException(status_code=404, detail="Post not found")



