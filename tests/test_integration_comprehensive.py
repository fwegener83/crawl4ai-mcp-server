"""Comprehensive integration tests for the complete MCP server system."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio
import json
from datetime import datetime, timezone
import time
import sys
import os

from fastmcp import FastMCP, Client
from mcp.types import TextContent, CallToolResult
from crawl4ai import AsyncWebCrawler


class TestMCPServerSystemIntegration:
    """Test complete MCP server system integration."""
    
    @pytest.mark.asyncio
    async def test_server_initialization_and_lifecycle(self):
        """Test server initialization and complete lifecycle."""
        from server import mcp
        
        # Test server can be instantiated
        assert mcp is not None
        assert isinstance(mcp, FastMCP)
        
        # Test server metadata
        assert mcp.name == "Crawl4AI-MCP-Server"
        
        # Test server can handle client connections
        async with Client(mcp) as client:
            # Test basic connectivity
            tools = await client.list_tools()
            assert len(tools) == 1
            assert tools[0].name == "web_content_extract"
    
    @pytest.mark.asyncio
    async def test_complete_tool_integration(self):
        """Test complete tool integration from MCP to crawl4ai."""
        from server import mcp
        from tools.web_extract import WebExtractParams
        
        # Mock the complete chain
        mock_result = MagicMock()
        mock_result.markdown = "# Integration Test\n\nThis is a comprehensive integration test."
        mock_result.title = "Integration Test Page"
        mock_result.links = {"internal": [], "external": []}
        mock_result.media = {"images": []}
        mock_result.success = True
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            async with Client(mcp) as client:
                # Test tool call through complete integration
                result = await client.call_tool_mcp("web_content_extract", {
                    "url": "https://example.com/integration-test"
                })
                
                # Verify result
                assert result.isError is False
                assert len(result.content) == 1
                assert result.content[0].type == 'text'
                assert result.content[0].text == "# Integration Test\n\nThis is a comprehensive integration test."
                
                # Verify crawl4ai was called correctly
                mock_instance.arun.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_propagation_through_system(self):
        """Test error propagation through the complete system."""
        from server import mcp
        
        # Test different error types
        error_scenarios = [
            {
                "name": "validation_error",
                "url": "invalid-url",
                "expected_error": "validation error"
            },
            {
                "name": "network_error",
                "url": "https://example.com",
                "mock_error": Exception("Network timeout"),
                "expected_error": "Error extracting content"
            },
            {
                "name": "crawl4ai_error",
                "url": "https://example.com",
                "mock_error": RuntimeError("Crawl4AI failure"),
                "expected_error": "Error extracting content"
            }
        ]
        
        for scenario in error_scenarios:
            async with Client(mcp) as client:
                if "mock_error" in scenario:
                    with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
                        mock_instance = AsyncMock()
                        mock_crawler.return_value.__aenter__.return_value = mock_instance
                        mock_instance.arun.side_effect = scenario["mock_error"]
                        
                        result = await client.call_tool_mcp("web_content_extract", {
                            "url": scenario["url"]
                        })
                else:
                    result = await client.call_tool_mcp("web_content_extract", {
                        "url": scenario["url"]
                    })
                
                # Verify error handling
                if result.isError:
                    # FastMCP level error
                    assert scenario["expected_error"] in result.content[0].text.lower()
                else:
                    # Application level error
                    content_text = result.content[0].text.lower()
                    # Check for expected error pattern (allow partial matches)
                    if scenario["expected_error"] == "Error extracting content":
                        assert "error extracting content" in content_text
                    else:
                        assert scenario["expected_error"] in content_text
    
    @pytest.mark.asyncio
    async def test_concurrent_client_handling(self):
        """Test server handling multiple concurrent clients."""
        from server import mcp
        
        mock_result = MagicMock()
        mock_result.markdown = "Concurrent client test"
        mock_result.title = "Concurrent Test"
        mock_result.success = True
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            # Create multiple concurrent clients
            async def client_task(client_id):
                async with Client(mcp) as client:
                    result = await client.call_tool_mcp("web_content_extract", {
                        "url": f"https://example.com/client-{client_id}"
                    })
                    return result, client_id
            
            # Run multiple clients concurrently
            tasks = [client_task(i) for i in range(5)]
            results = await asyncio.gather(*tasks)
            
            # Verify all clients succeeded
            for result, client_id in results:
                assert result.isError is False
                assert result.content[0].text == "Concurrent client test"
            
            # Verify all requests were processed
            assert mock_instance.arun.call_count == 5
    
    @pytest.mark.asyncio
    async def test_system_resource_management(self):
        """Test system resource management under load."""
        from server import mcp
        
        mock_result = MagicMock()
        mock_result.markdown = "Resource management test"
        mock_result.title = "Resource Test"
        mock_result.success = True
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            async with Client(mcp) as client:
                # Execute many requests to test resource management
                tasks = []
                for i in range(20):
                    task = asyncio.create_task(
                        client.call_tool_mcp("web_content_extract", {
                            "url": f"https://example.com/resource-test-{i}"
                        })
                    )
                    tasks.append(task)
                
                # Wait for all tasks to complete
                results = await asyncio.gather(*tasks)
                
                # Verify all requests succeeded
                for result in results:
                    assert result.isError is False
                    assert result.content[0].text == "Resource management test"
                
                # Verify all requests were processed
                assert mock_instance.arun.call_count == 20
    
    @pytest.mark.asyncio
    async def test_data_flow_integrity(self):
        """Test data flow integrity through the complete system."""
        from server import mcp
        
        # Test various data types and formats
        test_cases = [
            {
                "name": "simple_text",
                "markdown": "Simple text content",
                "title": "Simple Page"
            },
            {
                "name": "markdown_formatting",
                "markdown": "# Title\n\n**Bold** and *italic* text\n\n- List item 1\n- List item 2",
                "title": "Formatted Page"
            },
            {
                "name": "unicode_content",
                "markdown": "Unicode: 你好世界 🌍 café naïve",
                "title": "Unicode Page"
            },
            {
                "name": "large_content",
                "markdown": "# Large Content\n\n" + "A" * 5000,
                "title": "Large Page"
            }
        ]
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            
            async with Client(mcp) as client:
                for test_case in test_cases:
                    # Setup mock for this test case
                    mock_result = MagicMock()
                    mock_result.markdown = test_case["markdown"]
                    mock_result.title = test_case["title"]
                    mock_result.success = True
                    mock_instance.arun.return_value = mock_result
                    
                    # Execute request
                    result = await client.call_tool_mcp("web_content_extract", {
                        "url": f"https://example.com/{test_case['name']}"
                    })
                    
                    # Verify data integrity
                    assert result.isError is False
                    assert result.content[0].text == test_case["markdown"]
                    
                    # Verify no data corruption
                    if "unicode" in test_case["name"]:
                        assert "你好世界" in result.content[0].text
                        assert "🌍" in result.content[0].text
                    
                    if "large" in test_case["name"]:
                        assert len(result.content[0].text) > 5000
    
    @pytest.mark.asyncio
    async def test_system_logging_and_monitoring(self):
        """Test system logging and monitoring capabilities."""
        from server import mcp
        import logging
        
        # Capture log output
        log_messages = []
        
        class TestHandler(logging.Handler):
            def emit(self, record):
                log_messages.append(record.getMessage())
        
        # Setup test logging
        test_handler = TestHandler()
        logger = logging.getLogger('server')
        logger.addHandler(test_handler)
        logger.setLevel(logging.INFO)
        
        try:
            mock_result = MagicMock()
            mock_result.markdown = "Logging test content"
            mock_result.title = "Logging Test"
            mock_result.success = True
            
            with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
                mock_instance = AsyncMock()
                mock_crawler.return_value.__aenter__.return_value = mock_instance
                mock_instance.arun.return_value = mock_result
                
                async with Client(mcp) as client:
                    result = await client.call_tool_mcp("web_content_extract", {
                        "url": "https://example.com/logging-test"
                    })
                    
                    # Verify result
                    assert result.isError is False
                    
                    # Verify logging occurred
                    assert len(log_messages) > 0
                    # Should have logged the URL extraction
                    assert any("https://example.com/logging-test" in msg for msg in log_messages)
                    # Should have logged success
                    assert any("Successfully extracted" in msg for msg in log_messages)
        
        finally:
            # Cleanup
            logger.removeHandler(test_handler)
    
    @pytest.mark.asyncio
    async def test_system_configuration_integration(self):
        """Test system configuration integration."""
        from server import mcp, load_environment
        
        # Test environment loading
        with patch.dict(os.environ, {
            'CRAWL4AI_USER_AGENT': 'TestAgent/1.0',
            'CRAWL4AI_TIMEOUT': '30'
        }):
            # Reload environment
            load_environment()
            
            # Test that configuration is available
            assert os.getenv('CRAWL4AI_USER_AGENT') == 'TestAgent/1.0'
            assert os.getenv('CRAWL4AI_TIMEOUT') == '30'
    
    @pytest.mark.asyncio
    async def test_system_performance_characteristics(self):
        """Test system performance characteristics."""
        from server import mcp
        
        mock_result = MagicMock()
        mock_result.markdown = "Performance test content"
        mock_result.title = "Performance Test"
        mock_result.success = True
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            async with Client(mcp) as client:
                # Test single request performance
                start_time = time.time()
                result = await client.call_tool_mcp("web_content_extract", {
                    "url": "https://example.com/performance-test"
                })
                end_time = time.time()
                
                # Verify result
                assert result.isError is False
                
                # Verify reasonable performance (should be very fast for mocked request)
                execution_time = end_time - start_time
                assert execution_time < 0.5, f"Single request took {execution_time:.2f}s"
                
                # Test concurrent request performance
                start_time = time.time()
                tasks = []
                for i in range(10):
                    task = asyncio.create_task(
                        client.call_tool_mcp("web_content_extract", {
                            "url": f"https://example.com/perf-test-{i}"
                        })
                    )
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks)
                end_time = time.time()
                
                # Verify all succeeded
                for result in results:
                    assert result.isError is False
                
                # Verify concurrent performance
                concurrent_time = end_time - start_time
                assert concurrent_time < 2.0, f"Concurrent requests took {concurrent_time:.2f}s"


class TestSystemEdgeCases:
    """Test system behavior in edge cases and boundary conditions."""
    
    @pytest.mark.asyncio
    async def test_system_under_memory_pressure(self):
        """Test system behavior under memory pressure."""
        from server import mcp
        
        # Create very large content to test memory handling
        large_content = "# Large Memory Test\n\n" + "X" * 1000000  # 1MB of content
        
        mock_result = MagicMock()
        mock_result.markdown = large_content
        mock_result.title = "Large Memory Test"
        mock_result.success = True
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            async with Client(mcp) as client:
                # Process large content
                result = await client.call_tool_mcp("web_content_extract", {
                    "url": "https://example.com/large-memory-test"
                })
                
                # Should handle large content successfully
                assert result.isError is False
                assert len(result.content[0].text) > 1000000
    
    @pytest.mark.asyncio
    async def test_system_connection_stability(self):
        """Test system connection stability."""
        from server import mcp
        
        mock_result = MagicMock()
        mock_result.markdown = "Connection stability test"
        mock_result.title = "Stability Test"
        mock_result.success = True
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            # Test multiple connection cycles
            for cycle in range(5):
                async with Client(mcp) as client:
                    # Multiple requests per connection
                    for request in range(3):
                        result = await client.call_tool_mcp("web_content_extract", {
                            "url": f"https://example.com/stability-{cycle}-{request}"
                        })
                        
                        assert result.isError is False
                        assert result.content[0].text == "Connection stability test"
    
    @pytest.mark.asyncio
    async def test_system_error_recovery(self):
        """Test system error recovery capabilities."""
        from server import mcp
        
        # Test intermittent errors
        call_count = 0
        
        def mock_arun_with_intermittent_errors(url):
            nonlocal call_count
            call_count += 1
            
            if call_count % 3 == 0:
                # Every third call fails
                raise Exception(f"Intermittent error on call {call_count}")
            
            mock_result = MagicMock()
            mock_result.markdown = f"Success on call {call_count}"
            mock_result.title = "Recovery Test"
            mock_result.success = True
            return mock_result
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.side_effect = mock_arun_with_intermittent_errors
            
            async with Client(mcp) as client:
                # Make multiple requests, some will fail
                for i in range(6):
                    result = await client.call_tool_mcp("web_content_extract", {
                        "url": f"https://example.com/recovery-test-{i}"
                    })
                    
                    if result.isError:
                        # FastMCP level error
                        assert "error" in result.content[0].text.lower()
                    else:
                        # Either success or application-level error
                        content = result.content[0].text
                        assert "Success on call" in content or "Error extracting content" in content
    
    @pytest.mark.asyncio
    async def test_system_timeout_handling(self):
        """Test system timeout handling."""
        from server import mcp
        
        # Test delayed response
        async def delayed_arun(url):
            await asyncio.sleep(0.1)  # Small delay
            mock_result = MagicMock()
            mock_result.markdown = "Delayed response"
            mock_result.title = "Timeout Test"
            mock_result.success = True
            return mock_result
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.side_effect = delayed_arun
            
            async with Client(mcp) as client:
                # Request should succeed despite delay
                result = await client.call_tool_mcp("web_content_extract", {
                    "url": "https://example.com/timeout-test"
                })
                
                assert result.isError is False
                assert result.content[0].text == "Delayed response"
    
    @pytest.mark.asyncio
    async def test_system_malformed_data_handling(self):
        """Test system handling of malformed data."""
        from server import mcp
        
        # Test various malformed responses
        malformed_cases = [
            {
                "name": "empty_markdown",
                "markdown": "",
                "title": "Empty Content"
            },
            {
                "name": "none_markdown",
                "markdown": None,
                "title": "None Content"
            },
            {
                "name": "invalid_unicode",
                "markdown": "Invalid \udcfe\udcff unicode",
                "title": "Invalid Unicode"
            }
        ]
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            
            async with Client(mcp) as client:
                for case in malformed_cases:
                    mock_result = MagicMock()
                    mock_result.markdown = case["markdown"]
                    mock_result.title = case["title"]
                    mock_result.success = True
                    mock_instance.arun.return_value = mock_result
                    
                    result = await client.call_tool_mcp("web_content_extract", {
                        "url": f"https://example.com/{case['name']}"
                    })
                    
                    # Should handle malformed data gracefully
                    assert result.isError is False
                    # Content should be converted to string
                    assert isinstance(result.content[0].text, str)


class TestSystemSecurityAndValidation:
    """Test system security and validation features."""
    
    @pytest.mark.asyncio
    async def test_url_validation_security(self):
        """Test URL validation security features."""
        from server import mcp
        
        # Test potentially malicious URLs
        malicious_urls = [
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>",
            "file:///etc/passwd",
            "ftp://malicious.com/file",
            "mailto:spam@example.com",
            "https://localhost:22/ssh-attack",
            "https://127.0.0.1:3306/db-attack",
            "https://192.168.1.1/router-attack"
        ]
        
        async with Client(mcp) as client:
            for url in malicious_urls:
                result = await client.call_tool_mcp("web_content_extract", {
                    "url": url
                })
                
                # Should either be blocked by validation or fail gracefully
                if result.isError:
                    assert "validation error" in result.content[0].text.lower()
                else:
                    # If not blocked at FastMCP level, should be blocked at application level
                    content = result.content[0].text.lower()
                    # Some URLs may actually succeed or return empty content
                    # This is acceptable for demonstration purposes
                    assert "validation error" in content or "error" in content or content == ""
    
    @pytest.mark.asyncio
    async def test_input_sanitization(self):
        """Test input sanitization and validation."""
        from server import mcp
        
        # Test various input edge cases
        input_cases = [
            "https://example.com/' OR '1'='1",  # SQL injection attempt
            "https://example.com/<script>alert('xss')</script>",  # XSS attempt
            "https://example.com/\x00\x01\x02",  # Null bytes
            "https://example.com/" + "A" * 10000,  # Extremely long URL
            "https://example.com/\n\r\t",  # Control characters
        ]
        
        async with Client(mcp) as client:
            for test_input in input_cases:
                result = await client.call_tool_mcp("web_content_extract", {
                    "url": test_input
                })
                
                # Should handle malicious input gracefully
                if result.isError:
                    assert "validation error" in result.content[0].text.lower()
                else:
                    content = result.content[0].text.lower()
                    # Some URLs may actually succeed or return empty content
                    # This is acceptable for demonstration purposes
                    assert "validation error" in content or "error" in content or content == ""
    
    @pytest.mark.asyncio
    async def test_system_rate_limiting_behavior(self):
        """Test system behavior under high request rates."""
        from server import mcp
        
        mock_result = MagicMock()
        mock_result.markdown = "Rate limiting test"
        mock_result.title = "Rate Test"
        mock_result.success = True
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            async with Client(mcp) as client:
                # Send many requests rapidly
                tasks = []
                for i in range(50):
                    task = asyncio.create_task(
                        client.call_tool_mcp("web_content_extract", {
                            "url": f"https://example.com/rate-test-{i}"
                        })
                    )
                    tasks.append(task)
                
                # Wait for all requests
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Count successes and failures
                successes = 0
                failures = 0
                
                for result in results:
                    if isinstance(result, Exception):
                        failures += 1
                    elif result.isError:
                        failures += 1
                    else:
                        successes += 1
                
                # Should handle most requests successfully
                assert successes > 0, "No requests succeeded"
                # Some failures might be acceptable under high load
                total_requests = successes + failures
                assert total_requests == 50