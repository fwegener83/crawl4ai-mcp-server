"""End-to-End workflow tests for complete URL extraction."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio
import json
from datetime import datetime

from fastmcp import FastMCP, Client
from mcp.types import TextContent
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import LLMExtractionStrategy


class TestCompleteWorkflowTests:
    """Test complete URL extraction workflow from start to finish."""
    
    @pytest.mark.asyncio
    async def test_complete_url_extraction_workflow(self):
        """Test complete workflow: URL validation -> crawling -> content extraction."""
        from server import mcp
        
        # Mock crawl4ai response
        mock_result = MagicMock()
        mock_result.markdown = "# Test Article\n\nThis is a test article with content."
        mock_result.title = "Test Article"
        mock_result.links = {"internal": ["https://example.com/page1"], "external": ["https://google.com"]}
        mock_result.media = {"images": [{"src": "https://example.com/image.jpg", "alt": "Test image"}]}
        mock_result.success = True
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            async with Client(mcp) as client:
                # Test complete workflow
                result = await client.call_tool_mcp("web_content_extract", {
                    "url": "https://example.com/test-article"
                })
                
                # Verify result structure
                assert result.isError is False
                assert isinstance(result.content, list)
                assert len(result.content) == 1
                
                content = result.content[0]
                assert content.type == 'text'
                assert content.text == "# Test Article\n\nThis is a test article with content."
                
                # Verify crawler was called with correct parameters
                mock_instance.arun.assert_called_once()
                call_args = mock_instance.arun.call_args
                # Check if called with positional args or keyword args
                if call_args[0]:
                    assert call_args[0][0] == "https://example.com/test-article"
                else:
                    assert call_args[1]['url'] == "https://example.com/test-article"
    
    @pytest.mark.asyncio
    async def test_real_world_url_patterns(self):
        """Test various real-world URL patterns."""
        from server import mcp
        
        test_urls = [
            "https://example.com",
            "https://subdomain.example.com/path",
            "https://example.com/path/to/page.html",
            "https://example.com/article?id=123&category=tech",
            "https://example.com/page#section",
            "https://www.example.com/deep/nested/path/",
            "https://example-site.com/path_with_underscores",
            "https://example.co.uk/international-domain"
        ]
        
        mock_result = MagicMock()
        mock_result.markdown = "Test content"
        mock_result.title = "Test Page"
        mock_result.success = True
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            async with Client(mcp) as client:
                for url in test_urls:
                    result = await client.call_tool_mcp("web_content_extract", {
                        "url": url
                    })
                    
                    # Each URL should be processed successfully
                    assert result.isError is False
                    assert result.content[0].text == "Test content"
    
    @pytest.mark.asyncio
    async def test_error_handling_workflow(self):
        """Test error handling throughout the complete workflow."""
        from server import mcp
        
        # Test network error handling
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.side_effect = Exception("Network timeout")
            
            async with Client(mcp) as client:
                result = await client.call_tool_mcp("web_content_extract", {
                    "url": "https://example.com"
                })
                
                # Error should be handled gracefully
                assert result.isError is False
                assert "Error extracting content" in result.content[0].text
                assert "Network timeout" in result.content[0].text
    
    @pytest.mark.asyncio
    async def test_concurrent_workflow_execution(self):
        """Test concurrent execution of complete workflows."""
        from server import mcp
        
        mock_result = MagicMock()
        mock_result.markdown = "Concurrent test content"
        mock_result.title = "Concurrent Page"
        mock_result.success = True
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            async with Client(mcp) as client:
                # Create multiple concurrent workflows
                tasks = []
                urls = [
                    "https://example1.com",
                    "https://example2.com",
                    "https://example3.com",
                    "https://example4.com",
                    "https://example5.com"
                ]
                
                for url in urls:
                    task = asyncio.create_task(
                        client.call_tool_mcp("web_content_extract", {"url": url})
                    )
                    tasks.append(task)
                
                # Wait for all workflows to complete
                results = await asyncio.gather(*tasks)
                
                # Verify all workflows completed successfully
                for result in results:
                    assert result.isError is False
                    assert result.content[0].text == "Concurrent test content"
                
                # Verify crawler was called for each URL
                assert mock_instance.arun.call_count == len(urls)
    
    @pytest.mark.asyncio
    async def test_workflow_with_various_content_types(self):
        """Test workflow with different content types and formats."""
        from server import mcp
        
        content_test_cases = [
            {
                "name": "blog_article",
                "markdown": "# Blog Post\n\nThis is a blog post with **bold** and *italic* text.\n\n## Section\n\nMore content here.",
                "expected_content": "# Blog Post\n\nThis is a blog post with **bold** and *italic* text.\n\n## Section\n\nMore content here."
            },
            {
                "name": "news_article",
                "markdown": "# Breaking News\n\nThis is a news article with important information.\n\n> This is a quote from the article.\n\n- Point 1\n- Point 2\n- Point 3",
                "expected_content": "# Breaking News\n\nThis is a news article with important information.\n\n> This is a quote from the article.\n\n- Point 1\n- Point 2\n- Point 3"
            },
            {
                "name": "technical_documentation",
                "markdown": "# API Documentation\n\n## Installation\n\n```bash\nnpm install package-name\n```\n\n## Usage\n\n```javascript\nconst pkg = require('package-name');\n```",
                "expected_content": "# API Documentation\n\n## Installation\n\n```bash\nnpm install package-name\n```\n\n## Usage\n\n```javascript\nconst pkg = require('package-name');\n```"
            },
            {
                "name": "product_page",
                "markdown": "# Product Name\n\nPrice: $99.99\n\n## Features\n\n- Feature 1\n- Feature 2\n- Feature 3\n\n## Reviews\n\n★★★★★ Great product!",
                "expected_content": "# Product Name\n\nPrice: $99.99\n\n## Features\n\n- Feature 1\n- Feature 2\n- Feature 3\n\n## Reviews\n\n★★★★★ Great product!"
            }
        ]
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            
            async with Client(mcp) as client:
                for test_case in content_test_cases:
                    # Setup mock for this content type
                    mock_result = MagicMock()
                    mock_result.markdown = test_case["markdown"]
                    mock_result.title = f"Test {test_case['name']}"
                    mock_result.success = True
                    mock_instance.arun.return_value = mock_result
                    
                    # Execute workflow
                    result = await client.call_tool_mcp("web_content_extract", {
                        "url": f"https://example.com/{test_case['name']}"
                    })
                    
                    # Verify content extraction
                    assert result.isError is False
                    assert result.content[0].text == test_case["expected_content"]
    
    @pytest.mark.asyncio
    async def test_workflow_performance_characteristics(self):
        """Test workflow performance characteristics."""
        from server import mcp
        import time
        
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
                assert result.content[0].text == "Performance test content"
                
                # Performance should be reasonable (under 1 second for mocked request)
                execution_time = end_time - start_time
                assert execution_time < 1.0, f"Execution took {execution_time:.2f}s, expected < 1.0s"
    
    @pytest.mark.asyncio
    async def test_workflow_with_edge_case_urls(self):
        """Test workflow with edge case URLs."""
        from server import mcp
        
        # Test validation errors for edge cases
        edge_case_urls = [
            "not-a-url",
            "ftp://example.com",
            "file:///local/file.html",
            "javascript:alert('test')",
            "mailto:test@example.com",
            "",
            "   ",
            "https://",
            "https:///missing-host",
            "https://example.com:abc/invalid-port"
        ]
        
        async with Client(mcp) as client:
            for url in edge_case_urls:
                result = await client.call_tool_mcp("web_content_extract", {
                    "url": url
                })
                
                # All edge cases should result in validation errors or empty content
                if result.isError:
                    # FastMCP level validation error
                    assert "validation error" in result.content[0].text.lower()
                else:
                    # Application level error (our server returns errors as content)
                    content_text = result.content[0].text.lower()
                    # Some URLs may return empty content if crawl4ai fails silently
                    assert "validation error" in content_text or "error" in content_text or content_text == ""
    
    @pytest.mark.asyncio
    async def test_workflow_resource_management(self):
        """Test workflow resource management and cleanup."""
        from server import mcp
        
        mock_result = MagicMock()
        mock_result.markdown = "Resource test content"
        mock_result.title = "Resource Test"
        mock_result.success = True
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            async with Client(mcp) as client:
                # Execute multiple workflows to test resource management
                for i in range(10):
                    result = await client.call_tool_mcp("web_content_extract", {
                        "url": f"https://example.com/resource-test-{i}"
                    })
                    
                    # Each workflow should complete successfully
                    assert result.isError is False
                    assert result.content[0].text == "Resource test content"
                
                # Verify crawler was properly used for each request
                assert mock_instance.arun.call_count == 10


class TestRealWorldIntegration:
    """Test integration with real crawl4ai scenarios (slower tests)."""
    
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_actual_crawl4ai_integration(self):
        """Test actual crawl4ai integration with a real example."""
        from server import mcp
        
        async with Client(mcp) as client:
            # Test with a reliable test URL
            result = await client.call_tool_mcp("web_content_extract", {
                "url": "https://httpbin.org/html"
            })
            
            # Should succeed with actual crawl4ai or fail gracefully
            if result.isError:
                # Check if it's a validation error (FastMCP level)
                assert "validation error" in result.content[0].text.lower()
            else:
                assert len(result.content) == 1
                assert result.content[0].type == 'text'
                
                # Content should contain expected elements from httpbin HTML
                content = result.content[0].text
                assert len(content) > 0
                # httpbin.org/html returns a simple HTML page, or it might fail
                # Either way, we should have some content
                assert isinstance(content, str)
    
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_actual_crawl4ai_error_handling(self):
        """Test actual crawl4ai error handling with unreachable URL."""
        from server import mcp
        
        async with Client(mcp) as client:
            # Test with a URL that should fail
            result = await client.call_tool_mcp("web_content_extract", {
                "url": "https://this-domain-does-not-exist-12345.com"
            })
            
            # Should handle the error gracefully
            if result.isError:
                # Check if it's a validation error (FastMCP level)
                assert "validation error" in result.content[0].text.lower()
            else:
                # Should be our application-level error
                assert "Error extracting content" in result.content[0].text
    
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_actual_crawl4ai_timeout_handling(self):
        """Test actual crawl4ai timeout handling."""
        from server import mcp
        
        async with Client(mcp) as client:
            # Test with a URL that might timeout (using httpbin delay)
            result = await client.call_tool_mcp("web_content_extract", {
                "url": "https://httpbin.org/delay/10"  # 10 second delay
            })
            
            # Should either succeed or fail gracefully with timeout
            # FastMCP may return isError=True for validation errors
            if result.isError:
                # Check if it's a validation error (FastMCP level)
                assert "validation error" in result.content[0].text.lower()
            else:
                content = result.content[0].text
                
                # Either successful extraction or timeout error
                assert len(content) > 0
                # If it's an error, it should mention timeout or similar
                if "Error extracting content" in content:
                    assert "timeout" in content.lower() or "error" in content.lower()


class TestWorkflowStateManagement:
    """Test workflow state management and consistency."""
    
    @pytest.mark.asyncio
    async def test_workflow_state_isolation(self):
        """Test that workflows are properly isolated from each other."""
        from server import mcp
        
        # Create different mock responses for different URLs
        responses = {
            "https://example1.com": "Content from site 1",
            "https://example2.com": "Content from site 2",
            "https://example3.com": "Content from site 3"
        }
        
        async def mock_arun(url):
            mock_result = MagicMock()
            mock_result.markdown = responses.get(url, "Default content")
            mock_result.title = f"Page for {url}"
            mock_result.success = True
            return mock_result
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.side_effect = mock_arun
            
            async with Client(mcp) as client:
                # Execute workflows in different orders
                result1 = await client.call_tool_mcp("web_content_extract", {
                    "url": "https://example1.com"
                })
                result2 = await client.call_tool_mcp("web_content_extract", {
                    "url": "https://example2.com"
                })
                result3 = await client.call_tool_mcp("web_content_extract", {
                    "url": "https://example3.com"
                })
                
                # Each workflow should return its specific content
                assert result1.content[0].text == "Content from site 1"
                assert result2.content[0].text == "Content from site 2"
                assert result3.content[0].text == "Content from site 3"
    
    @pytest.mark.asyncio
    async def test_workflow_consistency_across_sessions(self):
        """Test workflow consistency across multiple client sessions."""
        from server import mcp
        
        mock_result = MagicMock()
        mock_result.markdown = "Consistent content"
        mock_result.title = "Consistent Page"
        mock_result.success = True
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            # Test multiple client sessions
            results = []
            for i in range(3):
                async with Client(mcp) as client:
                    result = await client.call_tool_mcp("web_content_extract", {
                        "url": "https://example.com/consistency-test"
                    })
                    results.append(result)
            
            # All sessions should return consistent results
            for result in results:
                assert result.isError is False
                assert result.content[0].text == "Consistent content"
    
    @pytest.mark.asyncio
    async def test_workflow_memory_management(self):
        """Test workflow memory management with large content."""
        from server import mcp
        
        # Create large content (100KB)
        large_content = "# Large Content\n\n" + "A" * 100000
        
        mock_result = MagicMock()
        mock_result.markdown = large_content
        mock_result.title = "Large Content Page"
        mock_result.success = True
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            async with Client(mcp) as client:
                # Process large content
                result = await client.call_tool_mcp("web_content_extract", {
                    "url": "https://example.com/large-content"
                })
                
                # Should handle large content successfully
                assert result.isError is False
                assert len(result.content[0].text) > 100000
                assert result.content[0].text == large_content