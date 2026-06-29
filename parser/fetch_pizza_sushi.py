# -*- coding: utf-8 -*-
"""
Парсинг рецептов из категорий «Пицца» и «Суши/Роллы» с povarenok.ru,
импорт в БД и присваивание правильной категории.
"""
import io
import json
import sys
import time
import logging
from pathlib import Path
from typing import List

import requests
from bs4 import BeautifulSoup

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).resolve().parent))
from web_parser import parse_povarenok_recipe, HEADERS  # type: ignore

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

CATEGORIES = [
    ('Пицца',     'https://www.povarenok.ru/recipes/category/28/',  3),
    ('Суши',      'https://www.povarenok.ru/recipes/category/246/', 3),
]


def fetch_links(session: requests.Session, base_url: str, pages: int) -> List[str]:
    links = set()
    for p in range(1, pages + 1):
        url = base_url if p == 1 else f'{base_url}~{p}/'
        try:
            r = session.get(url, timeout=20)
            soup = BeautifulSoup(r.text, 'lxml')
            for a in soup.find_all('a', href=True):
                if '/recipes/show/' in a['href']:
                    l = a['href'].split('#')[0].split('?')[0]
                    if not l.startswith('http'):
                        l = 'https://www.povarenok.ru' + l
                    links.add(l)
            time.sleep(0.4)
        except Exception as e:
            log.warning(f'fetch page {p}: {e}')
    return sorted(links)


def main():
    session = requests.Session()
    session.headers.update(HEADERS)

    out_path = Path(__file__).parent / 'parsed_recipes.json'
    existing = json.loads(out_path.read_text(encoding='utf-8')) if out_path.exists() else []
    existing_titles = {(r.get('title') or '').lower() for r in existing}
    log.info(f'Уже в parsed_recipes.json: {len(existing)}')

    new_recipes = []
    for category, url, pages in CATEGORIES:
        log.info(f'\n=== {category} ===')
        links = fetch_links(session, url, pages)
        log.info(f'  links: {len(links)}')
        for i, link in enumerate(links, 1):
            rec = parse_povarenok_recipe(session, link)
            if not rec:
                continue
            title = (rec.get('title') or '').strip()
            if not title or title.lower() in existing_titles:
                continue
            if not (rec.get('ingredients') and rec.get('instructions')):
                continue
            rec['category'] = category  # принудительно
            new_recipes.append(rec)
            existing_titles.add(title.lower())
            log.info(f'  [{i}/{len(links)}] + {title}')
            time.sleep(0.4)

    all_recipes = existing + new_recipes
    out_path.write_text(json.dumps(all_recipes, ensure_ascii=False, indent=2), encoding='utf-8')
    log.info(f'\nСохранено в JSON: {len(all_recipes)} (добавлено {len(new_recipes)})')


if __name__ == '__main__':
    main()
