from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db, Chat, ChatMember, Message, User
from .auth import get_current_user


router = APIRouter()


@router.get("/")
def list_chats(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    memberships = db.query(ChatMember).filter(ChatMember.user_id == current_user.id).all()
    if not memberships:
        # Auto-create welcome chat if user has none
        chat = Chat(name="Моя Волна")
        db.add(chat)
        db.commit()
        db.refresh(chat)
        db.add(ChatMember(chat_id=chat.id, user_id=current_user.id))
        db.add(Message(chat_id=chat.id, author_id=None, text="Добро пожаловать в Мою Волну! Здесь вы можете общаться и делиться идеями."))
        db.commit()
        memberships = db.query(ChatMember).filter(ChatMember.user_id == current_user.id).all()
    chat_ids = [m.chat_id for m in memberships]
    chats = db.query(Chat).filter(Chat.id.in_(chat_ids)).all()
    result = []
    for chat in chats:
        last_msg = db.query(Message).filter(Message.chat_id == chat.id).order_by(Message.created_at.desc()).first()
        result.append({
            "id": chat.id,
            "name": chat.name,
            "last_message": {
                "text": last_msg.text if last_msg else "",
                "created_at": last_msg.created_at.isoformat() if last_msg else None
            }
        })
    return result


@router.get("/{chat_id}/messages")
def list_messages(chat_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    membership = db.query(ChatMember).filter(ChatMember.chat_id == chat_id, ChatMember.user_id == current_user.id).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Forbidden")
    messages = db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at.asc()).all()
    return [
        {
            "id": m.id,
            "text": m.text,
            "author": ("Моя Волна" if (m.author is None) else (m.author.username if m.author and m.author.username else "Пользователь")),
            "created_at": m.created_at.isoformat() if m.created_at else None
        } for m in messages
    ]


@router.post("/{chat_id}/messages")
def send_message(chat_id: int, payload: dict, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    membership = db.query(ChatMember).filter(ChatMember.chat_id == chat_id, ChatMember.user_id == current_user.id).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Forbidden")
    text = payload.get("text", "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    msg = Message(chat_id=chat_id, author_id=current_user.id, text=text)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return {
        "id": msg.id,
        "text": msg.text,
        "author": current_user.username or "Пользователь",
        "created_at": msg.created_at.isoformat() if msg.created_at else None
    }


@router.post("/")
def create_chat(payload: dict, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    name = (payload or {}).get("name") or "Путешествие"
    chat = Chat(name=name)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    db.add(ChatMember(chat_id=chat.id, user_id=current_user.id))
    db.commit()
    return {"id": chat.id, "name": chat.name}


@router.post("/dm")
def create_dm_chat(payload: dict, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    username = (payload or {}).get("username", "").strip()
    if not username:
        raise HTTPException(status_code=400, detail="username is required")
    target = db.query(User).filter(User.username == username).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    # Create simple DM chat (no duplicate checks for simplicity)
    name = f"{current_user.username or 'Вы'} & {target.username}"
    chat = Chat(name=name)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    db.add(ChatMember(chat_id=chat.id, user_id=current_user.id))
    db.add(ChatMember(chat_id=chat.id, user_id=target.id))
    db.commit()
    return {"id": chat.id, "name": chat.name}

