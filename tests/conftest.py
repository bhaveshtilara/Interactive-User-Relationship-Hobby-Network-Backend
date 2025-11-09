import os
import pytest
from httpx import AsyncClient, ASGITransport

# Must be before imports
os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:postgres@localhost:5432/cybernauts_db_test"

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import event

from app.main import app
from app.database import Base, get_db
from app.config import settings

# Create the test engine
test_engine = create_async_engine(
    settings.DATABASE_URL,
    future=True,
)

# Session factory, no expire
SessionFactory = async_sessionmaker(
    bind=test_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Create/drop tables once."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await test_engine.dispose()


@pytest.fixture(scope="function")
async def db_session():
    """
    Each test runs inside:
    - One dedicated DB connection
    - One outer transaction
    - SAVEPOINT nesting to prevent asyncpg 'in progress' errors
    """
    async with test_engine.connect() as connection:
        trans = await connection.begin()  # BEGIN

        session = SessionFactory(bind=connection)

        # START SAVEPOINT
        nested = await session.begin_nested()

        # RESTART SAVEPOINT after each commit
        @event.listens_for(session.sync_session, "after_transaction_end")
        def restart_savepoint(sess, transaction):
            if transaction.nested and not transaction._parent.nested:
                sess.begin_nested()

        try:
            yield session
        finally:
            await session.close()
            await trans.rollback()  # ROLLBACK OUTER


@pytest.fixture(scope="function")
async def async_client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    client = AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    )

    try:
        yield client
    finally:
        await client.aclose()
        del app.dependency_overrides[get_db]
