from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File, Query, Depends
from sqlalchemy.orm import Session
from ..database import get_db, Post as PostModel, Photo as PhotoModel, Like as LikeModel, User
from ..models import Post, PostCreate, Comment, CommentCreate
from ..s3_service import s3_service
from datetime import datetime

router = APIRouter()


@router.get("/")
def list_posts(
    page: int = Query(1, ge=1), 
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit
    posts = db.query(PostModel).offset(offset).limit(limit).all()
    
    result = []
    for post in posts:
        post_dict = {
            "id": post.id,
            "title": post.title,
            "description": post.description,
            "author_id": post.author_id,
            "author": post.author,
            "likes_count": post.likes_count,
            "liked": False,  # Will be set by frontend
            "comments": post.comments,
            "photos": post.photos,
            "created_at": post.created_at,
            "updated_at": post.updated_at
        }
        result.append(post_dict)
    
    return result


@router.get("/count")
def get_posts_count(db: Session = Depends(get_db)):
    total = db.query(PostModel).count()
    return {"total": total}


@router.get("/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(PostModel).filter(PostModel.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post_dict = {
        "id": post.id,
        "title": post.title,
        "description": post.description,
        "author_id": post.author_id,
        "author": post.author,
        "likes_count": post.likes_count,
        "liked": False,
        "comments": post.comments,
        "photos": post.photos,
        "created_at": post.created_at,
        "updated_at": post.updated_at
    }
    
    return post_dict


@router.post("/")
def create_post(
    payload: PostCreate, 
    db: Session = Depends(get_db)
):
    # For now, create post without authentication
    # TODO: Add proper authentication
    post = PostModel(
        title=payload.title,
        description=payload.description,
        author_id=1  # Default user
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    
    # Add photos
    for photo_url in payload.photos:
        photo = PhotoModel(url=photo_url, post_id=post.id)
        db.add(photo)
    
    db.commit()
    db.refresh(post)
    
    return {
        "id": post.id,
        "title": post.title,
        "description": post.description,
        "author_id": post.author_id,
        "author": post.author,
        "likes_count": post.likes_count,
        "liked": False,
        "comments": post.comments,
        "photos": post.photos,
        "created_at": post.created_at,
        "updated_at": post.updated_at
    }


@router.post("/{post_id}/like")
def like_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(PostModel).filter(PostModel.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Simple like without user tracking for now
    post.likes_count += 1
    db.commit()
    db.refresh(post)
    
    return {
        "id": post.id,
        "title": post.title,
        "description": post.description,
        "author_id": post.author_id,
        "author": post.author,
        "likes_count": post.likes_count,
        "liked": True,
        "comments": post.comments,
        "photos": post.photos,
        "created_at": post.created_at,
        "updated_at": post.updated_at
    }


@router.post("/upload-photo")
async def upload_photo(file: UploadFile = File(...)):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        url = await s3_service.upload_file(file)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")