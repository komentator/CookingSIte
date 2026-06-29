from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List

from . import models, schemas
from .database import get_db
from .search import RecipeSearch
from .cache import cache

router = APIRouter(prefix="/api", tags=["recipes"])


# Рецепты
@router.get("/recipes", response_model=List[schemas.Recipe])
def get_recipes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Получить список рецептов"""
    recipes = db.query(models.Recipe).offset(skip).limit(limit).all()
    return recipes


@router.get("/recipes/{recipe_id}", response_model=schemas.Recipe)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """Получить рецепт по ID"""
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.post("/recipes", response_model=schemas.Recipe)
def create_recipe(recipe: schemas.RecipeCreate, db: Session = Depends(get_db)):
    """Создать новый рецепт"""
    db_recipe = models.Recipe(**recipe.dict(exclude={'ingredients', 'instructions'}))
    db.add(db_recipe)
    db.flush()

    # Добавляем ингредиенты
    for ingredient in recipe.ingredients:
        db_ingredient = models.RecipeIngredient(**ingredient.dict(), recipe_id=db_recipe.id)
        db.add(db_ingredient)

    # Добавляем инструкции
    for instruction in recipe.instructions:
        db_instruction = models.Instruction(**instruction.dict(), recipe_id=db_recipe.id)
        db.add(db_instruction)

    db.commit()
    db.refresh(db_recipe)
    return db_recipe


# Поиск
@router.post("/search/by-ingredients")
def search_by_ingredients(
    search: schemas.RecipeSearch,
    db: Session = Depends(get_db),
    fuzzy: bool = Query(True, description="Использовать нечеткий поиск"),
    fuzzy_threshold: float = Query(0.7, description="Порог для нечеткого поиска (0-1)"),
    use_cache: bool = Query(True, description="Использовать кэш результатов"),
):
    """Поиск рецептов по ингредиентам с поддержкой fuzzy matching"""

    # Проверяем кэш
    if use_cache:
        cache_key = {
            "ingredients": sorted(search.ingredients),
            "cooking_time": search.cooking_time_max,
            "fuzzy": fuzzy,
            "threshold": fuzzy_threshold,
        }
        cached_result = cache.get("search_by_ingredients", cache_key)
        if cached_result is not None:
            return cached_result

    if fuzzy:
        # Используем улучшенный поиск с fuzzy matching
        results = RecipeSearch.search_recipes(
            db=db,
            ingredients=search.ingredients,
            cooking_time_max=search.cooking_time_max,
            servings=search.servings,
            fuzzy_threshold=fuzzy_threshold,
        )
    else:
        # Обычный поиск (точное совпадение)
        ingredient_names = [ing.lower() for ing in search.ingredients]
        recipes = db.query(models.Recipe).all()

        results = {
            'can_cook_now': [],
            'need_buy_1_2': [],
            'need_many': [],
            'total': 0
        }

        for recipe in recipes:
            recipe_ingredients = [
                ing.ingredient.name.lower()
                for ing in recipe.ingredients
                if ing.is_required
            ]

            if not recipe_ingredients:
                continue

            matched = set(ingredient_names) & set(recipe_ingredients)
            total_required = len(recipe_ingredients)
            match_percent = (len(matched) / total_required) * 100 if total_required > 0 else 0

            if search.cooking_time_max and recipe.cooking_time and recipe.cooking_time > search.cooking_time_max:
                continue

            if match_percent > 0:
                missing = list(set(recipe_ingredients) - set(ingredient_names))
                recipe_data = {
                    'id': recipe.id,
                    'title': recipe.title,
                    'description': recipe.description,
                    'cooking_time': recipe.cooking_time,
                    'servings': recipe.servings,
                    'calories': recipe.calories,
                    'url': recipe.url,
                    'source': recipe.source,
                    'match_percent': round(match_percent, 1),
                    'missing_ingredients': missing
                }

                if match_percent == 100:
                    results['can_cook_now'].append(recipe_data)
                elif match_percent >= 50:
                    results['need_buy_1_2'].append(recipe_data)
                else:
                    results['need_many'].append(recipe_data)

        results['total'] = len(results['can_cook_now']) + len(results['need_buy_1_2']) + len(results['need_many'])

    # Сохраняем в кэш
    if use_cache:
        cache.set("search_by_ingredients", cache_key, results)

    return results


@router.get("/cache/stats")
def cache_stats():
    """Статистика кэша"""
    return cache.stats()


@router.delete("/cache/clear")
def cache_clear():
    """Очистить кэш"""
    cache.clear()
    return {"status": "cleared"}


@router.get("/recipes/{recipe_id}/similar")
def get_similar_recipes(recipe_id: int, limit: int = Query(5), db: Session = Depends(get_db)):
    """Получить похожие рецепты по ингредиентам"""
    similar = RecipeSearch.find_similar_recipes(db, recipe_id, limit)

    if not similar:
        raise HTTPException(status_code=404, detail="Recipe not found or no similar recipes")

    return {"recipe_id": recipe_id, "similar": similar, "count": len(similar)}


@router.get("/search/by-calories")
def search_by_calories(
    min_calories: int = 0,
    max_calories: int = 10000,
    db: Session = Depends(get_db)
):
    """Поиск рецептов по калорийности"""
    recipes = db.query(models.Recipe).filter(
        models.Recipe.calories >= min_calories,
        models.Recipe.calories <= max_calories,
        models.Recipe.calories.isnot(None)
    ).all()

    return {
        "min": min_calories,
        "max": max_calories,
        "recipes": [
            {
                "id": r.id,
                "title": r.title,
                "calories": r.calories,
                "cooking_time": r.cooking_time,
                "servings": r.servings
            }
            for r in recipes
        ],
        "count": len(recipes)
    }


@router.get("/search/by-time")
def search_by_time(
    max_minutes: int,
    db: Session = Depends(get_db)
):
    """Поиск рецептов по времени приготовления"""
    recipes = db.query(models.Recipe).filter(
        models.Recipe.cooking_time <= max_minutes,
        models.Recipe.cooking_time.isnot(None)
    ).order_by(models.Recipe.cooking_time).all()

    return {
        "max_minutes": max_minutes,
        "recipes": [
            {
                "id": r.id,
                "title": r.title,
                "cooking_time": r.cooking_time,
                "servings": r.servings,
                "calories": r.calories
            }
            for r in recipes
        ],
        "count": len(recipes)
    }


# Ингредиенты
@router.get("/ingredients", response_model=List[schemas.Ingredient])
def get_ingredients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить список ингредиентов"""
    ingredients = db.query(models.Ingredient).offset(skip).limit(limit).all()
    return ingredients


