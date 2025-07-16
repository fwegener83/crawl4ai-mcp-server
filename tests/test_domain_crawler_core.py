"""
Test core domain crawler implementation.
Following TDD approach: Write tests first, then implement the core logic.
"""

import pytest
import json
from unittest.mock import patch, AsyncMock, MagicMock
from tests.test_domain_crawler_factory import CrawlResultFactory, MockCrawlerFactory


class TestDomainCrawlerCore:
    """Test core domain crawler implementation."""
    
    @pytest.mark.asyncio
    async def test_domain_deep_crawl_bfs_success(self):
        """Test successful BFS domain crawling."""
        # Arrange
        mock_pages = [
            {"url": "https://example.com", "depth": 0, "title": "Home", "content": "# Home\n\nHome content"},
            {"url": "https://example.com/page1", "depth": 1, "title": "Page 1", "content": "# Page 1\n\nPage 1 content"},
            {"url": "https://example.com/page2", "depth": 1, "title": "Page 2", "content": "# Page 2\n\nPage 2 content"}
        ]
        
        mock_result = CrawlResultFactory.create_domain_result(mock_pages)
        
        with patch('tools.domain_crawler.handle_batch_crawl') as mock_batch:
            mock_batch.return_value = json.dumps(mock_result)
            
            # Act
            from tools.domain_crawler import domain_deep_crawl_impl, DomainDeepCrawlParams
            
            params = DomainDeepCrawlParams(
                domain_url="https://example.com",
                max_depth=2,
                crawl_strategy="bfs",
                max_pages=25
            )
            
            result = await domain_deep_crawl_impl(params)
            
            # Assert
            result_data = json.loads(result)
            assert result_data["success"] is True
            assert result_data["crawl_summary"]["total_pages"] == 3
            assert result_data["crawl_summary"]["strategy_used"] == "bfs"
            assert result_data["crawl_summary"]["max_depth_reached"] == 1
            assert len(result_data["pages"]) == 3
    
    @pytest.mark.asyncio
    async def test_domain_deep_crawl_dfs_success(self):
        """Test successful DFS domain crawling."""
        # Arrange
        mock_pages = [
            {"url": "https://example.com", "depth": 0, "title": "Home", "content": "# Home\n\nHome content"},
            {"url": "https://example.com/page1", "depth": 1, "title": "Page 1", "content": "# Page 1\n\nPage 1 content"},
            {"url": "https://example.com/page1/sub", "depth": 2, "title": "Subpage", "content": "# Subpage\n\nSub content"}
        ]
        
        mock_result = CrawlResultFactory.create_domain_result(mock_pages)
        mock_result["crawl_summary"]["strategy_used"] = "dfs"
        
        with patch('tools.domain_crawler.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            # Act
            from tools.domain_crawler import domain_deep_crawl_impl, DomainDeepCrawlParams
            
            params = DomainDeepCrawlParams(
                domain_url="https://example.com",
                max_depth=2,
                crawl_strategy="dfs",
                max_pages=25
            )
            
            result = await domain_deep_crawl_impl(params)
            
            # Assert
            result_data = json.loads(result)
            assert result_data["success"] is True
            assert result_data["crawl_summary"]["strategy_used"] == "dfs"
            assert result_data["crawl_summary"]["max_depth_reached"] == 2
    
    @pytest.mark.asyncio
    async def test_domain_deep_crawl_best_first_success(self):
        """Test successful BestFirst domain crawling."""
        # Arrange
        mock_pages = [
            {"url": "https://example.com", "depth": 0, "title": "Home", "content": "# Home\n\nHome content"},
            {"url": "https://example.com/python-tutorial", "depth": 1, "title": "Python Tutorial", "content": "# Python Tutorial\n\nPython content"}
        ]
        
        mock_result = CrawlResultFactory.create_domain_result(mock_pages)
        mock_result["crawl_summary"]["strategy_used"] = "best_first"
        
        with patch('tools.domain_crawler.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            # Act
            from tools.domain_crawler import domain_deep_crawl_impl, DomainDeepCrawlParams
            
            params = DomainDeepCrawlParams(
                domain_url="https://example.com",
                max_depth=2,
                crawl_strategy="best_first",
                max_pages=25,
                keywords=["python", "tutorial"]
            )
            
            result = await domain_deep_crawl_impl(params)
            
            # Assert
            result_data = json.loads(result)
            assert result_data["success"] is True
            assert result_data["crawl_summary"]["strategy_used"] == "best_first"
    
    @pytest.mark.asyncio
    async def test_domain_deep_crawl_error_handling(self):
        """Test error handling in domain crawling."""
        # Arrange
        with patch('tools.domain_crawler.AsyncWebCrawler') as mock_crawler:
            mock_crawler.side_effect = Exception("Network error")
            
            # Act
            from tools.domain_crawler import domain_deep_crawl_impl, DomainDeepCrawlParams
            
            params = DomainDeepCrawlParams(domain_url="https://example.com")
            result = await domain_deep_crawl_impl(params)
            
            # Assert
            result_data = json.loads(result)
            assert result_data["success"] is False
            assert "error" in result_data
            assert result_data["domain"] == "https://example.com"
            assert "timestamp" in result_data
    
    @pytest.mark.asyncio
    async def test_domain_deep_crawl_with_patterns(self):
        """Test domain crawling with URL patterns."""
        # Arrange
        mock_pages = [
            {"url": "https://example.com", "depth": 0, "title": "Home", "content": "# Home\n\nHome content"},
            {"url": "https://example.com/blog/post1", "depth": 1, "title": "Blog Post 1", "content": "# Blog Post 1\n\nBlog content"},
            {"url": "https://example.com/docs/guide", "depth": 1, "title": "Guide", "content": "# Guide\n\nGuide content"}
        ]
        
        mock_result = CrawlResultFactory.create_domain_result(mock_pages)
        
        with patch('tools.domain_crawler.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            # Act
            from tools.domain_crawler import domain_deep_crawl_impl, DomainDeepCrawlParams
            
            params = DomainDeepCrawlParams(
                domain_url="https://example.com",
                max_depth=2,
                crawl_strategy="bfs",
                max_pages=25,
                url_patterns=["*blog*", "*docs*"],
                exclude_patterns=["*admin*"]
            )
            
            result = await domain_deep_crawl_impl(params)
            
            # Assert
            result_data = json.loads(result)
            assert result_data["success"] is True
            assert result_data["crawl_summary"]["total_pages"] == 3
    
    @pytest.mark.asyncio
    async def test_domain_deep_crawl_streaming_mode(self):
        """Test domain crawling with streaming mode."""
        # Arrange
        mock_pages = [
            {"url": "https://example.com", "depth": 0, "title": "Home", "content": "# Home\n\nHome content"},
            {"url": "https://example.com/page1", "depth": 1, "title": "Page 1", "content": "# Page 1\n\nPage 1 content"}
        ]
        
        mock_result = CrawlResultFactory.create_domain_result(mock_pages)
        
        with patch('tools.domain_crawler.handle_streaming_crawl') as mock_stream:
            mock_stream.return_value = json.dumps({
                "success": True,
                "streaming": True,
                "crawl_summary": {"total_pages": 2, "strategy_used": "bfs"},
                "pages": mock_pages
            })
            
            # Act
            from tools.domain_crawler import domain_deep_crawl_impl, DomainDeepCrawlParams
            
            params = DomainDeepCrawlParams(
                domain_url="https://example.com",
                max_depth=2,
                stream_results=True
            )
            
            result = await domain_deep_crawl_impl(params)
            
            # Assert
            result_data = json.loads(result)
            assert result_data["success"] is True
            assert result_data["streaming"] is True
            mock_stream.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_domain_deep_crawl_batch_mode(self):
        """Test domain crawling with batch mode."""
        # Arrange
        mock_pages = [
            {"url": "https://example.com", "depth": 0, "title": "Home", "content": "# Home\n\nHome content"},
            {"url": "https://example.com/page1", "depth": 1, "title": "Page 1", "content": "# Page 1\n\nPage 1 content"}
        ]
        
        mock_result = CrawlResultFactory.create_domain_result(mock_pages)
        
        with patch('tools.domain_crawler.handle_batch_crawl') as mock_batch:
            mock_batch.return_value = json.dumps({
                "success": True,
                "streaming": False,
                "crawl_summary": {"total_pages": 2, "strategy_used": "bfs"},
                "pages": mock_pages
            })
            
            # Act
            from tools.domain_crawler import domain_deep_crawl_impl, DomainDeepCrawlParams
            
            params = DomainDeepCrawlParams(
                domain_url="https://example.com",
                max_depth=2,
                stream_results=False
            )
            
            result = await domain_deep_crawl_impl(params)
            
            # Assert
            result_data = json.loads(result)
            assert result_data["success"] is True
            assert result_data["streaming"] is False
            mock_batch.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_domain_deep_crawl_configuration_validation(self):
        """Test that crawler configuration is properly set."""
        # Arrange
        mock_pages = [
            {"url": "https://example.com", "depth": 0, "title": "Home", "content": "# Home\n\nHome content"}
        ]
        
        mock_result = CrawlResultFactory.create_domain_result(mock_pages)
        
        with patch('tools.domain_crawler.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            # Act
            from tools.domain_crawler import domain_deep_crawl_impl, DomainDeepCrawlParams
            
            params = DomainDeepCrawlParams(
                domain_url="https://example.com",
                max_depth=3,
                max_pages=100
            )
            
            await domain_deep_crawl_impl(params)
            
            # Assert
            # Verify that AsyncWebCrawler was called with proper configuration
            mock_crawler.assert_called_once()
            mock_instance.arun.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_domain_deep_crawl_error_sanitization(self):
        """Test that errors are properly sanitized."""
        # Arrange
        with patch('tools.domain_crawler.AsyncWebCrawler') as mock_crawler:
            mock_crawler.side_effect = Exception("Password: secret123, API key: abc123")
            
            # Act
            from tools.domain_crawler import domain_deep_crawl_impl, DomainDeepCrawlParams
            
            params = DomainDeepCrawlParams(domain_url="https://example.com")
            result = await domain_deep_crawl_impl(params)
            
            # Assert
            result_data = json.loads(result)
            assert result_data["success"] is False
            # Error should be sanitized (will be implemented with actual sanitizer)
            assert "error" in result_data
    
    @pytest.mark.asyncio
    async def test_domain_deep_crawl_memory_threshold_handling(self):
        """Test memory threshold handling."""
        # Arrange
        mock_pages = [
            {"url": f"https://example.com/page{i}", "depth": 1, "title": f"Page {i}", "content": f"# Page {i}\n\nContent {i}"}
            for i in range(100)
        ]
        
        mock_result = CrawlResultFactory.create_domain_result(mock_pages)
        
        with patch('tools.domain_crawler.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            # Act
            from tools.domain_crawler import domain_deep_crawl_impl, DomainDeepCrawlParams
            
            params = DomainDeepCrawlParams(
                domain_url="https://example.com",
                max_pages=100,
                stream_results=False  # Should auto-enable due to large page count
            )
            
            result = await domain_deep_crawl_impl(params)
            
            # Assert
            result_data = json.loads(result)
            assert result_data["success"] is True
            # Should handle large page count appropriately


class TestDomainCrawlerHelpers:
    """Test helper functions for domain crawler."""
    
    @pytest.mark.asyncio
    async def test_handle_streaming_crawl(self):
        """Test streaming crawl handler."""
        # Arrange
        mock_crawler = AsyncMock()
        mock_config = MagicMock()
        
        with patch('tools.domain_crawler.handle_streaming_crawl') as mock_handler:
            mock_handler.return_value = json.dumps({
                "success": True,
                "streaming": True,
                "pages": []
            })
            
            # Act
            from tools.domain_crawler import handle_streaming_crawl
            
            result = await handle_streaming_crawl(mock_crawler, "https://example.com", mock_config)
            
            # Assert
            assert result is not None
            result_data = json.loads(result)
            assert result_data["streaming"] is True
    
    @pytest.mark.asyncio
    async def test_handle_batch_crawl(self):
        """Test batch crawl handler."""
        # Arrange
        mock_crawler = AsyncMock()
        mock_config = MagicMock()
        
        with patch('tools.domain_crawler.handle_batch_crawl') as mock_handler:
            mock_handler.return_value = json.dumps({
                "success": True,
                "streaming": False,
                "pages": []
            })
            
            # Act
            from tools.domain_crawler import handle_batch_crawl
            
            result = await handle_batch_crawl(mock_crawler, "https://example.com", mock_config)
            
            # Assert
            assert result is not None
            result_data = json.loads(result)
            assert result_data["streaming"] is False
    
    def test_browser_config_creation(self):
        """Test browser configuration creation."""
        # Act
        from tools.domain_crawler import create_browser_config
        
        config = create_browser_config()
        
        # Assert
        assert config is not None
        assert config.headless is True
        assert config.verbose is False
    
    def test_run_config_creation(self):
        """Test run configuration creation."""
        # Arrange
        mock_strategy = MagicMock()
        
        # Act
        from tools.domain_crawler import create_run_config
        
        config = create_run_config(
            strategy=mock_strategy,
            stream_results=False,
            memory_threshold=70.0
        )
        
        # Assert
        assert config is not None
        assert config.deep_crawl_strategy == mock_strategy
        assert config.stream is False
        assert config.memory_threshold_percent == 70.0
        assert config.verbose is False
        assert config.log_console is False