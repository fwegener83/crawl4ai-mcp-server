"""Mock factory framework tests."""
import pytest
import asyncio
import os
import time
from unittest.mock import AsyncMock, patch, MagicMock


class TestCrawlResultFactory:
    """Test crawl result factory for creating realistic mock results."""
    
    def test_crawl_result_factory_success(self):
        """Test successful crawl result mock creation."""
        # This test will FAIL initially (Red phase) - CrawlResultFactory doesn't exist yet
        from tests.factories import CrawlResultFactory
        
        result = CrawlResultFactory.create_success_result(
            content="Test content",
            title="Test Title"
        )
        
        # Validate result structure
        assert result.markdown == "Test content"
        assert result.title == "Test Title" 
        assert result.success is True
        assert hasattr(result, 'url')
        assert hasattr(result, 'status_code')

    def test_crawl_result_factory_failure(self):
        """Test failure result mock creation."""
        from tests.factories import CrawlResultFactory
        
        result = CrawlResultFactory.create_failure_result(
            error_msg="Network error",
            url="https://example.com"
        )
        
        # Validate failure result structure
        assert result.markdown is None
        assert result.title is None
        assert result.success is False
        assert result.url == "https://example.com"
        assert result.error_message == "Network error"

    def test_crawl_result_factory_timeout(self):
        """Test timeout result mock creation."""
        from tests.factories import CrawlResultFactory
        
        result = CrawlResultFactory.create_timeout_result(url="https://slow-site.com")
        
        # Validate timeout result structure
        assert result.success is False
        assert result.url == "https://slow-site.com"
        assert "timeout" in result.error_message.lower()

    def test_crawl_result_factory_with_custom_attributes(self):
        """Test result factory with custom attributes."""
        from tests.factories import CrawlResultFactory
        
        result = CrawlResultFactory.create_success_result(
            content="# Custom Content\\n\\nThis is custom.",
            title="Custom Title",
            url="https://custom.com"
        )
        
        # Validate all expected attributes exist
        required_attributes = [
            'markdown', 'title', 'success', 'url', 'status_code',
            'cleaned_html', 'extracted_content', 'screenshot', 'links', 'media'
        ]
        
        for attr in required_attributes:
            assert hasattr(result, attr), f"Missing required attribute: {attr}"


class TestAsyncWebCrawlerMock:
    """Test AsyncWebCrawler mocking utilities."""
    
    @pytest.mark.asyncio
    async def test_async_web_crawler_mock_context_manager(self):
        """Test AsyncWebCrawler mock as context manager."""
        # This test will FAIL initially - need to implement async context manager helpers
        from tests.factories import AsyncWebCrawlerMockFactory
        
        mock_crawler, mock_instance = AsyncWebCrawlerMockFactory.create_mock()
        
        with patch('tools.web_extract.AsyncWebCrawler', mock_crawler):
            # Test that context manager mocking works
            async with mock_crawler() as crawler_instance:
                assert crawler_instance is mock_instance
                
                # Test that arun method exists and is callable
                assert hasattr(crawler_instance, 'arun')
                assert callable(crawler_instance.arun)

    @pytest.mark.asyncio
    async def test_async_web_crawler_mock_with_result(self):
        """Test AsyncWebCrawler mock with predefined result."""
        from tests.factories import AsyncWebCrawlerMockFactory, CrawlResultFactory
        
        # Create a test result
        test_result = CrawlResultFactory.create_success_result(
            content="Mock content",
            title="Mock Title"
        )
        
        mock_crawler, mock_instance = AsyncWebCrawlerMockFactory.create_mock(
            default_result=test_result
        )
        
        with patch('tools.web_extract.AsyncWebCrawler', mock_crawler):
            async with mock_crawler() as crawler_instance:
                result = await crawler_instance.arun(url="https://example.com")
                
                assert result.markdown == "Mock content"
                assert result.title == "Mock Title"
                assert result.success is True

    @pytest.mark.asyncio
    async def test_configurable_response_patterns(self):
        """Test configurable response patterns for different URLs."""
        from tests.factories import AsyncWebCrawlerMockFactory
        
        # Define response patterns
        response_config = {
            'javascript:': ValueError("Invalid URL scheme"),
            '127.0.0.1': ConnectionError("Private IP blocked"),
            ':22/': ConnectionRefusedError("Port blocked"),
            'default': 'success'
        }
        
        mock_crawler, mock_instance = AsyncWebCrawlerMockFactory.create_mock(
            response_config=response_config
        )
        
        with patch('tools.web_extract.AsyncWebCrawler', mock_crawler):
            async with mock_crawler() as crawler_instance:
                # Test different URL patterns
                test_cases = [
                    ("javascript:alert('test')", ValueError),
                    ("http://127.0.0.1/admin", ConnectionError),
                    ("http://example.com:22/ssh", ConnectionRefusedError),
                    ("https://example.com", None)  # Should succeed
                ]
                
                for url, expected_exception in test_cases:
                    if expected_exception:
                        with pytest.raises(expected_exception):
                            await crawler_instance.arun(url=url)
                    else:
                        result = await crawler_instance.arun(url=url)
                        assert result.success is True


