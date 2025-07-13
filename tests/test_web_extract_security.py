"""Web extract tool security integration tests."""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from tools.web_extract import WebExtractParams


class TestWebExtractSanitization:
    """Test web extract sanitizes error messages."""
    
    @pytest.mark.asyncio
    async def test_web_extract_sanitizes_network_errors(self):
        """Test web extract sanitizes network error messages."""
        # This test will FAIL initially (Red phase) - web_extract doesn't use sanitization yet
        
        # Mock network error with sensitive info
        def mock_error_side_effect(*args, **kwargs):
            raise Exception("Connection to postgresql://user:password@localhost failed")
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.side_effect = mock_error_side_effect
            
            from tools.web_extract import web_content_extract
            
            params = WebExtractParams(url="https://example.com")
            result = await web_content_extract(params)
            
            # Verify error is sanitized
            assert "password" not in result
            assert "Error extracting content" in result
            assert "[REDACTED]" in result

    @pytest.mark.asyncio
    async def test_web_extract_sanitizes_api_key_errors(self):
        """Test web extract sanitizes API key errors."""
        def mock_api_error(*args, **kwargs):
            raise Exception("API authentication failed with key sk-1234567890abcdef")
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.side_effect = mock_api_error
            
            from tools.web_extract import web_content_extract
            
            params = WebExtractParams(url="https://example.com")
            result = await web_content_extract(params)
            
            # Verify API key is sanitized
            assert "sk-1234567890abcdef" not in result
            assert "Error extracting content" in result
            assert "[REDACTED]" in result

    @pytest.mark.asyncio
    async def test_web_extract_sanitizes_system_path_errors(self):
        """Test web extract sanitizes system path errors."""
        def mock_path_error(*args, **kwargs):
            raise FileNotFoundError("Configuration file /etc/app/secret.conf not found")
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.side_effect = mock_path_error
            
            from tools.web_extract import web_content_extract
            
            params = WebExtractParams(url="https://example.com")
            result = await web_content_extract(params)
            
            # Verify system path is sanitized
            assert "/etc/app/secret.conf" not in result
            assert "Error extracting content" in result
            assert "[REDACTED]" in result

    @pytest.mark.asyncio
    async def test_web_extract_preserves_useful_error_info(self):
        """Test web extract preserves useful error information."""
        def mock_timeout_error(*args, **kwargs):
            raise asyncio.TimeoutError("Request timeout after 30 seconds")
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.side_effect = mock_timeout_error
            
            from tools.web_extract import web_content_extract
            
            params = WebExtractParams(url="https://example.com")
            result = await web_content_extract(params)
            
            # Verify useful info is preserved
            assert "timeout" in result.lower()
            assert "30 seconds" in result
            assert "Error extracting content" in result

    @pytest.mark.asyncio
    async def test_web_extract_multiple_error_sanitization(self):
        """Test web extract handles multiple sensitive items in one error."""
        def mock_complex_error(*args, **kwargs):
            raise Exception(
                "Database postgresql://admin:secret123@localhost failed. "
                "API fallback sk-abcd1234efgh5678 also rejected. "
                "Config /etc/app/config.yml missing."
            )
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.side_effect = mock_complex_error
            
            from tools.web_extract import web_content_extract
            
            params = WebExtractParams(url="https://example.com")
            result = await web_content_extract(params)
            
            # Verify all sensitive info is sanitized
            assert "secret123" not in result
            assert "admin:secret123" not in result
            assert "sk-abcd1234efgh5678" not in result
            assert "/etc/app/config.yml" not in result
            
            # Verify useful info is preserved
            assert "Database" in result
            assert "postgresql://" in result
            assert "localhost" in result
            assert "failed" in result
            assert "API fallback" in result
            assert "rejected" in result
            assert "Config" in result
            assert "missing" in result

    @pytest.mark.asyncio
    async def test_web_extract_logging_security(self):
        """Test that logging also uses sanitized messages."""
        import logging
        
        # Capture log messages
        log_messages = []
        
        class TestLogHandler(logging.Handler):
            def emit(self, record):
                log_messages.append(record.getMessage())
        
        def mock_sensitive_error(*args, **kwargs):
            raise Exception("Database connection postgresql://user:password@localhost failed")
        
        # Setup logging capture
        handler = TestLogHandler()
        logger = logging.getLogger('tools.web_extract')
        logger.addHandler(handler)
        logger.setLevel(logging.ERROR)
        
        try:
            with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
                mock_instance = AsyncMock()
                mock_crawler.return_value.__aenter__.return_value = mock_instance
                mock_instance.arun.side_effect = mock_sensitive_error
                
                from tools.web_extract import web_content_extract
                
                params = WebExtractParams(url="https://example.com")
                result = await web_content_extract(params)
                
                # Verify logging is also sanitized
                assert len(log_messages) > 0
                logged_message = " ".join(log_messages)
                assert "password" not in logged_message
                assert "[REDACTED]" in logged_message or "password" not in logged_message
                
        finally:
            logger.removeHandler(handler)


