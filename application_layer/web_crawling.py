"""
Web crawling use-case functions.

Contains protocol-agnostic business logic for web content extraction and crawling operations
that can be shared between API and MCP endpoints.
"""

from typing import List, Optional, Dict, Any
from services.interfaces import CrawlResult, DeepCrawlConfig, LinkPreview


class ValidationError(Exception):
    """Exception raised when input validation fails."""
    
    def __init__(self, code: str, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


async def extract_content_use_case(
    web_service,
    url: str
) -> CrawlResult:
    """
    Shared web content extraction logic for API and MCP protocols.
    
    Args:
        web_service: Web service instance
        url: URL to extract content from
        
    Returns:
        ExtractResult object with consistent format
        
    Raises:
        ValidationError: When input parameters are invalid
        Exception: When extraction errors occur
    """
    
    # Input validation (test-driven)
    if not isinstance(url, str):
        raise ValidationError("INVALID_URL_TYPE", "URL must be a string")
    
    if not url or not url.strip():
        raise ValidationError("MISSING_URL", "URL is required")
    
    # Normalize URL
    url = url.strip()
    
    # Basic URL format validation
    if not (url.startswith('http://') or url.startswith('https://')):
        raise ValidationError("INVALID_URL_FORMAT", "URL must start with http:// or https://")
    
    # Execute content extraction
    result = await web_service.extract_content(url)
    
    # Return consistent format
    return result


async def deep_crawl_use_case(
    web_service,
    domain_url: str,
    max_depth: int = 1,
    max_pages: int = 10,
    crawl_strategy: str = "bfs",
    include_external: bool = False,
    url_patterns: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None
) -> List[CrawlResult]:
    """
    Shared domain deep crawling logic for API and MCP protocols.
    
    Args:
        web_service: Web service instance
        domain_url: Domain URL to crawl
        max_depth: Maximum crawl depth
        max_pages: Maximum pages to crawl
        crawl_strategy: Crawling strategy (bfs, dfs)
        include_external: Include external links
        url_patterns: URL patterns to include
        exclude_patterns: URL patterns to exclude
        
    Returns:
        List of CrawlResult objects with consistent format
        
    Raises:
        ValidationError: When input parameters are invalid
        Exception: When crawling errors occur
    """
    
    # Input validation (test-driven)
    if not isinstance(domain_url, str):
        raise ValidationError("INVALID_DOMAIN_URL_TYPE", "Domain URL must be a string")
    
    if not domain_url or not domain_url.strip():
        raise ValidationError("MISSING_DOMAIN_URL", "Domain URL is required")
        
    if not isinstance(max_depth, int) or max_depth < 1:
        raise ValidationError("INVALID_MAX_DEPTH", "Max depth must be a positive integer")
        
    if not isinstance(max_pages, int) or max_pages < 1:
        raise ValidationError("INVALID_MAX_PAGES", "Max pages must be a positive integer")
        
    if crawl_strategy not in ["bfs", "dfs"]:
        raise ValidationError("INVALID_CRAWL_STRATEGY", "Crawl strategy must be 'bfs' or 'dfs'")
        
    if not isinstance(include_external, bool):
        raise ValidationError("INVALID_INCLUDE_EXTERNAL_TYPE", "Include external must be a boolean")
    
    # Normalize domain URL
    domain_url = domain_url.strip()
    
    # Create crawl configuration
    config = DeepCrawlConfig(
        domain_url=domain_url,
        max_depth=max_depth,
        max_pages=max_pages,
        crawl_strategy=crawl_strategy,
        include_external=include_external,
        url_patterns=url_patterns,
        exclude_patterns=exclude_patterns
    )
    
    # Execute deep crawling
    results = await web_service.deep_crawl(config)
    
    # Return consistent format
    return results


async def link_preview_use_case(
    web_service,
    domain_url: str,
    include_external: bool = False
) -> LinkPreview:
    """
    Shared link preview logic for API and MCP protocols.
    
    Args:
        web_service: Web service instance
        domain_url: Domain URL to preview links for
        include_external: Include external links
        
    Returns:
        LinkPreview object with consistent format
        
    Raises:
        ValidationError: When input parameters are invalid
        Exception: When preview errors occur
    """
    
    # Input validation (test-driven)
    if not isinstance(domain_url, str):
        raise ValidationError("INVALID_DOMAIN_URL_TYPE", "Domain URL must be a string")
    
    if not domain_url or not domain_url.strip():
        raise ValidationError("MISSING_DOMAIN_URL", "Domain URL is required")
        
    if not isinstance(include_external, bool):
        raise ValidationError("INVALID_INCLUDE_EXTERNAL_TYPE", "Include external must be a boolean")
    
    # Normalize domain URL
    domain_url = domain_url.strip()
    
    # Execute link preview
    result = await web_service.preview_links(domain_url, include_external)
    
    # Return consistent format
    return result