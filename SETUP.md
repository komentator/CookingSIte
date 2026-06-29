# CookingSite - Инструкции по запуску

## Локальная разработка

### 1. Backend (FastAPI)

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt

# Создать .env файл
cp ../.env.example .env

# Запустить сервер
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend будет доступен на: `http://localhost:8000`
Docs: `http://localhost:8000/docs`

### 2. Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

Frontend будет доступен на: `http://localhost:3000`

### 3. База данных (PostgreSQL)

Опция 1: Docker
```bash
docker run --name cookingsite-db \
  -e POSTGRES_USER=cookingsite \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=cookingsite \
  -p 5432:5432 \
  postgres:16-alpine
```

Опция 2: Docker Compose
```bash
docker-compose up -d
```

## Проверка

1. Перейти на http://localhost:3000
2. Введить ингредиенты (например: курица, картошка, лук)
3. Нажать "Найти рецепты"
4. Результаты должны прийти с backend'а

## Структура API

- `POST /api/search/by-ingredients` - поиск по ингредиентам
- `GET/POST /api/recipes` - список и создание рецептов
- `GET /api/recipes/{id}` - получить рецепт
- `POST /api/fridge/{user_id}` - добавить в холодильник
- `GET /api/fridge/{user_id}` - получить холодильник
- `GET/POST /api/ingredients` - ингредиенты

## Парсер рецептов

```bash
cd parser
pip install -r requirements.txt

# Использование
python -c "from recipe_parser import RecipeParser; p = RecipeParser(); print(p.parse_recipe('https://...'))"
```

Поддерживает:
- JSON-LD структурированные данные
- Generic HTML парсинг
- ISO 8601 duration парсинг
