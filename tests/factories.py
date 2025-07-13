"""Mock factories for testing."""
import re
from unittest.mock import AsyncMock, MagicMock
from typing import Dict, Any, Union, Optional


class CrawlResultFactory:
    """Factory for creating realistic crawl result mocks."""
    
    @staticmethod
    def create_success_result(content="Test content", title="Test Page", url="https://example.com"):
        """Create a successful crawl result mock."""
        result = MagicMock()
        result.markdown = content
        result.title = title
        result.success = True
        result.url = url
        result.status_code = 200
        result.cleaned_html = f"<html><body>{content}</body></html>"
        result.extracted_content = None
        result.screenshot = None
        result.links = {"internal": [], "external": []}
        result.media = {"images": [], "videos": [], "audios": []}
        return result
    
    @staticmethod
    def create_failure_result(error_msg="Network error", url="https://example.com"):
        """Create a failed crawl result mock."""
        result = MagicMock()
        result.markdown = None
        result.title = None
        result.success = False
        result.url = url
        result.status_code = 500
        result.error_message = error_msg
        return result
    
    @staticmethod
    def create_timeout_result(url="https://example.com"):
        """Create a timeout result mock."""
        return CrawlResultFactory.create_failure_result("Request timeout", url)


class AsyncContextManagerMock:
    """Custom async context manager mock for complex testing scenarios."""
    
    def __init__(self, mock_instance=None):
        self.mock_instance = mock_instance or AsyncMock()
        
    async def __aenter__(self):
        return self.mock_instance
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return None


class AsyncWebCrawlerMockFactory:
    """Factory for creating AsyncWebCrawler mocks with configurable behavior."""
    
    @staticmethod
    def create_mock(default_result=None, response_config=None):
        """
        Create AsyncWebCrawler mock with configurable responses.
        
        Args:
            default_result: Default result to return for unmatched URLs
            response_config: Dict mapping URL patterns to responses/exceptions
            
        Returns:
            Tuple of (mock_crawler, mock_instance)
        """
        mock_instance = AsyncMock()
        
        if response_config:
            def side_effect(url=None, config=None):
                url_lower = url.lower() if url else ""
                
                # Check response patterns
                for pattern, response in response_config.items():
                    if pattern == 'default':
                        continue
                    
                    if pattern in url_lower:
                        if isinstance(response, type) and issubclass(response, Exception):
                            raise response(f"Mock error for pattern '{pattern}': {url}")
                        elif isinstance(response, Exception):
                            raise response
                        else:
                            return response
                
                # Default response
                default_response = response_config.get('default', 'success')
                if default_response == 'success':
                    return default_result or CrawlResultFactory.create_success_result(url=url)
                else:
                    return default_response
            
            mock_instance.arun.side_effect = side_effect
        else:
            # Simple default behavior
            mock_instance.arun.return_value = default_result or CrawlResultFactory.create_success_result()
        
        # Create a mock class that acts as an async context manager factory
        class MockCrawlerClass:
            def __init__(self):
                pass
            
            def __call__(self, config=None):
                return AsyncContextManagerMock(mock_instance)
        
        mock_crawler = MockCrawlerClass()
        
        return mock_crawler, mock_instance


class SecurityMockFactory:
    """Factory for creating security scenario mock responses."""
    
    def __init__(self):
        """Initialize security mock factory with predefined patterns."""
        self.malicious_patterns = [
            'javascript:', 'data:', 'file:', 'ftp:', 'sftp:', 'ldap:', 'gopher:', 'mailto:'
        ]
        
        self.private_ip_patterns = [
            '127.0.0.1', 'localhost', '192.168.', '10.', '172.16.', '172.31.',
            '[::1]', '0.0.0.0'
        ]
        
        self.suspicious_ports = [
            ':22/', ':23/', ':25/', ':53/', ':110/', ':143/', ':993/', ':995/',
            ':1433/', ':1521/', ':3306/', ':5432/', ':6379/', ':27017/'
        ]
    
    def mock_response(self, url: str):
        """
        Generate mock response based on URL security analysis.
        
        Args:
            url: URL to analyze
            
        Returns:
            Mock crawl result or raises appropriate exception
            
        Raises:
            ValueError: For malicious URL schemes
            ConnectionError: For private IP access
            ConnectionRefusedError: For suspicious port access
        """
        url_lower = url.lower()
        
        # Check for malicious URL schemes
        for pattern in self.malicious_patterns:
            if pattern in url_lower:
                raise ValueError(f"Invalid URL scheme: {url}")
        
        # Check for private IP access
        for pattern in self.private_ip_patterns:
            if pattern in url_lower:
                raise ConnectionError(f"Private IP access denied: {url}")
        
        # Check for suspicious port access
        for pattern in self.suspicious_ports:
            if pattern in url:
                raise ConnectionRefusedError(f"Port access blocked: {url}")
        
        # Safe URL - return success result
        return CrawlResultFactory.create_success_result(
            content=f"Safe content from {url}",
            title="Safe Page",
            url=url
        )


class MockConfigValidator:
    """Validator for mock configuration."""
    
    @staticmethod
    def validate(config: Dict[str, Any]) -> bool:
        """
        Validate mock configuration structure.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(config, dict):
            return False
        
        for pattern, response in config.items():
            if pattern == 'default':
                if response not in ['success', 'error'] and not hasattr(response, '__call__'):
                    return False
            else:
                # Response should be an exception class, exception instance, or 'success'
                if not (
                    isinstance(response, type) and issubclass(response, Exception) or
                    isinstance(response, Exception) or
                    response == 'success' or
                    hasattr(response, '__call__')
                ):
                    return False
        
        return True


# Convenience function for quick mock setup
def create_security_test_mock(blocked_patterns=None, success_patterns=None):
    """
    Create a security test mock with common patterns.
    
    Args:
        blocked_patterns: List of URL patterns that should be blocked
        success_patterns: List of URL patterns that should succeed
        
    Returns:
        Configured AsyncWebCrawler mock
    """
    blocked_patterns = blocked_patterns or [
        'javascript:', 'file:', 'data:', '127.0.0.1', 'localhost', ':22/', ':3306/'
    ]
    
    response_config = {}
    
    # Add blocked patterns
    for pattern in blocked_patterns:
        if any(scheme in pattern for scheme in ['javascript:', 'file:', 'data:']):
            response_config[pattern] = ValueError("Invalid URL scheme")
        elif any(ip in pattern for ip in ['127.0.0.1', 'localhost', '192.168.']):
            response_config[pattern] = ConnectionError("Private IP blocked")
        elif ':' in pattern and '/' in pattern:  # Port pattern
            response_config[pattern] = ConnectionRefusedError("Port blocked")
    
    response_config['default'] = 'success'
    
    return AsyncWebCrawlerMockFactory.create_mock(response_config=response_config)