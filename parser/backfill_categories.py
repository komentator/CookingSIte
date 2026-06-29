# -*- coding: utf-8 -*-
"""
Добавляет колонку `category` в таблицу recipes (если ещё нет)
и заполняет её из parsed_recipes.json по title.
"""
import io
import json
import os
import sqlite3
import sys
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB = Path(__file__).resolve().parent.parent / 'cooking.db'
JSON_PATH = Path(__file__).resolve().parent / 'parsed_recipes.json'


def normalize_category(raw: str | None) -> str | None:
    if not raw:
        return None
    raw = raw.strip()
    # объединить похожие категории в общие
    mapping = {
        'Бульоны и супы': 'Супы',
        'Горячие блюда': 'Основные блюда',
        'Паста': 'Паста',
        'Выпечка': 'Выпечка',
        'Закуски': 'Закуски',
        'Салаты': 'Салаты',
        'Десерты': 'Десерты',
        'Напитки': 'Напитки',
        'Соусы': 'Соусы',
    }
    return mapping.get(raw, raw)


def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("PRAGMA table_info(recipes)")
    cols = [c[1] for c in cur.fetchall()]
    if 'category' not in cols:
        cur.execute("ALTER TABLE recipes ADD COLUMN category VARCHAR(100)")
        print('Добавлена колонка recipes.category')

    cur.execute("CREATE INDEX IF NOT EXISTS ix_recipes_category ON recipes(category)")

    data = json.loads(JSON_PATH.read_text(encoding='utf-8'))
    updated = 0
    for rec in data:
        title = (rec.get('title') or '').strip()
        cat = normalize_category(rec.get('category'))
        if title and cat:
            cur.execute("UPDATE recipes SET category=? WHERE title=?", (cat, title))
            if cur.rowcount > 0:
                updated += cur.rowcount

    conn.commit()
    print(f'Обновлено категорий: {updated}')

    cur.execute("SELECT category, COUNT(*) FROM recipes GROUP BY category ORDER BY 2 DESC")
    print('\nРаспределение по категориям:')
    for cat, n in cur.fetchall():
        print(f'  {cat!r}: {n}')

    conn.close()


if __name__ == '__main__':
    main()
