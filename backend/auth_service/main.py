from fastapi import FastAPI
from config import settings
from auth_router import router as auth_router

app = FastAPI(title="Auth Service")

app.include_router(auth_router, prefix="/auth", tags=["auth"])

@app.get("/health")
def health():
    return {"status": "ok"}
