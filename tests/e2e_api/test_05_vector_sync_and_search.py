"""
🧪 Test Package 05: Vector Sync & Search - Vector Database Integration

Tests vector synchronization and semantic search functionality.
Tests endpoints: /api/vector-sync/collections/{name}/sync, /api/vector-sync/collections/{name}/status,
/api/vector-sync/collections/statuses, /api/vector-sync/search
"""
import pytest
import pytest_asyncio
import httpx
import uuid
import asyncio


@pytest_asyncio.fixture
async def test_collection_with_content(client: httpx.AsyncClient, cleanup_collections):
    """Create a test collection with content for vector sync testing."""
    collection_name = f"vector_test_{uuid.uuid4().hex[:6]}"
    
    # Create collection
    response = await client.post("/api/file-collections", json={
        "name": collection_name,
        "description": "Test collection for vector sync"
    })
    
    assert response.status_code == 200
    collection_name = response.json()["data"]["name"]
    cleanup_collections(collection_name)
    
    # Add test content
    test_files = [
        {
            "filename": "ai_overview.md",
            "content": "# Artificial Intelligence Overview\n\nArtificial Intelligence (AI) is a branch of computer science that aims to create intelligent machines. Machine learning is a subset of AI that focuses on algorithms that can learn from data."
        },
        {
            "filename": "machine_learning.md", 
            "content": "# Machine Learning Fundamentals\n\nMachine learning algorithms can be categorized into supervised learning, unsupervised learning, and reinforcement learning. Neural networks are a popular approach in modern machine learning."
        },
        {
            "filename": "python_basics.md",
            "content": "# Python Programming\n\nPython is a high-level programming language known for its simplicity and readability. It's widely used in data science, web development, and automation."
        }
    ]
    
    for file_data in test_files:
        file_response = await client.post(f"/api/file-collections/{collection_name}/files", json=file_data)
        assert file_response.status_code == 200
    
    return {"collection_name": collection_name}


