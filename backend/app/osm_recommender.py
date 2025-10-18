import sqlite3
import time
from typing import List, Dict, Tuple, Optional

import numpy as np
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    import overpy
except Exception:  # overpy may be missing in some envs
    overpy = None


class OSMPlaceParser:
    """Парсинг мест из OpenStreetMap через Overpass API"""

    def __init__(self, db_path: str = 'places.db'):
        self.api = overpy.Overpass() if overpy else None
        self.db_path = db_path
        self.init_database()

        self.osm_categories = {
            'архитектура': ['building=cathedral', 'building=church', 'historic=castle',
                           'historic=monument', 'building=temple', 'historic=memorial'],
            'природа': ['leisure=park', 'leisure=garden', 'natural=beach',
                       'natural=forest', 'leisure=nature_reserve', 'natural=water'],
            'рестораны': ['amenity=restaurant', 'amenity=cafe', 'amenity=bar',
                         'amenity=fast_food', 'amenity=pub'],
            'музеи': ['tourism=museum', 'tourism=gallery', 'tourism=artwork'],
            'развлечения': ['tourism=attraction', 'leisure=stadium', 'amenity=theatre',
                          'leisure=cinema', 'shop=mall']
        }

    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS places (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                osm_id TEXT UNIQUE,
                name TEXT,
                name_en TEXT,
                description TEXT,
                category TEXT,
                city TEXT,
                lat REAL,
                lon REAL,
                tags TEXT,
                image_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS place_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                place_id INTEGER,
                image_url TEXT,
                source TEXT,
                FOREIGN KEY (place_id) REFERENCES places(id)
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_city ON places(city)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON places(category)')
        conn.commit()
        conn.close()

    def parse_city(self, city: str, country: str = 'Russia', radius_km: int = 20):
        if not self.api:
            raise RuntimeError("overpy is not available")
        center = self._get_city_center(city, country)
        if not center:
            return
        lat, lon = center
        radius = radius_km * 1000
        for category, osm_tags in self.osm_categories.items():
            for tag in osm_tags:
                try:
                    places = self._fetch_places(lat, lon, radius, tag, category, city)
                    self._save_places(places)
                    time.sleep(1)
                except Exception:
                    pass
        self._remove_duplicates()

    def _get_city_center(self, city: str, country: str) -> Optional[Tuple[float, float]]:
        if self.api:
            query = f"""
            [out:json];
            area["name"="{city}"]["admin_level"~"[4-8]"]->.a;
            node(area.a)["place"~"city|town"];
            out center;
            """
            try:
                result = self.api.query(query)
                if result.nodes:
                    node = result.nodes[0]
                    return (float(node.lat), float(node.lon))
            except Exception:
                pass
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = { 'q': f"{city}, {country}", 'format': 'json', 'limit': 1 }
            headers = {'User-Agent': 'TravelRecommender/1.0'}
            response = requests.get(url, params=params, headers=headers)
            data = response.json()
            if data:
                return (float(data[0]['lat']), float(data[0]['lon']))
        except Exception:
            pass
        return None

    def _fetch_places(self, lat: float, lon: float, radius: int, osm_tag: str, category: str, city: str) -> List[Dict]:
        query = f"""
        [out:json];
        (
          node[{osm_tag}](around:{radius},{lat},{lon});
          way[{osm_tag}](around:{radius},{lat},{lon});
          relation[{osm_tag}](around:{radius},{lat},{lon});
        );
        out center tags;
        """
        if not self.api:
            return []
        result = self.api.query(query)
        places: List[Dict] = []
        for node in getattr(result, 'nodes', []):
            place = self._parse_osm_element(node, category, city)
            if place:
                places.append(place)
        for way in getattr(result, 'ways', []):
            place = self._parse_osm_element(way, category, city)
            if place:
                places.append(place)
        for rel in getattr(result, 'relations', []):
            place = self._parse_osm_element(rel, category, city)
            if place:
                places.append(place)
        return places

    def _parse_osm_element(self, element, category: str, city: str) -> Optional[Dict]:
        tags = element.tags
        name = tags.get('name', tags.get('name:ru', ''))
        if not name:
            return None
        if hasattr(element, 'lat'):
            lat, lon = float(element.lat), float(element.lon)
        elif hasattr(element, 'center_lat'):
            lat, lon = float(element.center_lat), float(element.center_lon)
        else:
            return None
        description_parts: List[str] = []
        if 'description' in tags:
            description_parts.append(tags['description'])
        if 'description:en' in tags:
            description_parts.append(tags['description:en'])
        if 'tourism' in tags:
            description_parts.append(f"Type: {tags['tourism']}")
        if 'cuisine' in tags:
            description_parts.append(f"Cuisine: {tags['cuisine']}")
        description = '. '.join(description_parts) if description_parts else name
        return {
            'osm_id': f"{element.id}",
            'name': name,
            'name_en': tags.get('name:en', ''),
            'description': description,
            'category': category,
            'city': city,
            'lat': lat,
            'lon': lon,
            'tags': str(tags)
        }

    def _save_places(self, places: List[Dict]) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        saved = 0
        for place in places:
            try:
                cursor.execute('''
                    INSERT INTO places (osm_id, name, name_en, description, category, city, lat, lon, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    place['osm_id'], place['name'], place['name_en'], place['description'],
                    place['category'], place['city'], place['lat'], place['lon'], place['tags']
                ))
                saved += 1
            except sqlite3.IntegrityError:
                pass
        conn.commit()
        conn.close()
        return saved

    def _remove_duplicates(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, lat, lon FROM places ORDER BY id')
        rows = cursor.fetchall()
        to_delete = set()
        for i, (id1, name1, lat1, lon1) in enumerate(rows):
            if id1 in to_delete:
                continue
            for id2, name2, lat2, lon2 in rows[i+1:]:
                if id2 in to_delete:
                    continue
                n1, n2 = name1.lower(), name2.lower()
                if (n1 in n2 or n2 in n1):
                    distance = self._haversine_distance(lat1, lon1, lat2, lon2)
                    if distance < 0.1:
                        to_delete.add(id2)
        if to_delete:
            cursor.execute(f'DELETE FROM places WHERE id IN ({",".join(map(str, to_delete))})')
        conn.commit()
        conn.close()

    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        return R * c

    def get_places_from_db(self, city: str, category: Optional[str] = None) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if category:
            cursor.execute('''
                SELECT id, osm_id, name, name_en, description, category, city, lat, lon, image_url
                FROM places WHERE city = ? AND category = ?
            ''', (city, category))
        else:
            cursor.execute('''
                SELECT id, osm_id, name, name_en, description, category, city, lat, lon, image_url
                FROM places WHERE city = ?
            ''', (city,))
        places: List[Dict] = []
        for row in cursor.fetchall():
            places.append({
                'id': row[0], 'osm_id': row[1], 'name': row[2], 'name_en': row[3],
                'description': row[4], 'category': row[5], 'city': row[6],
                'lat': row[7], 'lon': row[8], 'image_url': row[9]
            })
        conn.close()
        return places


class ImageSearcher:
    def __init__(self, db_path: str = 'places.db'):
        self.db_path = db_path
        self.unsplash_access_key = None

    def search_wikimedia_image(self, place_name: str, city: str) -> Optional[str]:
        try:
            search_query = f"{place_name} {city}"
            url = "https://commons.wikimedia.org/w/api.php"
            params = { 'action': 'query', 'format': 'json', 'list': 'search', 'srsearch': search_query, 'srnamespace': 6, 'srlimit': 1 }
            response = requests.get(url, params=params)
            data = response.json()
            if data.get('query', {}).get('search'):
                file_title = data['query']['search'][0]['title']
                params2 = { 'action': 'query', 'format': 'json', 'titles': file_title, 'prop': 'imageinfo', 'iiprop': 'url' }
                response2 = requests.get(url, params=params2)
                data2 = response2.json()
                pages = data2.get('query', {}).get('pages', {})
                for page in pages.values():
                    if 'imageinfo' in page:
                        return page['imageinfo'][0]['url']
        except Exception:
            pass
        return None

    def search_unsplash_image(self, place_name: str) -> Optional[str]:
        if not self.unsplash_access_key:
            return None
        try:
            url = "https://api.unsplash.com/search/photos"
            headers = {'Authorization': f'Client-ID {self.unsplash_access_key}'}
            params = { 'query': place_name, 'per_page': 1 }
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            if data.get('results'):
                return data['results'][0]['urls']['regular']
        except Exception:
            pass
        return None

    def update_place_images(self, place_id: int, place_name: str, city: str):
        image_url = self.search_wikimedia_image(place_name, city)
        if not image_url:
            image_url = self.search_unsplash_image(place_name)
        if image_url:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('UPDATE places SET image_url = ? WHERE id = ?', (image_url, place_id))
            conn.commit()
            conn.close()
            return image_url
        return None

    def update_all_images(self, city: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, city FROM places WHERE city = ? AND image_url IS NULL', (city,))
        rows = cursor.fetchall()
        conn.close()
        for place_id, name, city in rows:
            self.update_place_images(place_id, name, city)
            time.sleep(1)


class TravelRecommender:
    def __init__(self, db_path: str = 'places.db'):
        self.db_path = db_path
        self.parser = OSMPlaceParser(db_path)
        self.image_searcher = ImageSearcher(db_path)
        self.vectorizer = TfidfVectorizer(max_features=100, ngram_range=(1, 2))
        self.places_cache: Dict[str, List[Dict]] = {}

    def load_city_places(self, city: str) -> List[Dict]:
        if city not in self.places_cache:
            self.places_cache[city] = self.parser.get_places_from_db(city)
        return self.places_cache[city]

    def get_recommendations(self, user_liked_ids: List[int], user_preferences: Dict[str, float], city: str, n_recommendations: int = 10) -> List[Tuple[Dict, float]]:
        places = self.load_city_places(city)
        if not places:
            return []
        texts = [f"{p['name']} {p['description']}" for p in places]
        place_vectors = self.vectorizer.fit_transform(texts)
        liked_indices = [i for i, p in enumerate(places) if p['id'] in user_liked_ids]
        if not liked_indices:
            scores = []
            for place in places:
                score = user_preferences.get(place['category'], 0.5)
                scores.append((place, score))
            scores.sort(key=lambda x: x[1], reverse=True)
            return scores[:n_recommendations]
        liked_vectors = place_vectors[liked_indices]
        avg_liked_vector = liked_vectors.mean(axis=0)
        recommendations: List[Tuple[Dict, float]] = []
        for i, place in enumerate(places):
            if i in liked_indices:
                continue
            similarity = cosine_similarity(avg_liked_vector, place_vectors[i])[0][0]
            category_score = user_preferences.get(place['category'], 0.5)
            final_score = 0.6 * similarity + 0.4 * category_score
            recommendations.append((place, final_score))
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:n_recommendations]








