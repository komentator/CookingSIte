# 🍳 CookingSite

Умный сайт рецептов с поиском по имеющимся продуктам. Найдите, что можно приготовить из того, что есть дома.

## 🌟 Фичи

### Основное
- ✅ **Поиск по продуктам** - введите ингредиенты, получите рецепты
- ✅ **Группировка рецептов** - "готово сейчас", "нужно докупить", "много не хватает"
- ✅ **Личный холодильник** - сохраняйте постоянные продукты
- ✅ **Процент совпадения** - видите, насколько хорошо подходит рецепт

### Умные функции (AI)
- ✅ **Умный поиск** - "есть курица, картошка, готовить 30 минут максимум"
- ✅ **Синонимы** - распознает "курочку" как "курица"
- ✅ **Замены ингредиентов** - предлагает что использовать вместо недостающего
- ✅ **Организованный список покупок** - категоризирует по типам
- ✅ **Оценка сложности** - easy/medium/hard

## 🏗️ Архитектура

**Frontend:** Next.js + TypeScript + Tailwind
**Backend:** FastAPI + SQLAlchemy + OpenAI
**Database:** PostgreSQL
**Parser:** BeautifulSoup4 (JSON-LD + HTML)

## 🚀 Быстрый старт

```bash
# Backend
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# PostgreSQL
docker run -d -p 5432:5432 postgres:16-alpine
```

Frontend: http://localhost:3000
Backend API Docs: http://localhost:8000/docs

## 📖 API

- `POST /api/search/by-ingredients` - поиск по ингредиентам
- `POST /api/ai/smart-search` - умный поиск
- `POST /api/ai/shopping-list` - список покупок
- `POST /api/ai/substitutes` - замены ингредиентов
- `GET/POST /api/fridge/{user_id}` - холодильник

## 🔐 Требуется

- `OPENAI_API_KEY` для AI функций
- `DATABASE_URL` для PostgreSQL

## 📄 Лицензия

MIT
