from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase
from .config import settings
from typing import AsyncIterator  

url = make_url(settings.DATABASE_URL)

if url.drivername == "postgresql":
    url.drivername = "postgresql+asyncpg"

engine = create_async_engine(
    url.render_as_string(hide_password=False),
    echo=False,
)
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)
class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncIterator[AsyncSession]:
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()