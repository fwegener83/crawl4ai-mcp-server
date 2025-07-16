"""
Domain link preview implementation.
This module provides quick domain link analysis without full crawling.
"""

import json
import logging
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict, field_validator
from urllib.parse import urlparse

# Mock imports for testing (will be replaced with real imports later)
try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
except ImportError:
    # Create mock classes for testing
    class AsyncWebCrawler:
        def __init__(self, config=None):
            self.config = config
        
        async def __aenter__(self):
            return self
        
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        
        async def arun(self, url, config=None):
            return {"success": True, "url": url}
    
    class BrowserConfig:
        def __init__(self, headless=True, verbose=False):
            self.headless = headless
            self.verbose = verbose
    
    class CrawlerRunConfig:
        def __init__(self, verbose=False, stream=False, log_console=False):
            self.verbose = verbose
            self.stream = stream
            self.log_console = log_console

# Set up logging
logger = logging.getLogger(__name__)


class DomainLinkPreviewParams(BaseModel):
    """Parameters for domain link preview."""
    
    model_config = ConfigDict(frozen=True)
    
    domain_url: str = Field(..., description="The base URL/domain to analyze")
    include_external: bool = Field(default=False, description="Include external links")
    
    @field_validator('domain_url')
    @classmethod
    def validate_domain_url(cls, v):
        """Validate domain URL format and scheme."""
        if not v or not v.strip():
            raise ValueError("Domain URL cannot be empty")
        
        # Strip whitespace
        v = v.strip()
        
        # Parse URL
        parsed = urlparse(v)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid domain URL format")
        
        # Check scheme
        if parsed.scheme not in ['http', 'https']:
            raise ValueError("Domain URL must use HTTP or HTTPS protocol")
        
        return v


def sanitize_error_message(error_message: str) -> str:
    """Sanitize error message (placeholder - will use actual sanitizer)."""
    # This is a placeholder - will integrate with actual error sanitizer
    return error_message


async def extract_links_from_domain(domain_url: str, include_external: bool = False) -> str:
    """Extract links from domain (mock implementation)."""
    # Mock implementation for testing
    parsed = urlparse(domain_url)
    domain = parsed.netloc
    
    mock_links = [
        {"url": f"{domain_url}/about", "text": "About", "type": "internal"},
        {"url": f"{domain_url}/contact", "text": "Contact", "type": "internal"}
    ]
    
    if include_external:
        mock_links.append({"url": "https://external.com", "text": "External", "type": "external"})
    
    internal_count = sum(1 for link in mock_links if link["type"] == "internal")
    external_count = sum(1 for link in mock_links if link["type"] == "external")
    
    return json.dumps({
        "success": True,
        "domain": domain,
        "total_links": len(mock_links),
        "internal_links": internal_count,
        "external_links": external_count,
        "links": mock_links
    })


async def domain_link_preview_impl(params: DomainLinkPreviewParams) -> str:
    """Implementation of domain link preview."""
    try:
        # Extract domain from URL
        parsed = urlparse(params.domain_url)
        domain = parsed.netloc
        
        # Extract links from domain
        result = await extract_links_from_domain(
            domain_url=params.domain_url,
            include_external=params.include_external
        )
        
        return result
        
    except Exception as e:
        sanitized_error = sanitize_error_message(str(e))
        logger.error(f"Domain link preview failed for {params.domain_url}: {sanitized_error}")
        
        # Extract domain for error response
        parsed = urlparse(params.domain_url)
        domain = parsed.netloc
        
        return json.dumps({
            "success": False,
            "error": sanitized_error,
            "domain": domain,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })