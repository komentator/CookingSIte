import os
from openai import OpenAI
import json
import logging

logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class AIService:
    """Сервис для работы с OpenAI API"""

    @staticmethod
    def parse_natural_language(query: str) -> dict:
        """
        Парсит естественный язык и извлекает ингредиенты, ограничения
        Пример: "есть курица, картошка и сыр, готовить не больше 30 минут"
        """
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a helpful assistant that parses cooking-related queries.
Extract ingredients and constraints from the user query.
Return a JSON object with:
- ingredients: list of strings (normalized ingredient names)
- cooking_time_max: int or null (in minutes)
- servings: int or null
- dietary: list of strings (vegan, gluten-free, etc.) or []

Be flexible with ingredient names and synonyms.
Respond ONLY with valid JSON, no other text.""",
                    },
                    {"role": "user", "content": query},
                ],
                temperature=0.3,
                max_tokens=200,
            )

            result = response.choices[0].message.content
            return json.loads(result)
        except Exception as e:
            logger.error(f"Error parsing query: {e}")
            return {
                "ingredients": [],
                "cooking_time_max": None,
                "servings": None,
                "dietary": [],
            }

    @staticmethod
    def find_ingredient_synonyms(ingredient: str) -> list[str]:
        """Находит синонимы для ингредиента"""
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a cooking expert. Generate common synonyms and variations for ingredients.
Return a JSON array of strings with ingredient synonyms.
Include variations like plural forms, shortened names, related ingredients.
Keep the list focused and practical for cooking.
Respond ONLY with a JSON array, no other text.
Example: ["chicken", "poultry", "chicken breast", "chicken fillet", "куриное филе"]""",
                    },
                    {"role": "user", "content": f"Ingredient: {ingredient}"},
                ],
                temperature=0.3,
                max_tokens=150,
            )

            result = response.choices[0].message.content
            return json.loads(result)
        except Exception as e:
            logger.error(f"Error finding synonyms: {e}")
            return [ingredient.lower()]

    @staticmethod
    def suggest_substitutes(ingredient: str) -> dict:
        """Предлагает замены для ингредиента"""
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a cooking expert. Suggest ingredient substitutes that work in most recipes.
Return a JSON object with:
- primary: string (best substitute)
- alternatives: array of strings (other options)
- notes: string (when to use substitutes)

Consider taste, texture, and cooking properties.
Respond ONLY with valid JSON, no other text.
Example: {
  "primary": "butter",
  "alternatives": ["ghee", "coconut oil", "olive oil"],
  "notes": "Works for most baking, use more ghee for richness"
}""",
                    },
                    {"role": "user", "content": f"I don't have {ingredient}. What can I use instead?"},
                ],
                temperature=0.3,
                max_tokens=150,
            )

            result = response.choices[0].message.content
            return json.loads(result)
        except Exception as e:
            logger.error(f"Error suggesting substitutes: {e}")
            return {
                "primary": None,
                "alternatives": [],
                "notes": "Unable to suggest substitutes",
            }

    @staticmethod
    def generate_shopping_list(missing_ingredients: list[str]) -> list[dict]:
        """Генерирует список покупок с категоризацией"""
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a grocery organizer. Categorize ingredients for efficient shopping.
Return a JSON object where keys are categories and values are arrays of items.
Categories should be: vegetables, dairy, meat, pantry, spices, other
Respond ONLY with valid JSON, no other text.""",
                    },
                    {
                        "role": "user",
                        "content": f"Organize for shopping: {', '.join(missing_ingredients)}",
                    },
                ],
                temperature=0.3,
                max_tokens=200,
            )

            result = response.choices[0].message.content
            categorized = json.loads(result)

            # Конвертируем в список
            shopping_list = []
            for category, items in categorized.items():
                for item in items:
                    shopping_list.append(
                        {"name": item, "category": category, "checked": False}
                    )

            return shopping_list
        except Exception as e:
            logger.error(f"Error generating shopping list: {e}")
            return [{"name": ing, "category": "other", "checked": False} for ing in missing_ingredients]

    @staticmethod
    def estimate_cooking_difficulty(recipe_title: str, instructions_count: int) -> str:
        """Оценивает сложность приготовления"""
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """Rate the cooking difficulty of a recipe.
Return one of: easy, medium, hard
Consider recipe name and number of steps.
Respond with ONLY the difficulty level, nothing else.""",
                    },
                    {
                        "role": "user",
                        "content": f"Recipe: {recipe_title}, Steps: {instructions_count}",
                    },
                ],
                temperature=0.3,
                max_tokens=10,
            )

            return response.choices[0].message.content.strip().lower()
        except Exception as e:
            logger.error(f"Error estimating difficulty: {e}")
            return "medium"
