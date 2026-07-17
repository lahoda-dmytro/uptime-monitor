import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_create_site(client: AsyncClient, db_session):
    response = await client.post(
        "/api/v1/sites",
        json={"url": "https://example.com", "name": "Example"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["url"] == "https://example.com"
    assert data["name"] == "Example"
    assert "id" in data

@pytest.mark.asyncio
async def test_create_duplicate_site(client: AsyncClient, db_session):
    # Create first
    await client.post("/api/v1/sites", json={"url": "https://example.com", "name": "Example"})
    
    # Create duplicate
    response = await client.post("/api/v1/sites", json={"url": "https://example.com", "name": "Example 2"})
    assert response.status_code == 400
    assert "already exist" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_sites(client: AsyncClient, db_session):
    await client.post("/api/v1/sites", json={"url": "https://test1.com", "name": "Test 1"})
    await client.post("/api/v1/sites", json={"url": "https://test2.com", "name": "Test 2"})
    
    response = await client.get("/api/v1/sites")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["url"] == "https://test1.com"

@pytest.mark.asyncio
async def test_delete_site(client: AsyncClient, db_session):
    create_response = await client.post("/api/v1/sites", json={"url": "https://example.com", "name": "Example"})
    site_id = create_response.json()["id"]
    
    delete_response = await client.delete(f"/api/v1/sites/{site_id}")
    assert delete_response.status_code == 204
    
    # Verify it's gone
    get_response = await client.get(f"/api/v1/sites/{site_id}")
    assert get_response.status_code == 404
