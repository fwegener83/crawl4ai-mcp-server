"""
E2E API Tests Configuration

This module provides test configuration and fixtures for API endpoint testing.
E2E API tests are disabled in CI environments but available for local development.
"""
import pytest
import pytest_asyncio
import httpx
import asyncio
import uvicorn
import threading
import time
import os
import sys
from typing import AsyncGenerator

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Skip all E2E API tests in CI environment  
if os.getenv("CI"):
    pytestmark = pytest.mark.skip(reason="E2E API tests disabled in CI environment - run locally for full API validation")

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 30.0


@pytest.fixture(scope="session")
def test_server():
    """Start the unified server for testing (local development only)."""
    # Skip server startup in CI environment
    if os.getenv("CI"):
        pytest.skip("E2E API tests disabled in CI environment - run locally for full API validation")
    
    # Check if server is already running
    try:
        import httpx
        with httpx.Client(timeout=2.0) as client:
            response = client.get(f"{BASE_URL}/api/health")
            if response.status_code == 200:
                # Server is already running
                yield
                return
    except:
        pass
    
    # Start UnifiedServer for local E2E testing
    from unified_server import UnifiedServer
    
    server_instance = UnifiedServer()
    app = server_instance.setup_http_app()
    
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="warning",
        access_log=False
    )
    server = uvicorn.Server(config)
    
    def run_server():
        try:
            asyncio.set_event_loop(asyncio.new_event_loop())
            server.run()
        except Exception as e:
            print(f"Server error: {e}")
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for server to be ready
    max_attempts = 30
    for _ in range(max_attempts):
        try:
            import httpx
            with httpx.Client(timeout=2.0) as client:
                response = client.get(f"{BASE_URL}/api/health")
                if response.status_code == 200:
                    break
        except:
            pass
        time.sleep(1)
    else:
        raise RuntimeError("Test server failed to start")
    
    yield
    
    # Cleanup happens automatically when test session ends


@pytest_asyncio.fixture
async def client(test_server) -> AsyncGenerator[httpx.AsyncClient, None]:
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