class TestSafeExtractFunction:
    """Test safe_extract function with sanitization."""
    
    @pytest.mark.asyncio
    async def test_safe_extract_sanitizes_errors(self):
        """Test safe_extract function sanitizes error information."""
        # This test will FAIL initially - safe_extract doesn't use sanitization yet
        
        def mock_sensitive_error(*args, **kwargs):
            raise Exception("Config error: SECRET_TOKEN=abc123def456 invalid")
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.side_effect = mock_sensitive_error
            
            from tools.web_extract import safe_extract
            
            result = await safe_extract("https://example.com")
            
            # Verify error sanitization in safe_extract
            assert result["success"] is False
            assert "error" in result
            assert "SECRET_TOKEN=abc123def456" not in result["error"]
            assert "[REDACTED]" in result["error"]

    @pytest.mark.asyncio
    async def test_safe_extract_preserves_useful_error_structure(self):
        """Test safe_extract preserves useful error structure."""
        def mock_connection_error(*args, **kwargs):
            raise ConnectionError("Unable to connect to https://example.com")
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.side_effect = mock_connection_error
            
            from tools.web_extract import safe_extract
            
            result = await safe_extract("https://example.com")
            
            # Verify structure is preserved
            assert result["success"] is False
            assert "error" in result
            assert "Unable to connect" in result["error"]
            assert "https://example.com" in result["error"]
            assert result["url"] == "https://example.com"
            assert result["content"] is None


class TestPydanticConfigMigration:
    """Test Pydantic ConfigDict migration."""
    
    def test_webextractparams_uses_configdict(self):
        """Test WebExtractParams uses ConfigDict instead of class Config."""
        # This test will FAIL initially - need to migrate to ConfigDict
        from tools.web_extract import WebExtractParams
        
        # Check that model_config exists and is ConfigDict
        assert hasattr(WebExtractParams, 'model_config')
        
        # Create instance to verify it works
        params = WebExtractParams(url="https://example.com")
        assert params.url == "https://example.com"

    def test_no_pydantic_warnings(self):
        """Test that no Pydantic deprecation warnings are generated."""
        import warnings
        
        # Capture warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            from tools.web_extract import WebExtractParams
            
            # Create instance
            params = WebExtractParams(url="https://example.com")
            
            # Check for Pydantic deprecation warnings
            pydantic_warnings = [
                warning for warning in w 
                if "PydanticDeprecatedSince20" in str(warning.category)
                or "class-based `config`" in str(warning.message)
            ]
            
            assert len(pydantic_warnings) == 0, f"Pydantic warnings found: {pydantic_warnings}"


