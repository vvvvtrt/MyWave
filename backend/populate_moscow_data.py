#!/usr/bin/env python3
"""
Скрипт для загрузки данных о Москве и создания фейковых аккаунтов с постами
"""

import sqlite3
import requests
import time
import random
from datetime import datetime, timedelta
import hashlib
import secrets
from typing import List, Dict

# Импортируем классы из нашего проекта
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.osm_recommender import OSMPlaceParser, ImageSearcher, TravelRecommender
from app.database import User, Post, Comment, Photo, Like, get_password_hash
from app.database import SessionLocal, engine
from sqlalchemy.orm import sessionmaker

# Настройки
DB_PATH = 'places.db'
MAIN_DB_URL = 'sqlite:///./app.db'

# Фейковые пользователи
FAKE_USERS = [
    {"username": "moscow_explorer", "email": "explorer@moscow.ru", "full_name": "Анна Москвина"},
    {"username": "red_square_fan", "email": "redsquare@mail.ru", "full_name": "Дмитрий Красноплощадский"},
    {"username": "kremlin_walker", "email": "kremlin@yandex.ru", "full_name": "Екатерина Кремлевская"},
    {"username": "metro_rider", "email": "metro@metro.ru", "full_name": "Сергей Метроходов"},
    {"username": "park_lover", "email": "parks@green.ru", "full_name": "Мария Парковая"},
    {"username": "museum_guide", "email": "museum@culture.ru", "full_name": "Иван Музейный"},
    {"username": "food_hunter", "email": "food@taste.ru", "full_name": "Ольга Вкусная"},
    {"username": "night_crawler", "email": "night@city.ru", "full_name": "Алексей Ночной"},
]

# Фейковые комментарии
FAKE_COMMENTS = [
    "Отличное место! Обязательно вернусь сюда.",
    "Красивая архитектура и интересная история.",
    "Прекрасные фотографии получаются здесь.",
    "Очень атмосферно, рекомендую всем.",
    "Была здесь в прошлом месяце, впечатления незабываемые.",
    "Отличное место для прогулки с семьей.",
    "Красивые виды и уютная атмосфера.",
    "Обязательно нужно посетить каждому туристу.",
    "Очень понравилось, особенно вечером.",
    "Прекрасное место для романтической прогулки.",
]

def create_fake_users():
    """Создание фейковых пользователей"""
    print("Создаю фейковых пользователей...")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    created_users = []
    
    for user_data in FAKE_USERS:
        # Проверяем, существует ли пользователь
        existing_user = db.query(User).filter(
            (User.email == user_data["email"]) | 
            (User.username == user_data["username"])
        ).first()
        
        if existing_user:
            print(f"Пользователь {user_data['username']} уже существует")
            created_users.append(existing_user)
            continue
        
        # Создаем нового пользователя
        hashed_password = get_password_hash("password123")
        user = User(
            email=user_data["email"],
            username=user_data["username"],
            hashed_password=hashed_password,
            full_name=user_data["full_name"],
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        created_users.append(user)
        print(f"Создан пользователь: {user_data['username']}")
    
    db.close()
    return created_users

def populate_moscow_places():
    """Загрузка мест Москвы из OSM"""
    print("Загружаю места Москвы из OSM...")
    
    parser = OSMPlaceParser(db_path=DB_PATH)
    
    try:
        # Парсим Москву с большим радиусом
        parser.parse_city('Moscow', 'Russia', radius_km=25)
        print("Парсинг Москвы завершен")
    except Exception as e:
        print(f"Ошибка при парсинге Москвы: {e}")
        return False
    
    # Обновляем изображения
    print("Обновляю изображения для мест...")
    image_searcher = ImageSearcher(db_path=DB_PATH)
    try:
        image_searcher.update_all_images('Moscow')
        print("Обновление изображений завершено")
    except Exception as e:
        print(f"Ошибка при обновлении изображений: {e}")
    
    return True

def create_fake_posts(users: List[User]):
    """Создание фейковых постов на основе реальных мест"""
    print("Создаю фейковые посты...")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    # Получаем места из OSM базы
    parser = OSMPlaceParser(db_path=DB_PATH)
    places = parser.get_places_from_db('Moscow')
    
    if not places:
        print("Нет мест в базе данных, создаю посты с заглушками")
        places = [
            {
                "id": i,
                "name": f"Место {i}",
                "description": f"Описание места {i}",
                "image_url": f"https://images.unsplash.com/photo-{1500000000000 + i}?q=80&w=1200&auto=format&fit=crop",
                "lat": 55.7558 + random.uniform(-0.1, 0.1),
                "lon": 37.6176 + random.uniform(-0.1, 0.1)
            }
            for i in range(1, 21)
        ]
    
    created_posts = []
    
    for i, place in enumerate(places[:50]):  # Создаем до 50 постов
        # Выбираем случайного пользователя
        author = random.choice(users)
        
        # Создаем пост
        post = Post(
            title=place["name"],
            description=place.get("description", f"Интересное место в Москве: {place['name']}"),
            author_id=author.id,
            likes_count=random.randint(0, 100),
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            updated_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
        )
        
        db.add(post)
        db.commit()
        db.refresh(post)
        
        # Добавляем фото, если есть URL
        if place.get("image_url"):
            photo = Photo(
                url=place["image_url"],
                post_id=post.id,
                created_at=datetime.utcnow()
            )
            db.add(photo)
            db.commit()
        
        # Добавляем случайные лайки
        for _ in range(random.randint(0, min(20, post.likes_count))):
            liker = random.choice(users)
            like = Like(
                user_id=liker.id,
                post_id=post.id,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            db.add(like)
        
        # Добавляем случайные комментарии
        for _ in range(random.randint(0, 5)):
            commenter = random.choice(users)
            comment = Comment(
                text=random.choice(FAKE_COMMENTS),
                post_id=post.id,
                author_id=commenter.id,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            db.add(comment)
        
        created_posts.append(post)
        print(f"Создан пост: {post.title}")
    
    db.commit()
    db.close()
    print(f"Создано {len(created_posts)} постов")
    return created_posts

def main():
    """Основная функция"""
    print("=== Загрузка данных о Москве ===")
    
    # 1. Загружаем места Москвы
    if not populate_moscow_places():
        print("Не удалось загрузить места Москвы")
        return
    
    # 2. Создаем фейковых пользователей
    users = create_fake_users()
    
    # 3. Создаем фейковые посты
    posts = create_fake_posts(users)
    
    print("=== Загрузка завершена ===")
    print(f"Создано пользователей: {len(users)}")
    print(f"Создано постов: {len(posts)}")
    
    # Показываем статистику
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    total_users = db.query(User).count()
    total_posts = db.query(Post).count()
    total_photos = db.query(Photo).count()
    total_comments = db.query(Comment).count()
    total_likes = db.query(Like).count()
    
    print(f"\n=== Статистика базы данных ===")
    print(f"Всего пользователей: {total_users}")
    print(f"Всего постов: {total_posts}")
    print(f"Всего фотографий: {total_photos}")
    print(f"Всего комментариев: {total_comments}")
    print(f"Всего лайков: {total_likes}")
    
    db.close()

if __name__ == "__main__":
    main()




