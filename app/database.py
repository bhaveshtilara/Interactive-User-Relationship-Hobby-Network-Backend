from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from .config import settings

db_url_str = settings.DATABASE_URL

if db_url_str.startswith("postgresql://"):
    db_url_str = db_url_str.replace("postgresql://", "postgresql+asyncpg://", 1)

if not db_url_str.startswith("postgresql+asyncpg://"):
    raise ValueError("DATABASE_URL must use the async driver, e.g. postgresql+asyncpg://...")


engine = create_async_engine(
    db_url_str,
    echo=False, 
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncSession:
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()