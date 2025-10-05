from typing import List
from fastapi import APIRouter, Query, Depends
from ..database import get_db, Post as PostModel
from sqlalchemy.orm import Session
from sqlalchemy import or_


router = APIRouter()


@router.get("/")
def search_posts(q: str = Query(""), db: Session = Depends(get_db)):
    term = q.strip().lower()
    if not term:
        return []
    
    # Поиск по заголовку и описанию
    posts = db.query(PostModel).filter(
        or_(
            PostModel.title.ilike(f"%{term}%"),
            PostModel.description.ilike(f"%{term}%")
        )
    ).all()
    
    return posts





