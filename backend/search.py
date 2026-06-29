"""
Улучшенная система поиска рецептов
"""

from difflib import SequenceMatcher
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from models import Recipe, Ingredient, RecipeIngredient
import logging

logger = logging.getLogger(__name__)


class RecipeSearch:
    """Поиск рецептов с нечетким матчингом"""

    # Синонимы ингредиентов (расширяемо)
    SYNONYMS = {
        "курица": ["курочка", "chicken", "цыпленок", "филе куриное"],
        "картошка": ["картофель", "potato", "картош"],
        "помидор": ["томат", "tomato", "помидорка"],
        "лук": ["луковица", "onion", "луковый"],
        "морковь": ["морковка", "carrot", "морк"],
        "сыр": ["сырок", "cheese", "сырный"],
        "молоко": ["молочко", "milk", "молочный"],
        "яйцо": ["яйца", "egg", "eggs", "яйцо"],
        "сливки": ["сливочные", "cream", "cream cheese"],
        "сметана": ["сметанка", "sour cream"],
        "чеснок": ["чесночок", "garlic", "чесночный"],
        "соль": ["соленая", "salt"],
        "перец": ["перчик", "pepper", "перец"],
    }

    @staticmethod
    def normalize_ingredient(ingredient: str) -> str:
        """Нормализует название ингредиента"""
        return ingredient.lower().strip()

    @staticmethod
    def fuzzy_match(user_ingredient: str, recipe_ingredient: str, threshold: float = 0.7) -> float:
        """
        Нечеткое совпадение ингредиентов (0-1)
        """
        user_norm = RecipeSearch.normalize_ingredient(user_ingredient)
        recipe_norm = RecipeSearch.normalize_ingredient(recipe_ingredient)

        # Точное совпадение
        if user_norm == recipe_norm:
            return 1.0

        # Проверка синонимов
        for main, synonyms in RecipeSearch.SYNONYMS.items():
            if user_norm == main or user_norm in synonyms:
                if recipe_norm == main or recipe_norm in synonyms:
                    return 0.95

        # Подстрока
        if user_norm in recipe_norm or recipe_norm in user_norm:
            return 0.85

        # Sequence matching
        ratio = SequenceMatcher(None, user_norm, recipe_norm).ratio()
        return ratio if ratio >= threshold else 0.0

    @staticmethod
    def search_recipes(
        db: Session,
        ingredients: List[str],
        cooking_time_max: Optional[int] = None,
        servings: Optional[int] = None,
        only_required: bool = True,
        fuzzy_threshold: float = 0.7,
    ) -> Dict:
        """
        Поиск рецептов с поддержкой нечеткого матчинга
        """

        # Нормализуем входные ингредиенты
        user_ingredients = [RecipeSearch.normalize_ingredient(ing) for ing in ingredients]

        # Получаем все рецепты
        query = db.query(Recipe)

        if cooking_time_max:
            query = query.filter(Recipe.cooking_time <= cooking_time_max)

        recipes = query.all()

        results = {
            "can_cook_now": [],
            "need_buy_1_2": [],
            "need_many": [],
            "total": 0,
        }

        for recipe in recipes:
            # Получаем ингредиенты рецепта
            recipe_ingredients = db.query(RecipeIngredient).filter(
                RecipeIngredient.recipe_id == recipe.id,
                RecipeIngredient.is_required == True if only_required else True,
            ).all()

            if not recipe_ingredients:
                continue

            # Считаем совпадения с fuzzy matching
            matched_count = 0
            match_scores = []

            for recipe_ing in recipe_ingredients:
                ing_name = recipe_ing.ingredient.name.lower()
                best_score = 0.0

                # Ищем лучшее совпадение
                for user_ing in user_ingredients:
                    score = RecipeSearch.fuzzy_match(
                        user_ing, ing_name, fuzzy_threshold
                    )
                    if score > best_score:
                        best_score = score

                match_scores.append(best_score)
                if best_score >= fuzzy_threshold:
                    matched_count += 1

            # Считаем процент совпадения (взвешенный)
            total_required = len(recipe_ingredients)
            if total_required == 0:
                continue

            avg_match = sum(match_scores) / len(match_scores) * 100
            exact_match_percent = (matched_count / total_required) * 100

            if exact_match_percent == 0:
                continue

            # Находим недостающие ингредиенты
            missing_ingredients = []
            for recipe_ing in recipe_ingredients:
                ing_name = recipe_ing.ingredient.name
                found = False
                for user_ing in user_ingredients:
                    if RecipeSearch.fuzzy_match(user_ing, ing_name, fuzzy_threshold) >= fuzzy_threshold:
                        found = True
                        break
                if not found:
                    missing_ingredients.append(ing_name)

            recipe_data = {
                "id": recipe.id,
                "title": recipe.title,
                "description": recipe.description,
                "cooking_time": recipe.cooking_time,
                "servings": recipe.servings,
                "calories": recipe.calories,
                "source": recipe.source,
                "url": recipe.url,
                "match_percent": round(exact_match_percent, 1),
                "avg_match_score": round(avg_match, 1),
                "matched_count": matched_count,
                "total_required": total_required,
                "missing_ingredients": missing_ingredients,
            }

            # Группируем по проценту совпадения
            if exact_match_percent == 100:
                results["can_cook_now"].append(recipe_data)
            elif exact_match_percent >= 50:
                results["need_buy_1_2"].append(recipe_data)
            else:
                results["need_many"].append(recipe_data)

        # Сортируем по проценту совпадения
        for key in ["can_cook_now", "need_buy_1_2", "need_many"]:
            results[key].sort(key=lambda x: x["match_percent"], reverse=True)

        results["total"] = (
            len(results["can_cook_now"])
            + len(results["need_buy_1_2"])
            + len(results["need_many"])
        )

        return results

    @staticmethod
    def find_similar_recipes(
        db: Session, recipe_id: int, limit: int = 5
    ) -> List[Dict]:
        """Находит похожие рецепты"""
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()

        if not recipe:
            return []

        # Получаем ингредиенты исходного рецепта
        ingredients = db.query(RecipeIngredient).filter(
            RecipeIngredient.recipe_id == recipe_id
        ).all()

        ingredient_names = [ing.ingredient.name for ing in ingredients]

        # Ищем рецепты с похожими ингредиентами
        similar = []

        all_recipes = db.query(Recipe).filter(Recipe.id != recipe_id).all()

        for other_recipe in all_recipes:
            other_ingredients = db.query(RecipeIngredient).filter(
                RecipeIngredient.recipe_id == other_recipe.id
            ).all()

            other_names = [ing.ingredient.name for ing in other_ingredients]

            # Считаем совпадения
            matches = len(set(ingredient_names) & set(other_names))

            if matches > 0:
                similarity = matches / max(len(ingredient_names), len(other_names))
                similar.append(
                    {
                        "id": other_recipe.id,
                        "title": other_recipe.title,
                        "similarity": round(similarity * 100, 1),
                        "common_ingredients": matches,
                    }
                )

        # Сортируем по схожести
        similar.sort(key=lambda x: x["similarity"], reverse=True)
        return similar[:limit]
