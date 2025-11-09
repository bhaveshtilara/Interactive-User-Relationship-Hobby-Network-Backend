from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import engine
from app.models import Base
from app.config import settings
import logging
import uvicorn 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This code runs on startup
    logger.info("Application starting up...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created (if they didn't exist).")
    
    yield
    
    # This code runs on shutdown
    logger.info("Application shutting down...")
    await engine.dispose()

# Create the FastAPI app instance
app = FastAPI(
    title="Cybernauts User Network",
    description="API for managing users and their hobby networks.",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Cybernauts API"}

if __name__ == "__main__":
    logger.info(f"Starting server on http://0.0.0.0:{settings.PORT}")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=True
    )