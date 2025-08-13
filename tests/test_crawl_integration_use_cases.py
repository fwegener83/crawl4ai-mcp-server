"""
Tests for crawl integration use-case functions.

These tests validate the protocol-agnostic business logic for crawling content 
and saving to collections, ensuring consistent behavior between API and MCP endpoints.
"""

import pytest
from unittest.mock import AsyncMock, Mock

from application_layer.crawl_integration import (
    crawl_single_page_to_collection_use_case,
    ValidationError
)
from services.interfaces import CrawlResult, FileInfo


@pytest.fixture
def mock_web_service():
    """Create a mock web service for testing."""
    service = AsyncMock()
    return service


@pytest.fixture
def mock_collection_service():
    """Create a mock collection service for testing."""
    service = AsyncMock()
    return service


@pytest.fixture
def sample_crawl_result():
    """Create a sample CrawlResult for testing."""
    return CrawlResult(
        url="https://example.com/blog/article",
        content="This is the article content",
        metadata={"title": "Example Article", "crawl_time": "2025-01-09T15:00:00Z"},
        error=None
    )


@pytest.fixture
def sample_file_info():
    """Create a sample FileInfo for testing."""
    return FileInfo(
        name="article.md",
        path="article.md",
        content="# Example Article\n\n**Source URL:** https://example.com/blog/article...",
        size=150,
        created_at="2025-01-09T15:00:00Z",
        updated_at="2025-01-09T15:00:00Z"
    )


