"""
🧪 Test Package 01: Health & Status - System Availability Tests

Tests basic system endpoints to verify the server is running and accessible.
Tests endpoints: /api/health, /api/status
"""
import pytest
import httpx


@pytest.mark.asyncio
async def test_health_endpoint(client: httpx.AsyncClient):
    """Test the health check endpoint."""
    response = await client.get("/api/health")
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_status_endpoint(client: httpx.AsyncClient):
    """Test the status endpoint."""
    response = await client.get("/api/status")
    
    assert response.status_code == 200
    data = response.json()
    assert "services" in data
    assert isinstance(data["services"], list)
    
    # Check that essential services are reported
    services = data["services"]
    assert "collection_management" in services
    assert "vector_sync" in services
    assert "web_crawling" in services
    
    # Verify response structure
    assert "status" in data
    assert "server_type" in data
    assert data["server_type"] == "unified"


@pytest.mark.asyncio
async def test_health_and_status_combined_flow(client: httpx.AsyncClient):
    """Test combined health and status check flow as a user would."""
    # Step 1: Check if system is healthy
    health_resp = await client.get("/api/health")
    assert health_resp.status_code == 200
    assert health_resp.json()["status"] == "healthy"
    
    # Step 2: If healthy, get detailed status
    status_resp = await client.get("/api/status")
    assert status_resp.status_code == 200
    
    status_data = status_resp.json()
    assert "services" in status_data
    
    # Verify essential services are present
    services = status_data["services"]
    assert isinstance(services, list)
    assert len(services) > 0
    assert "collection_management" in services


@pytest.mark.asyncio
async def test_invalid_endpoint_404(client: httpx.AsyncClient):
    """Test that non-existent endpoints return 404."""
    response = await client.get("/api/nonexistent")
    assert response.status_code == 404