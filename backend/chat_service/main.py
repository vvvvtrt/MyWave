from fastapi import FastAPI
from config import settings
from chats_router import router as chats_router

app = FastAPI(title="Chat Service")

app.include_router(chats_router, prefix="/chats", tags=["chats"])

@app.get("/health")
def health():
    return {"status": "ok"}
