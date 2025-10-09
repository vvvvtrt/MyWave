from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import hashlib
import secrets
from fastapi import HTTPException, status
from .config import settings
from .database import User, get_db
from sqlalchemy.orm import Session

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Простая схема хеширования с солью
    if not hashed_password or ':' not in hashed_password:
        return False
    salt, hash_part = hashed_password.split(':', 1)
    return hash_password(plain_password, salt) == hashed_password

def get_password_hash(password: str) -> str:
    # Генерируем соль и хешируем пароль
    salt = secrets.token_hex(16)
    return hash_password(password, salt)

def hash_password(password: str, salt: str) -> str:
    # Создаем хеш пароля с солью
    return f"{salt}:{hashlib.sha256((password + salt).encode()).hexdigest()}"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, email: str, username: str, password: str, full_name: str = None, city: str = None, favorite_cuisine: str = None, prefers: str = None, interests: str = None) -> User:
    hashed_password = get_password_hash(password)
    user = User(
        email=email,
        username=username,
        hashed_password=hashed_password,
        full_name=full_name,
        city=city,
        favorite_cuisine=favorite_cuisine,
        prefers=prefers,
        interests=interests
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def get_current_user(token: str, db: Session) -> Optional[User]:
    """Get current user from token"""
    payload = verify_token(token)
    if payload is None:
        return None
    
    email: str = payload.get("sub")
    if email is None:
        return None
    
    return get_user_by_email(db, email=email)
