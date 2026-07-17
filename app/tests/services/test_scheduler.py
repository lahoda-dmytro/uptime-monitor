import pytest
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
import crud
import schemas
import scheduler
from scheduler import ping_site
from tests.conftest import TestingSessionLocal

class MockResponse:
    def __init__(self, status_code):
        self.status_code = status_code

class MockSuccessClient:
    async def get(self, url, **kwargs):
        return MockResponse(200)
        
    async def post(self, url, **kwargs):
        pass

class MockFailureClient:
    async def get(self, url, **kwargs):
        return MockResponse(502)
        
    async def post(self, url, **kwargs):
        pass

class MockExceptionClient:
    async def get(self, url, **kwargs):
        raise httpx.ConnectError("Connection failed")
        
    async def post(self, url, **kwargs):
        pass

scheduler.SessionLocal = TestingSessionLocal

@pytest.mark.asyncio
async def test_ping_site_success(db_session: AsyncSession):
    site = await crud.create_site(db_session, schemas.SiteCreate(url="https://test.com", name="Test"))
    
    client = MockSuccessClient()
    await ping_site(client, site.id, site.url, site.name)
    
    last_log = await crud.get_last_ping_log(db_session, site.id)
    assert last_log is not None
    assert last_log.is_up is True
    assert last_log.status_code == 200

@pytest.mark.asyncio
async def test_ping_site_failure(db_session: AsyncSession):
    site = await crud.create_site(db_session, schemas.SiteCreate(url="https://test.com", name="Test"))
    
    client = MockFailureClient()
    await ping_site(client, site.id, site.url, site.name)
    
    last_log = await crud.get_last_ping_log(db_session, site.id)
    assert last_log is not None
    assert last_log.is_up is False
    assert last_log.status_code == 502

@pytest.mark.asyncio
async def test_ping_site_exception(db_session: AsyncSession):
    site = await crud.create_site(db_session, schemas.SiteCreate(url="https://test.com", name="Test"))
    
    client = MockExceptionClient()
    await ping_site(client, site.id, site.url, site.name)
    
    last_log = await crud.get_last_ping_log(db_session, site.id)
    assert last_log is not None
    assert last_log.is_up is False
    assert last_log.status_code is None
    assert "Connection failed" in last_log.error_message
