"""Shared fixtures for tests."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.database import Base, get_db
from app.main import app


# Global engine and session maker for test client calls
_test_engine = None
_test_session_maker = None
_test_session = None


@pytest_asyncio.fixture
async def test_db():
    """Create an in-memory test database."""
    global _test_engine, _test_session_maker, _test_session

    # Use SQLite in-memory for tests with URI to share db across connections
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False, "uri": True},
        poolclass=StaticPool,
    )
    _test_engine = engine

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    _test_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # Create a session for async tests
    async with _test_session_maker() as session:
        _test_session = session
        yield session
        _test_session = None

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
    _test_engine = None
    _test_session_maker = None


@pytest.fixture
async def db(test_db: AsyncSession) -> AsyncSession:
    """Provide database session to tests."""
    return test_db


@pytest.fixture
def override_get_db(test_db: AsyncSession):
    """Override the get_db dependency for tests."""

    async def _override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def override_get_db_for_client(test_db: AsyncSession):
    """Override the get_db dependency for TestClient tests."""

    async def _override_get_db_for_client():
        # Reuse the test session to share the in-memory database
        yield test_db

    app.dependency_overrides[get_db] = _override_get_db_for_client
    yield
    app.dependency_overrides.clear()
