# -*- coding: utf-8 -*-
"""
Унифицированный парсер рецептов с реальных сайтов.
Поддержка: barilla.ru (JSON-LD), povarenok.ru (microdata itemprop).
Сохраняет результат в parsed_recipes.json для последующего импорта в БД.
"""
import json
import re
import sys
import time
import io
import logging
from pathlib import Path
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36',
    'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
}

ISO_DURATION_RE = re.compile(r'^PT(?:(\d+)H)?(?:(\d+)M)?$')
NUMERIC_QTY_RE = re.compile(r'^[\d,./\s]+$')

UNITS = [
    'кг', 'грамм', 'г', 'мг', 'литр', 'л', 'мл',
    'ст.л.', 'ст. л.', 'ст.ложк', 'столовая ложка',
    'ч.л.', 'ч. л.', 'чайная ложка',
    'стакан', 'стакана', 'стаканов',
    'шт', 'шт.', 'штук', 'штуки',
    'зубчик', 'зубчика', 'зубчиков',
    'пучок', 'пучка',
    'долька', 'дольки',
    'упаковка', 'банка', 'банки',
    'по вкусу', 'щепотка',
]


def iso_to_minutes(iso: Optional[str]) -> Optional[int]:
    if not iso:
        return None
    m = ISO_DURATION_RE.match(iso.strip())
    if not m:
        return None
    h = int(m.group(1) or 0)
    mn = int(m.group(2) or 0)
    return h * 60 + mn


def text_to_minutes(text: Optional[str]) -> Optional[int]:
    if not text:
        return None
    total = 0
    h = re.search(r'(\d+)\s*ч', text)
    m = re.search(r'(\d+)\s*мин', text)
    if h:
        total += int(h.group(1)) * 60
    if m:
        total += int(m.group(1))
    return total or None


def parse_int(s: Optional[str]) -> Optional[int]:
    if not s:
        return None
    m = re.search(r'\d+', str(s))
    return int(m.group(0)) if m else None


def parse_ingredient_line(line: str) -> Dict:
    """Разбирает строку 'Курица 500 г' -> {name, quantity, unit}."""
    line = re.sub(r'\s+', ' ', line).strip()
    line = line.replace(' — ', ' ').replace('—', ' ')
    if not line:
        return {}

    quantity = None
    unit = None
    name = line

    # Unit + qty: "200 г", "1/2 ст.л.", "по вкусу"
    if 'по вкусу' in line.lower():
        name = re.sub(r'\s*по\s+вкусу\s*', '', line, flags=re.IGNORECASE).strip()
        quantity = 'по вкусу'
    else:
        # Поиск количества + единицы в конце
        # 1. "Сахар 5 ст.л."
        m = re.search(r'^(?P<name>.+?)\s+(?P<qty>[\d.,/]+)\s*(?P<unit>[а-яА-Яa-zA-Z.]+)?\s*$', line)
        if m:
            name = m.group('name').strip()
            quantity = m.group('qty').strip()
            unit = (m.group('unit') or '').strip() or None
        # 2. Если nothing matched — оставить целиком в name
    name = re.sub(r'\s+\(.*?\)\s*$', '', name).strip(' ,.;:-')
    return {
        'name': name.lower(),
        'quantity': quantity,
        'unit': unit,
        'is_required': True,
        'original': line,
    }


# ============================================================
# BARILLA.RU — JSON-LD
# ============================================================

def fetch_barilla_recipe_links(session: requests.Session) -> List[str]:
    r = session.get('https://barilla.ru/recipes', timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'lxml')
    links = set()
    for a in soup.find_all('a', href=True):
        h = a['href']
        if '/recipes/' in h and not h.rstrip('/').endswith('/recipes'):
            full = h if h.startswith('http') else 'https://barilla.ru' + h
            links.add(full.split('#')[0])
    return sorted(links)


def parse_barilla_recipe(session: requests.Session, url: str) -> Optional[Dict]:
    try:
        r = session.get(url, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'lxml')
        # Собрать ВСЕ Recipe-блоки, выбрать самый полный
        candidates = []
        for s in soup.find_all('script', type='application/ld+json'):
            if not s.string:
                continue
            try:
                data = json.loads(s.string)
            except json.JSONDecodeError:
                continue
            items = data if isinstance(data, list) else [data]
            for it in items:
                if isinstance(it, dict) and 'Recipe' in str(it.get('@type', '')):
                    candidates.append(it)
        if not candidates:
            return None
        it = max(candidates, key=lambda x: len(x.get('recipeIngredient') or []))
        if True:
                instructions = []
                for idx, step in enumerate(it.get('recipeInstructions', []) or [], start=1):
                    if isinstance(step, dict):
                        text = step.get('text') or step.get('name') or ''
                    else:
                        text = str(step)
                    text = text.strip()
                    if text:
                        instructions.append({'step_number': idx, 'description': text})

                ingredients = []
                for raw in it.get('recipeIngredient', []) or []:
                    parsed = parse_ingredient_line(str(raw))
                    if parsed.get('name'):
                        ingredients.append(parsed)

                cooking_time = iso_to_minutes(it.get('totalTime')) or \
                               (iso_to_minutes(it.get('prepTime') or '') or 0) + \
                               (iso_to_minutes(it.get('cookTime') or '') or 0) or None

                return {
                    'title': (it.get('name') or '').strip(),
                    'description': re.sub(r'\s+', ' ', (it.get('description') or '')).strip()[:1000],
                    'source': 'barilla.ru',
                    'url': url,
                    'image_url': it.get('image') if isinstance(it.get('image'), str) else None,
                    'cooking_time': cooking_time,
                    'servings': parse_int(it.get('recipeYield')),
                    'calories': None,
                    'category': it.get('recipeCategory'),
                    'cuisine': it.get('recipeCuisine'),
                    'ingredients': ingredients,
                    'instructions': instructions,
                }
    except Exception as e:
        log.warning(f'barilla: {url} — {e}')
    return None


