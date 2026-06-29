"""
Скрипт для добавления примеров рецептов в БД
"""

SAMPLE_RECIPES = [
    {
        "title": "Жаркое из курицы",
        "description": "Классическое русское блюдо с картошкой и мясом",
        "source": "local",
        "cooking_time": 90,
        "servings": 4,
        "calories": 350,
        "ingredients": [
            {"name": "курица", "quantity": "500", "unit": "г", "is_required": True},
            {"name": "картошка", "quantity": "600", "unit": "г", "is_required": True},
            {"name": "лук", "quantity": "2", "unit": "шт", "is_required": True},
            {"name": "морковь", "quantity": "2", "unit": "шт", "is_required": True},
            {"name": "чеснок", "quantity": "3", "unit": "зубчика", "is_required": False},
            {"name": "петрушка", "quantity": "пучок", "unit": "шт", "is_required": False},
        ],
        "instructions": [
            {"step_number": 1, "description": "Нарежьте курицу на куски и выложите в кастрюлю"},
            {"step_number": 2, "description": "Нарежьте картошку кубиками и добавьте к курице"},
            {"step_number": 3, "description": "Нарежьте лук и морковь, добавьте в кастрюлю"},
            {"step_number": 4, "description": "Залейте водой, доведите до кипения"},
            {"step_number": 5, "description": "Накройте крышкой и тушите на среднем огне 60 минут"},
            {"step_number": 6, "description": "Приправьте солью, перцем и подавайте горячим"},
        ],
    },
    {
        "title": "Борщ украинский",
        "description": "Традиционный украинский суп со свеклой и капустой",
        "source": "local",
        "cooking_time": 60,
        "servings": 6,
        "calories": 150,
        "ingredients": [
            {"name": "свекла", "quantity": "3", "unit": "шт", "is_required": True},
            {"name": "капуста", "quantity": "500", "unit": "г", "is_required": True},
            {"name": "картошка", "quantity": "3", "unit": "шт", "is_required": True},
            {"name": "помидор", "quantity": "2", "unit": "шт", "is_required": False},
            {"name": "говяжий фарш", "quantity": "300", "unit": "г", "is_required": False},
            {"name": "чеснок", "quantity": "4", "unit": "зубчика", "is_required": False},
        ],
        "instructions": [
            {"step_number": 1, "description": "Нарежьте свеклу соломкой и тушите в кастрюле"},
            {"step_number": 2, "description": "Нарежьте капусту тонкой соломкой"},
            {"step_number": 3, "description": "Нарежьте картошку кубиками"},
            {"step_number": 4, "description": "Залейте кипятком и варите 30 минут"},
            {"step_number": 5, "description": "Добавьте капусту и картошку, варите еще 20 минут"},
            {"step_number": 6, "description": "Приправьте уксусом, сметаной и подавайте"},
        ],
    },
    {
        "title": "Омлет с сыром",
        "description": "Быстрый и простой омлет с сыром к завтраку",
        "source": "local",
        "cooking_time": 15,
        "servings": 2,
        "calories": 250,
        "ingredients": [
            {"name": "яйцо", "quantity": "3", "unit": "шт", "is_required": True},
            {"name": "сыр", "quantity": "100", "unit": "г", "is_required": True},
            {"name": "масло сливочное", "quantity": "1", "unit": "ст.л.", "is_required": True},
            {"name": "молоко", "quantity": "50", "unit": "мл", "is_required": False},
            {"name": "зелень", "quantity": "щепотка", "unit": "шт", "is_required": False},
        ],
        "instructions": [
            {"step_number": 1, "description": "Разбейте яйца в миску и взбейте с молоком"},
            {"step_number": 2, "description": "Натрите сыр на терке"},
            {"step_number": 3, "description": "Разогрейте масло на сковороде"},
            {"step_number": 4, "description": "Вылейте смесь яиц на сковороду"},
            {"step_number": 5, "description": "Когда начнет схватываться, посыпьте сыром"},
            {"step_number": 6, "description": "Сложите пополам и подавайте горячим"},
        ],
    },
    {
        "title": "Макароны с томатным соусом",
        "description": "Простое итальянское блюдо на скорую руку",
        "source": "local",
        "cooking_time": 25,
        "servings": 3,
        "calories": 400,
        "ingredients": [
            {"name": "макароны", "quantity": "300", "unit": "г", "is_required": True},
            {"name": "помидор", "quantity": "4", "unit": "шт", "is_required": True},
            {"name": "чеснок", "quantity": "3", "unit": "зубчика", "is_required": True},
            {"name": "оливковое масло", "quantity": "3", "unit": "ст.л.", "is_required": True},
            {"name": "базилик", "quantity": "пучок", "unit": "шт", "is_required": False},
        ],
        "instructions": [
            {"step_number": 1, "description": "Отварите макароны до готовности"},
            {"step_number": 2, "description": "Нарежьте помидоры небольшими кусками"},
            {"step_number": 3, "description": "Нарежьте чеснок очень тонко"},
            {"step_number": 4, "description": "Прогрейте масло с чесноком на сковороде"},
            {"step_number": 5, "description": "Добавьте помидоры и тушите 10 минут"},
            {"step_number": 6, "description": "Смешайте с макаронами и подавайте горячим"},
        ],
    },
    {
        "title": "Куриный суп с лапшой",
        "description": "Теплый и сытный суп для холодных дней",
        "source": "local",
        "cooking_time": 45,
        "servings": 5,
        "calories": 200,
        "ingredients": [
            {"name": "курица", "quantity": "500", "unit": "г", "is_required": True},
            {"name": "лапша", "quantity": "150", "unit": "г", "is_required": True},
            {"name": "морковь", "quantity": "2", "unit": "шт", "is_required": True},
            {"name": "лук", "quantity": "1", "unit": "шт", "is_required": True},
            {"name": "сельдерей", "quantity": "1", "unit": "стебель", "is_required": False},
        ],
        "instructions": [
            {"step_number": 1, "description": "Вскипятите воду и положите курицу"},
            {"step_number": 2, "description": "Снимите пену и варите 20 минут"},
            {"step_number": 3, "description": "Нарежьте овощи и добавьте в бульон"},
            {"step_number": 4, "description": "Варите 15 минут до мягкости овощей"},
            {"step_number": 5, "description": "Добавьте лапшу и варите 10 минут"},
            {"step_number": 6, "description": "Приправьте солью и подавайте горячим"},
        ],
    },
]


