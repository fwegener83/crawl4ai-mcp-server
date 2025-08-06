"""
E2E API Tests Configuration

This module provides test configuration and fixtures for API endpoint testing.
"""
import pytest
import pytest_asyncio
import httpx
import asyncio
from typing import AsyncGenerator

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 30.0


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Async HTTP client for API testing."""
    async with httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=TEST_TIMEOUT,
        follow_redirects=True
    ) as client:
        yield client


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_collection_name() -> str:
    """Generate unique collection name for testing."""
    import uuid
    return f"test_col_{uuid.uuid4().hex[:8]}"


@pytest_asyncio.fixture
async def cleanup_collections():
    """Fixture to track and cleanup test collections."""
    collections_to_cleanup = []
    
    def track_collection(collection_name: str):
        collections_to_cleanup.append(collection_name)
    
    yield track_collection
    
    # Cleanup after test
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=TEST_TIMEOUT) as client:
        for collection_name in collections_to_cleanup:
            try:
                await client.delete(f"/api/file-collections/{collection_name}")
            except Exception:
                pass  # Ignore cleanup errors