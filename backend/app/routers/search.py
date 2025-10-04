from typing import List
from fastapi import APIRouter, Query
from ..models import Post
from ..data import POSTS


router = APIRouter()


@router.get("/", response_model=List[Post])
def search_posts(q: str = Query("") ):
    term = q.strip().lower()
    if not term:
        return POSTS
    return [p for p in POSTS if term in p.title.lower() or (p.description or "").lower().find(term) >= 0]





