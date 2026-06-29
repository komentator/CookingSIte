from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

import models, schemas
from database import get_db
from ai_service import AIService

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/parse-query")
def parse_natural_language(query: str):
    """Парсит естественный язык и извлекает ингредиенты"""
    result = AIService.parse_natural_language(query)
    return {
        "query": query,
        "parsed": result,
    }


@router.post("/synonyms")
def get_synonyms(ingredient: str):
    """Находит синонимы для ингредиента"""
    synonyms = AIService.find_ingredient_synonyms(ingredient)
    return {
        "ingredient": ingredient,
        "synonyms": synonyms,
    }


@router.post("/substitutes")
def get_substitutes(ingredient: str):
    """Предлагает замены для ингредиента"""
    substitutes = AIService.suggest_substitutes(ingredient)
    return {
        "ingredient": ingredient,
        "substitutes": substitutes,
    }


@router.post("/shopping-list")
def generate_shopping_list(ingredients: List[str]):
    """Генерирует организованный список покупок"""
    shopping_list = AIService.generate_shopping_list(ingredients)
    return {
        "items": shopping_list,
        "total": len(shopping_list),
    }


@router.get("/difficulty/{recipe_id}")
def get_recipe_difficulty(recipe_id: int, db: Session = Depends(get_db)):
    """Оценивает сложность рецепта"""
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()

    if not recipe:
        return {"error": "Recipe not found"}

    instructions_count = db.query(models.Instruction).filter(
        models.Instruction.recipe_id == recipe_id
    ).count()

    difficulty = AIService.estimate_cooking_difficulty(recipe.title, instructions_count)

    return {
        "recipe_id": recipe_id,
        "recipe_title": recipe.title,
        "difficulty": difficulty,
        "steps": instructions_count,
    }


@router.post("/smart-search")
def smart_search(query: str, db: Session = Depends(get_db)):
    """Умный поиск по естественному языку"""

    # Парсим запрос
    parsed = AIService.parse_natural_language(query)
    ingredients = parsed.get("ingredients", [])
    cooking_time_max = parsed.get("cooking_time_max")
    servings = parsed.get("servings")

    if not ingredients:
        return {
            "query": query,
            "parsed": parsed,
            "results": {
                "can_cook_now": [],
                "need_buy_1_2": [],
                "need_many": [],
            },
        }

    # Ищем рецепты
    recipes = db.query(models.Recipe).all()
    results_data = {
        "can_cook_now": [],
        "need_buy_1_2": [],
        "need_many": [],
    }

    for recipe in recipes:
        recipe_ingredients = [
            ing.ingredient.name.lower()
            for ing in recipe.ingredients
            if ing.is_required
        ]

        if not recipe_ingredients:
            continue

        # Расширяем ингредиенты синонимами
        expanded_user_ingredients = set()
        for ing in ingredients:
            expanded_user_ingredients.add(ing.lower())
            # Можно добавить поиск синонимов, но это долго
            # synonyms = AIService.find_ingredient_synonyms(ing)
            # expanded_user_ingredients.update(s.lower() for s in synonyms)

        matched = expanded_user_ingredients & set(recipe_ingredients)
        total_required = len(recipe_ingredients)
        match_percent = (len(matched) / total_required) * 100 if total_required > 0 else 0

        # Фильтруем по времени
        if cooking_time_max and recipe.cooking_time and recipe.cooking_time > cooking_time_max:
            continue

        if match_percent > 0:
            missing = list(set(recipe_ingredients) - expanded_user_ingredients)
            recipe_data = {
                "id": recipe.id,
                "title": recipe.title,
                "description": recipe.description,
                "cooking_time": recipe.cooking_time,
                "servings": recipe.servings,
                "match_percent": round(match_percent, 1),
                "missing_ingredients": missing,
            }

            if match_percent == 100:
                results_data["can_cook_now"].append(recipe_data)
            elif match_percent >= 50:
                results_data["need_buy_1_2"].append(recipe_data)
            else:
                results_data["need_many"].append(recipe_data)

    # Сортируем
    for key in results_data:
        results_data[key].sort(key=lambda x: x["match_percent"], reverse=True)

    return {
        "query": query,
        "parsed": parsed,
        "results": results_data,
    }
