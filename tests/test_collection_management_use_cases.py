"""
Tests for collection management use-case functions.

These tests validate the protocol-agnostic business logic for collection operations,
ensuring consistent behavior between API and MCP endpoints.
"""

import pytest
from unittest.mock import AsyncMock, Mock

from application_layer.collection_management import (
    list_collections_use_case,
    create_collection_use_case,
    get_collection_use_case,
    delete_collection_use_case,
    ValidationError
)
from services.interfaces import CollectionInfo


@pytest.fixture
def mock_collection_service():
    """Create a mock collection service for testing."""
    service = AsyncMock()
    return service


@pytest.fixture
def sample_collection_info():
    """Create a sample CollectionInfo for testing."""
    return CollectionInfo(
        id="test-collection",
        name="test-collection",
        description="A test collection",
        file_count=5,
        created_at="2025-01-09T10:00:00Z",
        updated_at="2025-01-09T10:00:00Z"
    )


class TestListCollectionsUseCase:
    """Test list_collections_use_case function."""
    
    @pytest.mark.asyncio
    async def test_list_collections_success(self, mock_collection_service, sample_collection_info):
        """Test successful collection listing."""
        # Arrange
        expected_collections = [sample_collection_info]
        mock_collection_service.list_collections.return_value = expected_collections
        
        # Act
        result = await list_collections_use_case(mock_collection_service)
        
        # Assert
        assert result == expected_collections
        mock_collection_service.list_collections.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_list_collections_empty(self, mock_collection_service):
        """Test listing when no collections exist."""
        # Arrange
        mock_collection_service.list_collections.return_value = []
        
        # Act
        result = await list_collections_use_case(mock_collection_service)
        
        # Assert
        assert result == []
        mock_collection_service.list_collections.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_list_collections_service_error(self, mock_collection_service):
        """Test handling of service layer errors."""
        # Arrange
        mock_collection_service.list_collections.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            await list_collections_use_case(mock_collection_service)


class TestCreateCollectionUseCase:
    """Test create_collection_use_case function."""
    
    @pytest.mark.asyncio
    async def test_create_collection_success(self, mock_collection_service, sample_collection_info):
        """Test successful collection creation."""
        # Arrange
        mock_collection_service.create_collection.return_value = sample_collection_info
        
        # Act
        result = await create_collection_use_case(
            mock_collection_service, "test-collection", "A test collection"
        )
        
        # Assert
        assert result == sample_collection_info
        mock_collection_service.create_collection.assert_called_once_with(
            "test-collection", "A test collection"
        )
    
    @pytest.mark.asyncio
    async def test_create_collection_without_description(self, mock_collection_service, sample_collection_info):
        """Test collection creation without description."""
        # Arrange
        mock_collection_service.create_collection.return_value = sample_collection_info
        
        # Act
        result = await create_collection_use_case(mock_collection_service, "test-collection")
        
        # Assert
        assert result == sample_collection_info
        mock_collection_service.create_collection.assert_called_once_with("test-collection", "")
    
    @pytest.mark.asyncio
    async def test_create_collection_missing_name(self, mock_collection_service):
        """Test validation error when name is missing."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await create_collection_use_case(mock_collection_service, "")
        
        assert exc_info.value.code == "MISSING_NAME"
        assert "required" in exc_info.value.message.lower()
        mock_collection_service.create_collection.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_create_collection_none_name(self, mock_collection_service):
        """Test validation error when name is None."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await create_collection_use_case(mock_collection_service, None)
        
        assert exc_info.value.code == "INVALID_NAME_TYPE"  # Fixed: None triggers INVALID_NAME_TYPE first
        mock_collection_service.create_collection.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_create_collection_whitespace_only_name(self, mock_collection_service):
        """Test validation error when name is only whitespace."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await create_collection_use_case(mock_collection_service, "   ")
        
        assert exc_info.value.code == "MISSING_NAME"  # Fixed: whitespace-only triggers MISSING_NAME
        mock_collection_service.create_collection.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_create_collection_invalid_name_type(self, mock_collection_service):
        """Test validation error when name is not a string."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await create_collection_use_case(mock_collection_service, 123)
        
        assert exc_info.value.code == "INVALID_NAME_TYPE"
        mock_collection_service.create_collection.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_create_collection_invalid_description_type(self, mock_collection_service):
        """Test validation error when description is not a string."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await create_collection_use_case(mock_collection_service, "test", 123)
        
        assert exc_info.value.code == "INVALID_DESCRIPTION_TYPE"
        mock_collection_service.create_collection.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_create_collection_name_trimming(self, mock_collection_service, sample_collection_info):
        """Test that collection name is properly trimmed."""
        # Arrange
        mock_collection_service.create_collection.return_value = sample_collection_info
        
        # Act
        result = await create_collection_use_case(mock_collection_service, "  test-collection  ", "desc")
        
        # Assert
        assert result == sample_collection_info
        mock_collection_service.create_collection.assert_called_once_with("test-collection", "desc")
    
    @pytest.mark.asyncio
    async def test_create_collection_already_exists(self, mock_collection_service):
        """Test handling when collection already exists."""
        # Arrange
        mock_collection_service.create_collection.side_effect = Exception("Collection already exists")
        
        # Act & Assert
        with pytest.raises(Exception, match="Collection already exists"):
            await create_collection_use_case(mock_collection_service, "existing-collection")


class TestGetCollectionUseCase:
    """Test get_collection_use_case function."""
    
    @pytest.mark.asyncio
    async def test_get_collection_success(self, mock_collection_service, sample_collection_info):
        """Test successful collection retrieval."""
        # Arrange
        mock_collection_service.get_collection.return_value = sample_collection_info
        
        # Act
        result = await get_collection_use_case(mock_collection_service, "test-collection")
        
        # Assert
        assert result == sample_collection_info
        mock_collection_service.get_collection.assert_called_once_with("test-collection")
    
    @pytest.mark.asyncio
    async def test_get_collection_missing_name(self, mock_collection_service):
        """Test validation error when name is missing."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await get_collection_use_case(mock_collection_service, "")
        
        assert exc_info.value.code == "MISSING_NAME"
        mock_collection_service.get_collection.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_collection_none_name(self, mock_collection_service):
        """Test validation error when name is None."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await get_collection_use_case(mock_collection_service, None)
        
        assert exc_info.value.code == "INVALID_NAME_TYPE"  # Fixed: None triggers INVALID_NAME_TYPE first
        mock_collection_service.get_collection.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_collection_invalid_name_type(self, mock_collection_service):
        """Test validation error when name is not a string."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await get_collection_use_case(mock_collection_service, 123)
        
        assert exc_info.value.code == "INVALID_NAME_TYPE"
        mock_collection_service.get_collection.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_collection_name_trimming(self, mock_collection_service, sample_collection_info):
        """Test that collection name is properly trimmed."""
        # Arrange
        mock_collection_service.get_collection.return_value = sample_collection_info
        
        # Act
        result = await get_collection_use_case(mock_collection_service, "  test-collection  ")
        
        # Assert
        assert result == sample_collection_info
        mock_collection_service.get_collection.assert_called_once_with("test-collection")
    
    @pytest.mark.asyncio
    async def test_get_collection_not_found(self, mock_collection_service):
        """Test handling when collection doesn't exist."""
        # Arrange
        mock_collection_service.get_collection.side_effect = Exception("Collection not found")
        
        # Act & Assert
        with pytest.raises(Exception, match="Collection not found"):
            await get_collection_use_case(mock_collection_service, "nonexistent-collection")


