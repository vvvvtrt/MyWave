from fastapi import APIRouter, HTTPException, Query
from random import choice
from ..osm_recommender import OSMPlaceParser, ImageSearcher
import requests
import urllib.parse


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

API_ENDPOINT = "https://commons.wikimedia.org/w/api.php"

def find_commons_image(query, thumb_width=640):
    """
    Ищет первый релевантный файл в Wikimedia Commons по текстовому запросу.
    Возвращает URL миниатюры (если доступна) или прямой URL на файл.
    Если ничего не найдено — возвращает placeholder с текстом запроса.
    """
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": "1",
        "prop": "imageinfo",
        "iiprop": "url|mime|extmetadata",
        "iiurlwidth": str(thumb_width),
    }
    try:
        resp = requests.get(API_ENDPOINT, params=params, timeout=10)
    except requests.RequestException as e:
        return placeholder_url(query)
    if resp.status_code != 200:
        return placeholder_url(query)
    data = resp.json()
    pages = data.get("query", {}).get("pages", {})
    if not pages:
        return placeholder_url(query)
    page = next(iter(pages.values()))
    imageinfo = page.get("imageinfo", [])
    if not imageinfo:
        return placeholder_url(query)
    info = imageinfo[0]
    thumb = info.get("thumburl") or info.get("iiurl") or info.get("url") or info.get("imageurl")
    if thumb:
        return thumb
    direct = info.get("url")
    if direct:
        return direct
    return placeholder_url(query)

def placeholder_url(query, w=640, h=400):
    text = urllib.parse.quote_plus(query)
    return f"https://placehold.co/{w}x{h}?text={text}"

def extract_russian_place_name(p):
    # Приоритет: name_ru (или name:ru в tags), затем name, потом переводить name_en (если захочется)
    name = p.get("name_ru") or p.get("name") or p.get("name_en")
    return name


@router.get("/")
def list_places(city: str = Query("Moscow")):
    # Try to return real places from local OSM DB; fallback to mock
    try:
        parser = OSMPlaceParser(db_path='places.db')
        places = parser.get_places_from_db(city)
        import random
        if places:
            result = []
            # Честная выборка: случайная уникальная восьмерка
            if len(places) > 8:
                sample_places = random.sample(places, 8)
            else:
                random.shuffle(places)
                sample_places = places
            for p in sample_places:
                name = extract_russian_place_name(p)
                image = p.get("image_url")
                if not image:
                    image = find_commons_image(f"{name} {city}")
                if not image:
                    image = placeholder_url(name)
                description = p.get("description") or "Подходит для прогулки и вдохновения"
                result.append({
                    "id": p["id"],
                    "name": name,
                    "image": image,
                    "description": description,
                })
            return result
    except Exception:
        pass
    items = []
    for i in range(8):
        name = choice(_NAMES)
        img = find_commons_image(f"{name} {city}")
        items.append({
            "id": i + 1,
            "name": name,
            "image": img,
            "description": "Подходит для прогулки и вдохновения",
        })
    return items


