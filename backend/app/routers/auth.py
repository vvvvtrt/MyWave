from fastapi import APIRouter
from ..models import AuthRequest, AuthResponse, User


router = APIRouter()


@router.post("/login", response_model=AuthResponse)
def login(payload: AuthRequest):
    user = User(id=1, name=(payload.name or "Гость"), email=payload.email or "guest@example.com")
    return AuthResponse(token="stub-token", user=user)


@router.post("/register", response_model=AuthResponse)
def register(payload: AuthRequest):
    user = User(id=2, name=(payload.name or "Новый пользователь"), email=payload.email or "new@example.com")
    return AuthResponse(token="stub-token", user=user)



