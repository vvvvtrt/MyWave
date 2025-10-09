from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from .config import settings
from .routers import auth, posts, comments, groups, search, chats, places, friends
from .database import engine
from sqlalchemy import text, inspect

app = FastAPI(title="MyWave API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple migration for new user columns (works with Postgres and SQLite)
try:
    inspector = inspect(engine)
    existing_cols = {col['name'] for col in inspector.get_columns('users')}
    to_add = [
        ("city", "VARCHAR"),
        ("favorite_cuisine", "VARCHAR"),
        ("prefers", "VARCHAR"),
        ("interests", "TEXT"),
    ]
    if any(col not in existing_cols for col, _ in to_add):
        with engine.begin() as conn:
            for col, coltype in to_add:
                if col not in existing_cols:
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {col} {coltype}"))
except Exception:
    # Best-effort; if it fails, the error will surface on insert
    pass

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(posts.router, prefix="/posts", tags=["posts"])
app.include_router(comments.router, prefix="/comments", tags=["comments"])
app.include_router(groups.router, prefix="/groups", tags=["groups"])
app.include_router(search.router, prefix="/search", tags=["search"])
app.include_router(chats.router, prefix="/chats", tags=["chats"])
app.include_router(places.router, prefix="/places", tags=["places"])
app.include_router(friends.router, prefix="/friends", tags=["friends"])



