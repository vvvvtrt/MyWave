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
    
    return comment