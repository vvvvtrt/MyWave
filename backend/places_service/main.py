from fastapi import FastAPI
from config import settings
from places_router import router as places_router
from recommendations_router import router as recommendations_router
from survey_router import router as survey_router

app = FastAPI(title="Places Service")

app.include_router(places_router, prefix="/places", tags=["places"])
app.include_router(recommendations_router, prefix="/recs", tags=["recs"])
app.include_router(survey_router, prefix="/survey", tags=["survey"])

@app.get("/health")
def health():
    return {"status": "ok"}
