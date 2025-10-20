from fastapi import FastAPI
from config import settings
from friends_router import router as friends_router
from groups_router import router as groups_router

app = FastAPI(title="User Service")

app.include_router(friends_router, prefix="/friends", tags=["friends"])
app.include_router(groups_router, prefix="/groups", tags=["groups"])

@app.get("/health")
def health():
    return {"status": "ok"}
