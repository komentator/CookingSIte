"""
Интеграционные тесты для CookingSite API
Требует: pytest, httpx
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from database import SessionLocal
from models import Base, Recipe, Ingredient, RecipeIngredient, Instruction
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")

client = TestClient(app)


@pytest.fixture
def db():
    """Fixture для БД"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_health():
    """Тест health endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_recipe(db):
    """Тест создания рецепта"""
    recipe_data = {
        "title": "Test Recipe",
        "description": "A test recipe",
        "cooking_time": 30,
        "servings": 4,
        "ingredients": [
            {
                "ingredient_id": 1,
                "quantity": "500",
                "unit": "g",
                "is_required": True
            }
        ],
        "instructions": [
            {
                "step_number": 1,
                "description": "Do something"
            }
        ]
    }

    response = client.post("/api/recipes", json=recipe_data)
    assert response.status_code == 200
    assert response.json()["title"] == "Test Recipe"


def test_get_recipes():
    """Тест получения списка рецептов"""
    response = client.get("/api/recipes")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_search_by_ingredients():
    """Тест поиска по ингредиентам"""
    search_data = {
        "ingredients": ["курица", "картошка"],
        "cooking_time_max": None,
        "servings": None
    }

    response = client.post("/api/search/by-ingredients", json=search_data)
    assert response.status_code == 200
    data = response.json()
    assert "can_cook_now" in data
    assert "need_buy_1_2" in data
    assert "need_many" in data


def test_fridge_operations():
    """Тест операций с холодильником"""
    user_id = 1
    ingredients = ["курица", "картошка", "лук"]

    # Добавляем ингредиенты
    response = client.post(
        f"/api/fridge/{user_id}",
        json=ingredients
    )
    assert response.status_code == 200
    assert len(response.json()["added"]) == 3

    # Получаем холодильник
    response = client.get(f"/api/fridge/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["ingredients"]) == 3


def test_ingredients():
    """Тест работы с ингредиентами"""
    # Создаем ингредиент
    response = client.post(
        "/api/ingredients",
        json={"name": "помидор", "category": "овощи"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "помидор"

    # Получаем ингредиенты
    response = client.get("/api/ingredients")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_parse_query():
    """Тест парсинга естественного языка"""
    query = "есть курица и картошка, готовить 30 минут"

    response = client.post(
        "/api/ai/parse-query",
        params={"query": query}
    )
    assert response.status_code == 200
    data = response.json()
    assert "parsed" in data
    assert "ingredients" in data["parsed"]


def test_get_synonyms():
    """Тест получения синонимов"""
    response = client.post(
        "/api/ai/synonyms",
        params={"ingredient": "курица"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "synonyms" in data
    assert isinstance(data["synonyms"], list)


def test_get_substitutes():
    """Тест получения замен"""
    response = client.post(
        "/api/ai/substitutes",
        params={"ingredient": "сливки"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "substitutes" in data


def test_shopping_list():
    """Тест генерации списка покупок"""
    ingredients = ["курица", "картошка", "морковь", "сыр"]

    response = client.post(
        "/api/ai/shopping-list",
        json=ingredients
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) > 0


def test_api_docs():
    """Тест доступности документации"""
    response = client.get("/docs")
    assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
