"""
Система рекомендаций рецептов
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Recipe, RecipeIngredient, UserFridge, Ingredient
import logging

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Рекомендует рецепты на основе истории и предпочтений"""

    @staticmethod
    def get_quick_recipes(db: Session, max_minutes: int = 30, limit: int = 5) -> List[Dict]:
        """Быстрые рецепты"""
        recipes = (
            db.query(Recipe)
            .filter(Recipe.cooking_time <= max_minutes)
            .order_by(Recipe.cooking_time)
            .limit(limit)
            .all()
        )

        return [
            {
                "id": r.id,
                "title": r.title,
                "cooking_time": r.cooking_time,
                "servings": r.servings,
                "calories": r.calories,
                "type": "quick"
            }
            for r in recipes
        ]

    @staticmethod
    def get_trending_recipes(db: Session, limit: int = 5) -> List[Dict]:
        """Популярные рецепты (со многими ингредиентами - сложные)"""
        recipes = (
            db.query(Recipe)
            .join(RecipeIngredient, Recipe.id == RecipeIngredient.recipe_id)
            .group_by(Recipe.id)
            .order_by(func.count(RecipeIngredient.id).desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "id": r.id,
                "title": r.title,
                "cooking_time": r.cooking_time,
                "ingredients_count": len(r.ingredients),
                "type": "trending"
            }
            for r in recipes
        ]

    @staticmethod
    def get_low_calorie_recipes(db: Session, limit: int = 5) -> List[Dict]:
        """Низкокалорийные рецепты"""
        recipes = (
            db.query(Recipe)
            .filter(Recipe.calories.isnot(None))
            .order_by(Recipe.calories)
            .limit(limit)
            .all()
        )

        return [
            {
                "id": r.id,
                "title": r.title,
                "calories": r.calories,
                "cooking_time": r.cooking_time,
                "type": "low_calorie"
            }
            for r in recipes
        ]

    @staticmethod
    def get_high_protein_recipes(db: Session, limit: int = 5) -> List[Dict]:
        """Рецепты с белком (мясо, рыба)"""
        protein_keywords = ["курица", "рыба", "мясо", "говядина", "свинина", "яйцо"]

        recipes = []
        all_recipes = db.query(Recipe).all()

        for recipe in all_recipes:
            ingredients = db.query(RecipeIngredient).filter(
                RecipeIngredient.recipe_id == recipe.id
            ).all()

            has_protein = any(
                any(kw in ing.ingredient.name.lower() for kw in protein_keywords)
                for ing in ingredients
            )

            if has_protein:
                recipes.append(
                    {
                        "id": recipe.id,
                        "title": recipe.title,
                        "calories": recipe.calories,
                        "cooking_time": recipe.cooking_time,
                        "type": "protein"
                    }
                )

        return recipes[:limit]

    @staticmethod
    def get_recommendations_for_user(
        db: Session,
        user_id: int,
        limit: int = 10
    ) -> Dict[str, List[Dict]]:
        """
        Получить персонализированные рекомендации для пользователя
        на основе его холодильника
        """

        # Получаем содержимое холодильника
        fridge_items = db.query(UserFridge).filter(
            UserFridge.user_id == user_id
        ).all()

        if not fridge_items:
            # Если холодильник пуст, показываем популярные рецепты
            return {
                "quick": RecommendationEngine.get_quick_recipes(db, limit=5),
                "trending": RecommendationEngine.get_trending_recipes(db, limit=5),
                "low_calorie": RecommendationEngine.get_low_calorie_recipes(db, limit=5),
            }

        user_ingredients = [item.ingredient.name.lower() for item in fridge_items]

        # Находим рецепты, которые почти можно готовить
        recipes = db.query(Recipe).all()
        matches = []

        for recipe in recipes:
            recipe_ingredients = db.query(RecipeIngredient).filter(
                RecipeIngredient.recipe_id == recipe.id,
                RecipeIngredient.is_required == True
            ).all()

            if not recipe_ingredients:
                continue

            matched = sum(
                1 for ing in recipe_ingredients
                if ing.ingredient.name.lower() in user_ingredients
            )

            match_percent = (matched / len(recipe_ingredients)) * 100

            if match_percent >= 50:  # Как минимум половину можно готовить
                matches.append(
                    {
                        "id": recipe.id,
                        "title": recipe.title,
                        "cooking_time": recipe.cooking_time,
                        "calories": recipe.calories,
                        "match_percent": round(match_percent, 1),
                        "type": "personalized"
                    }
                )

        # Сортируем по проценту совпадения
        matches.sort(key=lambda x: x["match_percent"], reverse=True)

        return {
            "personalized": matches[:limit],
            "quick": RecommendationEngine.get_quick_recipes(db, limit=3),
            "protein": RecommendationEngine.get_high_protein_recipes(db, limit=3),
        }

    @staticmethod
    def get_recipe_statistics(db: Session) -> Dict:
        """Статистика по рецептам"""
        total_recipes = db.query(func.count(Recipe.id)).scalar() or 0
        avg_cooking_time = db.query(func.avg(Recipe.cooking_time)).scalar() or 0
        avg_calories = db.query(func.avg(Recipe.calories)).scalar() or 0
        total_ingredients = db.query(func.count(Ingredient.id)).scalar() or 0

        # Рецепты по времени приготовления
        quick = (
            db.query(func.count(Recipe.id))
            .filter(Recipe.cooking_time <= 30)
            .scalar() or 0
        )
        medium = (
            db.query(func.count(Recipe.id))
            .filter(Recipe.cooking_time > 30, Recipe.cooking_time <= 60)
            .scalar() or 0
        )
        long = (
            db.query(func.count(Recipe.id))
            .filter(Recipe.cooking_time > 60)
            .scalar() or 0
        )

        return {
            "total_recipes": total_recipes,
            "total_ingredients": total_ingredients,
            "avg_cooking_time_minutes": round(avg_cooking_time, 1),
            "avg_calories": round(avg_calories, 1),
            "by_cooking_time": {
                "quick_30min": quick,
                "medium_30_60min": medium,
                "long_over_60min": long
            }
        }
