"""
Domain link preview implementation.
This module provides quick domain link analysis without full crawling.
"""

import json
import logging
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict, field_validator
from urllib.parse import urlparse

# Real Crawl4AI imports with fallback to mocks for CI
try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    CRAWL4AI_AVAILABLE = True
except ImportError:
    # Mock implementations for CI
    CRAWL4AI_AVAILABLE = False
    
    class AsyncWebCrawler:
        def __init__(self, config=None):
            self.config = config
        
        async def __aenter__(self):
            return self
        
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        
        async def arun(self, url, config=None):
            return MockCrawlResult(url=url)
    
    class BrowserConfig:
        def __init__(self, headless=True, verbose=False):
            self.headless = headless
            self.verbose = verbose
    
    class CrawlerRunConfig:
        def __init__(self, verbose=False, log_console=False, **kwargs):
            self.verbose = verbose
            self.log_console = log_console
    
    class MockCrawlResult:
        def __init__(self, url="https://example.com", title="Mock Title", 
                     content="Mock content", success=True):
            self.url = url
            self.markdown = content
            self.success = success
            self.links = {
                "internal": [{"href": f"{url}/about", "text": "About"}],
                "external": [{"href": "https://external.com", "text": "External"}]
            }
            self.metadata = {"title": title}

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
    """Sanitize error message using actual sanitizer."""
    try:
        from tools.error_sanitizer import sanitize_error_message as real_sanitizer
        return real_sanitizer(error_message)
    except ImportError:
        # Fallback if sanitizer not available
        return error_message


async def extract_links_from_domain(domain_url: str, include_external: bool = False) -> str:
    """Extract links from domain using real Crawl4AI."""
    try:
        # Extract domain from URL
        parsed = urlparse(domain_url)
        domain = parsed.netloc
        
        # Configure browser for link extraction
        browser_config = BrowserConfig(headless=True, verbose=False)
        config = CrawlerRunConfig(verbose=False, log_console=False)
        
        # Perform crawl to extract links
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=domain_url, config=config)
            
            if not result.success:
                return json.dumps({
                    "success": False,
                    "error": "Failed to crawl domain",
                    "domain": domain,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            
            # Extract links from the result
            links = []
            internal_count = 0
            external_count = 0
            
            # Get links from result (if available)
            if hasattr(result, 'links') and result.links:
                # Handle both dict and list formats
                if isinstance(result.links, dict):
                    links_data = result.links.get('internal', []) + result.links.get('external', [])
                else:
                    links_data = result.links
                
                for link in links_data:
                    # Handle different link formats
                    if isinstance(link, dict):
                        link_url = link.get('href', '') or link.get('url', '')
                        link_text = link.get('text', '') or link.get('title', '')
                    else:
                        # Handle string links
                        link_url = str(link)
                        link_text = link_url
                    
                    # Determine if link is internal or external
                    if link_url.startswith(('http://', 'https://')):
                        link_parsed = urlparse(link_url)
                        is_internal = link_parsed.netloc == domain
                    else:
                        # Relative links are internal
                        is_internal = True
                        if link_url.startswith('/'):
                            link_url = f"{parsed.scheme}://{domain}{link_url}"
                        else:
                            link_url = f"{domain_url.rstrip('/')}/{link_url}"
                    
                    link_type = "internal" if is_internal else "external"
                    
                    # Count links
                    if is_internal:
                        internal_count += 1
                    else:
                        external_count += 1
                    
                    # Add to links list if appropriate
                    if is_internal or include_external:
                        links.append({
                            "url": link_url,
                            "text": link_text,
                            "type": link_type
                        })
            
            # If no links found in result, try to extract from markdown
            if not links and hasattr(result, 'markdown') and result.markdown:
                # Simple markdown link extraction
                import re
                link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
                markdown_links = re.findall(link_pattern, result.markdown)
                
                for link_text, link_url in markdown_links:
                    # Determine if link is internal or external
                    if link_url.startswith(('http://', 'https://')):
                        link_parsed = urlparse(link_url)
                        is_internal = link_parsed.netloc == domain
                    else:
                        # Relative links are internal
                        is_internal = True
                        if link_url.startswith('/'):
                            link_url = f"{parsed.scheme}://{domain}{link_url}"
                        else:
                            link_url = f"{domain_url.rstrip('/')}/{link_url}"
                    
                    link_type = "internal" if is_internal else "external"
                    
                    # Count links
                    if is_internal:
                        internal_count += 1
                    else:
                        external_count += 1
                    
                    # Add to links list if appropriate
                    if is_internal or include_external:
                        links.append({
                            "url": link_url,
                            "text": link_text,
                            "type": link_type
                        })
            
            return json.dumps({
                "success": True,
                "domain": domain,
                "total_links": len(links),
                "internal_links": internal_count,
                "external_links": external_count,
                "links": links
            })
            
    except Exception as e:
        logger.error(f"Link extraction failed: {e}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "domain": domain,
            "timestamp": datetime.now(timezone.utc).isoformat()
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