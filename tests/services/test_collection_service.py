"""
Tests for CollectionService.

Tests the protocol-agnostic collection management business logic
with mocked dependencies for isolation.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json
from pathlib import Path

from services.collection_service import CollectionService
from services.interfaces import CollectionInfo, FileInfo


class TestCollectionService:
    """Test suite for CollectionService."""
    
    @pytest.fixture
    def mock_collection_manager(self):
        """Create a mock collection manager."""
        return AsyncMock()
    
    @pytest.fixture
    def service(self, mock_collection_manager):
        """Create a CollectionService instance for testing."""
        with patch('services.collection_service.create_collection_manager') as mock_create:
            mock_create.return_value = mock_collection_manager
            service = CollectionService()
            service.collection_manager = mock_collection_manager
            return service
    
    @pytest.mark.asyncio
    async def test_list_collections_success(self, service, mock_collection_manager):
        """Test successful collection listing."""
        mock_result = {
            "success": True,
            "collections": [
                {
                    "name": "test-collection",
                    "description": "Test collection",
                    "file_count": 5,
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-05T00:00:00Z",
                    "metadata": {"type": "web-content"}
                },
                {
                    "name": "docs-collection",
                    "description": "Documentation",
                    "file_count": 10,
                    "created_at": "2025-01-02T00:00:00Z",
                    "updated_at": "2025-01-04T00:00:00Z",
                    "metadata": {}
                }
            ]
        }
        
        mock_collection_manager.list_collections.return_value = json.dumps(mock_result)
        
        results = await service.list_collections()
        
        assert len(results) == 2
        
        # Check first collection
        col1 = results[0]
        assert isinstance(col1, CollectionInfo)
        assert col1.name == "test-collection"
        assert col1.description == "Test collection"
        assert col1.file_count == 5
        assert col1.created_at == "2025-01-01T00:00:00Z"
        assert col1.updated_at == "2025-01-05T00:00:00Z"
        assert col1.metadata == {"type": "web-content"}
        
        # Check second collection
        col2 = results[1]
        assert col2.name == "docs-collection"
        assert col2.description == "Documentation"
        assert col2.file_count == 10
        
        mock_collection_manager.list_collections.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_list_collections_failure(self, service, mock_collection_manager):
        """Test collection listing failure."""
        mock_result = {"success": False}
        mock_collection_manager.list_collections.return_value = json.dumps(mock_result)
        
        results = await service.list_collections()
        
        assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_list_collections_exception(self, service, mock_collection_manager):
        """Test collection listing with exception."""
        mock_collection_manager.list_collections.side_effect = Exception("Database error")
        
        results = await service.list_collections()
        
        assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_create_collection_success(self, service, mock_collection_manager):
        """Test successful collection creation."""
        mock_result = {
            "success": True,
            "collection": {
                "name": "new-collection",
                "description": "A new collection",
                "file_count": 0,
                "created_at": "2025-01-05T23:00:00Z",
                "updated_at": "2025-01-05T23:00:00Z",
                "metadata": {}
            }
        }
        
        mock_collection_manager.create_collection.return_value = json.dumps(mock_result)
        
        result = await service.create_collection("new-collection", "A new collection")
        
        assert isinstance(result, CollectionInfo)
        assert result.name == "new-collection"
        assert result.description == "A new collection"
        assert result.file_count == 0
        assert result.created_at == "2025-01-05T23:00:00Z"
        assert result.updated_at == "2025-01-05T23:00:00Z"
        
        mock_collection_manager.create_collection.assert_called_once_with("new-collection", "A new collection")
    
    @pytest.mark.asyncio
    async def test_create_collection_failure(self, service, mock_collection_manager):
        """Test collection creation failure."""
        mock_result = {
            "success": False,
            "error": "Collection already exists"
        }
        
        mock_collection_manager.create_collection.return_value = json.dumps(mock_result)
        
        with pytest.raises(Exception) as exc_info:
            await service.create_collection("existing-collection")
        
        assert "Collection already exists" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_collection_success(self, service, mock_collection_manager):
        """Test successful collection retrieval."""
        mock_result = {
            "success": True,
            "collection": {
                "name": "test-collection",
                "description": "Test collection",
                "file_count": 3,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-05T00:00:00Z",
                "metadata": {"type": "test"}
            }
        }
        
        mock_collection_manager.get_collection_info.return_value = json.dumps(mock_result)
        
        result = await service.get_collection("test-collection")
        
        assert isinstance(result, CollectionInfo)
        assert result.name == "test-collection"
        assert result.description == "Test collection"
        assert result.file_count == 3
        
        mock_collection_manager.get_collection_info.assert_called_once_with("test-collection")
    
    @pytest.mark.asyncio
    async def test_get_collection_not_found(self, service, mock_collection_manager):
        """Test collection retrieval when collection not found."""
        mock_result = {"success": False, "error": "Collection not found"}
        mock_collection_manager.get_collection_info.return_value = json.dumps(mock_result)
        
        with pytest.raises(Exception) as exc_info:
            await service.get_collection("nonexistent-collection")
        
        assert "Collection not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_delete_collection_success(self, service, mock_collection_manager):
        """Test successful collection deletion."""
        mock_result = {
            "success": True,
            "deleted_files": 5
        }
        
        mock_collection_manager.delete_collection.return_value = json.dumps(mock_result)
        
        result = await service.delete_collection("test-collection")
        
        assert result["success"] is True
        assert result["message"] == "Collection test-collection deleted successfully"
        assert result["deleted_files"] == 5
        
        mock_collection_manager.delete_collection.assert_called_once_with("test-collection")
    
    @pytest.mark.asyncio
    async def test_list_files_success(self, service, mock_collection_manager):
        """Test successful file listing."""
        mock_result = {
            "success": True,
            "files": ["document1.md", "document2.txt", "subfolder/document3.md"]
        }
        
        mock_collection_manager.list_files.return_value = json.dumps(mock_result)
        
        result = await service.list_files("test-collection", "")
        
        assert len(result) == 3
        assert "document1.md" in result
        assert "document2.txt" in result
        assert "subfolder/document3.md" in result
        
        mock_collection_manager.list_files.assert_called_once_with("test-collection", "")
    
    @pytest.mark.asyncio
    async def test_save_file_success(self, service, mock_collection_manager):
        """Test successful file saving."""
        mock_result = {
            "success": True,
            "file": {
                "path": "test-file.md",
                "metadata": {"size": 100},
                "created_at": "2025-01-05T23:00:00Z",
                "updated_at": "2025-01-05T23:00:00Z"
            }
        }
        
        mock_collection_manager.save_to_collection.return_value = json.dumps(mock_result)
        
        result = await service.save_file(
            "test-collection", 
            "test-file.md", 
            "# Test Content\n\nThis is test content.",
            ""
        )
        
        assert isinstance(result, FileInfo)
        assert result.path == "test-file.md"
        assert result.content == "# Test Content\n\nThis is test content."
        assert result.metadata == {"size": 100}
        assert result.created_at == "2025-01-05T23:00:00Z"
        assert result.updated_at == "2025-01-05T23:00:00Z"
        
        mock_collection_manager.save_to_collection.assert_called_once_with(
            "test-collection", "test-file.md", "# Test Content\n\nThis is test content.", ""
        )
    
    @pytest.mark.asyncio
    async def test_get_file_success(self, service, mock_collection_manager):
        """Test successful file retrieval."""
        mock_result = {
            "success": True,
            "file": {
                "path": "test-file.md",
                "content": "# Test Content\n\nFile content here.",
                "metadata": {"size": 150},
                "created_at": "2025-01-05T22:00:00Z",
                "updated_at": "2025-01-05T23:00:00Z"
            }
        }
        
        mock_collection_manager.read_from_collection.return_value = json.dumps(mock_result)
        
        result = await service.get_file("test-collection", "test-file.md", "")
        
        assert isinstance(result, FileInfo)
        assert result.path == "test-file.md"
        assert result.content == "# Test Content\n\nFile content here."
        assert result.metadata == {"size": 150}
        
        mock_collection_manager.read_from_collection.assert_called_once_with(
            "test-collection", "test-file.md", ""
        )
    
    @pytest.mark.asyncio
    async def test_get_file_not_found(self, service, mock_collection_manager):
        """Test file retrieval when file not found."""
        mock_result = {"success": False, "error": "File not found"}
        mock_collection_manager.read_from_collection.return_value = json.dumps(mock_result)
        
        with pytest.raises(Exception) as exc_info:
            await service.get_file("test-collection", "nonexistent.md")
        
        assert "File not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_update_file_success(self, service, mock_collection_manager):
        """Test successful file updating."""
        # Since update_file currently delegates to save_file, we test that behavior
        mock_result = {
            "success": True,
            "file": {
                "path": "test-file.md",
                "metadata": {"size": 200},
                "created_at": "2025-01-05T22:00:00Z",
                "updated_at": "2025-01-05T23:30:00Z"
            }
        }
        
        mock_collection_manager.save_to_collection.return_value = json.dumps(mock_result)
        
        result = await service.update_file(
            "test-collection", 
            "test-file.md", 
            "# Updated Content\n\nThis content was updated."
        )
        
        assert isinstance(result, FileInfo)
        assert result.path == "test-file.md"
        assert result.content == "# Updated Content\n\nThis content was updated."
        assert result.updated_at == "2025-01-05T23:30:00Z"
    
    @pytest.mark.asyncio
    async def test_delete_file_not_implemented(self, service):
        """Test that file deletion raises NotImplementedError."""
        with pytest.raises(NotImplementedError) as exc_info:
            await service.delete_file("test-collection", "test-file.md")
        
        assert "File deletion not yet implemented" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_service_initialization_with_base_dir(self):
        """Test service initialization with custom base directory."""
        test_base_dir = Path("/custom/path")
        
        with patch('services.collection_service.create_collection_manager') as mock_create:
            mock_manager = AsyncMock()
            mock_create.return_value = mock_manager
            
            service = CollectionService(base_dir=test_base_dir)
            
            mock_create.assert_called_once_with(test_base_dir)
            assert service.collection_manager == mock_manager