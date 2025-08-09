"""
Tests for web crawling use-case functions.

These tests validate the protocol-agnostic business logic for web crawling operations,
ensuring consistent behavior between API and MCP endpoints.
"""

import pytest
from unittest.mock import AsyncMock, Mock

from application_layer.web_crawling import (
    extract_content_use_case,
    deep_crawl_use_case,
    link_preview_use_case,
    ValidationError
)
from services.interfaces import CrawlResult, DeepCrawlConfig, LinkPreview


@pytest.fixture
def mock_web_service():
    """Create a mock web service for testing."""
    service = AsyncMock()
    return service


@pytest.fixture
def sample_crawl_result():
    """Create a sample CrawlResult for testing."""
    return CrawlResult(
        url="https://example.com",
        content="Sample content",
        metadata={"title": "Example Page"},
        error=None
    )


@pytest.fixture
def sample_link_preview():
    """Create a sample LinkPreview for testing."""
    return LinkPreview(
        domain="https://example.com",
        links=["https://example.com/page1", "https://example.com/page2"],
        metadata={"total_links": 2}
    )


class TestExtractContentUseCase:
    """Test extract_content_use_case function."""
    
    @pytest.mark.asyncio
    async def test_extract_content_success(self, mock_web_service, sample_crawl_result):
        """Test successful content extraction."""
        # Arrange
        mock_web_service.extract_content.return_value = sample_crawl_result
        
        # Act
        result = await extract_content_use_case(mock_web_service, "https://example.com")
        
        # Assert
        assert result == sample_crawl_result
        mock_web_service.extract_content.assert_called_once_with("https://example.com")
    
    @pytest.mark.asyncio
    async def test_extract_content_url_trimming(self, mock_web_service, sample_crawl_result):
        """Test that URL is properly trimmed."""
        # Arrange
        mock_web_service.extract_content.return_value = sample_crawl_result
        
        # Act
        result = await extract_content_use_case(mock_web_service, "  https://example.com  ")
        
        # Assert
        assert result == sample_crawl_result
        mock_web_service.extract_content.assert_called_once_with("https://example.com")
    
    @pytest.mark.asyncio
    async def test_extract_content_invalid_url_type(self, mock_web_service):
        """Test validation error when URL is not a string."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await extract_content_use_case(mock_web_service, 123)
        
        assert exc_info.value.code == "INVALID_URL_TYPE"
        mock_web_service.extract_content.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_extract_content_missing_url(self, mock_web_service):
        """Test validation error when URL is empty."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await extract_content_use_case(mock_web_service, "")
        
        assert exc_info.value.code == "MISSING_URL"
        mock_web_service.extract_content.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_extract_content_none_url(self, mock_web_service):
        """Test validation error when URL is None."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await extract_content_use_case(mock_web_service, None)
        
        assert exc_info.value.code == "INVALID_URL_TYPE"
        mock_web_service.extract_content.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_extract_content_whitespace_only_url(self, mock_web_service):
        """Test validation error when URL is only whitespace."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await extract_content_use_case(mock_web_service, "   ")
        
        assert exc_info.value.code == "MISSING_URL"
        mock_web_service.extract_content.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_extract_content_service_error(self, mock_web_service):
        """Test handling of service layer errors."""
        # Arrange
        mock_web_service.extract_content.side_effect = Exception("Network error")
        
        # Act & Assert
        with pytest.raises(Exception, match="Network error"):
            await extract_content_use_case(mock_web_service, "https://example.com")


