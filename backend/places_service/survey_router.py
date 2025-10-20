from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from database import get_db, UserSurvey
from auth import get_current_user


router = APIRouter()


class SurveyPayload(BaseModel):
    favorite_category: Optional[str] = None
    activity_level: Optional[str] = None
    budget_level: Optional[str] = None
    city: Optional[str] = None


@router.get("/status")
def survey_status(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(UserSurvey).filter(UserSurvey.user_id == current_user.id).first()
    return {"completed": existing is not None}


@router.get("/questions")
def survey_questions():
    # Simple static small questionnaire
    return {
        "questions": [
            {
                "id": "favorite_category",
                "label": "Что вам ближе?",
                "type": "select",
                "options": ["Природа", "Еда", "Искусство", "Спорт", "Музыка", "Книги", "Путешествия"],
            },
            {
                "id": "city",
                "label": "Ваш город",
                "type": "text",
            },
            {
                "id": "activity_level",
                "label": "Какой уровень активности предпочитаете?",
                "type": "select",
                "options": ["Спокойный", "Умеренный", "Активный"],
            },
            {
                "id": "budget_level",
                "label": "Какой бюджет обычно закладываете?",
                "type": "select",
                "options": ["Низкий", "Средний", "Высокий"],
            },
        ]
    }


@router.post("/")
def submit_survey(payload: SurveyPayload, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(UserSurvey).filter(UserSurvey.user_id == current_user.id).first()
    if existing:
        # Update existing
        existing.favorite_category = payload.favorite_category
        existing.activity_level = payload.activity_level
        existing.budget_level = payload.budget_level
        existing.city = payload.city
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return {"status": "updated"}

    survey = UserSurvey(
        user_id=current_user.id,
        favorite_category=payload.favorite_category,
        activity_level=payload.activity_level,
        budget_level=payload.budget_level,
        city=payload.city,
    )
    db.add(survey)
    db.commit()
    db.refresh(survey)
    return {"status": "created"}


