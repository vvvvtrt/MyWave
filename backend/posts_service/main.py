from fastapi import FastAPI
from config import settings
from posts_router import router as posts_router
from comments_router import router as comments_router

app = FastAPI(title="Posts Service")

app.include_router(posts_router, prefix="/posts", tags=["posts"])
app.include_router(comments_router, prefix="/comments", tags=["comments"])

@app.get("/health")
def health():
    return {"status": "ok"}
