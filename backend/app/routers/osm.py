from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from ..osm_recommender import OSMPlaceParser, ImageSearcher, TravelRecommender

router = APIRouter()

@router.get("/categories", response_model=List[str])
def get_categories():
    parser = OSMPlaceParser()
    return list(parser.osm_categories.keys())

@router.post("/parse_city")
def parse_city(city: str = Query(...), country: str = Query("Russia"), radius_km: int = Query(20)):
    parser = OSMPlaceParser()
    try:
        parser.parse_city(city, country, radius_km)
        return {"status": "ok", "message": f"City {city} parsed and saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/places")
def get_places(city: str = Query(...), category: Optional[str] = Query(None)):
    parser = OSMPlaceParser()
    try:
        places = parser.get_places_from_db(city, category)
        return places
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/image")
def get_image(place_name: str = Query(...), city: str = Query("Moscow")):
    searcher = ImageSearcher()
    url = searcher.search_wikimedia_image(place_name, city)
    if url:
        return {"image_url": url}
    url = searcher.search_unsplash_image(place_name)
    if url:
        return {"image_url": url}
    raise HTTPException(status_code=404, detail="Image not found")

@router.get("/recommendations")
def get_travel_recommendations(city: str = Query(...), n: int = Query(10)):
    recommender = TravelRecommender()
    try:
        recs = recommender.get_recommendations(user_liked_ids=[], user_preferences={}, city=city, n_recommendations=n)
        return [{"place": obj[0], "score": obj[1]} for obj in recs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
