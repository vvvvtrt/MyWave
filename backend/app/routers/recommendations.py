from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from random import choice, randint, sample
from typing import List, Dict
from ..database import get_db, User
from ..routers.auth import get_current_user
from ..database import UserSurvey
from ..osm_recommender import TravelRecommender


router = APIRouter()


_AUTHORS = [
    "Ольга", "Иван", "Анна", "Дима", "Мария", "Пётр", "Лена", "Сергей", "Екатерина", "Алексей"
]


@router.get("/")
def get_recommendations_endpoint(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    survey = db.query(UserSurvey).filter(UserSurvey.user_id == current_user.id).first()
    city = (survey.city if survey and survey.city else "Saint Petersburg")
    user_prefs: Dict[str, float] = {}
    if survey and survey.favorite_category:
        user_prefs[survey.favorite_category.lower()] = 0.9
    # reasonable defaults
    for cat in ['архитектура','природа','рестораны','музеи','развлечения']:
        user_prefs.setdefault(cat, 0.5)

    recommender = TravelRecommender(db_path='places.db')
    # No likes history available yet -> empty
    recs = recommender.get_recommendations(user_liked_ids=[], user_preferences=user_prefs, city=city, n_recommendations=16)

    posts = []
    for place, score in recs:
        posts.append({
            "id": place["id"],
            "title": place["name"],
            "description": place.get("description") or f"Рекомендовано для вас в {city}",
            "author": choice(_AUTHORS),
            "likes": randint(0, 250),
            "liked": False,
            "comments": [],
            "photos": ([{"url": place.get("image_url")}] if place.get("image_url") else []),
            "route": []
        })

    # If recommender returns nothing, fallback to empty
    return posts