class TestDeleteCollectionUseCase:
    """Test delete_collection_use_case function."""
    
    @pytest.mark.asyncio
    async def test_delete_collection_success(self, mock_collection_service):
        """Test successful collection deletion."""
        # Arrange
        expected_result = {"success": True, "message": "Collection deleted"}
        mock_collection_service.delete_collection.return_value = expected_result
        
        # Act
        result = await delete_collection_use_case(mock_collection_service, "test-collection")
        
        # Assert
        assert result == expected_result
        mock_collection_service.delete_collection.assert_called_once_with("test-collection")
    
    @pytest.mark.asyncio
    async def test_delete_collection_missing_name(self, mock_collection_service):
        """Test validation error when name is missing."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await delete_collection_use_case(mock_collection_service, "")
        
        assert exc_info.value.code == "MISSING_NAME"
        mock_collection_service.delete_collection.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_delete_collection_none_name(self, mock_collection_service):
        """Test validation error when name is None."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await delete_collection_use_case(mock_collection_service, None)
        
        assert exc_info.value.code == "INVALID_NAME_TYPE"  # Fixed: None triggers INVALID_NAME_TYPE first
        mock_collection_service.delete_collection.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_delete_collection_invalid_name_type(self, mock_collection_service):
        """Test validation error when name is not a string."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await delete_collection_use_case(mock_collection_service, 123)
        
        assert exc_info.value.code == "INVALID_NAME_TYPE"
        mock_collection_service.delete_collection.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_delete_collection_name_trimming(self, mock_collection_service):
        """Test that collection name is properly trimmed."""
        # Arrange
        expected_result = {"success": True, "message": "Collection deleted"}
        mock_collection_service.delete_collection.return_value = expected_result
        
        # Act
        result = await delete_collection_use_case(mock_collection_service, "  test-collection  ")
        
        # Assert
        assert result == expected_result
        mock_collection_service.delete_collection.assert_called_once_with("test-collection")
    
    @pytest.mark.asyncio
    async def test_delete_collection_not_found(self, mock_collection_service):
        """Test handling when collection doesn't exist."""
        # Arrange
        mock_collection_service.delete_collection.side_effect = Exception("Collection not found")
        
        # Act & Assert
        with pytest.raises(Exception, match="Collection not found"):
            await delete_collection_use_case(mock_collection_service, "nonexistent-collection")


class TestValidationError:
    """Test ValidationError class."""
    
    def test_validation_error_creation(self):
        """Test ValidationError creation with all parameters."""
        error = ValidationError("TEST_CODE", "Test message", {"field": "value"})
        
        assert error.code == "TEST_CODE"
        assert error.message == "Test message"
        assert error.details == {"field": "value"}
        assert str(error) == "Test message"
    
    def test_validation_error_without_details(self):
        """Test ValidationError creation without details."""
        error = ValidationError("TEST_CODE", "Test message")
        
        assert error.code == "TEST_CODE"
        assert error.message == "Test message"
        assert error.details == {}
        assert str(error) == "Test message"