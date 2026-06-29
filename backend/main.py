from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from models import Base
from database import engine
from routes import router
from routes_ai import router as ai_router
from routes_recommendations import router as recommendations_router
from routes_reviews import router as reviews_router
from routes_dietary import router as dietary_router
from routes_user import router as user_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database ready")
    yield
    # Shutdown
    logger.info("Shutting down...")


app = FastAPI(
    title="CookingSite API",
    description="API для поиска рецептов по продуктам",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем маршруты
app.include_router(router)
app.include_router(ai_router)
app.include_router(recommendations_router)
app.include_router(reviews_router)
app.include_router(dietary_router)
app.include_router(user_router)


@app.get("/")
async def root():
    return {
        "message": "CookingSite API",
        "docs": "/docs",
        "version": "0.1.0"
    }


@app.get("/api/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
