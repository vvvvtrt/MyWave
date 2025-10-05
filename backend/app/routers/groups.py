from typing import List
from fastapi import APIRouter, HTTPException, Depends
from ..models import Group
from ..database import get_db
from sqlalchemy.orm import Session


router = APIRouter()


@router.get("/")
def list_groups(db: Session = Depends(get_db)):
    # Пока что возвращаем пустой список, так как группы не реализованы в базе данных
    return []


@router.get("/{group_id}")
def get_group(group_id: int, db: Session = Depends(get_db)):
    raise HTTPException(status_code=404, detail="Group not found")


@router.post("/")
def create_group(name: str, db: Session = Depends(get_db)):
    raise HTTPException(status_code=501, detail="Groups not implemented yet")


@router.post("/{group_id}/join")
def join_group(group_id: int, db: Session = Depends(get_db)):
    raise HTTPException(status_code=501, detail="Groups not implemented yet")


@router.post("/{group_id}/leave")
def leave_group(group_id: int, db: Session = Depends(get_db)):
    raise HTTPException(status_code=501, detail="Groups not implemented yet")