def seed_database():
    """Добавить примеры рецептов в БД"""
    import sys
    sys.path.insert(0, '../backend')

    from database import SessionLocal
    from models import Recipe, Ingredient, RecipeIngredient, Instruction

    db = SessionLocal()

    try:
        # Очистим старые рецепты если нужно
        # db.query(Recipe).delete()
        # db.commit()

        for recipe_data in SAMPLE_RECIPES:
            # Проверяем, не существует ли уже
            existing = db.query(Recipe).filter(Recipe.title == recipe_data['title']).first()
            if existing:
                print(f"Recipe '{recipe_data['title']}' already exists, skipping...")
                continue

            # Создаем рецепт
            recipe = Recipe(
                title=recipe_data['title'],
                description=recipe_data['description'],
                source=recipe_data['source'],
                cooking_time=recipe_data['cooking_time'],
                servings=recipe_data['servings'],
                calories=recipe_data['calories'],
            )
            db.add(recipe)
            db.flush()

            # Добавляем ингредиенты
            for ing_data in recipe_data['ingredients']:
                # Ищем или создаем ингредиент
                ingredient = db.query(Ingredient).filter(
                    Ingredient.name.ilike(ing_data['name'])
                ).first()

                if not ingredient:
                    ingredient = Ingredient(name=ing_data['name'])
                    db.add(ingredient)
                    db.flush()

                # Добавляем в рецепт
                recipe_ing = RecipeIngredient(
                    recipe_id=recipe.id,
                    ingredient_id=ingredient.id,
                    quantity=ing_data.get('quantity'),
                    unit=ing_data.get('unit'),
                    is_required=ing_data.get('is_required', True),
                )
                db.add(recipe_ing)

            # Добавляем инструкции
            for inst_data in recipe_data['instructions']:
                instruction = Instruction(
                    recipe_id=recipe.id,
                    step_number=inst_data['step_number'],
                    description=inst_data['description'],
                )
                db.add(instruction)

            db.commit()
            print(f"Added recipe: {recipe_data['title']}")

        print(f"\nSuccessfully added {len(SAMPLE_RECIPES)} recipes!")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == '__main__':
    seed_database()