class TestSecurityMockFactory:
    """Test security scenario mock factory."""
    
    def test_security_scenario_mock_factory_creation(self):
        """Test security scenario mock factory can be created."""
        # This test will FAIL initially - SecurityMockFactory doesn't exist yet
        from tests.factories import SecurityMockFactory
        
        factory = SecurityMockFactory()
        assert factory is not None
        assert hasattr(factory, 'mock_response')

    def test_malicious_url_blocking_patterns(self):
        """Test malicious URL blocking mock responses."""
        from tests.factories import SecurityMockFactory
        
        factory = SecurityMockFactory()
        
        malicious_urls = [
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>",
            "file:///etc/passwd"
        ]
        
        for url in malicious_urls:
            with pytest.raises(ValueError, match="Invalid URL scheme"):
                factory.mock_response(url)

    def test_private_ip_blocking_patterns(self):
        """Test private IP blocking mock responses."""
        from tests.factories import SecurityMockFactory
        
        factory = SecurityMockFactory()
        
        private_ips = [
            "http://127.0.0.1/admin",
            "http://localhost:8080/admin",
            "http://192.168.1.1/router"
        ]
        
        for url in private_ips:
            with pytest.raises(ConnectionError, match="Private IP"):
                factory.mock_response(url)

    def test_port_scanning_blocking_patterns(self):
        """Test port scanning prevention mock responses."""
        from tests.factories import SecurityMockFactory
        
        factory = SecurityMockFactory()
        
        suspicious_ports = [
            "http://example.com:22/ssh",
            "http://example.com:3306/mysql",
            "http://example.com:5432/postgresql"
        ]
        
        for url in suspicious_ports:
            with pytest.raises(ConnectionRefusedError, match="Port"):
                factory.mock_response(url)

    def test_safe_url_success_response(self):
        """Test safe URLs return success responses."""
        from tests.factories import SecurityMockFactory, CrawlResultFactory
        
        factory = SecurityMockFactory()
        
        safe_urls = [
            "https://example.com",
            "https://httpbin.org/get",
            "http://example.com/safe-path"
        ]
        
        for url in safe_urls:
            result = factory.mock_response(url)
            assert result.success is True
            assert result.url == url
            assert isinstance(result.markdown, str)


