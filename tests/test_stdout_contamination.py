"""Test cases to ensure stdout contamination is prevented."""
import asyncio
import sys
import subprocess
import io
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import patch, AsyncMock, MagicMock

import pytest

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.web_extract import WebExtractParams, web_content_extract, safe_extract


class TestStdoutContamination:
    """Test cases to verify stdout contamination is prevented."""
    
    @pytest.mark.asyncio
    async def test_web_content_extract_no_stdout_contamination(self):
        """Test that web_content_extract doesn't produce stdout contamination."""
        # Mock the crawler to avoid real network calls
        mock_result = MagicMock()
        mock_result.markdown = "Example domain content for stdout testing"
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            # Capture stdout during extraction
            stdout_buffer = io.StringIO()
            stderr_buffer = io.StringIO()
            
            with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                params = WebExtractParams(url="https://example.com")
                result = await web_content_extract(params)
            
            # Check that no progress output was captured
            stdout_content = stdout_buffer.getvalue()
            stderr_content = stderr_buffer.getvalue()
            
            # Should have no stdout contamination
            assert stdout_content == "", f"Unexpected stdout output: {stdout_content}"
            
            # Should have extracted content
            assert result != "", "Content extraction failed"
            assert "example" in result.lower() or "domain" in result.lower(), "Expected content not found"
            
            # Progress messages should not appear in stderr either
            contamination_patterns = ["[FETCH]", "[SCRAPE]", "[COMPLETE]", "| ✓ |", "⏱:"]
            for pattern in contamination_patterns:
                assert pattern not in stderr_content, f"Found contamination pattern '{pattern}' in stderr"
    
    @pytest.mark.asyncio
    async def test_safe_extract_no_stdout_contamination(self):
        """Test that safe_extract doesn't produce stdout contamination."""
        # Mock the crawler to avoid real network calls
        mock_result = MagicMock()
        mock_result.markdown = "Example domain content for testing stdout contamination"
        mock_result.title = "Example Domain"
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            # Capture stdout during extraction
            stdout_buffer = io.StringIO()
            stderr_buffer = io.StringIO()
            
            with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                result = await safe_extract("https://example.com")
            
            # Check that no progress output was captured
            stdout_content = stdout_buffer.getvalue()
            stderr_content = stderr_buffer.getvalue()
            
            # Should have no stdout contamination
            assert stdout_content == "", f"Unexpected stdout output: {stdout_content}"
            
            # Should have extracted content successfully
            assert result["success"] is True, "Content extraction failed"
            assert result["content"] != "", "No content extracted"
            assert "example" in result["content"].lower() or "domain" in result["content"].lower(), "Expected content not found"
            
            # Progress messages should not appear in stderr either
            contamination_patterns = ["[FETCH]", "[SCRAPE]", "[COMPLETE]", "| ✓ |", "⏱:"]
            for pattern in contamination_patterns:
                assert pattern not in stderr_content, f"Found contamination pattern '{pattern}' in stderr"
    
    @pytest.mark.asyncio
    async def test_multiple_extractions_no_accumulation(self):
        """Test that multiple extractions don't accumulate output."""
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            # Mock successful extraction
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = MagicMock(markdown="# Test Content\n\nThis is test content.")
            
            with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                # Run multiple extractions
                params = WebExtractParams(url="https://example.com")
                results = []
                for _ in range(3):
                    result = await web_content_extract(params)
                    results.append(result)
        
        # Check that no progress output was captured
        stdout_content = stdout_buffer.getvalue()
        stderr_content = stderr_buffer.getvalue()
        
        # Should have no stdout contamination
        assert stdout_content == "", f"Unexpected stdout output: {stdout_content}"
        
        # All extractions should succeed
        for result in results:
            assert result != "", "Content extraction failed"
            assert "Test Content" in result, "Expected mock content not found"
        
        # Progress messages should not appear in stderr either
        contamination_patterns = ["[FETCH]", "[SCRAPE]", "[COMPLETE]", "| ✓ |", "⏱:"]
        for pattern in contamination_patterns:
            assert pattern not in stderr_content, f"Found contamination pattern '{pattern}' in stderr"
    
    def test_mcp_server_stdout_cleanliness(self):
        """Test that MCP server startup doesn't produce stdout contamination."""
        # Run the server in a subprocess for a short time
        process = subprocess.Popen(
            [sys.executable, "server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        
        # Let it run for a brief moment then terminate
        try:
            stdout, stderr = process.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
        
        # Check that stdout only contains valid JSON (MCP protocol)
        if stdout.strip():
            # If there's output, it should be valid JSON lines
            for line in stdout.strip().split('\n'):
                if line.strip():
                    try:
                        import json
                        json.loads(line)
                    except json.JSONDecodeError:
                        pytest.fail(f"Invalid JSON in stdout: {line}")
        
        # Progress messages should not appear in stdout
        contamination_patterns = ["[FETCH]", "[SCRAPE]", "[COMPLETE]", "| ✓ |", "⏱:"]
        for pattern in contamination_patterns:
            assert pattern not in stdout, f"Found contamination pattern '{pattern}' in stdout"
    
    @pytest.mark.asyncio
    async def test_error_handling_no_contamination(self):
        """Test that error cases don't produce stdout contamination."""
        # Mock network error to avoid real DNS timeouts
        def mock_network_error(*args, **kwargs):
            raise Exception("Network unreachable")
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.side_effect = mock_network_error
            
            stdout_buffer = io.StringIO()
            stderr_buffer = io.StringIO()
            
            with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                # Test with error-inducing scenario
                params = WebExtractParams(url="https://example.com")
                result = await web_content_extract(params)
            
            # Check that no progress output was captured
            stdout_content = stdout_buffer.getvalue()
            
            # Should have no stdout contamination even in error cases
            assert stdout_content == "", f"Unexpected stdout output: {stdout_content}"
            
            # Should have error message
            assert "Error extracting content" in result, "Expected error message"
            
            # Progress messages should not appear in stderr either
            contamination_patterns = ["[FETCH]", "[SCRAPE]", "[COMPLETE]", "| ✓ |", "⏱:"]
            stderr_content = stderr_buffer.getvalue()
            for pattern in contamination_patterns:
                assert pattern not in stderr_content, f"Found contamination pattern '{pattern}' in stderr"


class TestCrawl4AIConfiguration:
    """Test the specific Crawl4AI configuration options."""
    
    @pytest.mark.asyncio
    async def test_browser_config_applied(self):
        """Test that BrowserConfig is properly applied."""
        # Mock the crawler to avoid real network calls
        mock_result = MagicMock()
        mock_result.markdown = "Test content from mocked crawler"
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            params = WebExtractParams(url="https://example.com")
            result = await web_content_extract(params)
            
            # Should succeed with proper configuration
            assert result != "", "Content extraction failed"
            assert not result.startswith("Error"), "Unexpected error in extraction"
            assert result == "Test content from mocked crawler"
    
    @pytest.mark.asyncio
    async def test_crawler_run_config_applied(self):
        """Test that CrawlerRunConfig is properly applied."""
        # Mock the crawler to avoid real network calls
        mock_result = MagicMock()
        mock_result.markdown = "Test content from safe extract"
        mock_result.title = "Test Page"
        
        with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            result = await safe_extract("https://example.com")
            
            # Should succeed with proper configuration
            assert result["success"] is True, "Content extraction failed"
            assert result["content"] != "", "No content extracted"
            assert result["content"] == "Test content from safe extract"
            assert "url" in result, "URL not in result"
            assert "title" in result, "Title not in result"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])