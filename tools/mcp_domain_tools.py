"""
MCP tool registration for domain crawler tools.
This module provides MCP tool decorators and integrations.
"""

import logging
from typing import List, Optional

# Import the core implementations
from tools.domain_crawler import domain_deep_crawl_impl, DomainDeepCrawlParams
from tools.domain_link_preview import domain_link_preview_impl, DomainLinkPreviewParams
from tools.error_sanitizer import sanitize_error_message

# Set up logging
logger = logging.getLogger(__name__)


async def domain_deep_crawl(
    domain_url: str,
    max_depth: int = 2,
    crawl_strategy: str = "bfs",
    max_pages: int = 50,
    include_external: bool = False,
    url_patterns: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None,
    keywords: Optional[List[str]] = None,
    stream_results: bool = False
) -> str:
    """
    Crawl a complete domain with configurable depth and strategies.
    
    Args:
        domain_url: The base URL/domain to crawl
        max_depth: Maximum crawl depth (0-10)
        crawl_strategy: Crawling strategy (bfs, dfs, best_first)
        max_pages: Maximum pages to crawl (1-1000)
        include_external: Whether to include external links
        url_patterns: URL patterns to include (glob patterns)
        exclude_patterns: URL patterns to exclude (glob patterns)
        keywords: Keywords for BestFirst scoring
        stream_results: Whether to stream results in real-time
        
    Returns:
        JSON string with crawl results or error information
    """
    logger.info(f"Starting domain deep crawl for: {domain_url}")
    
    try:
        params = DomainDeepCrawlParams(
            domain_url=domain_url,
            max_depth=max_depth,
            crawl_strategy=crawl_strategy,
            max_pages=max_pages,
            include_external=include_external,
            url_patterns=url_patterns,
            exclude_patterns=exclude_patterns,
            keywords=keywords,
            stream_results=stream_results
        )
        
        result = await domain_deep_crawl_impl(params)
        
        logger.info(f"Domain crawl completed for {domain_url}")
        return result
        
    except Exception as e:
        error_msg = f"Domain crawl failed: {str(e)}"
        logger.error(error_msg)
        return sanitize_error_message(error_msg)


async def domain_link_preview(
    domain_url: str,
    include_external: bool = False
) -> str:
    """
    Get a quick preview of links available on a domain.
    
    Args:
        domain_url: The base URL/domain to analyze
        include_external: Whether to include external links
        
    Returns:
        JSON string with link preview or error information
    """
    logger.info(f"Starting domain link preview for: {domain_url}")
    
    try:
        params = DomainLinkPreviewParams(
            domain_url=domain_url,
            include_external=include_external
        )
        
        result = await domain_link_preview_impl(params)
        
        logger.info(f"Domain link preview completed for {domain_url}")
        return result
        
    except Exception as e:
        error_msg = f"Domain link preview failed: {str(e)}"
        logger.error(error_msg)
        return sanitize_error_message(error_msg)