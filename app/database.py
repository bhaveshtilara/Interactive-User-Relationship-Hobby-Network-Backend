from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from .config import settings

# Create the async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # Log SQL queries (good for dev)
)

# Create a session factory
# We will use this to get a new session for each request
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for our SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Dependency to get a DB session in our API routes
async def get_db() -> AsyncSession:
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()