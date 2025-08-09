"""
Tests for file management use-case functions.

These tests validate the protocol-agnostic business logic for file operations,
ensuring consistent behavior between API and MCP endpoints.
"""

import pytest
from unittest.mock import AsyncMock, Mock

from application_layer.file_management import (
    save_file_use_case,
    get_file_use_case,
    update_file_use_case,
    delete_file_use_case,
    list_files_use_case,
    ValidationError
)
from services.interfaces import FileInfo


@pytest.fixture
def mock_collection_service():
    """Create a mock collection service for testing."""
    service = AsyncMock()
    return service


@pytest.fixture
def sample_file_info():
    """Create a sample FileInfo for testing."""
    return FileInfo(
        name="test-file.txt",
        path="test-file.txt",
        content="Test content",
        size=12,
        created_at="2025-01-09T10:00:00Z",
        updated_at="2025-01-09T10:00:00Z"
    )


class TestSaveFileUseCase:
    """Test save_file_use_case function."""
    
    @pytest.mark.asyncio
    async def test_save_file_success(self, mock_collection_service, sample_file_info):
        """Test successful file saving."""
        # Arrange
        mock_collection_service.save_file.return_value = sample_file_info
        
        # Act
        result = await save_file_use_case(
            mock_collection_service, "test-collection", "test-file.txt", "Test content", ""
        )
        
        # Assert
        assert result == sample_file_info
        mock_collection_service.save_file.assert_called_once_with(
            "test-collection", "test-file.txt", "Test content", ""
        )
    
    @pytest.mark.asyncio
    async def test_save_file_with_folder(self, mock_collection_service, sample_file_info):
        """Test file saving with folder path."""
        # Arrange
        mock_collection_service.save_file.return_value = sample_file_info
        
        # Act
        result = await save_file_use_case(
            mock_collection_service, "test-collection", "test-file.txt", "Test content", "subfolder"
        )
        
        # Assert
        assert result == sample_file_info
        mock_collection_service.save_file.assert_called_once_with(
            "test-collection", "test-file.txt", "Test content", "subfolder"
        )
    
    @pytest.mark.asyncio
    async def test_save_file_url_decoding(self, mock_collection_service, sample_file_info):
        """Test URL decoding of collection name and file path."""
        # Arrange
        mock_collection_service.save_file.return_value = sample_file_info
        
        # Act
        result = await save_file_use_case(
            mock_collection_service, "test%20collection", "test%20file.txt", "Test content", "sub%20folder"
        )
        
        # Assert
        assert result == sample_file_info
        mock_collection_service.save_file.assert_called_once_with(
            "test collection", "test file.txt", "Test content", "sub folder"
        )
    
    @pytest.mark.asyncio
    async def test_save_file_invalid_collection_name_type(self, mock_collection_service):
        """Test validation error when collection name is not a string."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await save_file_use_case(mock_collection_service, 123, "file.txt", "content", "")
        
        assert exc_info.value.code == "INVALID_COLLECTION_NAME_TYPE"
        mock_collection_service.save_file.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_save_file_invalid_file_path_type(self, mock_collection_service):
        """Test validation error when file path is not a string."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await save_file_use_case(mock_collection_service, "collection", 123, "content", "")
        
        assert exc_info.value.code == "INVALID_FILE_PATH_TYPE"
        mock_collection_service.save_file.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_save_file_invalid_content_type(self, mock_collection_service):
        """Test validation error when content is not a string."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await save_file_use_case(mock_collection_service, "collection", "file.txt", 123, "")
        
        assert exc_info.value.code == "INVALID_CONTENT_TYPE"
        mock_collection_service.save_file.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_save_file_missing_collection_name(self, mock_collection_service):
        """Test validation error when collection name is empty."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await save_file_use_case(mock_collection_service, "", "file.txt", "content", "")
        
        assert exc_info.value.code == "MISSING_COLLECTION_NAME"
        mock_collection_service.save_file.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_save_file_missing_file_path(self, mock_collection_service):
        """Test validation error when file path is empty."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await save_file_use_case(mock_collection_service, "collection", "", "content", "")
        
        assert exc_info.value.code == "MISSING_FILE_PATH"
        mock_collection_service.save_file.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_save_file_missing_content(self, mock_collection_service):
        """Test validation error when content is None."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await save_file_use_case(mock_collection_service, "collection", "file.txt", None, "")
        
        assert exc_info.value.code == "MISSING_CONTENT"
        mock_collection_service.save_file.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_save_file_empty_content(self, mock_collection_service):
        """Test validation error when content is empty string."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await save_file_use_case(mock_collection_service, "collection", "file.txt", "", "")
        
        assert exc_info.value.code == "MISSING_CONTENT"
        mock_collection_service.save_file.assert_not_called()


class TestGetFileUseCase:
    """Test get_file_use_case function."""
    
    @pytest.mark.asyncio
    async def test_get_file_success(self, mock_collection_service, sample_file_info):
        """Test successful file retrieval."""
        # Arrange
        mock_collection_service.get_file.return_value = sample_file_info
        
        # Act
        result = await get_file_use_case(
            mock_collection_service, "test-collection", "test-file.txt", ""
        )
        
        # Assert
        assert result == sample_file_info
        mock_collection_service.get_file.assert_called_once_with(
            "test-collection", "test-file.txt", ""
        )
    
    @pytest.mark.asyncio
    async def test_get_file_with_folder(self, mock_collection_service, sample_file_info):
        """Test file retrieval with folder path."""
        # Arrange
        mock_collection_service.get_file.return_value = sample_file_info
        
        # Act
        result = await get_file_use_case(
            mock_collection_service, "test-collection", "test-file.txt", "subfolder"
        )
        
        # Assert
        assert result == sample_file_info
        mock_collection_service.get_file.assert_called_once_with(
            "test-collection", "test-file.txt", "subfolder"
        )
    
    @pytest.mark.asyncio
    async def test_get_file_url_decoding(self, mock_collection_service, sample_file_info):
        """Test URL decoding of collection name and file path."""
        # Arrange
        mock_collection_service.get_file.return_value = sample_file_info
        
        # Act
        result = await get_file_use_case(
            mock_collection_service, "test%20collection", "test%20file.txt", "sub%20folder"
        )
        
        # Assert
        assert result == sample_file_info
        mock_collection_service.get_file.assert_called_once_with(
            "test collection", "test file.txt", "sub folder"
        )
    
    @pytest.mark.asyncio
    async def test_get_file_invalid_collection_name_type(self, mock_collection_service):
        """Test validation error when collection name is not a string."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await get_file_use_case(mock_collection_service, 123, "file.txt", "")
        
        assert exc_info.value.code == "INVALID_COLLECTION_NAME_TYPE"
        mock_collection_service.get_file.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_file_missing_collection_name(self, mock_collection_service):
        """Test validation error when collection name is empty."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await get_file_use_case(mock_collection_service, "", "file.txt", "")
        
        assert exc_info.value.code == "MISSING_COLLECTION_NAME"
        mock_collection_service.get_file.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_file_not_found(self, mock_collection_service):
        """Test handling when file doesn't exist."""
        # Arrange
        mock_collection_service.get_file.side_effect = Exception("File not found")
        
        # Act & Assert
        with pytest.raises(Exception, match="File not found"):
            await get_file_use_case(mock_collection_service, "collection", "nonexistent.txt", "")


