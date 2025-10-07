from typing import List
from fastapi import APIRouter, HTTPException, Depends
from ..models import Group
from ..database import get_db, Chat, ChatMember, User
from sqlalchemy.orm import Session
from .auth import get_current_user


router = APIRouter()


@router.get("/")
def list_groups(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    memberships = db.query(ChatMember).filter(ChatMember.user_id == current_user.id).all()
    chat_ids = [m.chat_id for m in memberships]
    chats = db.query(Chat).filter(Chat.id.in_(chat_ids)).all()
    return [{"id": c.id, "name": c.name} for c in chats]


@router.get("/{group_id}")
def get_group(group_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    membership = db.query(ChatMember).filter(ChatMember.chat_id == group_id, ChatMember.user_id == current_user.id).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Forbidden")
    chat = db.query(Chat).filter(Chat.id == group_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Group not found")
    members = db.query(ChatMember).filter(ChatMember.chat_id == chat.id).all()
    users = []
    for m in members:
        u = db.query(User).filter(User.id == m.user_id).first()
        if u:
            users.append({"id": u.id, "username": u.username})
    return {"id": chat.id, "name": chat.name, "members": users}


@router.post("/")
def create_group(payload: dict, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    name = (payload or {}).get("name", "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="name is required")
    chat = Chat(name=name)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    db.add(ChatMember(chat_id=chat.id, user_id=current_user.id))
    db.commit()
    return {"id": chat.id, "name": chat.name}


@router.post("/{group_id}/add-member")
def add_member(group_id: int, payload: dict, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    membership = db.query(ChatMember).filter(ChatMember.chat_id == group_id, ChatMember.user_id == current_user.id).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Forbidden")
    user_id = (payload or {}).get("user_id")
    if not isinstance(user_id, int):
        raise HTTPException(status_code=400, detail="user_id is required")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    exists = db.query(ChatMember).filter(ChatMember.chat_id == group_id, ChatMember.user_id == user_id).first()
    if exists:
        return {"status": "ok"}
    db.add(ChatMember(chat_id=group_id, user_id=user_id))
    db.commit()
    return {"status": "ok"}


@router.post("/{group_id}/leave")
def leave_group(group_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    membership = db.query(ChatMember).filter(ChatMember.chat_id == group_id, ChatMember.user_id == current_user.id).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Forbidden")
    db.delete(membership)
    db.commit()
    return {"status": "ok"}
