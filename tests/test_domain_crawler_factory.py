"""
Test factory for domain crawler test development.
This module provides comprehensive test data factories for domain deep crawling tests.
"""

import pytest
from datetime import datetime
from typing import Dict, List, Any
from unittest.mock import MagicMock, AsyncMock


class CrawlResultFactory:
    """Factory for creating mock crawl results for testing."""
    
    @staticmethod
    def create_success_result(
        content: str = "# Test Page\n\nTest content",
        title: str = "Test Page",
        url: str = "https://example.com",
        success: bool = True
    ) -> MagicMock:
        """Create a successful crawl result."""
        result = MagicMock()
        result.markdown = content
        result.title = title
        result.url = url
        result.success = success
        result.links = []
        result.metadata = {
            "crawl_time": datetime.utcnow().isoformat(),
            "status_code": 200
        }
        return result
    
    @staticmethod
    def create_domain_result(pages_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create mock domain crawl result."""
        def count_pages_by_depth(pages: List[Dict[str, Any]]) -> Dict[str, int]:
            depth_counts = {}
            for page in pages:
                depth = str(page.get("depth", 0))
                depth_counts[depth] = depth_counts.get(depth, 0) + 1
            return depth_counts
        
        return {
            "success": True,
            "crawl_summary": {
                "total_pages": len(pages_data),
                "max_depth_reached": max(page.get("depth", 0) for page in pages_data) if pages_data else 0,
                "strategy_used": "bfs",
                "pages_by_depth": count_pages_by_depth(pages_data)
            },
            "pages": pages_data
        }
    
    @staticmethod
    def create_link_preview_result(links_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create mock link preview result."""
        internal_count = sum(1 for link in links_data if link.get("type") == "internal")
        external_count = sum(1 for link in links_data if link.get("type") == "external")
        
        return {
            "success": True,
            "domain": "example.com",
            "total_links": len(links_data),
            "internal_links": internal_count,
            "external_links": external_count,
            "links": links_data
        }
    
    @staticmethod
    def create_error_result(error_message: str = "Test error") -> MagicMock:
        """Create a failed crawl result."""
        result = MagicMock()
        result.success = False
        result.error_message = error_message
        result.markdown = None
        result.title = None
        result.url = None
        return result


class MockCrawlerFactory:
    """Factory for creating mock AsyncWebCrawler instances."""
    
    @staticmethod
    def create_mock_crawler(mock_result: Any = None) -> AsyncMock:
        """Create a mock AsyncWebCrawler."""
        mock_crawler = AsyncMock()
        mock_instance = AsyncMock()
        
        # Set up context manager behavior
        mock_crawler.return_value.__aenter__ = AsyncMock(return_value=mock_instance)
        mock_crawler.return_value.__aexit__ = AsyncMock(return_value=None)
        
        # Set up crawl result
        if mock_result:
            mock_instance.arun.return_value = mock_result
        
        return mock_crawler
    
    @staticmethod
    def create_streaming_mock_crawler(results_sequence: List[Any]) -> AsyncMock:
        """Create a mock AsyncWebCrawler for streaming results."""
        mock_crawler = AsyncMock()
        mock_instance = AsyncMock()
        
        # Set up context manager behavior
        mock_crawler.return_value.__aenter__ = AsyncMock(return_value=mock_instance)
        mock_crawler.return_value.__aexit__ = AsyncMock(return_value=None)
        
        # Set up streaming results
        async def mock_arun(*args, **kwargs):
            for result in results_sequence:
                yield result
        
        mock_instance.arun.return_value = mock_arun()
        
        return mock_crawler


@pytest.fixture
def mock_successful_crawl_result():
    """Fixture for successful crawl result."""
    return CrawlResultFactory.create_success_result()


@pytest.fixture
def mock_domain_crawl_result():
    """Fixture for domain crawl result."""
    pages_data = [
        {"url": "https://example.com", "depth": 0, "title": "Home", "content": "# Home\n\nHome content"},
        {"url": "https://example.com/page1", "depth": 1, "title": "Page 1", "content": "# Page 1\n\nPage 1 content"},
        {"url": "https://example.com/page2", "depth": 1, "title": "Page 2", "content": "# Page 2\n\nPage 2 content"}
    ]
    return CrawlResultFactory.create_domain_result(pages_data)


@pytest.fixture
def mock_link_preview_result():
    """Fixture for link preview result."""
    links_data = [
        {"url": "https://example.com/about", "text": "About", "type": "internal"},
        {"url": "https://example.com/contact", "text": "Contact", "type": "internal"},
        {"url": "https://external.com", "text": "External", "type": "external"}
    ]
    return CrawlResultFactory.create_link_preview_result(links_data)


@pytest.fixture
def mock_error_result():
    """Fixture for error result."""
    return CrawlResultFactory.create_error_result("Network connection failed")


# Test the factory itself
class TestCrawlResultFactory:
    """Test the CrawlResultFactory functionality."""
    
    def test_create_success_result(self):
        """Test creating a successful crawl result."""
        result = CrawlResultFactory.create_success_result()
        
        assert result.markdown == "# Test Page\n\nTest content"
        assert result.title == "Test Page"
        assert result.url == "https://example.com"
        assert result.success is True
        assert result.links == []
        assert "crawl_time" in result.metadata
        assert result.metadata["status_code"] == 200
    
    def test_create_success_result_with_custom_data(self):
        """Test creating a successful crawl result with custom data."""
        result = CrawlResultFactory.create_success_result(
            content="# Custom Page\n\nCustom content",
            title="Custom Title",
            url="https://custom.com"
        )
        
        assert result.markdown == "# Custom Page\n\nCustom content"
        assert result.title == "Custom Title"
        assert result.url == "https://custom.com"
        assert result.success is True
    
    def test_create_domain_result(self):
        """Test creating a domain crawl result."""
        pages_data = [
            {"url": "https://example.com", "depth": 0, "title": "Home"},
            {"url": "https://example.com/page1", "depth": 1, "title": "Page 1"},
            {"url": "https://example.com/page2", "depth": 1, "title": "Page 2"}
        ]
        
        result = CrawlResultFactory.create_domain_result(pages_data)
        
        assert result["success"] is True
        assert result["crawl_summary"]["total_pages"] == 3
        assert result["crawl_summary"]["max_depth_reached"] == 1
        assert result["crawl_summary"]["strategy_used"] == "bfs"
        assert result["crawl_summary"]["pages_by_depth"] == {"0": 1, "1": 2}
        assert result["pages"] == pages_data
    
    def test_create_link_preview_result(self):
        """Test creating a link preview result."""
        links_data = [
            {"url": "https://example.com/about", "text": "About", "type": "internal"},
            {"url": "https://example.com/contact", "text": "Contact", "type": "internal"},
            {"url": "https://external.com", "text": "External", "type": "external"}
        ]
        
        result = CrawlResultFactory.create_link_preview_result(links_data)
        
        assert result["success"] is True
        assert result["domain"] == "example.com"
        assert result["total_links"] == 3
        assert result["internal_links"] == 2
        assert result["external_links"] == 1
        assert result["links"] == links_data
    
    def test_create_error_result(self):
        """Test creating an error result."""
        result = CrawlResultFactory.create_error_result("Connection timeout")
        
        assert result.success is False
        assert result.error_message == "Connection timeout"
        assert result.markdown is None
        assert result.title is None
        assert result.url is None


class TestMockCrawlerFactory:
    """Test the MockCrawlerFactory functionality."""
    
    def test_create_mock_crawler(self):
        """Test creating a mock crawler."""
        mock_result = CrawlResultFactory.create_success_result()
        mock_crawler = MockCrawlerFactory.create_mock_crawler(mock_result)
        
        assert mock_crawler is not None
        assert hasattr(mock_crawler, 'return_value')
    
    def test_create_streaming_mock_crawler(self):
        """Test creating a streaming mock crawler."""
        results = [
            CrawlResultFactory.create_success_result(url="https://example.com/page1"),
            CrawlResultFactory.create_success_result(url="https://example.com/page2")
        ]
        
        mock_crawler = MockCrawlerFactory.create_streaming_mock_crawler(results)
        
        assert mock_crawler is not None
        assert hasattr(mock_crawler, 'return_value')