class TestIntegrationWithMCP:
    """Test integration with MCP server."""
    
    @pytest.mark.asyncio
    async def test_mcp_server_sanitizes_tool_errors(self):
        """Test MCP server returns sanitized errors from tool calls."""
        def mock_sensitive_error(*args, **kwargs):
            raise Exception("Database mysql://root:admin123@localhost:3306 unavailable")
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.side_effect = mock_sensitive_error
            
            from fastmcp import Client
            from server import mcp
            
            async with Client(mcp) as client:
                result = await client.call_tool_mcp("web_content_extract", {
                    "url": "https://example.com"
                })
                
                # Extract response content
                if result.isError:
                    response_text = result.content[0].text
                else:
                    response_text = result.content[0].text
                
                # Verify sanitization at MCP level
                assert "admin123" not in response_text
                assert "root:admin123" not in response_text
                assert "[REDACTED]" in response_text or "Error extracting content" in response_text

    @pytest.mark.asyncio
    async def test_mcp_server_preserves_valid_responses(self):
        """Test MCP server preserves valid responses without sanitization."""
        mock_result = MagicMock()
        mock_result.markdown = "# Valid Content\n\nThis is safe content."
        mock_result.title = "Valid Page"
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            from fastmcp import Client
            from server import mcp
            
            async with Client(mcp) as client:
                result = await client.call_tool_mcp("web_content_extract", {
                    "url": "https://example.com"
                })
                
                # Verify valid content is not affected
                assert result.isError is False
                response_text = result.content[0].text
                assert "# Valid Content" in response_text
                assert "This is safe content." in response_text
                assert "[REDACTED]" not in response_text


class TestErrorSanitizationPerformance:
    """Test error sanitization performance in web extract."""
    
    @pytest.mark.asyncio
    async def test_sanitization_performance_overhead(self):
        """Test that error sanitization doesn't add significant overhead."""
        import time
        
        def mock_error(*args, **kwargs):
            raise Exception("Error with sensitive data: password123, sk-abcd1234, /etc/passwd")
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.side_effect = mock_error
            
            from tools.web_extract import web_content_extract
            
            # Time multiple sanitization operations
            start_time = time.perf_counter()
            
            for _ in range(100):
                params = WebExtractParams(url="https://example.com")
                result = await web_content_extract(params)
                assert "[REDACTED]" in result
            
            duration = time.perf_counter() - start_time
            
            # Should be reasonably fast (under 3 seconds for 100 operations including mock overhead)
            assert duration < 3.0, f"Sanitization overhead too high: {duration:.4f}s for 100 operations"

    @pytest.mark.asyncio
    async def test_no_sanitization_on_success(self):
        """Test that successful operations don't trigger sanitization."""
        mock_result = MagicMock()
        mock_result.markdown = "Normal content without sensitive data"
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            from tools.web_extract import web_content_extract
            
            params = WebExtractParams(url="https://example.com")
            result = await web_content_extract(params)
            
            # Verify normal content is returned unchanged
            assert result == "Normal content without sensitive data"
            assert "[REDACTED]" not in result


class TestBackwardCompatibility:
    """Test backward compatibility after sanitization integration."""
    
    @pytest.mark.asyncio
    async def test_return_format_unchanged(self):
        """Test that return format is unchanged after sanitization."""
        def mock_error(*args, **kwargs):
            raise Exception("Test error with password: secret123")
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.side_effect = mock_error
            
            from tools.web_extract import web_content_extract
            
            params = WebExtractParams(url="https://example.com")
            result = await web_content_extract(params)
            
            # Verify return type and format
            assert isinstance(result, str)
            assert result.startswith("Error extracting content:")
            assert "secret123" not in result

    @pytest.mark.asyncio
    async def test_safe_extract_format_unchanged(self):
        """Test that safe_extract format is unchanged."""
        def mock_error(*args, **kwargs):
            raise Exception("Database error: postgresql://user:pass@localhost")
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.side_effect = mock_error
            
            from tools.web_extract import safe_extract
            
            result = await safe_extract("https://example.com")
            
            # Verify return structure is unchanged
            assert isinstance(result, dict)
            assert "success" in result
            assert "error" in result
            assert "url" in result
            assert "content" in result
            assert result["success"] is False
            assert "pass" not in result["error"]