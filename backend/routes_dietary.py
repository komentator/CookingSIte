from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

import models, schemas
from database import get_db

router = APIRouter(prefix="/api/recipes", tags=["dietary"])


@router.get("/filter/dietary")
def filter_by_dietary(
    vegan: bool = Query(False),
    vegetarian: bool = Query(False),
    gluten_free: bool = Query(False),
    dairy_free: bool = Query(False),
    nut_free: bool = Query(False),
    min_rating: float = Query(0.0),
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Фильтр рецептов по диетическим ограничениям"""

    query = db.query(models.Recipe)

    if vegan:
        query = query.filter(models.Recipe.is_vegan == True)
    if vegetarian:
        query = query.filter(models.Recipe.is_vegetarian == True)
    if gluten_free:
        query = query.filter(models.Recipe.is_gluten_free == True)
    if dairy_free:
        query = query.filter(models.Recipe.is_dairy_free == True)
    if nut_free:
        query = query.filter(models.Recipe.is_nut_free == True)

    if min_rating > 0:
        query = query.filter(models.Recipe.rating >= min_rating)

    recipes = query.order_by(models.Recipe.rating.desc()).offset(skip).limit(limit).all()

    return {
        "filters": {
            "vegan": vegan,
            "vegetarian": vegetarian,
            "gluten_free": gluten_free,
            "dairy_free": dairy_free,
            "nut_free": nut_free,
            "min_rating": min_rating
        },
        "recipes": [
            {
                "id": r.id,
                "title": r.title,
                "cooking_time": r.cooking_time,
                "calories": r.calories,
                "rating": r.rating,
                "reviews_count": r.reviews_count,
                "dietary_tags": {
                    "vegan": r.is_vegan,
                    "vegetarian": r.is_vegetarian,
                    "gluten_free": r.is_gluten_free,
                    "dairy_free": r.is_dairy_free,
                    "nut_free": r.is_nut_free
                }
            }
            for r in recipes
        ],
        "count": len(recipes)
    }


@router.get("/vegan")
def get_vegan_recipes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Веганские рецепты"""
    recipes = (
        db.query(models.Recipe)
        .filter(models.Recipe.is_vegan == True)
        .order_by(models.Recipe.rating.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {
        "type": "vegan",
        "recipes": [
            {
                "id": r.id,
                "title": r.title,
                "cooking_time": r.cooking_time,
                "rating": r.rating
            }
            for r in recipes
        ],
        "count": len(recipes)
    }


@router.get("/vegetarian")
def get_vegetarian_recipes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Вегетарианские рецепты"""
    recipes = (
        db.query(models.Recipe)
        .filter(models.Recipe.is_vegetarian == True)
        .order_by(models.Recipe.rating.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {
        "type": "vegetarian",
        "recipes": [
            {
                "id": r.id,
                "title": r.title,
                "cooking_time": r.cooking_time,
                "rating": r.rating
            }
            for r in recipes
        ],
        "count": len(recipes)
    }


@router.get("/gluten-free")
def get_gluten_free_recipes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Рецепты без глютена"""
    recipes = (
        db.query(models.Recipe)
        .filter(models.Recipe.is_gluten_free == True)
        .order_by(models.Recipe.rating.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {
        "type": "gluten_free",
        "recipes": [
            {
                "id": r.id,
                "title": r.title,
                "cooking_time": r.cooking_time,
                "rating": r.rating
            }
            for r in recipes
        ],
        "count": len(recipes)
    }


@router.post("/{recipe_id}/mark-dietary")
def mark_dietary_flags(
    recipe_id: int,
    vegan: Optional[bool] = None,
    vegetarian: Optional[bool] = None,
    gluten_free: Optional[bool] = None,
    dairy_free: Optional[bool] = None,
    nut_free: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Отметить диетические характеристики рецепта"""
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()

    if not recipe:
        return {"error": "Recipe not found"}

    if vegan is not None:
        recipe.is_vegan = vegan
    if vegetarian is not None:
        recipe.is_vegetarian = vegetarian
    if gluten_free is not None:
        recipe.is_gluten_free = gluten_free
    if dairy_free is not None:
        recipe.is_dairy_free = dairy_free
    if nut_free is not None:
        recipe.is_nut_free = nut_free

    db.commit()

    return {
        "recipe_id": recipe_id,
        "dietary_tags": {
            "vegan": recipe.is_vegan,
            "vegetarian": recipe.is_vegetarian,
            "gluten_free": recipe.is_gluten_free,
            "dairy_free": recipe.is_dairy_free,
            "nut_free": recipe.is_nut_free
        }
    }