class TestUpdateFileUseCase:
    """Test update_file_use_case function."""
    
    @pytest.mark.asyncio
    async def test_update_file_success(self, mock_collection_service, sample_file_info):
        """Test successful file updating."""
        # Arrange
        mock_collection_service.update_file.return_value = sample_file_info
        
        # Act
        result = await update_file_use_case(
            mock_collection_service, "test-collection", "test-file.txt", "Updated content", ""
        )
        
        # Assert
        assert result == sample_file_info
        mock_collection_service.update_file.assert_called_once_with(
            "test-collection", "test-file.txt", "Updated content", ""
        )
    
    @pytest.mark.asyncio
    async def test_update_file_with_folder(self, mock_collection_service, sample_file_info):
        """Test file updating with folder path."""
        # Arrange
        mock_collection_service.update_file.return_value = sample_file_info
        
        # Act
        result = await update_file_use_case(
            mock_collection_service, "test-collection", "test-file.txt", "Updated content", "subfolder"
        )
        
        # Assert
        assert result == sample_file_info
        mock_collection_service.update_file.assert_called_once_with(
            "test-collection", "test-file.txt", "Updated content", "subfolder"
        )
    
    @pytest.mark.asyncio
    async def test_update_file_invalid_content_type(self, mock_collection_service):
        """Test validation error when content is not a string."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await update_file_use_case(mock_collection_service, "collection", "file.txt", 123, "")
        
        assert exc_info.value.code == "INVALID_CONTENT_TYPE"
        mock_collection_service.update_file.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_update_file_missing_content(self, mock_collection_service):
        """Test validation error when content is None."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await update_file_use_case(mock_collection_service, "collection", "file.txt", None, "")
        
        assert exc_info.value.code == "MISSING_CONTENT"
        mock_collection_service.update_file.assert_not_called()


