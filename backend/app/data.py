from typing import List
from .models import Post, Comment, RoutePoint, User, Group


def sample_route() -> List[RoutePoint]:
    return [
        RoutePoint(lat=59.9386, lng=30.3141),
        RoutePoint(lat=60.0, lng=30.2),
        RoutePoint(lat=60.05, lng=30.1),
    ]


def mock_posts() -> List[Post]:
    return [
        Post(
            id=1,
            title="Северная бухта",
            author="Анна",
            description="Красивый маршрут вдоль побережья",
            likes=42,
            liked=False,
            comments=[
                Comment(id=11, post_id=1, text="Великолепно!", author="Иван"),
            ],
            route=sample_route(),
            photos=[
                "https://images.unsplash.com/photo-1507525428034-b723cf961d3e",
                "https://images.unsplash.com/photo-1506744038136-46273834b3fb",
            ],
        ),
        Post(
            id=2,
            title="Горная тропа",
            author="Илья",
            description="Короткий поход в горы",
            likes=13,
            liked=False,
            comments=[],
            route=sample_route(),
            photos=[
                "https://images.unsplash.com/photo-1501785888041-af3ef285b470",
            ],
        ),
    ]


POSTS: List[Post] = mock_posts()
USERS: List[User] = [User(id=1, name="Гость", email="guest@example.com")]
GROUPS: List[Group] = [Group(id=1, name="Друзья", members=USERS)]



