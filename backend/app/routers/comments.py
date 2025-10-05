from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import get_db, Comment as CommentModel, Post as PostModel
from ..models import Comment, CommentCreate

router = APIRouter()


@router.get("/by-post/{post_id}")
def list_comments(post_id: int, db: Session = Depends(get_db)):
    comments = db.query(CommentModel).filter(CommentModel.post_id == post_id).all()
    return comments


@router.post("/")
def add_comment(
    payload: CommentCreate, 
    db: Session = Depends(get_db)
):
    # Check if post exists
    post = db.query(PostModel).filter(PostModel.id == payload.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Create comment
    comment = CommentModel(
        text=payload.text,
        post_id=payload.post_id,
        author_id=1  # Default user for now
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    # Get author name
    author_name = "Пользователь"
    if hasattr(comment, 'author') and comment.author:
        if hasattr(comment.author, 'username'):
            author_name = comment.author.username
        elif hasattr(comment.author, 'full_name') and comment.author.full_name:
            author_name = comment.author.full_name
    
    return {
        "id": comment.id,
        "text": comment.text,
        "author": author_name
    }