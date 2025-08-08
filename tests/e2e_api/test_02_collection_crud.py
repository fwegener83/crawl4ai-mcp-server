"""
🧪 Test Package 02: Collection CRUD - Collection Management Flow

Tests complete CRUD operations for file collections.
Tests endpoints: GET /api/file-collections, POST /api/file-collections, 
GET /api/file-collections/{id}, DELETE /api/file-collections/{id}
"""
import pytest
import httpx
import uuid


@pytest.mark.asyncio
async def test_create_collection(client: httpx.AsyncClient):
    """Test creating a new collection."""
    collection_name = f"test_col_{uuid.uuid4().hex[:6]}"
    
    response = await client.post("/api/file-collections", json={
        "name": collection_name,
        "description": "Test collection for CRUD operations"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    
    collection = data["data"]
    assert collection["name"] == collection_name
    assert collection["description"] == "Test collection for CRUD operations"
    
    return collection["name"]  # Collection name is the identifier


@pytest.mark.asyncio
async def test_list_collections(client: httpx.AsyncClient):
    """Test listing all collections."""
    response = await client.get("/api/file-collections")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "collections" in data
    assert isinstance(data["collections"], list)


@pytest.mark.asyncio
async def test_get_collection_by_id(client: httpx.AsyncClient, cleanup_collections):
    """Test getting a specific collection by ID."""
    # First create a collection
    collection_name = f"test_get_{uuid.uuid4().hex[:6]}"
    create_response = await client.post("/api/file-collections", json={
        "name": collection_name,
        "description": "Test collection for get operation"
    })
    
    assert create_response.status_code == 200
    collection_name = create_response.json()["data"]["name"]
    cleanup_collections(collection_name)
    
    # Then get it by name
    get_response = await client.get(f"/api/file-collections/{collection_name}")
    
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["success"] is True
    assert "data" in data
    
    collection = data["data"]
    assert collection["name"] == collection_name
    assert collection["description"] == "Test collection for get operation"


@pytest.mark.asyncio
async def test_delete_collection(client: httpx.AsyncClient):
    """Test deleting a collection."""
    # First create a collection
    collection_name = f"test_delete_{uuid.uuid4().hex[:6]}"
    create_response = await client.post("/api/file-collections", json={
        "name": collection_name,
        "description": "Test collection for deletion"
    })
    
    assert create_response.status_code == 200
    collection_name = create_response.json()["data"]["name"]
    
    # Delete the collection
    delete_response = await client.delete(f"/api/file-collections/{collection_name}")
    
    assert delete_response.status_code == 200
    data = delete_response.json()
    assert data["success"] is True
    
    # Verify it's gone
    get_response = await client.get(f"/api/file-collections/{collection_name}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_full_collection_crud_flow(client: httpx.AsyncClient):
    """Test complete CRUD flow for collections."""
    collection_name = f"crud_flow_{uuid.uuid4().hex[:6]}"
    
    # CREATE
    create_response = await client.post("/api/file-collections", json={
        "name": collection_name,
        "description": "Full CRUD flow test"
    })
    assert create_response.status_code == 200
    collection_name = create_response.json()["data"]["name"]
    
    # READ - Get by name
    get_response = await client.get(f"/api/file-collections/{collection_name}")
    assert get_response.status_code == 200
    collection = get_response.json()["data"]
    assert collection["name"] == collection_name
    
    # READ - List (verify it's in the list)
    list_response = await client.get("/api/file-collections")
    assert list_response.status_code == 200
    collections = list_response.json()["collections"]
    assert any(col["name"] == collection_name for col in collections)
    
    # DELETE
    delete_response = await client.delete(f"/api/file-collections/{collection_name}")
    assert delete_response.status_code == 200
    
    # VERIFY DELETION
    verify_response = await client.get(f"/api/file-collections/{collection_name}")
    assert verify_response.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_collection(client: httpx.AsyncClient):
    """Test getting a non-existent collection returns 404."""
    fake_name = f"nonexistent_{uuid.uuid4().hex[:6]}"
    response = await client.get(f"/api/file-collections/{fake_name}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_collection(client: httpx.AsyncClient):
    """Test deleting a non-existent collection returns proper error."""
    fake_name = f"nonexistent_{uuid.uuid4().hex[:6]}"
    response = await client.delete(f"/api/file-collections/{fake_name}")
    assert response.status_code == 404  # RESTful: 404 for collection not found


@pytest.mark.asyncio
async def test_create_collection_with_invalid_data(client: httpx.AsyncClient):
    """Test creating collection with invalid data."""
    # Test missing name
    response = await client.post("/api/file-collections", json={
        "description": "Missing name field"
    })
    assert response.status_code == 400  # Bad request for missing required field
    
    # Test empty name
    response = await client.post("/api/file-collections", json={
        "name": "",
        "description": "Empty name"
    })
    assert response.status_code in [400, 422]  # Bad request or validation error