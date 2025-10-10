from fastapi import APIRouter, HTTPException, Query
from random import choice
from ..osm_recommender import OSMPlaceParser


router = APIRouter()


_NAMES = [
    "Набережная у моста",
    "Уютная кофейня",
    "Старый дворик",
    "Галерея современного искусства",
    "Смотровая площадка",
    "Парк на холме",
]

_IMAGES = [
    "https://images.unsplash.com/photo-1505761671935-60b3a7427bad?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1504754524776-8f4f37790ca0?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1501785888041-af3ef285b470?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1518779578993-ec3579fee39f?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1469474968028-56623f02e42e?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1491553895911-0055eca6402d?q=80&w=1200&auto=format&fit=crop",
]


@router.get("/")
def list_places(city: str = Query("Saint Petersburg")):
    # Try to return real places from local OSM DB; fallback to mock
    try:
        parser = OSMPlaceParser(db_path='places.db')
        places = parser.get_places_from_db(city)
        if places:
            return [
                {
                    "id": p["id"],
                    "name": p["name"],
                    "image": p["image_url"] or choice(_IMAGES),
                    "description": p["description"] or "Подходит для прогулки и вдохновения",
                }
                for p in places[:32]
            ]
    except Exception:
        pass
    items = []
    for i in range(8):
        name = choice(_NAMES)
        img = choice(_IMAGES)
        items.append({
            "id": i + 1,
            "name": name,
            "image": img,
            "description": "Подходит для прогулки и вдохновения",
        })
    return items


