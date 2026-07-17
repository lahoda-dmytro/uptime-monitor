import os
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from httpx import AsyncClient, ASGITransport

from database import Base, get_db
from main import app

# Use a temporary SQLite file for testing instead of in-memory to allow multiple concurrent connections
# to see the same database schema and data.
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test_temp.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope="function")
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture(scope="session", autouse=True)
async def cleanup_db_file():
    # Remove file if it exists from a crashed run
    try:
        if os.path.exists("./test_temp.db"):
            os.remove("./test_temp.db")
    except Exception:
        pass
    yield
    await engine.dispose()
    try:
        if os.path.exists("./test_temp.db"):
            os.remove("./test_temp.db")
    except Exception:
        pass