# ============================================================
# POVARENOK.RU — microdata (itemprop)
# ============================================================

def fetch_povarenok_recipe_links(session: requests.Session, pages: int = 3) -> List[str]:
    links = set()
    for p in range(1, pages + 1):
        url = 'https://www.povarenok.ru/recipes/' if p == 1 else f'https://www.povarenok.ru/recipes/~{p}/'
        try:
            r = session.get(url, timeout=20)
            soup = BeautifulSoup(r.text, 'lxml')
            for a in soup.find_all('a', href=True):
                h = a['href']
                if '/recipes/show/' in h:
                    clean = h.split('#')[0].split('?')[0]
                    if not clean.startswith('http'):
                        clean = 'https://www.povarenok.ru' + clean
                    links.add(clean)
            time.sleep(0.5)
        except Exception as e:
            log.warning(f'povarenok page {p}: {e}')
    return sorted(links)


def parse_povarenok_recipe(session: requests.Session, url: str) -> Optional[Dict]:
    try:
        r = session.get(url, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'lxml')

        def get_prop(prop: str) -> Optional[str]:
            el = soup.find(attrs={'itemprop': prop})
            if not el:
                return None
            return (el.get('content') or el.get_text(' ', strip=True) or '').strip() or None

        title = get_prop('name')
        if not title:
            return None

        description = get_prop('description') or ''
        description = re.sub(r'\s+', ' ', description).strip()[:1000]

        ingredients = []
        for el in soup.find_all(attrs={'itemprop': 'recipeIngredient'}):
            raw = ' '.join(el.get_text(' ', strip=True).split())
            if raw:
                parsed = parse_ingredient_line(raw)
                if parsed.get('name'):
                    ingredients.append(parsed)

        instructions = []
        steps_els = soup.find_all(attrs={'itemprop': 'recipeInstructions'})
        # часто весь текст в одном блоке — разрежем на шаги по предложениям/абзацам
        if len(steps_els) == 1:
            raw = steps_els[0].get_text('\n', strip=True)
            parts = [p.strip() for p in re.split(r'\n+|(?<=[.!?])\s+(?=[А-ЯA-Z])', raw) if p.strip()]
            for idx, p in enumerate(parts, 1):
                if len(p) > 5:
                    instructions.append({'step_number': idx, 'description': p[:500]})
        else:
            for idx, el in enumerate(steps_els, 1):
                txt = ' '.join(el.get_text(' ', strip=True).split())
                if txt:
                    instructions.append({'step_number': idx, 'description': txt[:500]})

        return {
            'title': title,
            'description': description,
            'source': 'povarenok.ru',
            'url': url,
            'image_url': None,
            'cooking_time': text_to_minutes(get_prop('totalTime')),
            'servings': parse_int(get_prop('recipeYield')),
            'calories': parse_int(get_prop('calories')),
            'category': get_prop('recipeCategory'),
            'cuisine': None,
            'ingredients': ingredients,
            'instructions': instructions,
        }
    except Exception as e:
        log.warning(f'povarenok: {url} — {e}')
    return None


# ============================================================
# Main
# ============================================================

def main():
    session = requests.Session()
    session.headers.update(HEADERS)

    out: List[Dict] = []
    seen_titles = set()

    log.info('Fetching barilla.ru recipe links...')
    barilla_links = fetch_barilla_recipe_links(session)
    log.info(f'  found {len(barilla_links)} links')
    for i, url in enumerate(barilla_links, 1):
        rec = parse_barilla_recipe(session, url)
        if rec and rec['title'] and rec['title'].lower() not in seen_titles:
            if rec['ingredients'] and rec['instructions']:
                out.append(rec)
                seen_titles.add(rec['title'].lower())
                log.info(f'  [{i}/{len(barilla_links)}] OK: {rec["title"]} ({len(rec["ingredients"])} ing, {len(rec["instructions"])} steps)')
        time.sleep(0.4)

    log.info('Fetching povarenok.ru recipe links...')
    povarenok_links = fetch_povarenok_recipe_links(session, pages=3)
    log.info(f'  found {len(povarenok_links)} links')
    limit = 50
    for i, url in enumerate(povarenok_links[:limit], 1):
        rec = parse_povarenok_recipe(session, url)
        if rec and rec['title'] and rec['title'].lower() not in seen_titles:
            if rec['ingredients'] and rec['instructions']:
                out.append(rec)
                seen_titles.add(rec['title'].lower())
                log.info(f'  [{i}/{min(limit,len(povarenok_links))}] OK: {rec["title"]} ({len(rec["ingredients"])} ing, {len(rec["instructions"])} steps)')
        time.sleep(0.4)

    out_path = Path(__file__).parent / 'parsed_recipes.json'
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    log.info(f'Saved {len(out)} recipes to {out_path}')


if __name__ == '__main__':
    main()
