# -*- coding: utf-8 -*-
"""
Импорт спарсенных рецептов (parsed_recipes.json) в БД CookingSite.
Дедупликация по title. Создаёт ингредиенты, если их ещё нет.
"""
import sys
import io
import json
import logging
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'backend'))

import os
# Fallback на SQLite если Postgres недоступен
_sqlite_path = Path(__file__).resolve().parent.parent / 'cooking.db'
os.environ.setdefault('DATABASE_URL', f'sqlite:///{_sqlite_path}')

try:
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    sock.connect(('localhost', 5432))
    sock.close()
except Exception:
    os.environ['DATABASE_URL'] = f'sqlite:///{_sqlite_path}'

from database import SessionLocal, engine  # noqa: E402
from models import Base, Recipe, Ingredient, RecipeIngredient, Instruction  # noqa: E402

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

VEGAN_BLOCKERS = {'мясо', 'курица', 'свинина', 'говядина', 'рыба', 'индейка', 'телятина',
                  'фарш', 'ветчина', 'бекон', 'колбаса', 'сосиски', 'креветки', 'кальмар',
                  'мидии', 'лосось', 'тунец', 'яйцо', 'молоко', 'сыр', 'масло сливочное',
                  'сметана', 'творог', 'йогурт', 'сливки'}
VEGETARIAN_BLOCKERS = {'мясо', 'курица', 'свинина', 'говядина', 'рыба', 'индейка',
                       'телятина', 'фарш', 'ветчина', 'бекон', 'колбаса', 'сосиски',
                       'креветки', 'кальмар', 'мидии', 'лосось', 'тунец'}
GLUTEN_BLOCKERS = {'мука', 'хлеб', 'макароны', 'спагетти', 'лапша', 'булгур', 'манная крупа'}
DAIRY_BLOCKERS = {'молоко', 'сыр', 'масло сливочное', 'сметана', 'творог', 'йогурт', 'сливки'}
NUT_BLOCKERS = {'орех', 'миндаль', 'фундук', 'арахис', 'кешью', 'фисташки'}


def has_any(ing_names: set, blockers: set) -> bool:
    return any(any(b in n for b in blockers) for n in ing_names)


def import_recipes():
    path = Path(__file__).parent / 'parsed_recipes.json'
    if not path.exists():
        log.error(f'Файл не найден: {path}. Сначала запустите web_parser.py')
        return
    data = json.loads(path.read_text(encoding='utf-8'))
    log.info(f'Загружено {len(data)} рецептов из JSON')

    Base.metadata.create_all(engine)
    db = SessionLocal()
    added = skipped = 0

    try:
        for rd in data:
            title = (rd.get('title') or '').strip()
            if not title:
                continue
            if db.query(Recipe).filter(Recipe.title == title).first():
                skipped += 1
                continue

            ing_names = {(i.get('name') or '').lower() for i in rd.get('ingredients', [])}

            recipe = Recipe(
                title=title,
                description=rd.get('description') or '',
                source=rd.get('source') or 'web',
                url=rd.get('url'),
                cooking_time=rd.get('cooking_time'),
                servings=rd.get('servings'),
                calories=rd.get('calories'),
                is_vegan=not has_any(ing_names, VEGAN_BLOCKERS),
                is_vegetarian=not has_any(ing_names, VEGETARIAN_BLOCKERS),
                is_gluten_free=not has_any(ing_names, GLUTEN_BLOCKERS),
                is_dairy_free=not has_any(ing_names, DAIRY_BLOCKERS),
                is_nut_free=not has_any(ing_names, NUT_BLOCKERS),
            )
            db.add(recipe)
            db.flush()

            for ing_data in rd.get('ingredients', []):
                name = (ing_data.get('name') or '').strip()
                if not name:
                    continue
                ing = db.query(Ingredient).filter(Ingredient.name.ilike(name)).first()
                if not ing:
                    ing = Ingredient(name=name)
                    db.add(ing)
                    db.flush()
                db.add(RecipeIngredient(
                    recipe_id=recipe.id,
                    ingredient_id=ing.id,
                    quantity=ing_data.get('quantity'),
                    unit=ing_data.get('unit'),
                    is_required=ing_data.get('is_required', True),
                ))

            for step in rd.get('instructions', []):
                db.add(Instruction(
                    recipe_id=recipe.id,
                    step_number=step.get('step_number'),
                    description=step.get('description'),
                ))

            db.commit()
            added += 1
            log.info(f'  + {title} ({rd.get("source")}) — {len(rd.get("ingredients",[]))} ing')

        log.info(f'Готово: добавлено {added}, пропущено (дубликаты) {skipped}')
    except Exception as e:
        db.rollback()
        log.exception(f'Ошибка импорта: {e}')
        raise
    finally:
        db.close()


if __name__ == '__main__':
    import_recipes()
