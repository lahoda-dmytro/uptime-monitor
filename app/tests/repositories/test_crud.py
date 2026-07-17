import pytest
from sqlalchemy.ext.asyncio import AsyncSession
import crud
import schemas

@pytest.mark.asyncio
async def test_create_and_get_site(db_session: AsyncSession):
    site_in = schemas.SiteCreate(url="https://test.com", name="Test")
    site = await crud.create_site(db_session, site_in)
    
    assert site.id is not None
    assert site.url == "https://test.com"
    
    fetched = await crud.get_site(db_session, site.id)
    assert fetched.id == site.id

@pytest.mark.asyncio
async def test_ping_logs(db_session: AsyncSession):
    site_in = schemas.SiteCreate(url="https://test.com", name="Test")
    site = await crud.create_site(db_session, site_in)
    
    await crud.create_ping_log(
        db_session, site_id=site.id, status_code=200, 
        response_time_ms=100, is_up=True, error_message=None
    )
    
    log2 = await crud.create_ping_log(
        db_session, site_id=site.id, status_code=500, 
        response_time_ms=150, is_up=False, error_message="Server error"
    )
    
    logs = await crud.get_site_logs(db_session, site.id)
    assert len(logs) == 2
    assert logs[0].id == log2.id
    
    last_log = await crud.get_last_ping_log(db_session, site.id)
    assert last_log.id == log2.id
    assert last_log.is_up is False
