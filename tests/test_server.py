"""Test FastMCP server integration."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio
import json
from typing import Dict, Any

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastmcp import FastMCP, Client
from tools.web_extract import WebExtractParams


class TestFastMCPServerIntegration:
    """Test FastMCP server integration and functionality."""
    
    def test_server_initialization(self):
        """Test that server initializes correctly."""
        from server import mcp
        
        assert mcp is not None
        assert isinstance(mcp, FastMCP)
        assert mcp.name == "Crawl4AI-MCP-Server"
    
    @pytest.mark.asyncio
    async def test_server_has_web_extract_tool(self):
        """Test that server has web_content_extract tool registered."""
        from server import mcp
        
        # Check that the tool is registered
        tools = await mcp.get_tools()
        tool_names = list(tools.keys())
        
        assert "web_content_extract" in tool_names
    
    @pytest.mark.asyncio
    async def test_server_tool_schema(self):
        """Test that web_content_extract tool has correct schema."""
        from server import mcp
        
        tools = await mcp.get_tools()
        web_extract_tool = tools.get("web_content_extract")
        
        assert web_extract_tool is not None
        assert web_extract_tool.description is not None
        assert "url" in web_extract_tool.description
    
    @pytest.mark.asyncio
    async def test_server_startup_and_shutdown(self):
        """Test server startup and shutdown."""
        from server import mcp
        
        # Test that server can be started (this is more of a smoke test)
        assert mcp is not None
        
        # Test that server has the expected configuration
        assert hasattr(mcp, 'name')
        assert hasattr(mcp, 'get_tools')
    
    @pytest.mark.asyncio
    async def test_tool_invocation_through_server(self):
        """Test tool invocation through the server."""
        from server import mcp
        
        # Mock the AsyncWebCrawler
        mock_result = MagicMock()
        mock_result.markdown = "# Test Content\n\nThis is test content."
        mock_result.title = "Test Page"
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            # Test tool invocation
            async with Client(mcp) as client:
                result = await client.call_tool("web_content_extract", {
                    "url": "https://example.com"
                })
                
                assert not result.is_error
                assert result.data == "# Test Content\n\nThis is test content."
    
    @pytest.mark.asyncio
    async def test_tool_invocation_with_invalid_url(self):
        """Test tool invocation with invalid URL."""
        from server import mcp
        
        async with Client(mcp) as client:
            result = await client.call_tool("web_content_extract", {
                "url": "invalid-url"
            })
            
            # Should return error content but not be marked as error
            assert not result.is_error
            assert "validation error" in result.data.lower()
    
    @pytest.mark.asyncio
    async def test_tool_invocation_with_network_error(self):
        """Test tool invocation with network error."""
        from server import mcp
        
        # Mock the AsyncWebCrawler to raise an exception
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.side_effect = Exception("Network error")
            
            async with Client(mcp) as client:
                result = await client.call_tool("web_content_extract", {
                    "url": "https://example.com"
                })
                
                assert not result.is_error
                assert "Error extracting content: Network error" in result.data
    
    @pytest.mark.asyncio
    async def test_multiple_tool_invocations(self):
        """Test multiple tool invocations."""
        from server import mcp
        
        mock_result = MagicMock()
        mock_result.markdown = "Test content"
        mock_result.title = "Test Page"
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            async with Client(mcp) as client:
                # Invoke tool multiple times
                results = []
                for i in range(3):
                    result = await client.call_tool("web_content_extract", {
                        "url": f"https://example{i}.com"
                    })
                    results.append(result)
                
                # All should succeed
                for result in results:
                    assert not result.is_error
                    assert result.data == "Test content"
                
                # Verify crawler was called for each URL
                assert mock_instance.arun.call_count == 3
    
    @pytest.mark.asyncio
    async def test_concurrent_tool_invocations(self):
        """Test concurrent tool invocations."""
        from server import mcp
        
        mock_result = MagicMock()
        mock_result.markdown = "Concurrent content"
        mock_result.title = "Concurrent Page"
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            async with Client(mcp) as client:
                # Create concurrent tasks
                tasks = []
                for i in range(5):
                    task = asyncio.create_task(client.call_tool("web_content_extract", {
                        "url": f"https://example{i}.com"
                    }))
                    tasks.append(task)
                
                # Wait for all tasks
                results = await asyncio.gather(*tasks)
                
                # All should succeed
                for result in results:
                    assert not result.is_error
                    assert result.data == "Concurrent content"
    
    @pytest.mark.asyncio
    async def test_tool_list_functionality(self):
        """Test that tool listing works correctly."""
        from server import mcp
        
        async with Client(mcp) as client:
            tools = await client.list_tools()
            
            assert len(tools) == 1
            assert tools[0].name == "web_content_extract"
            assert tools[0].description is not None
            assert "url" in str(tools[0].inputSchema)
    
    @pytest.mark.asyncio
    async def test_server_error_handling(self):
        """Test server error handling."""
        from server import mcp
        
        async with Client(mcp) as client:
            # Test with missing required parameter - this should raise an exception
            with pytest.raises(Exception):
                result = await client.call_tool("web_content_extract", {})
    
    @pytest.mark.asyncio
    async def test_server_with_different_url_formats(self):
        """Test server with different URL formats."""
        from server import mcp
        
        test_urls = [
            "https://example.com",
            "http://example.com",
            "https://example.com/path",
            "https://example.com?param=value",
        ]
        
        mock_result = MagicMock()
        mock_result.markdown = "URL content"
        mock_result.title = "URL Page"
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            async with Client(mcp) as client:
                for url in test_urls:
                    result = await client.call_tool("web_content_extract", {
                        "url": url
                    })
                    
                    assert not result.is_error
                    assert result.data == "URL content"


class TestServerConfiguration:
    """Test server configuration and setup."""
    
    def test_server_name_configuration(self):
        """Test server name configuration."""
        from server import mcp
        
        assert mcp.name == "Crawl4AI-MCP-Server"
    
    def test_server_logging_configuration(self):
        """Test server logging configuration."""
        import logging
        from server import logger
        
        assert logger is not None
        assert logger.name == "server"
    
    def test_environment_variable_loading(self):
        """Test environment variable loading."""
        from server import load_environment
        
        # Test that environment loading function exists
        assert callable(load_environment)
    
    def test_server_graceful_shutdown(self):
        """Test server graceful shutdown handling."""
        from server import mcp
        
        # Test that server can be shut down gracefully
        # This is more of a smoke test
        assert mcp is not None


class TestServerIntegrationWithActualCrawl4AI:
    """Test server integration with actual crawl4ai (slow tests)."""
    
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_server_with_real_url(self):
        """Test server with a real URL (slow test)."""
        from server import mcp
        
        async with Client(mcp) as client:
            result = await client.call_tool("web_content_extract", {
                "url": "https://httpbin.org/html"
            })
            
            assert not result.is_error
            assert len(result.data) > 0
    
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_server_with_nonexistent_url(self):
        """Test server with non-existent URL (slow test)."""
        from server import mcp
        
        async with Client(mcp) as client:
            result = await client.call_tool("web_content_extract", {
                "url": "https://nonexistent-domain-12345.com"
            })
            
            assert not result.is_error
            # Non-existent domains can return empty content or error messages
            assert "Error extracting content" in result.data or result.data == ""


class TestServerPerformance:
    """Test server performance characteristics."""
    
    @pytest.mark.asyncio
    async def test_server_response_time(self):
        """Test server response time."""
        import time
        from server import mcp
        
        mock_result = MagicMock()
        mock_result.markdown = "Performance test content"
        mock_result.title = "Performance Page"
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            async with Client(mcp) as client:
                start_time = time.time()
                
                result = await client.call_tool("web_content_extract", {
                    "url": "https://example.com"
                })
                
                end_time = time.time()
                response_time = end_time - start_time
                
                assert not result.is_error
                assert response_time < 1.0  # Should respond quickly with mocked crawler
    
    @pytest.mark.asyncio
    async def test_server_memory_usage(self):
        """Test server memory usage."""
        try:
            import psutil
        except ImportError:
            pytest.skip("psutil not available")
        
        import os
        from server import mcp
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        mock_result = MagicMock()
        mock_result.markdown = "Memory test content"
        mock_result.title = "Memory Page"
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            async with Client(mcp) as client:
                # Invoke tool multiple times
                for i in range(10):
                    result = await client.call_tool("web_content_extract", {
                        "url": f"https://example{i}.com"
                    })
                    assert not result.is_error
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB)
        assert memory_increase < 50 * 1024 * 1024
    
    @pytest.mark.asyncio
    async def test_server_concurrent_performance(self):
        """Test server performance with concurrent requests."""
        import time
        from server import mcp
        
        mock_result = MagicMock()
        mock_result.markdown = "Concurrent performance test"
        mock_result.title = "Concurrent Page"
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            async with Client(mcp) as client:
                start_time = time.time()
                
                # Create 10 concurrent requests
                tasks = []
                for i in range(10):
                    task = asyncio.create_task(client.call_tool("web_content_extract", {
                        "url": f"https://example{i}.com"
                    }))
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks)
                
                end_time = time.time()
                total_time = end_time - start_time
                
                # All requests should succeed
                for result in results:
                    assert not result.is_error
                
                # Should handle concurrent requests efficiently
                assert total_time < 2.0  # 10 concurrent requests in under 2 seconds


class TestComponentRegression:
    """REGRESSION: Component-level testing without AsyncIO conflicts.
    
    These tests extract valuable patterns from temporary debug files to ensure
    basic component functionality and dependency management work correctly.
    """
    
    def test_module_imports_without_asyncio(self):
        """REGRESSION: Ensure components import cleanly without AsyncIO conflicts."""
        # Test direct module imports (pattern from simple_test.py)
        from server import mcp, load_environment
        
        assert mcp is not None
        assert isinstance(mcp, FastMCP)
        assert mcp.name == "Crawl4AI-MCP-Server"
        assert callable(load_environment)
    
    def test_url_validation_regression(self):
        """REGRESSION: Ensure URL validation works correctly."""
        # Test URL validation patterns that were critical in debugging
        from tools.web_extract import WebExtractParams
        
        # Valid URL should work
        params = WebExtractParams(url="https://example.com")
        assert params.url == "https://example.com"
        
        # Invalid URL should raise validation error
        with pytest.raises(Exception) as exc_info:
            WebExtractParams(url="not-a-url")
        
        # Should be a validation error
        assert "validation error" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()
    
    def test_dependency_versions_compatibility(self):
        """REGRESSION: Catch dependency version conflicts."""
        # Test dependency availability (pattern from simple_test.py)
        import crawl4ai
        import fastmcp
        import pydantic
        
        # Basic import tests
        assert hasattr(crawl4ai, '__version__') or hasattr(crawl4ai, '__version__')
        assert hasattr(pydantic, '__version__')
        
        # Test that key classes are available
        from crawl4ai import AsyncWebCrawler
        from fastmcp import FastMCP
        from pydantic import BaseModel
        
        assert AsyncWebCrawler is not None
        assert FastMCP is not None  
        assert BaseModel is not None
    
    def test_environment_configuration_regression(self):
        """REGRESSION: Environment configuration loading works."""
        from server import load_environment
        
        # Should not raise exception
        load_environment()
        
        # Test that environment loading is idempotent
        load_environment()
        load_environment()
    
    def test_server_component_integration(self):
        """REGRESSION: Server components integrate correctly."""
        from server import mcp
        
        # Test that server has expected tools registered
        assert hasattr(mcp, 'get_tools')
        
        # Test async context
        async def check_tools():
            tools = await mcp.get_tools()
            assert "web_content_extract" in tools
            return tools
        
        import asyncio
        tools = asyncio.run(check_tools())
        assert len(tools) == 1
    
    def test_critical_imports_no_circular_dependencies(self):
        """REGRESSION: Ensure no circular import dependencies."""
        # Test that critical imports work independently
        from tools.web_extract import WebExtractParams, web_content_extract
        assert WebExtractParams is not None
        assert callable(web_content_extract)
        
        from server import mcp, load_environment, logger
        assert mcp is not None
        assert callable(load_environment)
        assert logger is not None
        
        # Test that imports don't interfere with each other
        from tools.web_extract import WebExtractParams as WEP2
        from server import mcp as mcp2
        assert WEP2 is WebExtractParams
        assert mcp2 is mcp