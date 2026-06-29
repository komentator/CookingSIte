from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
import json

import models, schemas
from database import get_db

router = APIRouter(prefix="/api/user", tags=["user"])


@router.post("/{user_id}/search-history")
def add_search_history(
    user_id: int,
    ingredients: List[str],
    filters: dict = None,
    results_count: int = 0,
    db: Session = Depends(get_db)
):
    """Добавить поиск в историю"""
    query = ", ".join(ingredients)

    history = models.SearchHistory(
        user_id=user_id,
        query=query,
        ingredients=json.dumps(ingredients),
        filters=json.dumps(filters or {}),
        results_count=results_count,
    )

    db.add(history)
    db.commit()
    db.refresh(history)

    return {
        "id": history.id,
        "query": history.query,
        "created_at": history.created_at
    }


@router.get("/{user_id}/search-history")
def get_search_history(
    user_id: int,
    limit: int = Query(10),
    db: Session = Depends(get_db)
):
    """Получить историю поиска пользователя"""
    history = (
        db.query(models.SearchHistory)
        .filter(models.SearchHistory.user_id == user_id)
        .order_by(desc(models.SearchHistory.created_at))
        .limit(limit)
        .all()
    )

    return {
        "user_id": user_id,
        "searches": [
            {
                "id": h.id,
                "query": h.query,
                "ingredients": json.loads(h.ingredients) if h.ingredients else [],
                "results_count": h.results_count,
                "created_at": h.created_at
            }
            for h in history
        ],
        "total": len(history)
    }


@router.delete("/{user_id}/search-history/{history_id}")
def delete_search_history(
    user_id: int,
    history_id: int,
    db: Session = Depends(get_db)
):
    """Удалить элемент из истории"""
    history = db.query(models.SearchHistory).filter(
        models.SearchHistory.id == history_id,
        models.SearchHistory.user_id == user_id
    ).first()

    if not history:
        raise HTTPException(status_code=404, detail="History not found")

    db.delete(history)
    db.commit()

    return {"deleted": True}


@router.delete("/{user_id}/search-history")
def clear_search_history(user_id: int, db: Session = Depends(get_db)):
    """Очистить всю историю поиска"""
    db.query(models.SearchHistory).filter(
        models.SearchHistory.user_id == user_id
    ).delete()
    db.commit()

    return {"cleared": True}


@router.post("/{user_id}/favorites/{recipe_id}")
def add_to_favorites(
    user_id: int,
    recipe_id: int,
    db: Session = Depends(get_db)
):
    """Добавить рецепт в избранное"""
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Проверяем, не в избранном ли уже
    existing = db.query(models.FavoriteRecipe).filter(
        models.FavoriteRecipe.user_id == user_id,
        models.FavoriteRecipe.recipe_id == recipe_id
    ).first()

    if existing:
        return {"message": "Already in favorites"}

    favorite = models.FavoriteRecipe(user_id=user_id, recipe_id=recipe_id)
    db.add(favorite)
    db.commit()

    return {"added": True, "recipe_id": recipe_id}


@router.delete("/{user_id}/favorites/{recipe_id}")
def remove_from_favorites(
    user_id: int,
    recipe_id: int,
    db: Session = Depends(get_db)
):
    """Удалить рецепт из избранного"""
    favorite = db.query(models.FavoriteRecipe).filter(
        models.FavoriteRecipe.user_id == user_id,
        models.FavoriteRecipe.recipe_id == recipe_id
    ).first()

    if not favorite:
        raise HTTPException(status_code=404, detail="Not in favorites")

    db.delete(favorite)
    db.commit()

    return {"removed": True}


@router.get("/{user_id}/favorites")
def get_favorites(
    user_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Получить избранные рецепты"""
    favorites = (
        db.query(models.FavoriteRecipe)
        .filter(models.FavoriteRecipe.user_id == user_id)
        .order_by(desc(models.FavoriteRecipe.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {
        "user_id": user_id,
        "recipes": [
            {
                "id": f.recipe.id,
                "title": f.recipe.title,
                "cooking_time": f.recipe.cooking_time,
                "rating": f.recipe.rating,
                "added_at": f.created_at
            }
            for f in favorites
        ],
        "total": len(favorites)
    }


@router.get("/{user_id}/favorites/count")
def count_favorites(user_id: int, db: Session = Depends(get_db)):
    """Количество избранных рецептов"""
    count = db.query(models.FavoriteRecipe).filter(
        models.FavoriteRecipe.user_id == user_id
    ).count()

    return {"user_id": user_id, "count": count}
