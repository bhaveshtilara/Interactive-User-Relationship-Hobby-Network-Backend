from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import engine
from app.models import Base
from app.config import settings
import logging
import uvicorn
from fastapi.middleware.cors import CORSMiddleware 
from app.api import routes as api_routes

# ... (logging setup, lifespan function - no changes there) ...
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This code runs on startup
    logger.info(f"Application starting up in {settings.APP_ENV} mode...")
    
    # Only create tables if we are NOT in "test" mode
    if settings.APP_ENV != "test":
        logger.info("Creating database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created (if they didn't exist).")
    else:
        logger.info("Running in 'test' mode, skipping table creation.")
    
    yield
    logger.info("Application shutting down...")
    await engine.dispose()

# Create the FastAPI app instance
app = FastAPI(
    title="Cybernauts User Network",
    description="API for managing users and their hobby networks.",
    version="1.0.0",
    lifespan=lifespan
)

# --- NEW: Add CORS Middleware ---
# This allows our React app (running on a different port) : to make requests to this backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins (for development)
    # In production, you'd list your frontend's domain: ["https://myapp.com"]
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"], # Allow all methods
    allow_headers=["*"], # Allow all headers
)

# --- NEW: Include our API routes ---
app.include_router(api_routes.router) # All routes from routes.py


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