class TestMockUtilities:
    """Test mock utility functions."""
    
    def test_async_context_manager_mock_utility(self):
        """Test async context manager mock utility."""
        # This test will FAIL initially - need to implement utility
        from tests.factories import AsyncContextManagerMock
        
        mock_instance = AsyncMock()
        context_mock = AsyncContextManagerMock(mock_instance)
        
        # Test that it's a proper async context manager
        assert hasattr(context_mock, '__aenter__')
        assert hasattr(context_mock, '__aexit__')

    @pytest.mark.asyncio
    async def test_async_context_manager_mock_behavior(self):
        """Test async context manager mock behavior."""
        from tests.factories import AsyncContextManagerMock
        
        mock_instance = AsyncMock()
        mock_instance.test_method.return_value = "test_result"
        
        context_mock = AsyncContextManagerMock(mock_instance)
        
        async with context_mock as instance:
            assert instance is mock_instance
            result = await instance.test_method()
            assert result == "test_result"

    def test_mock_configuration_validation(self):
        """Test mock configuration validation."""
        from tests.factories import MockConfigValidator
        
        # Test valid configuration
        valid_config = {
            'javascript:': ValueError("Invalid URL scheme"),
            '127.0.0.1': ConnectionError("Private IP blocked"),
            'default': 'success'
        }
        
        assert MockConfigValidator.validate(valid_config) is True
        
        # Test invalid configuration
        invalid_config = {
            'pattern1': "not_an_exception",  # Should be exception or 'success'
        }
        
        assert MockConfigValidator.validate(invalid_config) is False

    def test_performance_mock_timing(self):
        """Test that mocked operations are fast."""
        import time
        from tests.factories import SecurityMockFactory
        
        factory = SecurityMockFactory()
        
        start_time = time.perf_counter()
        
        # Run multiple mock operations
        for i in range(100):
            try:
                factory.mock_response(f"javascript:alert('{i}')")
            except ValueError:
                pass  # Expected
        
        duration = time.perf_counter() - start_time
        
        # Mock operations should be extremely fast
        assert duration < 0.1, f"Mock operations too slow: {duration:.4f}s"


class TestMockIntegration:
    """Test mock integration with existing codebase."""
    
    @pytest.mark.asyncio
    async def test_mock_integration_with_fastmcp_client(self):
        """Test mock integration with FastMCP Client."""
        from tests.factories import AsyncWebCrawlerMockFactory, CrawlResultFactory
        from fastmcp import Client
        
        # Create mock that simulates successful crawling
        test_result = CrawlResultFactory.create_success_result(
            content="Integration test content",
            title="Integration Test"
        )
        
        mock_crawler, mock_instance = AsyncWebCrawlerMockFactory.create_mock(
            default_result=test_result
        )
        
        with patch('tools.web_extract.AsyncWebCrawler', mock_crawler):
            from server import mcp
            
            async with Client(mcp) as client:
                result = await client.call_tool_mcp("web_content_extract", {
                    "url": "https://example.com"
                })
                
                # Verify integration works
                assert result.isError is False
                assert "Integration test content" in result.content[0].text

    @pytest.mark.asyncio
    async def test_mock_preserves_error_handling(self):
        """Test that mocks preserve proper error handling."""
        from tests.factories import AsyncWebCrawlerMockFactory
        from fastmcp import Client
        
        # Mock that raises exceptions
        def error_side_effect(url=None, config=None):
            if 'javascript:' in url:
                raise ValueError(f"Invalid URL scheme: {url}")
            else:
                raise ConnectionError("Network error")
        
        mock_crawler, mock_instance = AsyncWebCrawlerMockFactory.create_mock()
        mock_instance.arun.side_effect = error_side_effect
        
        with patch('tools.web_extract.AsyncWebCrawler', mock_crawler):
            from server import mcp
            
            async with Client(mcp) as client:
                # Test malicious URL handling
                result = await client.call_tool_mcp("web_content_extract", {
                    "url": "javascript:alert('test')"
                })
                
                # Should be blocked at FastMCP level or return error
                assert result.isError or "error" in result.content[0].text.lower()

    def test_mock_factory_performance_targets(self):
        """Test mock factory meets performance targets."""
        import time
        from tests.factories import CrawlResultFactory, SecurityMockFactory
        
        # Test CrawlResultFactory performance
        start_time = time.perf_counter()
        
        for i in range(1000):
            result = CrawlResultFactory.create_success_result(
                content=f"Content {i}",
                title=f"Title {i}"
            )
            assert result.success is True
        
        factory_duration = time.perf_counter() - start_time
        # CI environments can be slower, allow more generous timeout
        max_duration = 0.2 if os.getenv('CI') else 0.1
        assert factory_duration < max_duration, f"CrawlResultFactory too slow: {factory_duration:.4f}s (max: {max_duration}s)"
        
        # Test SecurityMockFactory performance
        factory = SecurityMockFactory()
        start_time = time.perf_counter()
        
        for i in range(1000):
            try:
                factory.mock_response(f"javascript:alert('{i}')")
            except ValueError:
                pass  # Expected
        
        security_duration = time.perf_counter() - start_time
        assert security_duration < 0.1, f"SecurityMockFactory too slow: {security_duration:.4f}s"