"""
Tests for WebCrawlingService.

Tests the protocol-agnostic web crawling business logic
with mocked dependencies for isolation.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json

from services.web_crawling_service import WebCrawlingService
from services.interfaces import CrawlResult, DeepCrawlConfig, LinkPreview


class TestWebCrawlingService:
    """Test suite for WebCrawlingService."""
    
    @pytest.fixture
    def service(self):
        """Create a WebCrawlingService instance for testing."""
        return WebCrawlingService()
    
    @pytest.mark.asyncio
    async def test_extract_content_success(self, service):
        """Test successful content extraction."""
        # Mock the web_content_extract function
        mock_result = {
            "success": True,
            "content": "Test content from webpage",
            "title": "Test Page Title"
        }
        
        with patch('services.web_crawling_service.web_content_extract', new_callable=AsyncMock) as mock_extract:
            mock_extract.return_value = json.dumps(mock_result)
            
            result = await service.extract_content("https://example.com")
            
            assert isinstance(result, CrawlResult)
            assert result.url == "https://example.com"
            assert result.content == "Test content from webpage"
            assert result.error is None
            assert result.metadata["title"] == "Test Page Title"
            assert result.metadata["word_count"] == 4  # "Test content from webpage"
            assert result.metadata["extraction_method"] == "crawl4ai"
            
            # Check that web_content_extract was called with WebExtractParams
            mock_extract.assert_called_once()
            call_args = mock_extract.call_args[0][0]  # Get the first positional argument
            assert hasattr(call_args, 'url')
            assert call_args.url == "https://example.com"
    
    @pytest.mark.asyncio
    async def test_extract_content_failure(self, service):
        """Test content extraction failure."""
        mock_result = {
            "success": False,
            "error": "Failed to fetch URL"
        }
        
        with patch('services.web_crawling_service.web_content_extract', new_callable=AsyncMock) as mock_extract:
            mock_extract.return_value = json.dumps(mock_result)
            
            result = await service.extract_content("https://invalid-url.com")
            
            assert isinstance(result, CrawlResult)
            assert result.url == "https://invalid-url.com"
            assert result.content == ""
            assert result.error == "Failed to fetch URL"
            assert result.metadata == {}
    
    @pytest.mark.asyncio
    async def test_extract_content_exception(self, service):
        """Test content extraction with exception."""
        with patch('services.web_crawling_service.web_content_extract', new_callable=AsyncMock) as mock_extract:
            mock_extract.side_effect = Exception("Network error")
            
            result = await service.extract_content("https://example.com")
            
            assert isinstance(result, CrawlResult)
            assert result.url == "https://example.com"
            assert result.content == ""
            assert result.error == "Network error"
            assert result.metadata == {}
    
    @pytest.mark.asyncio
    async def test_deep_crawl_success(self, service):
        """Test successful deep crawling."""
        config = DeepCrawlConfig(
            domain_url="https://example.com",
            max_depth=2,
            max_pages=5,
            crawl_strategy="bfs"
        )
        
        mock_result = {
            "success": True,
            "pages": [
                {
                    "url": "https://example.com",
                    "title": "Home Page",
                    "content": "Welcome to our site",
                    "depth": 0
                },
                {
                    "url": "https://example.com/about",
                    "title": "About Page",
                    "content": "Learn about our company",
                    "depth": 1
                }
            ]
        }
        
        with patch('services.web_crawling_service.domain_deep_crawl', new_callable=AsyncMock) as mock_crawl:
            mock_crawl.return_value = json.dumps(mock_result)
            
            results = await service.deep_crawl(config)
            
            assert len(results) == 2
            
            # Check first result
            result1 = results[0]
            assert isinstance(result1, CrawlResult)
            assert result1.url == "https://example.com"
            assert result1.content == "Welcome to our site"
            assert result1.error is None
            assert result1.metadata["title"] == "Home Page"
            assert result1.metadata["depth"] == 0
            assert result1.metadata["crawl_strategy"] == "bfs"
            
            # Check second result
            result2 = results[1]
            assert result2.url == "https://example.com/about"
            assert result2.content == "Learn about our company"
            assert result2.metadata["title"] == "About Page"
            assert result2.metadata["depth"] == 1
            
            # Verify the mock was called with correct parameters
            mock_crawl.assert_called_once_with(
                domain_url="https://example.com",
                max_depth=2,
                max_pages=5,
                crawl_strategy="bfs",
                include_external=False
            )
    
    @pytest.mark.asyncio
    async def test_deep_crawl_with_patterns(self, service):
        """Test deep crawling with URL patterns."""
        config = DeepCrawlConfig(
            domain_url="https://example.com",
            url_patterns=["*/blog/*"],
            exclude_patterns=["*/admin/*"]
        )
        
        mock_result = {"success": True, "pages": []}
        
        with patch('services.web_crawling_service.domain_deep_crawl', new_callable=AsyncMock) as mock_crawl:
            mock_crawl.return_value = json.dumps(mock_result)
            
            await service.deep_crawl(config)
            
            # Verify patterns were passed correctly
            mock_crawl.assert_called_once_with(
                domain_url="https://example.com",
                max_depth=1,  # default
                max_pages=10,  # default
                crawl_strategy="bfs",  # default
                include_external=False,  # default
                url_patterns=["*/blog/*"],
                exclude_patterns=["*/admin/*"]
            )
    
    @pytest.mark.asyncio
    async def test_deep_crawl_failure(self, service):
        """Test deep crawling failure."""
        config = DeepCrawlConfig(domain_url="https://invalid-domain.com")
        
        mock_result = {
            "success": False,
            "error": "Domain not accessible"
        }
        
        with patch('services.web_crawling_service.domain_deep_crawl', new_callable=AsyncMock) as mock_crawl:
            mock_crawl.return_value = json.dumps(mock_result)
            
            results = await service.deep_crawl(config)
            
            assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_deep_crawl_exception(self, service):
        """Test deep crawling with exception."""
        config = DeepCrawlConfig(domain_url="https://example.com")
        
        with patch('services.web_crawling_service.domain_deep_crawl', new_callable=AsyncMock) as mock_crawl:
            mock_crawl.side_effect = Exception("Crawling error")
            
            results = await service.deep_crawl(config)
            
            assert len(results) == 1
            result = results[0]
            assert result.url == "https://example.com"
            assert result.content == ""
            assert result.error == "Crawling error"
            assert result.metadata["crawl_strategy"] == "bfs"
    
    @pytest.mark.asyncio
    async def test_preview_links_success(self, service):
        """Test successful link preview."""
        mock_result = {
            "success": True,
            "links": [
                "https://example.com/page1",
                "https://example.com/page2"
            ],
            "external_links": [
                "https://external.com/link1"
            ],
            "timestamp": "2025-01-05T23:00:00Z"
        }
        
        with patch('services.web_crawling_service.domain_link_preview', new_callable=AsyncMock) as mock_preview:
            mock_preview.return_value = json.dumps(mock_result)
            
            result = await service.preview_links("https://example.com", include_external=True)
            
            assert isinstance(result, LinkPreview)
            assert result.domain == "https://example.com"
            assert len(result.links) == 2
            assert "https://example.com/page1" in result.links
            assert "https://example.com/page2" in result.links
            assert len(result.external_links) == 1
            assert "https://external.com/link1" in result.external_links
            assert result.metadata["total_links"] == 2
            assert result.metadata["external_count"] == 1
            assert result.metadata["preview_timestamp"] == "2025-01-05T23:00:00Z"
            
            mock_preview.assert_called_once_with(
                domain_url="https://example.com",
                include_external=True
            )
    
    @pytest.mark.asyncio
    async def test_preview_links_without_external(self, service):
        """Test link preview without external links."""
        mock_result = {
            "success": True,
            "links": ["https://example.com/page1"],
            "external_links": []
        }
        
        with patch('services.web_crawling_service.domain_link_preview', new_callable=AsyncMock) as mock_preview:
            mock_preview.return_value = json.dumps(mock_result)
            
            result = await service.preview_links("https://example.com", include_external=False)
            
            assert result.external_links is None  # Should be None when not requested
            assert result.metadata["external_count"] == 0
            
            mock_preview.assert_called_once_with(
                domain_url="https://example.com",
                include_external=False
            )
    
    @pytest.mark.asyncio
    async def test_preview_links_failure(self, service):
        """Test link preview failure."""
        mock_result = {
            "success": False,
            "error": "Domain not found"
        }
        
        with patch('services.web_crawling_service.domain_link_preview', new_callable=AsyncMock) as mock_preview:
            mock_preview.return_value = json.dumps(mock_result)
            
            result = await service.preview_links("https://invalid-domain.com")
            
            assert isinstance(result, LinkPreview)
            assert result.domain == "https://invalid-domain.com"
            assert len(result.links) == 0
            assert result.external_links is None  # Should be None when include_external=False by default
            assert result.metadata["error"] == "Domain not found"
            assert result.metadata["total_links"] == 0
    
    @pytest.mark.asyncio
    async def test_preview_links_exception(self, service):
        """Test link preview with exception."""
        with patch('services.web_crawling_service.domain_link_preview', new_callable=AsyncMock) as mock_preview:
            mock_preview.side_effect = Exception("Preview error")
            
            result = await service.preview_links("https://example.com")
            
            assert result.domain == "https://example.com"
            assert len(result.links) == 0
            assert result.metadata["error"] == "Preview error"