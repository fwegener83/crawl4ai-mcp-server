"""
🧪 Test Package 04: Web Crawling Flow - Web Content Extraction and Storage

Tests web crawling endpoints and page storage functionality.
Tests endpoints: /api/extract, /api/deep-crawl, /api/link-preview, /api/crawl/single/{collection_id}
"""
import pytest
import httpx
import uuid
from unittest.mock import patch


@pytest.fixture
async def test_collection_for_crawling(client: httpx.AsyncClient, cleanup_collections):
    """Create a test collection for crawling operations."""
    collection_name = f"crawl_test_{uuid.uuid4().hex[:6]}"
    response = await client.post("/api/file-collections", json={
        "name": collection_name,
        "description": "Test collection for web crawling"
    })
    
    assert response.status_code == 200
    collection_id = response.json()["collection"]["id"]
    cleanup_collections(collection_id)
    
    return collection_id


@pytest.mark.asyncio
async def test_single_page_extract(client: httpx.AsyncClient):
    """Test single page content extraction."""
    test_url = "https://example.com"
    
    response = await client.post("/api/extract", json={
        "url": test_url,
        "extraction_strategy": "NoExtractionStrategy"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "result" in data
    
    result = data["result"]
    assert "markdown" in result
    assert "url" in result
    assert result["url"] == test_url


@pytest.mark.asyncio
async def test_link_preview(client: httpx.AsyncClient):
    """Test link preview functionality."""
    test_domain = "https://example.com"
    
    response = await client.post("/api/link-preview", json={
        "domain_url": test_domain,
        "include_external": False
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "links" in data
    assert isinstance(data["links"], list)


@pytest.mark.asyncio
async def test_deep_crawl(client: httpx.AsyncClient):
    """Test deep domain crawling."""
    test_domain = "https://example.com"
    
    response = await client.post("/api/deep-crawl", json={
        "domain_url": test_domain,
        "max_pages": 2,
        "max_depth": 1,
        "crawl_strategy": "bfs",
        "include_external": False
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "results" in data
    assert isinstance(data["results"], list)
    
    # Check that we got some results
    results = data["results"]
    assert len(results) > 0
    
    # Verify result structure
    for result in results:
        assert "url" in result
        assert "markdown" in result
        assert "success" in result


@pytest.mark.asyncio
async def test_crawl_single_page_to_collection(client: httpx.AsyncClient, test_collection_for_crawling: str):
    """Test crawling single page and saving to collection."""
    test_url = "https://example.com"
    
    response = await client.post(f"/api/crawl/single/{test_collection_for_crawling}", json={
        "url": test_url
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "file" in data
    
    file_info = data["file"]
    assert "filename" in file_info
    assert file_info["collection_id"] == test_collection_for_crawling
    
    # Verify the file was actually created in the collection
    files_response = await client.get(f"/api/file-collections/{test_collection_for_crawling}/files")
    assert files_response.status_code == 200
    files = files_response.json()["files"]
    assert any(f["filename"] == file_info["filename"] for f in files)
    
    # Verify file content
    file_response = await client.get(f"/api/file-collections/{test_collection_for_crawling}/files/{file_info['filename']}")
    assert file_response.status_code == 200
    file_data = file_response.json()["file"]
    assert len(file_data["content"]) > 0  # Should have some content


@pytest.mark.asyncio
async def test_crawl_single_invalid_url(client: httpx.AsyncClient, test_collection_for_crawling: str):
    """Test crawling invalid URL returns proper error."""
    invalid_url = "not-a-valid-url"
    
    response = await client.post(f"/api/crawl/single/{test_collection_for_crawling}", json={
        "url": invalid_url
    })
    
    # Should return an error for invalid URL
    assert response.status_code in [400, 422]  # Bad request or validation error


@pytest.mark.asyncio
async def test_crawl_to_nonexistent_collection(client: httpx.AsyncClient):
    """Test crawling to non-existent collection returns 404."""
    fake_collection_id = f"fake_{uuid.uuid4().hex[:6]}"
    test_url = "https://example.com"
    
    response = await client.post(f"/api/crawl/single/{fake_collection_id}", json={
        "url": test_url
    })
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_extract_with_different_strategies(client: httpx.AsyncClient):
    """Test extraction with different strategies."""
    test_url = "https://example.com"
    
    strategies = ["NoExtractionStrategy", "LLMExtractionStrategy", "CosineStrategy"]
    
    for strategy in strategies:
        response = await client.post("/api/extract", json={
            "url": test_url,
            "extraction_strategy": strategy
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "result" in data


@pytest.mark.asyncio
async def test_deep_crawl_with_parameters(client: httpx.AsyncClient):
    """Test deep crawl with various parameters."""
    test_domain = "https://example.com"
    
    response = await client.post("/api/deep-crawl", json={
        "domain_url": test_domain,
        "max_pages": 3,
        "max_depth": 2,
        "crawl_strategy": "dfs",
        "include_external": True,
        "url_patterns": ["*/about*", "*/contact*"],
        "exclude_patterns": ["*/admin*", "*/private*"]
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "results" in data


@pytest.mark.asyncio
async def test_web_crawling_error_handling(client: httpx.AsyncClient):
    """Test error handling in web crawling operations."""
    # Test with unreachable URL
    unreachable_url = "https://this-domain-definitely-does-not-exist-12345.com"
    
    response = await client.post("/api/extract", json={
        "url": unreachable_url,
        "extraction_strategy": "NoExtractionStrategy"
    })
    
    # Should handle the error gracefully
    assert response.status_code in [200, 400, 500]  # Various possible error responses
    
    if response.status_code == 200:
        # If successful, check for error indication in response
        data = response.json()
        if not data.get("success", True):
            assert "error" in data or "message" in data


@pytest.mark.asyncio
async def test_complete_crawling_workflow(client: httpx.AsyncClient, test_collection_for_crawling: str):
    """Test complete crawling workflow from preview to storage."""
    test_domain = "https://example.com"
    
    # Step 1: Preview links
    preview_response = await client.post("/api/link-preview", json={
        "domain_url": test_domain,
        "include_external": False
    })
    assert preview_response.status_code == 200
    
    # Step 2: Extract single page
    extract_response = await client.post("/api/extract", json={
        "url": test_domain,
        "extraction_strategy": "NoExtractionStrategy"
    })
    assert extract_response.status_code == 200
    
    # Step 3: Save to collection
    crawl_response = await client.post(f"/api/crawl/single/{test_collection_for_crawling}", json={
        "url": test_domain
    })
    assert crawl_response.status_code == 200
    
    # Step 4: Verify file was created
    files_response = await client.get(f"/api/file-collections/{test_collection_for_crawling}/files")
    assert files_response.status_code == 200
    files = files_response.json()["files"]
    assert len(files) > 0
    
    # Step 5: Verify content is accessible
    filename = files[0]["filename"]
    content_response = await client.get(f"/api/file-collections/{test_collection_for_crawling}/files/{filename}")
    assert content_response.status_code == 200
    file_data = content_response.json()["file"]
    assert len(file_data["content"]) > 0