"""
🧪 Test Package 03: File CRUD in Collections - File Management Flow

Tests complete CRUD operations for files within collections.
Tests endpoints: GET /api/file-collections/{id}/files, POST /api/file-collections/{id}/files,
GET /api/file-collections/{id}/files/{filename}, PUT /api/file-collections/{id}/files/{filename},
DELETE /api/file-collections/{id}/files/{filename}
"""
import pytest
import pytest_asyncio
import httpx
import uuid


@pytest_asyncio.fixture
async def test_collection(client: httpx.AsyncClient, cleanup_collections):
    """Create a test collection for file operations."""
    collection_name = f"file_test_{uuid.uuid4().hex[:6]}"
    response = await client.post("/api/file-collections", json={
        "name": collection_name,
        "description": "Test collection for file operations"
    })
    
    assert response.status_code == 200
    collection_name = response.json()["collection"]["name"]
    cleanup_collections(collection_name)
    
    return collection_name


@pytest.mark.asyncio
async def test_create_file_in_collection(client: httpx.AsyncClient, test_collection: str):
    """Test creating a file in a collection."""
    filename = f"test_file_{uuid.uuid4().hex[:6]}.md"
    content = "# Test File\n\nThis is a test markdown file."
    
    response = await client.post(f"/api/file-collections/{test_collection}/files", json={
        "filename": filename,
        "content": content
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    
    file_info = data["data"]
    assert file_info["path"] == filename  # API uses "path" instead of "filename"
    # Collection name is the identifier, not separate collection_id


@pytest.mark.asyncio
async def test_list_files_in_collection(client: httpx.AsyncClient, test_collection: str):
    """Test listing files in a collection."""
    # First create a file
    filename = f"list_test_{uuid.uuid4().hex[:6]}.md"
    await client.post(f"/api/file-collections/{test_collection}/files", json={
        "filename": filename,
        "content": "Test content for listing"
    })
    
    # Then list files
    response = await client.get(f"/api/file-collections/{test_collection}/files")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "files" in data["data"]
    assert isinstance(data["data"]["files"], list)
    
    # Find our created file
    files = data["data"]["files"]
    assert any(f["path"] == filename for f in files)


@pytest.mark.asyncio
async def test_get_file_content(client: httpx.AsyncClient, test_collection: str):
    """Test getting specific file content."""
    filename = f"content_test_{uuid.uuid4().hex[:6]}.md"
    original_content = "# Test Content\n\nThis is the original content."
    
    # Create file
    create_response = await client.post(f"/api/file-collections/{test_collection}/files", json={
        "filename": filename,
        "content": original_content
    })
    assert create_response.status_code == 200
    
    # Get file content
    get_response = await client.get(f"/api/file-collections/{test_collection}/files/{filename}")
    
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["success"] is True
    assert "data" in data
    
    file_data = data["data"]
    assert file_data["content"] == original_content


@pytest.mark.asyncio
async def test_update_file_content(client: httpx.AsyncClient, test_collection: str):
    """Test updating file content."""
    filename = f"update_test_{uuid.uuid4().hex[:6]}.md"
    original_content = "# Original Content"
    updated_content = "# Updated Content\n\nThis content has been updated."
    
    # Create file
    create_response = await client.post(f"/api/file-collections/{test_collection}/files", json={
        "filename": filename,
        "content": original_content
    })
    assert create_response.status_code == 200
    
    # Update file
    update_response = await client.put(f"/api/file-collections/{test_collection}/files/{filename}", json={
        "content": updated_content
    })
    
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["success"] is True
    
    # Verify update
    get_response = await client.get(f"/api/file-collections/{test_collection}/files/{filename}")
    assert get_response.status_code == 200
    file_data = get_response.json()["data"]
    assert file_data["content"] == updated_content


@pytest.mark.asyncio
async def test_delete_file(client: httpx.AsyncClient, test_collection: str):
    """Test deleting a file from collection."""
    filename = f"delete_test_{uuid.uuid4().hex[:6]}.md"
    
    # Create file
    create_response = await client.post(f"/api/file-collections/{test_collection}/files", json={
        "filename": filename,
        "content": "Content to be deleted"
    })
    assert create_response.status_code == 200
    
    # Delete file
    delete_response = await client.delete(f"/api/file-collections/{test_collection}/files/{filename}")
    
    assert delete_response.status_code == 200
    data = delete_response.json()
    assert data["success"] is True
    
    # Verify deletion
    get_response = await client.get(f"/api/file-collections/{test_collection}/files/{filename}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_full_file_crud_flow(client: httpx.AsyncClient, test_collection: str):
    """Test complete CRUD flow for files in collection."""
    filename = f"crud_flow_{uuid.uuid4().hex[:6]}.md"
    original_content = "# CRUD Test\n\nOriginal content."
    updated_content = "# CRUD Test\n\nUpdated content."
    
    # CREATE
    create_response = await client.post(f"/api/file-collections/{test_collection}/files", json={
        "filename": filename,
        "content": original_content
    })
    assert create_response.status_code == 200
    
    # READ - Get specific file
    get_response = await client.get(f"/api/file-collections/{test_collection}/files/{filename}")
    assert get_response.status_code == 200
    file_data = get_response.json()["data"]
    assert file_data["content"] == original_content
    
    # READ - List files (verify it's in the list)
    list_response = await client.get(f"/api/file-collections/{test_collection}/files")
    assert list_response.status_code == 200
    files = list_response.json()["data"]["files"]
    assert any(f["path"] == filename for f in files)
    
    # UPDATE
    update_response = await client.put(f"/api/file-collections/{test_collection}/files/{filename}", json={
        "content": updated_content
    })
    assert update_response.status_code == 200
    
    # VERIFY UPDATE
    verify_response = await client.get(f"/api/file-collections/{test_collection}/files/{filename}")
    assert verify_response.status_code == 200
    assert verify_response.json()["data"]["content"] == updated_content
    
    # DELETE
    delete_response = await client.delete(f"/api/file-collections/{test_collection}/files/{filename}")
    assert delete_response.status_code == 200
    
    # VERIFY DELETION
    final_response = await client.get(f"/api/file-collections/{test_collection}/files/{filename}")
    assert final_response.status_code == 404


@pytest.mark.asyncio
async def test_file_operations_with_invalid_collection(client: httpx.AsyncClient):
    """Test file operations with non-existent collection."""
    fake_collection_id = f"fake_{uuid.uuid4().hex[:6]}"
    filename = "test.md"
    
    # Test create file in non-existent collection
    create_response = await client.post(f"/api/file-collections/{fake_collection_id}/files", json={
        "filename": filename,
        "content": "Test content"
    })
    assert create_response.status_code == 500  # API returns 500 for collection not found
    
    # Test list files in non-existent collection
    list_response = await client.get(f"/api/file-collections/{fake_collection_id}/files")
    assert list_response.status_code == 500  # API returns 500 for collection not found


@pytest.mark.asyncio
async def test_get_nonexistent_file(client: httpx.AsyncClient, test_collection: str):
    """Test getting a non-existent file returns 404."""
    fake_filename = f"nonexistent_{uuid.uuid4().hex[:6]}.md"
    response = await client.get(f"/api/file-collections/{test_collection}/files/{fake_filename}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_file_with_invalid_extension(client: httpx.AsyncClient, test_collection: str):
    """Test creating file with invalid extension."""
    filename = f"test_{uuid.uuid4().hex[:6]}.exe"  # Invalid extension
    
    response = await client.post(f"/api/file-collections/{test_collection}/files", json={
        "filename": filename,
        "content": "This should not be allowed"
    })
    
    # Should return error for invalid file extension
    assert response.status_code == 500  # API returns 500 for invalid extension


@pytest.mark.asyncio
async def test_create_file_with_empty_content(client: httpx.AsyncClient, test_collection: str):
    """Test creating file with empty content."""
    filename = f"empty_{uuid.uuid4().hex[:6]}.md"
    
    response = await client.post(f"/api/file-collections/{test_collection}/files", json={
        "filename": filename,
        "content": ""
    })
    
    assert response.status_code == 400  # API returns 400 for empty content
    # Note: API doesn't allow empty content