import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecipeParser:
    """Парсер рецептов с различных источников"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def parse_recipe(self, url: str, source: str = "unknown") -> Optional[Dict]:
        """Парсить рецепт по URL"""
        try:
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')

            recipe = {
                'title': None,
                'description': None,
                'source': source,
                'url': url,
                'cooking_time': None,
                'servings': None,
                'calories': None,
                'ingredients': [],
                'instructions': []
            }

            # Пытаемся найти структурированные данные (JSON-LD)
            structured_data = soup.find('script', {'type': 'application/ld+json'})
            if structured_data:
                try:
                    data = json.loads(structured_data.string)
                    return self._parse_structured_data(data, url, source)
                except:
                    pass

            # Fallback на общий парсинг
            return self._parse_generic(soup, recipe)

        except Exception as e:
            logger.error(f"Error parsing {url}: {str(e)}")
            return None

    def _parse_structured_data(self, data: dict, url: str, source: str) -> Optional[Dict]:
        """Парсинг структурированных данных (JSON-LD)"""
        if data.get('@type') != 'Recipe':
            return None

        recipe = {
            'title': data.get('name'),
            'description': data.get('description'),
            'source': source,
            'url': url,
            'cooking_time': self._parse_duration(data.get('cookTime')),
            'servings': data.get('recipeYield', {}).get('value') if isinstance(data.get('recipeYield'), dict) else data.get('recipeYield'),
            'calories': data.get('nutrition', {}).get('calories') if isinstance(data.get('nutrition'), dict) else None,
            'ingredients': [],
            'instructions': []
        }

        # Ингредиенты
        for ingredient_text in data.get('recipeIngredient', []):
            recipe['ingredients'].append({
                'name': ingredient_text.strip(),
                'quantity': None,
                'unit': None,
                'is_required': True
            })

        # Инструкции
        instructions = data.get('recipeInstructions', [])
        if isinstance(instructions, list):
            for idx, instruction in enumerate(instructions):
                if isinstance(instruction, dict):
                    text = instruction.get('text', '')
                else:
                    text = str(instruction)
                recipe['instructions'].append({
                    'step_number': idx + 1,
                    'description': text.strip()
                })

        return recipe if recipe['title'] else None

    def _parse_generic(self, soup: BeautifulSoup, recipe: Dict) -> Dict:
        """Общий парсинг когда нет структурированных данных"""
        # Поиск названия
        h1 = soup.find('h1')
        if h1:
            recipe['title'] = h1.get_text(strip=True)

        # Поиск описания
        description = soup.find('meta', {'name': 'description'})
        if description:
            recipe['description'] = description.get('content', '')

        # Поиск ингредиентов (различные селекторы)
        ingredients_selectors = [
            {'class': 'ingredients'},
            {'class': 'recipe-ingredients'},
            {'id': 'ingredients'},
        ]

        for selector in ingredients_selectors:
            ingredients_section = soup.find('div', selector)
            if ingredients_section:
                for item in ingredients_section.find_all(['li', 'div']):
                    text = item.get_text(strip=True)
                    if text:
                        recipe['ingredients'].append({
                            'name': text,
                            'quantity': None,
                            'unit': None,
                            'is_required': True
                        })
                break

        # Поиск инструкций
        instructions_selectors = [
            {'class': 'instructions'},
            {'class': 'recipe-instructions'},
            {'id': 'instructions'},
        ]

        step_num = 1
        for selector in instructions_selectors:
            instructions_section = soup.find('div', selector)
            if instructions_section:
                for item in instructions_section.find_all(['li', 'div', 'p']):
                    text = item.get_text(strip=True)
                    if text and len(text) > 20:
                        recipe['instructions'].append({
                            'step_number': step_num,
                            'description': text
                        })
                        step_num += 1
                break

        return recipe

    def _parse_duration(self, duration_str: Optional[str]) -> Optional[int]:
        """Парсить ISO 8601 duration в минуты"""
        if not duration_str:
            return None

        # PT1H30M -> 90 минут
        import re
        match = re.match(r'PT(\d+H)?(\d+M)?(\d+S)?', duration_str)
        if not match:
            return None

        hours = int(match.group(1).rstrip('H') or 0)
        minutes = int(match.group(2).rstrip('M') or 0)
        seconds = int(match.group(3).rstrip('S') or 0)

        total_minutes = hours * 60 + minutes + (seconds // 60)
        return total_minutes if total_minutes > 0 else None

    def search_recipes_by_ingredients(self,
                                     recipes: List[Dict],
                                     user_ingredients: List[str],
                                     match_threshold: float = 0.5) -> List[Dict]:
        """Поиск рецептов по ингредиентам"""

        user_ingredients_set = {ing.lower() for ing in user_ingredients}
        results = []

        for recipe in recipes:
            recipe_ingredients_set = {
                ing['name'].lower() for ing in recipe.get('ingredients', [])
                if ing.get('is_required', True)
            }

            if not recipe_ingredients_set:
                continue

            matched = user_ingredients_set & recipe_ingredients_set
            match_percent = len(matched) / len(recipe_ingredients_set) * 100

            if match_percent >= match_threshold * 100:
                results.append({
                    **recipe,
                    'match_percent': match_percent,
                    'matched_ingredients': list(matched),
                    'missing_ingredients': list(recipe_ingredients_set - user_ingredients_set)
                })

        return sorted(results, key=lambda x: x['match_percent'], reverse=True)
