from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from . import models, schemas
from .database import get_db

router = APIRouter(prefix="/api/recipes", tags=["reviews"])


@router.post("/{recipe_id}/reviews", response_model=schemas.RecipeReview)
def create_review(
    recipe_id: int,
    review: schemas.RecipeReviewCreate,
    db: Session = Depends(get_db)
):
    """Добавить отзыв на рецепт"""
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    if review.rating < 1 or review.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    db_review = models.RecipeReview(
        recipe_id=recipe_id,
        user_id=review.user_id,
        rating=review.rating,
        comment=review.comment,
    )

    db.add(db_review)

    # Обновляем рейтинг рецепта
    all_reviews = db.query(models.RecipeReview).filter(
        models.RecipeReview.recipe_id == recipe_id
    ).all()

    if all_reviews:
        avg_rating = sum(r.rating for r in all_reviews) / len(all_reviews)
        recipe.rating = avg_rating
        recipe.reviews_count = len(all_reviews)

    db.commit()
    db.refresh(db_review)
    return db_review


@router.get("/{recipe_id}/reviews", response_model=List[schemas.RecipeReview])
def get_reviews(
    recipe_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Получить отзывы на рецепт"""
    reviews = (
        db.query(models.RecipeReview)
        .filter(models.RecipeReview.recipe_id == recipe_id)
        .order_by(models.RecipeReview.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return reviews


@router.get("/{recipe_id}/rating")
def get_rating(recipe_id: int, db: Session = Depends(get_db)):
    """Получить рейтинг рецепта"""
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return {
        "recipe_id": recipe_id,
        "title": recipe.title,
        "rating": recipe.rating,
        "reviews_count": recipe.reviews_count,
        "average_rating": round(recipe.rating, 1) if recipe.rating > 0 else 0
    }


@router.delete("/{recipe_id}/reviews/{review_id}")
def delete_review(
    recipe_id: int,
    review_id: int,
    db: Session = Depends(get_db)
):
    """Удалить отзыв"""
    review = db.query(models.RecipeReview).filter(
        models.RecipeReview.id == review_id,
        models.RecipeReview.recipe_id == recipe_id
    ).first()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    db.delete(review)

    # Обновляем рейтинг
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    reviews = db.query(models.RecipeReview).filter(
        models.RecipeReview.recipe_id == recipe_id
    ).all()

    if reviews:
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
        recipe.rating = avg_rating
        recipe.reviews_count = len(reviews)
    else:
        recipe.rating = 0.0
        recipe.reviews_count = 0

    db.commit()
    return {"deleted": True}
