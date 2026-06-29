from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from . import models
from .database import get_db
from .recommendations import RecommendationEngine

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("/stats")
def get_statistics(db: Session = Depends(get_db)):
    """Статистика по рецептам"""
    stats = RecommendationEngine.get_recipe_statistics(db)
    return stats


@router.get("/quick")
def get_quick_recipes(
    max_minutes: int = Query(30),
    limit: int = Query(5),
    db: Session = Depends(get_db)
):
    """Быстрые рецепты"""
    recipes = RecommendationEngine.get_quick_recipes(db, max_minutes, limit)
    return {
        "type": "quick",
        "max_minutes": max_minutes,
        "recipes": recipes,
        "count": len(recipes)
    }


@router.get("/trending")
def get_trending_recipes(
    limit: int = Query(5),
    db: Session = Depends(get_db)
):
    """Популярные рецепты"""
    recipes = RecommendationEngine.get_trending_recipes(db, limit)
    return {
        "type": "trending",
        "recipes": recipes,
        "count": len(recipes)
    }


@router.get("/low-calorie")
def get_low_calorie_recipes(
    limit: int = Query(5),
    db: Session = Depends(get_db)
):
    """Низкокалорийные рецепты"""
    recipes = RecommendationEngine.get_low_calorie_recipes(db, limit)
    return {
        "type": "low_calorie",
        "recipes": recipes,
        "count": len(recipes)
    }


@router.get("/protein")
def get_protein_recipes(
    limit: int = Query(5),
    db: Session = Depends(get_db)
):
    """Рецепты с белком"""
    recipes = RecommendationEngine.get_high_protein_recipes(db, limit)
    return {
        "type": "protein",
        "recipes": recipes,
        "count": len(recipes)
    }


@router.get("/for-user/{user_id}")
def get_user_recommendations(
    user_id: int,
    limit: int = Query(10),
    db: Session = Depends(get_db)
):
    """
    Персонализированные рекомендации для пользователя
    на основе его холодильника
    """
    recommendations = RecommendationEngine.get_recommendations_for_user(db, user_id, limit)
    return {
        "user_id": user_id,
        "recommendations": recommendations
    }
