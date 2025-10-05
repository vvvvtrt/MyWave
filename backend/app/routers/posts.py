from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File, Query, Depends
from sqlalchemy.orm import Session
from ..database import get_db, Post as PostModel, Photo as PhotoModel, Like as LikeModel, User
from ..models import Post, PostCreate, Comment, CommentCreate
from ..s3_service import s3_service
from .auth import get_current_user
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
        # Get author name
        author_name = "Пользователь"
        if hasattr(post, 'author') and post.author:
            if hasattr(post.author, 'username'):
                author_name = post.author.username
            elif hasattr(post.author, 'full_name') and post.author.full_name:
                author_name = post.author.full_name
        
        # Get comments as list
        comments_list = []
        if hasattr(post, 'comments') and post.comments:
            for comment in post.comments:
                comment_author = "Пользователь"
                if hasattr(comment, 'author') and comment.author:
                    if hasattr(comment.author, 'username'):
                        comment_author = comment.author.username
                    elif hasattr(comment.author, 'full_name') and comment.author.full_name:
                        comment_author = comment.author.full_name
                
                comments_list.append({
                    "id": comment.id,
                    "text": comment.text,
                    "author": comment_author
                })
        
        # Get photos as list
        photos_list = []
        if hasattr(post, 'photos') and post.photos:
            for photo in post.photos:
                photos_list.append({
                    "id": photo.id,
                    "url": photo.url
                })
        
        post_dict = {
            "id": post.id,
            "title": post.title,
            "description": post.description or "",
            "author": author_name,
            "likes": post.likes_count or 0,
            "liked": False,
            "comments": comments_list,
            "photos": photos_list,
            "route": [],  # Empty route for now
            "created_at": post.created_at.isoformat() if post.created_at else None,
            "updated_at": post.updated_at.isoformat() if post.updated_at else None
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = PostModel(
        title=payload.title,
        description=payload.description,
        author_id=current_user.id
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
    
    # Get author name
    author_name = current_user.username if current_user.username else "Пользователь"
    
    # Get photos as list
    photos_list = []
    if hasattr(post, 'photos') and post.photos:
        for photo in post.photos:
            photos_list.append({
                "id": photo.id,
                "url": photo.url
            })
    
    return {
        "id": post.id,
        "title": post.title,
        "description": post.description or "",
        "author": author_name,
        "likes": post.likes_count or 0,
        "liked": False,
        "comments": [],
        "photos": photos_list,
        "route": [],
        "created_at": post.created_at.isoformat() if post.created_at else None,
        "updated_at": post.updated_at.isoformat() if post.updated_at else None
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