class TestDeepCrawlUseCase:
    """Test deep_crawl_use_case function."""
    
    @pytest.mark.asyncio
    async def test_deep_crawl_success(self, mock_web_service, sample_crawl_result):
        """Test successful deep crawling."""
        # Arrange
        expected_results = [sample_crawl_result]
        mock_web_service.deep_crawl.return_value = expected_results
        
        # Act
        result = await deep_crawl_use_case(mock_web_service, "https://example.com")
        
        # Assert
        assert result == expected_results
        # Verify DeepCrawlConfig was created with default values
        mock_web_service.deep_crawl.assert_called_once()
        call_args = mock_web_service.deep_crawl.call_args[0][0]
        assert isinstance(call_args, DeepCrawlConfig)
        assert call_args.domain_url == "https://example.com"
        assert call_args.max_depth == 1
        assert call_args.max_pages == 10
        assert call_args.crawl_strategy == "bfs"
        assert call_args.include_external == False
    
    @pytest.mark.asyncio
    async def test_deep_crawl_custom_parameters(self, mock_web_service, sample_crawl_result):
        """Test deep crawling with custom parameters."""
        # Arrange
        expected_results = [sample_crawl_result]
        mock_web_service.deep_crawl.return_value = expected_results
        
        # Act
        result = await deep_crawl_use_case(
            mock_web_service, 
            "https://example.com",
            max_depth=3,
            max_pages=50,
            crawl_strategy="dfs",
            include_external=True,
            url_patterns=["*.html"],
            exclude_patterns=["*/admin/*"]
        )
        
        # Assert
        assert result == expected_results
        call_args = mock_web_service.deep_crawl.call_args[0][0]
        assert call_args.max_depth == 3
        assert call_args.max_pages == 50
        assert call_args.crawl_strategy == "dfs"
        assert call_args.include_external == True
        assert call_args.url_patterns == ["*.html"]
        assert call_args.exclude_patterns == ["*/admin/*"]
    
    @pytest.mark.asyncio
    async def test_deep_crawl_invalid_domain_url_type(self, mock_web_service):
        """Test validation error when domain URL is not a string."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await deep_crawl_use_case(mock_web_service, 123)
        
        assert exc_info.value.code == "INVALID_DOMAIN_URL_TYPE"
        mock_web_service.deep_crawl.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_deep_crawl_missing_domain_url(self, mock_web_service):
        """Test validation error when domain URL is empty."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await deep_crawl_use_case(mock_web_service, "")
        
        assert exc_info.value.code == "MISSING_DOMAIN_URL"
        mock_web_service.deep_crawl.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_deep_crawl_invalid_max_depth(self, mock_web_service):
        """Test validation error when max_depth is invalid."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await deep_crawl_use_case(mock_web_service, "https://example.com", max_depth=0)
        
        assert exc_info.value.code == "INVALID_MAX_DEPTH"
        mock_web_service.deep_crawl.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_deep_crawl_invalid_max_pages(self, mock_web_service):
        """Test validation error when max_pages is invalid."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await deep_crawl_use_case(mock_web_service, "https://example.com", max_pages=-1)
        
        assert exc_info.value.code == "INVALID_MAX_PAGES"
        mock_web_service.deep_crawl.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_deep_crawl_invalid_crawl_strategy(self, mock_web_service):
        """Test validation error when crawl_strategy is invalid."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await deep_crawl_use_case(mock_web_service, "https://example.com", crawl_strategy="invalid")
        
        assert exc_info.value.code == "INVALID_CRAWL_STRATEGY"
        mock_web_service.deep_crawl.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_deep_crawl_invalid_include_external_type(self, mock_web_service):
        """Test validation error when include_external is not a boolean."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await deep_crawl_use_case(mock_web_service, "https://example.com", include_external="yes")
        
        assert exc_info.value.code == "INVALID_INCLUDE_EXTERNAL_TYPE"
        mock_web_service.deep_crawl.assert_not_called()


class TestLinkPreviewUseCase:
    """Test link_preview_use_case function."""
    
    @pytest.mark.asyncio
    async def test_link_preview_success(self, mock_web_service, sample_link_preview):
        """Test successful link preview."""
        # Arrange
        mock_web_service.preview_links.return_value = sample_link_preview
        
        # Act
        result = await link_preview_use_case(mock_web_service, "https://example.com")
        
        # Assert
        assert result == sample_link_preview
        mock_web_service.preview_links.assert_called_once_with("https://example.com", False)
    
    @pytest.mark.asyncio
    async def test_link_preview_with_external(self, mock_web_service, sample_link_preview):
        """Test link preview with external links included."""
        # Arrange
        mock_web_service.preview_links.return_value = sample_link_preview
        
        # Act
        result = await link_preview_use_case(mock_web_service, "https://example.com", include_external=True)
        
        # Assert
        assert result == sample_link_preview
        mock_web_service.preview_links.assert_called_once_with("https://example.com", True)
    
    @pytest.mark.asyncio
    async def test_link_preview_domain_url_trimming(self, mock_web_service, sample_link_preview):
        """Test that domain URL is properly trimmed."""
        # Arrange
        mock_web_service.preview_links.return_value = sample_link_preview
        
        # Act
        result = await link_preview_use_case(mock_web_service, "  https://example.com  ")
        
        # Assert
        assert result == sample_link_preview
        mock_web_service.preview_links.assert_called_once_with("https://example.com", False)
    
    @pytest.mark.asyncio
    async def test_link_preview_invalid_domain_url_type(self, mock_web_service):
        """Test validation error when domain URL is not a string."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await link_preview_use_case(mock_web_service, 123)
        
        assert exc_info.value.code == "INVALID_DOMAIN_URL_TYPE"
        mock_web_service.preview_links.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_link_preview_missing_domain_url(self, mock_web_service):
        """Test validation error when domain URL is empty."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await link_preview_use_case(mock_web_service, "")
        
        assert exc_info.value.code == "MISSING_DOMAIN_URL"
        mock_web_service.preview_links.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_link_preview_invalid_include_external_type(self, mock_web_service):
        """Test validation error when include_external is not a boolean."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await link_preview_use_case(mock_web_service, "https://example.com", include_external="yes")
        
        assert exc_info.value.code == "INVALID_INCLUDE_EXTERNAL_TYPE"
        mock_web_service.preview_links.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_link_preview_service_error(self, mock_web_service):
        """Test handling of service layer errors."""
        # Arrange
        mock_web_service.preview_links.side_effect = Exception("Connection error")
        
        # Act & Assert
        with pytest.raises(Exception, match="Connection error"):
            await link_preview_use_case(mock_web_service, "https://example.com")


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