@router.post("/ingredients", response_model=schemas.Ingredient)
def create_ingredient(ingredient: schemas.IngredientCreate, db: Session = Depends(get_db)):
    """Создать новый ингредиент"""
    existing = db.query(models.Ingredient).filter(
        func.lower(models.Ingredient.name) == ingredient.name.lower()
    ).first()

    if existing:
        return existing

    db_ingredient = models.Ingredient(**ingredient.dict())
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient


# Холодильник
@router.post("/fridge/{user_id}")
def add_to_fridge(
    user_id: int,
    ingredients: List[str],
    db: Session = Depends(get_db)
):
    """Добавить ингредиенты в холодильник"""
    fridge_items = []

    for ingredient_name in ingredients:
        # Ищем или создаем ингредиент
        ingredient = db.query(models.Ingredient).filter(
            func.lower(models.Ingredient.name) == ingredient_name.lower()
        ).first()

        if not ingredient:
            ingredient = models.Ingredient(name=ingredient_name)
            db.add(ingredient)
            db.flush()

        # Добавляем в холодильник
        fridge_item = models.UserFridge(
            user_id=user_id,
            ingredient_id=ingredient.id
        )
        db.add(fridge_item)
        fridge_items.append(ingredient_name)

    db.commit()
    return {'added': fridge_items, 'user_id': user_id}


@router.get("/fridge/{user_id}")
def get_fridge(user_id: int, db: Session = Depends(get_db)):
    """Получить содержимое холодильника"""
    fridge = db.query(models.UserFridge).filter(
        models.UserFridge.user_id == user_id
    ).all()

    return {
        'user_id': user_id,
        'ingredients': [
            {
                'id': item.ingredient.id,
                'name': item.ingredient.name,
                'added_at': item.added_at,
                'expiry_date': item.expiry_date
            }
            for item in fridge
        ]
    }


@router.delete("/fridge/{user_id}/{ingredient_id}")
def remove_from_fridge(user_id: int, ingredient_id: int, db: Session = Depends(get_db)):
    """Удалить ингредиент из холодильника"""
    fridge_item = db.query(models.UserFridge).filter(
        models.UserFridge.user_id == user_id,
        models.UserFridge.ingredient_id == ingredient_id
    ).first()

    if not fridge_item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(fridge_item)
    db.commit()
    return {'removed': True}