@pytest.mark.asyncio
async def test_sync_collection_to_vectors(client: httpx.AsyncClient, test_collection_with_content):
    """Test syncing collection content to vector database."""
    collection_name = test_collection_with_content["collection_name"]
    
    response = await client.post(f"/api/vector-sync/collections/{collection_name}/sync", json={
        "force_reprocess": False,
        "chunking_strategy": "sentence"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "sync_result" in data
    
    sync_result = data["sync_result"]
    assert "collection_name" in sync_result
    assert sync_result["collection_name"] == collection_name
    assert "vector_count" in sync_result
    assert sync_result["vector_count"] > 0  # Should have created some vectors


@pytest.mark.asyncio
async def test_get_collection_sync_status(client: httpx.AsyncClient, test_collection_with_content):
    """Test getting sync status for a specific collection."""
    collection_name = test_collection_with_content["collection_name"]
    
    # First sync the collection
    sync_response = await client.post(f"/api/vector-sync/collections/{collection_name}/sync", json={
        "force_reprocess": False
    })
    assert sync_response.status_code == 200
    
    # Get sync status
    status_response = await client.get(f"/api/vector-sync/collections/{collection_name}/status")
    
    assert status_response.status_code == 200
    data = status_response.json()
    assert data["success"] is True
    assert "status" in data
    
    status = data["status"]
    assert status["collection_name"] == collection_name
    assert "sync_status" in status
    assert "vector_count" in status
    assert "last_sync" in status
    assert status["vector_count"] > 0


@pytest.mark.asyncio
async def test_get_all_sync_statuses(client: httpx.AsyncClient, test_collection_with_content):
    """Test getting sync status for all collections."""
    collection_name = test_collection_with_content["collection_name"]
    
    # Sync the collection first
    sync_response = await client.post(f"/api/vector-sync/collections/{collection_name}/sync", json={
        "force_reprocess": False
    })
    assert sync_response.status_code == 200
    
    # Get all statuses
    response = await client.get("/api/vector-sync/collections/statuses")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "statuses" in data
    assert isinstance(data["statuses"], dict)
    
    # Our collection should be in the statuses
    statuses = data["statuses"]
    assert collection_name in statuses
    
    collection_status = statuses[collection_name]
    assert collection_status["collection_name"] == collection_name
    assert "sync_status" in collection_status
    assert "vector_count" in collection_status


@pytest.mark.asyncio
async def test_vector_search(client: httpx.AsyncClient, test_collection_with_content):
    """Test semantic search across vector database."""
    collection_name = test_collection_with_content["collection_name"]
    
    # First sync the collection
    sync_response = await client.post(f"/api/vector-sync/collections/{collection_name}/sync", json={
        "force_reprocess": False
    })
    assert sync_response.status_code == 200
    
    # Wait longer for ChromaDB indexing to complete
    await asyncio.sleep(5)
    
    # Test search for AI-related content
    search_response = await client.post("/api/vector-sync/search", json={
        "query": "artificial intelligence and machine learning",
        "collection_name": collection_name,
        "limit": 5,
        "similarity_threshold": 0.15  # Realistic threshold based on observed scores
    })
    
    assert search_response.status_code == 200
    data = search_response.json()
    assert data["success"] is True
    assert "results" in data
    
    results = data["results"]
    assert isinstance(results, list)
    assert len(results) > 0  # Should find some relevant content
    
    # Check result structure
    for result in results:
        assert "content" in result
        assert "similarity_score" in result
        assert "metadata" in result
        assert result["similarity_score"] >= 0.15  # Above our threshold


@pytest.mark.asyncio
async def test_vector_search_cross_collection(client: httpx.AsyncClient, test_collection_with_content):
    """Test search across all collections."""
    # Sync our test collection
    collection_name = test_collection_with_content["collection_name"]
    sync_response = await client.post(f"/api/vector-sync/collections/{collection_name}/sync", json={
        "force_reprocess": False
    })
    assert sync_response.status_code == 200
    
    # Wait for indexing
    await asyncio.sleep(2)
    
    # Search without specifying collection (searches all)
    search_response = await client.post("/api/vector-sync/search", json={
        "query": "programming languages and python",
        "limit": 10,
        "similarity_threshold": 0.2
    })
    
    assert search_response.status_code == 200
    data = search_response.json()
    assert data["success"] is True
    assert "results" in data


@pytest.mark.asyncio
async def test_force_reprocess_sync(client: httpx.AsyncClient, test_collection_with_content):
    """Test force reprocessing during sync."""
    collection_name = test_collection_with_content["collection_name"]
    
    # First normal sync
    sync_response1 = await client.post(f"/api/vector-sync/collections/{collection_name}/sync", json={
        "force_reprocess": False
    })
    assert sync_response1.status_code == 200
    
    # Force reprocess sync
    sync_response2 = await client.post(f"/api/vector-sync/collections/{collection_name}/sync", json={
        "force_reprocess": True
    })
    assert sync_response2.status_code == 200
    
    # Should still have vectors (might be same count if content unchanged)
    reprocessed_vector_count = sync_response2.json()["sync_result"]["vector_count"]
    assert reprocessed_vector_count > 0


@pytest.mark.asyncio
async def test_sync_empty_collection(client: httpx.AsyncClient, cleanup_collections):
    """Test syncing an empty collection."""
    collection_name = f"empty_test_{uuid.uuid4().hex[:6]}"
    
    # Create empty collection
    response = await client.post("/api/file-collections", json={
        "name": collection_name,
        "description": "Empty collection for sync testing"
    })
    assert response.status_code == 200
    collection_name = response.json()["data"]["name"]
    cleanup_collections(collection_name)
    
    # Try to sync empty collection
    sync_response = await client.post(f"/api/vector-sync/collections/{collection_name}/sync", json={
        "force_reprocess": False
    })
    
    assert sync_response.status_code == 200
    data = sync_response.json()
    assert data["success"] is True
    
    # Should have 0 vectors for empty collection
    sync_result = data["sync_result"]
    assert sync_result["vector_count"] == 0


@pytest.mark.asyncio
async def test_sync_nonexistent_collection(client: httpx.AsyncClient):
    """Test syncing non-existent collection returns proper error."""
    fake_collection_name = f"nonexistent_{uuid.uuid4().hex[:6]}"
    
    response = await client.post(f"/api/vector-sync/collections/{fake_collection_name}/sync", json={
        "force_reprocess": False
    })
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    error = data["detail"]["error"]
    assert error["code"] == "COLLECTION_NOT_FOUND"
    assert "does not exist" in error["message"]


@pytest.mark.asyncio
async def test_get_status_nonexistent_collection(client: httpx.AsyncClient):
    """Test getting status of non-existent collection returns proper error."""
    fake_collection_name = f"nonexistent_{uuid.uuid4().hex[:6]}"
    
    response = await client.get(f"/api/vector-sync/collections/{fake_collection_name}/status")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    error = data["detail"]["error"]
    assert error["code"] == "COLLECTION_NOT_FOUND"
    assert "does not exist" in error["message"]


@pytest.mark.asyncio
async def test_search_with_invalid_parameters(client: httpx.AsyncClient):
    """Test search with various invalid parameters."""
    # Empty query
    response1 = await client.post("/api/vector-sync/search", json={
        "query": "",
        "limit": 5
    })
    assert response1.status_code in [400, 422]  # Should return validation error
    
    # Negative limit
    response2 = await client.post("/api/vector-sync/search", json={
        "query": "test query",
        "limit": -1
    })
    assert response2.status_code in [400, 422]
    
    # Invalid similarity threshold
    response3 = await client.post("/api/vector-sync/search", json={
        "query": "test query",
        "similarity_threshold": 1.5  # Should be between 0 and 1
    })
    assert response3.status_code in [400, 422]


@pytest.mark.asyncio
async def test_complete_vector_workflow(client: httpx.AsyncClient, test_collection_with_content):
    """Test complete vector sync and search workflow."""
    collection_name = test_collection_with_content["collection_name"]
    
    # Step 1: Check initial status (should be never_synced)
    initial_status_response = await client.get(f"/api/vector-sync/collections/{collection_name}/status")
    assert initial_status_response.status_code == 200
    
    # Step 2: Sync collection
    sync_response = await client.post(f"/api/vector-sync/collections/{collection_name}/sync", json={
        "force_reprocess": False,
        "chunking_strategy": "sentence"
    })
    assert sync_response.status_code == 200
    sync_result = sync_response.json()["sync_result"]
    assert sync_result["vector_count"] > 0
    
    # Step 3: Check status after sync (should be in_sync)
    synced_status_response = await client.get(f"/api/vector-sync/collections/{collection_name}/status")
    assert synced_status_response.status_code == 200
    synced_status = synced_status_response.json()["status"]
    assert synced_status["sync_status"] == "in_sync"
    assert synced_status["vector_count"] == sync_result["vector_count"]
    
    # Step 4: Verify in all statuses list
    all_statuses_response = await client.get("/api/vector-sync/collections/statuses")
    assert all_statuses_response.status_code == 200
    all_statuses = all_statuses_response.json()["statuses"]
    assert collection_name in all_statuses
    assert all_statuses[collection_name]["sync_status"] == "in_sync"
    
    # Step 5: Search for content
    await asyncio.sleep(2)  # Allow indexing to complete
    search_response = await client.post("/api/vector-sync/search", json={
        "query": "machine learning algorithms",
        "collection_name": collection_name,
        "limit": 3,
        "similarity_threshold": 0.15  # Realistic threshold based on observed scores
    })
    assert search_response.status_code == 200
    search_results = search_response.json()["results"]
    assert len(search_results) > 0
    
    # Step 6: Verify search results contain relevant content
    found_ml_content = False
    for result in search_results:
        if "machine learning" in result["content"].lower():
            found_ml_content = True
            break
    assert found_ml_content, "Search should find machine learning related content"