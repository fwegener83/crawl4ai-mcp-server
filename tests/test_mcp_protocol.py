"""Test MCP protocol compliance."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio
import json

from fastmcp import FastMCP, Client
from mcp.types import CallToolResult as MCPCallToolResult
from mcp.types import TextContent, ListToolsResult, Tool


class TestMCPProtocolCompliance:
    """Test MCP protocol compliance and message formatting."""
    
    @pytest.mark.asyncio
    async def test_mcp_tool_listing_response_format(self):
        """Test that tool response follows MCP protocol format."""
        from server import mcp
        
        # Mock the crawler to avoid real network calls
        mock_result = MagicMock()
        mock_result.markdown = "Test content for MCP format validation"
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            async with Client(mcp) as client:
                # Test MCP response format with mocked content
                result = await client.call_tool_mcp("web_content_extract", {
                    "url": "https://example.com"
                })
                
                # Test that the response has the correct MCP format
                assert hasattr(result, 'content')
                assert hasattr(result, 'isError')
                assert isinstance(result.content, list)
                
                if result.content:
                    content_item = result.content[0]
                    assert hasattr(content_item, 'type')
                    assert hasattr(content_item, 'text')
                    assert content_item.type == 'text'
    
    @pytest.mark.asyncio
    async def test_mcp_tool_schema_compliance(self):
        """Test that tool schemas comply with MCP specification."""
        from server import mcp
        
        async with Client(mcp) as client:
            tools = await client.list_tools()
            
            assert len(tools) >= 1
            tool_names = [t.name for t in tools]
            assert "web_content_extract" in tool_names
            
            # Find the specific tool we want to test
            tool = next(t for t in tools if t.name == "web_content_extract")
            
            # Test tool structure compliance
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'description')
            assert hasattr(tool, 'inputSchema')
            
            # Test specific tool properties
            assert tool.name == "web_content_extract"
            assert tool.description is not None
            assert tool.inputSchema is not None
            
            # Test input schema structure
            schema = tool.inputSchema
            assert 'type' in schema
            assert 'properties' in schema
            assert 'required' in schema
            
            # Test URL parameter in schema
            assert 'url' in schema['properties']
            assert 'url' in schema['required']
            assert schema['properties']['url']['type'] == 'string'
    
    @pytest.mark.asyncio
    async def test_mcp_successful_tool_call_format(self):
        """Test successful tool call response format."""
        from server import mcp
        
        mock_result = MagicMock()
        mock_result.markdown = "# Test Content"
        mock_result.title = "Test Page"
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            async with Client(mcp) as client:
                result = await client.call_tool_mcp("web_content_extract", {
                    "url": "https://example.com"
                })
                
                # Test MCP protocol compliance
                assert hasattr(result, 'content')
                assert hasattr(result, 'isError')
                assert result.isError is False
                
                # Test content format
                assert isinstance(result.content, list)
                assert len(result.content) == 1
                
                content_item = result.content[0]
                assert hasattr(content_item, 'type')
                assert hasattr(content_item, 'text')
                assert content_item.type == 'text'
                
                # Parse the JSON response from the unified MCP tool
                response_data = json.loads(content_item.text)
                assert response_data["success"] is True
                assert response_data["content"] == "# Test Content"
                assert "metadata" in response_data
    
    @pytest.mark.asyncio
    async def test_mcp_error_response_format(self):
        """Test error response format compliance."""
        from server import mcp
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.side_effect = Exception("Network error")
            
            async with Client(mcp) as client:
                result = await client.call_tool_mcp("web_content_extract", {
                    "url": "https://example.com"
                })
                
                # Test MCP protocol compliance for error handling
                assert hasattr(result, 'content')
                assert hasattr(result, 'isError')
                assert result.isError is False  # Our server returns errors as content
                
                # Test error content format
                assert isinstance(result.content, list)
                assert len(result.content) == 1
                
                content_item = result.content[0]
                assert content_item.type == 'text'
                assert "Error extracting content" in content_item.text
                assert "Network error" in content_item.text
    
    @pytest.mark.asyncio
    async def test_mcp_validation_error_format(self):
        """Test validation error response format."""
        from server import mcp
        
        async with Client(mcp) as client:
            result = await client.call_tool_mcp("web_content_extract", {
                "url": "invalid-url"
            })
            
            # Test MCP protocol compliance for validation errors
            assert hasattr(result, 'content')
            assert hasattr(result, 'isError')
            assert result.isError is False  # Our server returns errors as content
            
            # Test validation error content format
            assert isinstance(result.content, list)
            assert len(result.content) == 1
            
            content_item = result.content[0]
            assert content_item.type == 'text'
            assert "validation error" in content_item.text.lower()
    
    @pytest.mark.asyncio
    async def test_mcp_missing_parameter_handling(self):
        """Test handling of missing required parameters."""
        from server import mcp
        
        async with Client(mcp) as client:
            # This should raise a protocol-level error
            try:
                result = await client.call_tool_mcp("web_content_extract", {})
                # If it doesn't raise, it should be an error response
                assert result.isError or "missing" in result.content[0].text.lower()
            except Exception as exc:
                # The error should be related to missing required parameter
                assert "required" in str(exc).lower() or "missing" in str(exc).lower()
    
    @pytest.mark.asyncio
    async def test_mcp_invalid_tool_name_handling(self):
        """Test handling of invalid tool names."""
        from server import mcp
        
        async with Client(mcp) as client:
            # This should raise a protocol-level error
            try:
                result = await client.call_tool_mcp("nonexistent_tool", {
                    "url": "https://example.com"
                })
                # If it doesn't raise, it should be an error response
                assert result.isError or "unknown" in result.content[0].text.lower()
            except Exception as exc:
                # The error should be related to unknown tool
                assert "unknown" in str(exc).lower() or "not found" in str(exc).lower()
    
    @pytest.mark.asyncio
    async def test_mcp_tool_metadata_compliance(self):
        """Test tool metadata compliance with MCP specification."""
        from server import mcp
        
        async with Client(mcp) as client:
            tools = await client.list_tools()
            
            assert len(tools) >= 1
            tool_names = [t.name for t in tools]
            assert "web_content_extract" in tool_names
            
            # Find the specific tool we want to test
            tool = next(t for t in tools if t.name == "web_content_extract")
            
            # Test required metadata fields
            assert tool.name == "web_content_extract"
            assert isinstance(tool.description, str)
            assert len(tool.description) > 0
            
            # Test that description is meaningful
            assert "extract" in tool.description.lower()
            assert "webpage" in tool.description.lower() or "web" in tool.description.lower()
            
            # Test input schema completeness
            schema = tool.inputSchema
            assert schema['type'] == 'object'
            assert 'properties' in schema
            assert 'required' in schema
            
            # Test URL parameter metadata
            url_prop = schema['properties']['url']
            assert url_prop['type'] == 'string'
            # Description might be in 'title' field instead of 'description'
            assert 'title' in url_prop or 'description' in url_prop
    
    @pytest.mark.asyncio
    async def test_mcp_concurrent_requests_protocol(self):
        """Test MCP protocol compliance with concurrent requests."""
        from server import mcp
        
        mock_result = MagicMock()
        mock_result.markdown = "Concurrent test content"
        mock_result.title = "Concurrent Page"
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            async with Client(mcp) as client:
                # Create multiple concurrent requests
                tasks = []
                for i in range(3):
                    task = asyncio.create_task(
                        client.call_tool_mcp("web_content_extract", {
                            "url": f"https://example{i}.com"
                        })
                    )
                    tasks.append(task)
                
                # Wait for all requests to complete
                results = await asyncio.gather(*tasks)
                
                # Test that all responses comply with MCP protocol
                for result in results:
                    assert hasattr(result, 'content')
                    assert hasattr(result, 'isError')
                    assert result.isError is False
                    
                    assert isinstance(result.content, list)
                    assert len(result.content) == 1
                    
                    content_item = result.content[0]
                    assert content_item.type == 'text'
                    assert content_item.text == "Concurrent test content"
    
    @pytest.mark.asyncio
    async def test_mcp_large_content_handling(self):
        """Test MCP protocol handling of large content."""
        from server import mcp
        
        # Create large content (10KB)
        large_content = "# Large Content\n" + "A" * 10000
        
        mock_result = MagicMock()
        mock_result.markdown = large_content
        mock_result.title = "Large Page"
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            async with Client(mcp) as client:
                result = await client.call_tool_mcp("web_content_extract", {
                    "url": "https://example.com"
                })
                
                # Test MCP protocol compliance with large content
                assert hasattr(result, 'content')
                assert hasattr(result, 'isError')
                assert result.isError is False
                
                assert isinstance(result.content, list)
                assert len(result.content) == 1
                
                content_item = result.content[0]
                assert content_item.type == 'text'
                assert content_item.text == large_content
                assert len(content_item.text) > 10000


class TestMCPMessageFormats:
    """Test specific MCP message format requirements."""
    
    @pytest.mark.asyncio
    async def test_mcp_json_rpc_compliance(self):
        """Test JSON-RPC compliance in MCP messages."""
        from server import mcp
        
        async with Client(mcp) as client:
            # Test that the client can successfully communicate
            tools = await client.list_tools()
            
            # Basic JSON-RPC compliance check
            assert len(tools) >= 1
            assert tools[0].name == "web_content_extract"
    
    @pytest.mark.asyncio
    async def test_mcp_content_type_validation(self):
        """Test content type validation in MCP responses."""
        from server import mcp
        
        mock_result = MagicMock()
        mock_result.markdown = "Test content"
        mock_result.title = "Test Page"
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            async with Client(mcp) as client:
                result = await client.call_tool_mcp("web_content_extract", {
                    "url": "https://example.com"
                })
                
                # Test content type validation
                assert isinstance(result.content, list)
                for content_item in result.content:
                    assert hasattr(content_item, 'type')
                    assert content_item.type in ['text', 'image', 'resource']
                    
                    if content_item.type == 'text':
                        assert hasattr(content_item, 'text')
                        assert isinstance(content_item.text, str)
    
    @pytest.mark.asyncio
    async def test_mcp_unicode_content_handling(self):
        """Test MCP protocol handling of Unicode content."""
        from server import mcp
        
        unicode_content = "# Unicode Test 🌍\n\n你好世界 café naïve résumé"
        
        mock_result = MagicMock()
        mock_result.markdown = unicode_content
        mock_result.title = "Unicode Page"
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            async with Client(mcp) as client:
                result = await client.call_tool_mcp("web_content_extract", {
                    "url": "https://example.com"
                })
                
                # Test Unicode handling in MCP protocol
                assert result.isError is False
                assert isinstance(result.content, list)
                assert len(result.content) == 1
                
                content_item = result.content[0]
                assert content_item.type == 'text'
                assert content_item.text == unicode_content
                
                # Test that Unicode is properly encoded/decoded
                assert "🌍" in content_item.text
                assert "你好世界" in content_item.text
                assert "café" in content_item.text
    
    @pytest.mark.asyncio
    async def test_mcp_empty_content_handling(self):
        """Test MCP protocol handling of empty content."""
        from server import mcp
        
        mock_result = MagicMock()
        mock_result.markdown = ""
        mock_result.title = "Empty Page"
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            async with Client(mcp) as client:
                result = await client.call_tool_mcp("web_content_extract", {
                    "url": "https://example.com"
                })
                
                # Test empty content handling
                assert result.isError is False
                assert isinstance(result.content, list)
                assert len(result.content) == 1
                
                content_item = result.content[0]
                assert content_item.type == 'text'
                assert content_item.text == ""


class TestMCPServerBehavior:
    """Test MCP server behavior and state management."""
    
    @pytest.mark.asyncio
    async def test_mcp_server_stateless_behavior(self):
        """Test that MCP server maintains stateless behavior."""
        from server import mcp
        
        mock_result = MagicMock()
        mock_result.markdown = "Stateless test"
        mock_result.title = "Stateless Page"
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            # Test multiple independent client connections
            async with Client(mcp) as client1:
                result1 = await client1.call_tool_mcp("web_content_extract", {
                    "url": "https://example1.com"
                })
                
                async with Client(mcp) as client2:
                    result2 = await client2.call_tool_mcp("web_content_extract", {
                        "url": "https://example2.com"
                    })
                    
                    # Both results should be independent and identical
                    assert result1.content[0].text == result2.content[0].text
                    assert result1.isError == result2.isError
    
    @pytest.mark.asyncio
    async def test_mcp_server_connection_lifecycle(self):
        """Test MCP server connection lifecycle."""
        from server import mcp
        
        # Test that server can handle multiple connection cycles
        for i in range(3):
            async with Client(mcp) as client:
                tools = await client.list_tools()
                assert len(tools) >= 1
                tool_names = [t.name for t in tools]
                assert "web_content_extract" in tool_names
    
    @pytest.mark.asyncio
    async def test_mcp_server_error_recovery(self):
        """Test MCP server error recovery behavior."""
        from server import mcp
        
        async with Client(mcp) as client:
            # First, cause an error
            result1 = await client.call_tool_mcp("web_content_extract", {
                "url": "invalid-url"
            })
            
            assert result1.isError is False  # Error returned as content
            assert "validation error" in result1.content[0].text.lower()
            
            # Then test that server recovers for next request
            mock_result = MagicMock()
            mock_result.markdown = "Recovery test"
            mock_result.title = "Recovery Page"
            
            with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
                mock_instance = AsyncMock()
                mock_crawler.return_value.__aenter__.return_value = mock_instance
                mock_instance.arun.return_value = mock_result
                
                result2 = await client.call_tool_mcp("web_content_extract", {
                    "url": "https://example.com"
                })
                
                # Server should have recovered
                assert result2.isError is False
                assert result2.content[0].text == "Recovery test"