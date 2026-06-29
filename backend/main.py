from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

app = FastAPI(title="CookingSite API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "CookingSite API"}


@app.get("/api/health")
async def health():
    return {"status": "ok"}


# Routes для рецептов
@app.get("/api/recipes/search")
async def search_recipes(ingredients: list[str]):
    """Поиск рецептов по ингредиентам"""
    return {
        "ingredients": ingredients,
        "recipes": []
    }


@app.get("/api/recipes/{recipe_id}")
async def get_recipe(recipe_id: int):
    """Получить рецепт по ID"""
    return {"id": recipe_id, "title": "Recipe"}


@app.post("/api/fridge")
async def add_to_fridge(ingredients: list[str]):
    """Добавить продукты в личный холодильник"""
    return {"added": ingredients}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
