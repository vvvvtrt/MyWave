from fastapi import APIRouter, HTTPException, Query
from random import choice
from ..osm_recommender import OSMPlaceParser


router = APIRouter()


_NAMES = [
    "Мгновение гармонии",
    "Точка вдохновения",
    "Сокровище воспоминаний",
    "Светлое пространство",
    "Тайна покоя",
    "Оазис мечты",
    "Вдохновляющий вид",
    "Эхо истории",
    "Пространство уединения",
    "Незабудка момента",
]

_IMAGES = [
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRn0vHkKa6sM1YZcYrbB84uNeD6620LmAkr2A&s",
    "https://www.multitour.ru/files/out/topplace-moscow/Moskovskii_universitet/Moskovskii_universitet_3.jpg",
    "https://mperspektiva.ru/upload/resize_cache/webp/iblock/771/77188ea7a4ad4a2175860a0d25ce4e28.webp",
    "https://moscowchronology.ru/sites/default/files/images/about/O_Moskve_119.jpg",
    "https://geopro-photos.storage.yandexcloud.net/h-editor/imgs/a92/a92f7a985315377fb8615dc69de04074/4kopiya_4.jpg",
    "https://cdn.7days.ru/pic/c65/941842/565812/86.jpg",
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


