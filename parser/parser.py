import requests
from bs4 import BeautifulSoup
import json
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecipeParser:
    """Парсер рецептов с различных сайтов"""

    def __init__(self):
        self.recipes = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def parse_retsepti_ru(self, url: str) -> Optional[Dict]:
        """Парсинг рецептов с рецепты.рф"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'lxml')

            recipe = {
                'source': 'retsepti.ru',
                'url': url,
                'title': None,
                'time': None,
                'servings': None,
                'ingredients': [],
                'instructions': None,
                'calories': None
            }

            # Парсим название
            title = soup.find('h1')
            if title:
                recipe['title'] = title.text.strip()

            # Парсим время и порции
            info = soup.find_all('div', class_='recipe-info')
            for inf in info:
                if 'время' in inf.text.lower():
                    recipe['time'] = inf.text.strip()

            # Парсим ингредиенты
            ingredients_section = soup.find('div', class_='ingredients')
            if ingredients_section:
                for item in ingredients_section.find_all('li'):
                    ingredient_text = item.text.strip()
                    if ingredient_text:
                        recipe['ingredients'].append({
                            'name': ingredient_text,
                            'required': True,
                            'category': 'ingredient'
                        })

            # Парсим инструкции
            instructions = soup.find('div', class_='instructions')
            if instructions:
                recipe['instructions'] = instructions.text.strip()

            return recipe if recipe['title'] else None

        except Exception as e:
            logger.error(f"Error parsing {url}: {str(e)}")
            return None

    def parse_edadeal_ru(self, url: str) -> Optional[Dict]:
        """Парсинг рецептов с edadeal.ru"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'lxml')

            recipe = {
                'source': 'edadeal.ru',
                'url': url,
                'title': None,
                'time': None,
                'servings': None,
                'ingredients': [],
                'instructions': None,
                'calories': None
            }

            # Парсим по структуре сайта
            title = soup.find('h1', class_='recipe-title')
            if title:
                recipe['title'] = title.text.strip()

            # Ингредиенты
            ingredients = soup.find_all('li', class_='ingredient')
            for item in ingredients:
                name = item.find('span', class_='ingredient-name')
                quantity = item.find('span', class_='ingredient-quantity')
                if name:
                    recipe['ingredients'].append({
                        'name': name.text.strip(),
                        'quantity': quantity.text.strip() if quantity else None,
                        'required': True,
                        'category': 'ingredient'
                    })

            return recipe if recipe['title'] else None

        except Exception as e:
            logger.error(f"Error parsing {url}: {str(e)}")
            return None

    def get_recipes_by_ingredients(self, ingredients: List[str]) -> List[Dict]:
        """Поиск рецептов по ингредиентам"""
        matching_recipes = []

        for recipe in self.recipes:
            recipe_ingredients = set(
                ing['name'].lower() for ing in recipe.get('ingredients', [])
            )
            user_ingredients = set(ing.lower() for ing in ingredients)

            # Расчет процента совпадения
            if recipe_ingredients:
                match_percent = len(
                    recipe_ingredients & user_ingredients
                ) / len(recipe_ingredients) * 100

                if match_percent > 0:
                    recipe['match_percent'] = match_percent
                    matching_recipes.append(recipe)

        return sorted(matching_recipes, key=lambda x: x['match_percent'], reverse=True)


if __name__ == '__main__':
    parser = RecipeParser()
    print("Recipe parser initialized")