class TestCrawlSinglePageToCollectionUseCase:
    """Test crawl_single_page_to_collection_use_case function."""
    
    @pytest.mark.asyncio
    async def test_crawl_and_save_success(self, mock_web_service, mock_collection_service, 
                                         sample_crawl_result, sample_file_info):
        """Test successful crawling and saving to collection."""
        # Arrange
        mock_web_service.extract_content.return_value = sample_crawl_result
        mock_collection_service.save_file.return_value = sample_file_info
        
        # Act
        result = await crawl_single_page_to_collection_use_case(
            mock_web_service, mock_collection_service, 
            "test-collection", "https://example.com/blog/article", ""
        )
        
        # Assert
        assert result == sample_file_info
        mock_web_service.extract_content.assert_called_once_with("https://example.com/blog/article")
        mock_collection_service.save_file.assert_called_once()
        
        # Verify save_file was called with processed content
        call_args = mock_collection_service.save_file.call_args
        assert call_args[0][0] == "test-collection"  # collection_name
        assert call_args[0][1] == "article.md"  # filename (generated from URL)
        assert "# Example Article" in call_args[0][2]  # content contains title
        assert "https://example.com/blog/article" in call_args[0][2]  # content contains URL
        assert call_args[0][3] == ""  # folder
    
    @pytest.mark.asyncio
    async def test_crawl_and_save_with_folder(self, mock_web_service, mock_collection_service,
                                             sample_crawl_result, sample_file_info):
        """Test crawling and saving with folder path."""
        # Arrange
        mock_web_service.extract_content.return_value = sample_crawl_result
        mock_collection_service.save_file.return_value = sample_file_info
        
        # Act
        result = await crawl_single_page_to_collection_use_case(
            mock_web_service, mock_collection_service,
            "test-collection", "https://example.com/blog/article", "subfolder"
        )
        
        # Assert
        assert result == sample_file_info
        call_args = mock_collection_service.save_file.call_args
        assert call_args[0][3] == "subfolder"  # folder
    
    @pytest.mark.asyncio
    async def test_crawl_and_save_domain_only_url(self, mock_web_service, mock_collection_service,
                                                  sample_file_info):
        """Test filename generation for domain-only URL."""
        # Arrange
        crawl_result = CrawlResult(
            url="https://example.com",
            content="Home page content",
            metadata={"title": "Example Home", "crawl_time": "2025-01-09T15:00:00Z"},
            error=None
        )
        mock_web_service.extract_content.return_value = crawl_result
        mock_collection_service.save_file.return_value = sample_file_info
        
        # Act
        result = await crawl_single_page_to_collection_use_case(
            mock_web_service, mock_collection_service,
            "test-collection", "https://example.com", ""
        )
        
        # Assert
        call_args = mock_collection_service.save_file.call_args
        assert call_args[0][1] == "example_com.md"  # filename from domain
    
    @pytest.mark.asyncio
    async def test_crawl_and_save_filename_sanitization(self, mock_web_service, mock_collection_service,
                                                       sample_file_info):
        """Test filename sanitization for URLs with invalid characters."""
        # Arrange
        crawl_result = CrawlResult(
            url="https://example.com/path/with<>invalid:chars",
            content="Content",
            metadata={"title": "Test Title", "crawl_time": "2025-01-09T15:00:00Z"},
            error=None
        )
        mock_web_service.extract_content.return_value = crawl_result
        mock_collection_service.save_file.return_value = sample_file_info
        
        # Act
        result = await crawl_single_page_to_collection_use_case(
            mock_web_service, mock_collection_service,
            "test-collection", "https://example.com/path/with<>invalid:chars", ""
        )
        
        # Assert
        call_args = mock_collection_service.save_file.call_args
        filename = call_args[0][1]
        assert "<" not in filename
        assert ">" not in filename
        assert ":" not in filename
        assert filename.endswith(".md")
    
    @pytest.mark.asyncio
    async def test_crawl_and_save_invalid_collection_name_type(self, mock_web_service, mock_collection_service):
        """Test validation error when collection name is not a string."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await crawl_single_page_to_collection_use_case(
                mock_web_service, mock_collection_service, 123, "https://example.com", ""
            )
        
        assert exc_info.value.code == "INVALID_COLLECTION_NAME_TYPE"
        mock_web_service.extract_content.assert_not_called()
        mock_collection_service.save_file.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_crawl_and_save_missing_collection_name(self, mock_web_service, mock_collection_service):
        """Test validation error when collection name is empty."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await crawl_single_page_to_collection_use_case(
                mock_web_service, mock_collection_service, "", "https://example.com", ""
            )
        
        assert exc_info.value.code == "MISSING_COLLECTION_NAME"
        mock_web_service.extract_content.assert_not_called()
        mock_collection_service.save_file.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_crawl_and_save_invalid_url_type(self, mock_web_service, mock_collection_service):
        """Test validation error when URL is not a string."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await crawl_single_page_to_collection_use_case(
                mock_web_service, mock_collection_service, "test-collection", 123, ""
            )
        
        assert exc_info.value.code == "INVALID_URL_TYPE"
        mock_web_service.extract_content.assert_not_called()
        mock_collection_service.save_file.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_crawl_and_save_missing_url(self, mock_web_service, mock_collection_service):
        """Test validation error when URL is empty."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await crawl_single_page_to_collection_use_case(
                mock_web_service, mock_collection_service, "test-collection", "", ""
            )
        
        assert exc_info.value.code == "MISSING_URL"
        mock_web_service.extract_content.assert_not_called()
        mock_collection_service.save_file.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_crawl_and_save_invalid_folder_type(self, mock_web_service, mock_collection_service):
        """Test validation error when folder is not a string."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await crawl_single_page_to_collection_use_case(
                mock_web_service, mock_collection_service, "test-collection", "https://example.com", 123
            )
        
        assert exc_info.value.code == "INVALID_FOLDER_TYPE"
        mock_web_service.extract_content.assert_not_called()
        mock_collection_service.save_file.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_crawl_and_save_crawl_error(self, mock_web_service, mock_collection_service):
        """Test handling when web crawling fails."""
        # Arrange
        crawl_result = CrawlResult(
            url="https://example.com",
            content="",
            metadata={},
            error="Network timeout"
        )
        mock_web_service.extract_content.return_value = crawl_result
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await crawl_single_page_to_collection_use_case(
                mock_web_service, mock_collection_service, "test-collection", "https://example.com", ""
            )
        
        assert exc_info.value.code == "CRAWL_FAILED"
        assert "Network timeout" in exc_info.value.message
        mock_collection_service.save_file.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_crawl_and_save_collection_service_error(self, mock_web_service, mock_collection_service, sample_crawl_result):
        """Test handling when collection service fails."""
        # Arrange
        mock_web_service.extract_content.return_value = sample_crawl_result
        mock_collection_service.save_file.side_effect = Exception("Collection not found")
        
        # Act & Assert
        with pytest.raises(Exception, match="Collection not found"):
            await crawl_single_page_to_collection_use_case(
                mock_web_service, mock_collection_service, "test-collection", "https://example.com", ""
            )
    
    @pytest.mark.asyncio
    async def test_crawl_and_save_url_parsing_fallback(self, mock_web_service, mock_collection_service, sample_file_info):
        """Test fallback filename when URL parsing fails."""
        # Arrange
        crawl_result = CrawlResult(
            url="invalid-url-format",
            content="Content",
            metadata={"title": "Test", "crawl_time": "2025-01-09T15:00:00Z"},
            error=None
        )
        mock_web_service.extract_content.return_value = crawl_result
        mock_collection_service.save_file.return_value = sample_file_info
        
        # Act
        result = await crawl_single_page_to_collection_use_case(
            mock_web_service, mock_collection_service,
            "test-collection", "invalid-url-format", ""
        )
        
        # Assert
        call_args = mock_collection_service.save_file.call_args
        assert call_args[0][1] == "invalid-url-format.md"  # filename from path
    
    @pytest.mark.asyncio  
    async def test_crawl_and_save_input_trimming(self, mock_web_service, mock_collection_service,
                                                sample_crawl_result, sample_file_info):
        """Test that inputs are properly trimmed."""
        # Arrange
        mock_web_service.extract_content.return_value = sample_crawl_result
        mock_collection_service.save_file.return_value = sample_file_info
        
        # Act
        result = await crawl_single_page_to_collection_use_case(
            mock_web_service, mock_collection_service,
            "  test-collection  ", "  https://example.com  ", ""
        )
        
        # Assert
        mock_web_service.extract_content.assert_called_once_with("https://example.com")
        call_args = mock_collection_service.save_file.call_args
        assert call_args[0][0] == "test-collection"  # collection_name trimmed


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