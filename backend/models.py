from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    source = Column(String(100))
    url = Column(Text)
    cooking_time = Column(Integer)  # в минутах
    servings = Column(Integer)
    calories = Column(Integer)
    is_vegan = Column(Boolean, default=False)
    is_vegetarian = Column(Boolean, default=False)
    is_gluten_free = Column(Boolean, default=False)
    is_dairy_free = Column(Boolean, default=False)
    is_nut_free = Column(Boolean, default=False)
    rating = Column(Float, default=0.0)  # средняя оценка (0-5)
    reviews_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    ingredients = relationship("RecipeIngredient", back_populates="recipe")
    instructions = relationship("Instruction", back_populates="recipe")
    reviews = relationship("RecipeReview", back_populates="recipe")


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    category = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    recipes = relationship("RecipeIngredient", back_populates="ingredient")
    synonyms = relationship("IngredientSynonym", back_populates="ingredient")
    user_fridge = relationship("UserFridge", back_populates="ingredient")


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False)
    quantity = Column(String(100))
    unit = Column(String(50))
    is_required = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    recipe = relationship("Recipe", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="recipes")


class Instruction(Base):
    __tablename__ = "instructions"

    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    step_number = Column(Integer)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    recipe = relationship("Recipe", back_populates="instructions")


class UserFridge(Base):
    __tablename__ = "user_fridge"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False)
    quantity = Column(String(100))
    expiry_date = Column(Date)
    added_at = Column(DateTime, default=datetime.utcnow)

    ingredient = relationship("Ingredient", back_populates="user_fridge")


class IngredientSynonym(Base):
    __tablename__ = "ingredient_synonyms"

    id = Column(Integer, primary_key=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False)
    synonym = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    ingredient = relationship("Ingredient", back_populates="synonyms")


class RecipeReview(Base):
    __tablename__ = "recipe_reviews"

    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    user_id = Column(Integer, nullable=False)
    rating = Column(Float, nullable=False)  # 1-5
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    recipe = relationship("Recipe", back_populates="reviews")
