from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, Friendship, User
from auth import get_current_user


router = APIRouter()


@router.get("/")
def list_friends(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Symmetric friendship: return all users who are either user_id->friend_id or friend_id->user_id
    outgoing = db.query(Friendship).filter(Friendship.user_id == current_user.id).all()
    incoming = db.query(Friendship).filter(Friendship.friend_id == current_user.id).all()
    friend_ids = {f.friend_id for f in outgoing} | {f.user_id for f in incoming}
    users = db.query(User).filter(User.id.in_(list(friend_ids))).all()
    return [{"id": u.id, "username": u.username} for u in users]


@router.post("/")
def add_friend(payload: dict, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    friend_id = (payload or {}).get("user_id")
    if not isinstance(friend_id, int):
        raise HTTPException(status_code=400, detail="user_id is required")
    if friend_id == current_user.id:
        raise HTTPException(status_code=400, detail="cannot add self")
    user = db.query(User).filter(User.id == friend_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    exists = db.query(Friendship).filter(Friendship.user_id == current_user.id, Friendship.friend_id == friend_id).first()
    if exists:
        return {"status": "ok"}
    f = Friendship(user_id=current_user.id, friend_id=friend_id)
    db.add(f)
    db.commit()
    return {"status": "ok"}