class TestDeleteFileUseCase:
    """Test delete_file_use_case function."""
    
    @pytest.mark.asyncio
    async def test_delete_file_success(self, mock_collection_service):
        """Test successful file deletion."""
        # Arrange
        expected_result = {"success": True, "message": "File deleted"}
        mock_collection_service.delete_file.return_value = expected_result
        
        # Act
        result = await delete_file_use_case(
            mock_collection_service, "test-collection", "test-file.txt", ""
        )
        
        # Assert
        assert result == expected_result
        mock_collection_service.delete_file.assert_called_once_with(
            "test-collection", "test-file.txt", ""
        )
    
    @pytest.mark.asyncio
    async def test_delete_file_with_folder(self, mock_collection_service):
        """Test file deletion with folder path."""
        # Arrange
        expected_result = {"success": True, "message": "File deleted"}
        mock_collection_service.delete_file.return_value = expected_result
        
        # Act
        result = await delete_file_use_case(
            mock_collection_service, "test-collection", "test-file.txt", "subfolder"
        )
        
        # Assert
        assert result == expected_result
        mock_collection_service.delete_file.assert_called_once_with(
            "test-collection", "test-file.txt", "subfolder"
        )
    
    @pytest.mark.asyncio
    async def test_delete_file_url_decoding(self, mock_collection_service):
        """Test URL decoding of collection name and file path."""
        # Arrange
        expected_result = {"success": True, "message": "File deleted"}
        mock_collection_service.delete_file.return_value = expected_result
        
        # Act
        result = await delete_file_use_case(
            mock_collection_service, "test%20collection", "test%20file.txt", "sub%20folder"
        )
        
        # Assert
        assert result == expected_result
        mock_collection_service.delete_file.assert_called_once_with(
            "test collection", "test file.txt", "sub folder"
        )
    
    @pytest.mark.asyncio
    async def test_delete_file_invalid_collection_name_type(self, mock_collection_service):
        """Test validation error when collection name is not a string."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await delete_file_use_case(mock_collection_service, 123, "file.txt", "")
        
        assert exc_info.value.code == "INVALID_COLLECTION_NAME_TYPE"
        mock_collection_service.delete_file.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_delete_file_missing_collection_name(self, mock_collection_service):
        """Test validation error when collection name is empty."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await delete_file_use_case(mock_collection_service, "", "file.txt", "")
        
        assert exc_info.value.code == "MISSING_COLLECTION_NAME"
        mock_collection_service.delete_file.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_delete_file_not_found(self, mock_collection_service):
        """Test handling when file doesn't exist."""
        # Arrange
        mock_collection_service.delete_file.side_effect = Exception("File not found")
        
        # Act & Assert
        with pytest.raises(Exception, match="File not found"):
            await delete_file_use_case(mock_collection_service, "collection", "nonexistent.txt", "")


class TestListFilesUseCase:
    """Test list_files_use_case function."""
    
    @pytest.mark.asyncio
    async def test_list_files_success(self, mock_collection_service, sample_file_info):
        """Test successful file listing."""
        # Arrange
        expected_files = [sample_file_info]
        mock_collection_service.list_files_in_collection.return_value = expected_files
        
        # Act
        result = await list_files_use_case(mock_collection_service, "test-collection")
        
        # Assert
        assert result == expected_files
        mock_collection_service.list_files_in_collection.assert_called_once_with("test-collection")
    
    @pytest.mark.asyncio
    async def test_list_files_empty(self, mock_collection_service):
        """Test listing when no files exist."""
        # Arrange
        mock_collection_service.list_files_in_collection.return_value = []
        
        # Act
        result = await list_files_use_case(mock_collection_service, "test-collection")
        
        # Assert
        assert result == []
        mock_collection_service.list_files_in_collection.assert_called_once_with("test-collection")
    
    @pytest.mark.asyncio
    async def test_list_files_url_decoding(self, mock_collection_service, sample_file_info):
        """Test URL decoding of collection name."""
        # Arrange
        expected_files = [sample_file_info]
        mock_collection_service.list_files_in_collection.return_value = expected_files
        
        # Act
        result = await list_files_use_case(mock_collection_service, "test%20collection")
        
        # Assert
        assert result == expected_files
        mock_collection_service.list_files_in_collection.assert_called_once_with("test collection")
    
    @pytest.mark.asyncio
    async def test_list_files_invalid_collection_name_type(self, mock_collection_service):
        """Test validation error when collection name is not a string."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await list_files_use_case(mock_collection_service, 123)
        
        assert exc_info.value.code == "INVALID_COLLECTION_NAME_TYPE"
        mock_collection_service.list_files_in_collection.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_list_files_missing_collection_name(self, mock_collection_service):
        """Test validation error when collection name is empty."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await list_files_use_case(mock_collection_service, "")
        
        assert exc_info.value.code == "MISSING_COLLECTION_NAME"
        mock_collection_service.list_files_in_collection.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_list_files_collection_not_found(self, mock_collection_service):
        """Test handling when collection doesn't exist."""
        # Arrange
        mock_collection_service.list_files_in_collection.side_effect = Exception("Collection not found")
        
        # Act & Assert
        with pytest.raises(Exception, match="Collection not found"):
            await list_files_use_case(mock_collection_service, "nonexistent-collection")


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