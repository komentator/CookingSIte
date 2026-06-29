from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class IngredientBase(BaseModel):
    name: str
    category: Optional[str] = None


class IngredientCreate(IngredientBase):
    pass


class Ingredient(IngredientBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class RecipeIngredientBase(BaseModel):
    ingredient_id: int
    quantity: Optional[str] = None
    unit: Optional[str] = None
    is_required: bool = True


class RecipeIngredientCreate(RecipeIngredientBase):
    pass


class RecipeIngredient(RecipeIngredientBase):
    id: int
    recipe_id: int
    ingredient: Ingredient

    class Config:
        from_attributes = True


class InstructionBase(BaseModel):
    step_number: int
    description: str


class InstructionCreate(InstructionBase):
    pass


class Instruction(InstructionBase):
    id: int
    recipe_id: int

    class Config:
        from_attributes = True


class RecipeBase(BaseModel):
    title: str
    description: Optional[str] = None
    source: Optional[str] = None
    url: Optional[str] = None
    cooking_time: Optional[int] = None
    servings: Optional[int] = None
    calories: Optional[int] = None


class RecipeCreate(RecipeBase):
    ingredients: List[RecipeIngredientCreate] = []
    instructions: List[InstructionCreate] = []


class Recipe(RecipeBase):
    id: int
    created_at: datetime
    updated_at: datetime
    ingredients: List[RecipeIngredient]
    instructions: List[Instruction]

    class Config:
        from_attributes = True


class RecipeSearch(BaseModel):
    ingredients: List[str]
    cooking_time_max: Optional[int] = None
    servings: Optional[int] = None


class UserFridgeBase(BaseModel):
    ingredient_id: int
    quantity: Optional[str] = None
    expiry_date: Optional[str] = None


class UserFridgeCreate(UserFridgeBase):
    pass


class UserFridge(UserFridgeBase):
    id: int
    user_id: int
    added_at: datetime

    class Config:
        from_attributes = True
