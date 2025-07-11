"""Test web content extraction functionality."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio
from pydantic import ValidationError

# We'll create this module in the next step
from tools.web_extract import WebExtractParams, web_content_extract, safe_extract


class TestWebExtractParams:
    """Test WebExtractParams model validation."""
    
    def test_valid_url_parameter(self):
        """Test that valid URLs are accepted."""
        params = WebExtractParams(url="https://example.com")
        assert params.url == "https://example.com"
    
    def test_valid_http_url(self):
        """Test that HTTP URLs are accepted."""
        params = WebExtractParams(url="http://example.com")
        assert params.url == "http://example.com"
    
    def test_url_with_path(self):
        """Test that URLs with paths are accepted."""
        params = WebExtractParams(url="https://example.com/path/to/page")
        assert params.url == "https://example.com/path/to/page"
    
    def test_url_with_query_params(self):
        """Test that URLs with query parameters are accepted."""
        params = WebExtractParams(url="https://example.com?param=value&other=123")
        assert params.url == "https://example.com?param=value&other=123"
    
    def test_empty_url_raises_validation_error(self):
        """Test that empty URL raises validation error."""
        with pytest.raises(ValidationError):
            WebExtractParams(url="")
    
    def test_none_url_raises_validation_error(self):
        """Test that None URL raises validation error."""
        with pytest.raises(ValidationError):
            WebExtractParams(url=None)
    
    def test_invalid_url_format_raises_validation_error(self):
        """Test that invalid URL format raises validation error."""
        with pytest.raises(ValidationError):
            WebExtractParams(url="not-a-valid-url")
    
    def test_model_serialization(self):
        """Test that model can be serialized."""
        params = WebExtractParams(url="https://example.com")
        serialized = params.model_dump()
        assert serialized == {"url": "https://example.com"}
    
    def test_model_deserialization(self):
        """Test that model can be deserialized."""
        data = {"url": "https://example.com"}
        params = WebExtractParams(**data)
        assert params.url == "https://example.com"


class TestWebContentExtract:
    """Test web_content_extract function."""
    
    @pytest.mark.asyncio
    async def test_successful_extraction(self):
        """Test successful content extraction."""
        mock_result = MagicMock()
        mock_result.markdown = "# Test Content\n\nThis is test content."
        mock_result.title = "Test Page"
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            params = WebExtractParams(url="https://example.com")
            result = await web_content_extract(params)
            
            assert result == "# Test Content\n\nThis is test content."
            mock_instance.arun.assert_called_once_with(url="https://example.com")
    
    @pytest.mark.asyncio
    async def test_extraction_with_empty_content(self):
        """Test extraction that returns empty content."""
        mock_result = MagicMock()
        mock_result.markdown = ""
        mock_result.title = "Empty Page"
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            params = WebExtractParams(url="https://example.com")
            result = await web_content_extract(params)
            
            assert result == ""
    
    @pytest.mark.asyncio
    async def test_extraction_with_network_error(self):
        """Test extraction with network error."""
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.side_effect = Exception("Network error")
            
            params = WebExtractParams(url="https://example.com")
            result = await web_content_extract(params)
            
            assert "Error extracting content: Network error" in result
    
    @pytest.mark.asyncio
    async def test_extraction_with_timeout_error(self):
        """Test extraction with timeout error."""
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.side_effect = asyncio.TimeoutError("Request timed out")
            
            params = WebExtractParams(url="https://example.com")
            result = await web_content_extract(params)
            
            assert "Error extracting content: Request timed out" in result
    
    @pytest.mark.asyncio
    async def test_extraction_with_invalid_response(self):
        """Test extraction with invalid response."""
        mock_result = MagicMock()
        mock_result.markdown = None  # Invalid response
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            params = WebExtractParams(url="https://example.com")
            result = await web_content_extract(params)
            
            # Should handle None markdown gracefully
            assert result == "" or "Error extracting content" in result
    
    @pytest.mark.asyncio
    async def test_extraction_with_various_urls(self):
        """Test extraction with various URL formats."""
        test_urls = [
            "https://example.com",
            "http://example.com",
            "https://example.com/path",
            "https://example.com?param=value",
            "https://subdomain.example.com",
        ]
        
        mock_result = MagicMock()
        mock_result.markdown = "Test content"
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            for url in test_urls:
                params = WebExtractParams(url=url)
                result = await web_content_extract(params)
                assert result == "Test content"


class TestSafeExtract:
    """Test safe_extract function."""
    
    @pytest.mark.asyncio
    async def test_successful_safe_extraction(self):
        """Test successful safe extraction."""
        mock_result = MagicMock()
        mock_result.markdown = "# Test Content"
        mock_result.title = "Test Page"
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            result = await safe_extract("https://example.com")
            
            assert result["success"] is True
            assert result["content"] == "# Test Content"
            assert result["url"] == "https://example.com"
            assert result["title"] == "Test Page"
    
    @pytest.mark.asyncio
    async def test_safe_extraction_with_no_title(self):
        """Test safe extraction when no title is available."""
        mock_result = MagicMock()
        mock_result.markdown = "# Test Content"
        mock_result.title = None
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            result = await safe_extract("https://example.com")
            
            assert result["success"] is True
            assert result["title"] == "No title"
    
    @pytest.mark.asyncio
    async def test_safe_extraction_with_error(self):
        """Test safe extraction with error handling."""
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.side_effect = Exception("Network error")
            
            result = await safe_extract("https://example.com")
            
            assert result["success"] is False
            assert result["error"] == "Network error"
            assert result["url"] == "https://example.com"
            assert result["content"] is None
    
    @pytest.mark.asyncio
    async def test_safe_extraction_error_logging(self):
        """Test that errors are logged properly."""
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler, \
             patch('tools.web_extract.logger') as mock_logger:
            
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.side_effect = Exception("Network error")
            
            result = await safe_extract("https://example.com")
            
            # Verify error was logged
            mock_logger.error.assert_called_once()
            assert "Content extraction failed for https://example.com" in str(mock_logger.error.call_args)
    
    @pytest.mark.asyncio
    async def test_safe_extraction_with_different_error_types(self):
        """Test safe extraction with different error types."""
        error_types = [
            ValueError("Invalid URL"),
            ConnectionError("Connection failed"),
            TimeoutError("Request timed out"),
            Exception("Generic error"),
        ]
        
        for error in error_types:
            with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
                mock_instance = AsyncMock()
                mock_crawler.return_value.__aenter__.return_value = mock_instance
                mock_instance.arun.side_effect = error
                
                result = await safe_extract("https://example.com")
                
                assert result["success"] is False
                assert str(error) in result["error"]
    
    @pytest.mark.asyncio
    async def test_safe_extraction_return_format(self):
        """Test that safe extraction returns correct format."""
        mock_result = MagicMock()
        mock_result.markdown = "Content"
        mock_result.title = "Title"
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            result = await safe_extract("https://example.com")
            
            # Check that all required keys are present
            required_keys = ["success", "content", "url", "title"]
            for key in required_keys:
                assert key in result
            
            # Check types
            assert isinstance(result["success"], bool)
            assert isinstance(result["content"], str)
            assert isinstance(result["url"], str)
            assert isinstance(result["title"], str)


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.mark.asyncio
    async def test_malformed_url_handling(self):
        """Test handling of malformed URLs that pass validation."""
        # URLs that might pass basic validation but fail in crawler
        problematic_urls = [
            "https://localhost:-1",
            "https://example.com:99999",
        ]
        
        for url in problematic_urls:
            with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
                mock_instance = AsyncMock()
                mock_crawler.return_value.__aenter__.return_value = mock_instance
                mock_instance.arun.side_effect = Exception(f"Invalid URL: {url}")
                
                params = WebExtractParams(url=url)
                result = await web_content_extract(params)
                
                assert "Error extracting content" in result
    
    @pytest.mark.asyncio
    async def test_large_content_handling(self):
        """Test handling of large content."""
        large_content = "# Large Content\n" + "A" * 10000
        
        mock_result = MagicMock()
        mock_result.markdown = large_content
        mock_result.title = "Large Page"
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            params = WebExtractParams(url="https://example.com")
            result = await web_content_extract(params)
            
            assert result == large_content
    
    @pytest.mark.asyncio
    async def test_unicode_content_handling(self):
        """Test handling of Unicode content."""
        unicode_content = "# Unicode Test\n\n你好世界 🌍 café naïve résumé"
        
        mock_result = MagicMock()
        mock_result.markdown = unicode_content
        mock_result.title = "Unicode Page"
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            params = WebExtractParams(url="https://example.com")
            result = await web_content_extract(params)
            
            assert result == unicode_content
    
    @pytest.mark.asyncio
    async def test_concurrent_extractions(self):
        """Test concurrent content extractions."""
        mock_result = MagicMock()
        mock_result.markdown = "Concurrent content"
        mock_result.title = "Concurrent Page"
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            # Create multiple concurrent tasks
            tasks = []
            for i in range(5):
                params = WebExtractParams(url=f"https://example{i}.com")
                task = asyncio.create_task(web_content_extract(params))
                tasks.append(task)
            
            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks)
            
            # Verify all results are correct
            for result in results:
                assert result == "Concurrent content"
            
            # Verify crawler was called for each URL
            assert mock_instance.arun.call_count == 5