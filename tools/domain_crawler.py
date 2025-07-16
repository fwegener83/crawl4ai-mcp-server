"""
Domain deep crawler implementation.
This module provides domain-based deep crawling capabilities for MCP tools.
"""

import json
import logging
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional, Any, Dict
from urllib.parse import urlparse, urljoin

# Real Crawl4AI imports
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.deep_crawling import (
    BFSDeepCrawlStrategy, 
    DFSDeepCrawlStrategy, 
    BestFirstCrawlingStrategy,
    FilterChain,
    DomainFilter,
    URLPatternFilter,
    KeywordRelevanceScorer
)

# Set up logging
logger = logging.getLogger(__name__)


class DomainDeepCrawlParams(BaseModel):
    """Parameters for domain deep crawling."""
    
    model_config = ConfigDict(frozen=True)
    
    domain_url: str = Field(..., description="The base URL/domain to crawl")
    max_depth: int = Field(default=2, ge=0, le=10, description="Maximum crawl depth")
    crawl_strategy: str = Field(default="bfs", description="Crawling strategy")
    max_pages: int = Field(default=50, ge=1, le=1000, description="Maximum pages to crawl")
    include_external: bool = Field(default=False, description="Include external links")
    url_patterns: List[str] = Field(default=[], description="URL patterns to include")
    exclude_patterns: List[str] = Field(default=[], description="URL patterns to exclude")
    keywords: List[str] = Field(default=[], description="Keywords for BestFirst scoring")
    stream_results: bool = Field(default=False, description="Stream results in real-time")
    
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
    
    @field_validator('crawl_strategy')
    @classmethod
    def validate_crawl_strategy(cls, v):
        """Validate crawl strategy."""
        allowed_strategies = ['bfs', 'dfs', 'best_first']
        if v not in allowed_strategies:
            raise ValueError(f"Strategy must be one of: {allowed_strategies}")
        return v


# Real Crawl4AI strategy implementations


def create_crawl_strategy(
    strategy_name: str,
    max_depth: int,
    max_pages: int,
    filter_chain: Optional[FilterChain],
    keywords: List[str]
) -> Any:
    """Create a real Crawl4AI deep crawling strategy."""
    
    valid_strategies = ['bfs', 'dfs', 'best_first']
    if strategy_name not in valid_strategies:
        raise ValueError(f"Unknown strategy: {strategy_name}")
    
    # Create the appropriate strategy
    if strategy_name == "bfs":
        return BFSDeepCrawlStrategy(
            max_depth=max_depth,
            max_pages=max_pages,
            filter_chain=filter_chain,
            include_external=False
        )
    elif strategy_name == "dfs":
        return DFSDeepCrawlStrategy(
            max_depth=max_depth,
            max_pages=max_pages,
            filter_chain=filter_chain,
            include_external=False
        )
    elif strategy_name == "best_first":
        # Create keyword scorer if keywords are provided
        scorer = None
        if keywords:
            scorer = KeywordRelevanceScorer(keywords=keywords, weight=0.8)
        
        return BestFirstCrawlingStrategy(
            max_depth=max_depth,
            max_pages=max_pages,
            filter_chain=filter_chain,
            url_scorer=scorer,
            include_external=False
        )


def build_filter_chain(
    domain_url: str,
    include_external: bool,
    url_patterns: List[str],
    exclude_patterns: List[str]
) -> FilterChain:
    """Build real Crawl4AI filter chain for URL filtering."""
    
    # Extract domain from URL
    parsed = urlparse(domain_url)
    domain = parsed.netloc
    
    # Create list of filters
    filters = []
    
    # Add domain filter if not including external links
    if not include_external:
        filters.append(DomainFilter(allowed_domains=[domain]))
    
    # Add URL pattern filters
    if url_patterns:
        filters.append(URLPatternFilter(patterns=url_patterns))
    
    # Add exclude pattern filters (implemented as reverse patterns)
    if exclude_patterns:
        # Create a filter that excludes the patterns using reverse=True
        filters.append(URLPatternFilter(patterns=exclude_patterns, reverse=True))
    
    # Create and return filter chain
    return FilterChain(filters=filters)


def create_keyword_scorer(keywords: List[str], weight: float) -> Optional[KeywordRelevanceScorer]:
    """Create real Crawl4AI keyword scorer for BestFirst strategy."""
    
    if not keywords:
        return None
    
    return KeywordRelevanceScorer(keywords=keywords, weight=weight)


def create_browser_config() -> BrowserConfig:
    """Create browser configuration for silent operation."""
    return BrowserConfig(
        headless=True,
        verbose=False
    )


def create_run_config(
    strategy: Any,
    stream_results: bool,
    memory_threshold: float = 70.0
) -> CrawlerRunConfig:
    """Create crawler run configuration."""
    return CrawlerRunConfig(
        verbose=False,
        log_console=False,
        deep_crawl_strategy=strategy,
        stream=stream_results
    )


async def handle_streaming_crawl(crawler: AsyncWebCrawler, domain_url: str, config: CrawlerRunConfig, strategy: Any) -> str:
    """Handle streaming crawl mode with real Crawl4AI."""
    try:
        # Execute the crawl with deep crawling strategy in config
        result = await crawler.arun(url=domain_url, config=config)
        
        # Process and format the result
        return format_crawl_result(result, streaming=True)
        
    except Exception as e:
        logger.error(f"Streaming crawl failed: {e}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "domain": domain_url,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })


async def handle_batch_crawl(crawler: AsyncWebCrawler, domain_url: str, config: CrawlerRunConfig, strategy: Any) -> str:
    """Handle batch crawl mode with real Crawl4AI."""
    try:
        # Execute the crawl with deep crawling strategy in config
        result = await crawler.arun(url=domain_url, config=config)
        
        # Process and format the result
        return format_crawl_result(result, streaming=False)
        
    except Exception as e:
        logger.error(f"Batch crawl failed: {e}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "domain": domain_url,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })


def format_crawl_result(result: Any, streaming: bool = False) -> str:
    """Format crawl result into expected JSON structure."""
    try:
        # Handle different result types from Crawl4AI
        if isinstance(result, list):
            # List of CrawlResult objects from deep crawling
            pages = []
            pages_by_depth = {}
            max_depth = 0
            
            for page_result in result:
                depth = getattr(page_result, 'depth', 0)
                max_depth = max(max_depth, depth)
                
                # Count pages by depth
                depth_str = str(depth)
                pages_by_depth[depth_str] = pages_by_depth.get(depth_str, 0) + 1
                
                # Format page data
                page_data = {
                    "url": page_result.url,
                    "depth": depth,
                    "title": page_result.metadata.get('title', '') if hasattr(page_result, 'metadata') else "",
                    "content": page_result.markdown or "",
                    "success": page_result.success,
                    "metadata": {
                        "crawl_time": datetime.now(timezone.utc).isoformat(),
                        "score": getattr(page_result, 'score', 0.0)
                    }
                }
                pages.append(page_data)
            
            return json.dumps({
                "success": True,
                "streaming": streaming,
                "crawl_summary": {
                    "total_pages": len(pages),
                    "strategy_used": "bfs",
                    "max_depth_reached": max_depth,
                    "pages_by_depth": pages_by_depth
                },
                "pages": pages
            })
            
        elif hasattr(result, 'results') and result.results:
            # Multi-page result
            pages = []
            pages_by_depth = {}
            max_depth = 0
            
            for page_result in result.results:
                depth = getattr(page_result, 'depth', 0)
                max_depth = max(max_depth, depth)
                
                # Count pages by depth
                depth_str = str(depth)
                pages_by_depth[depth_str] = pages_by_depth.get(depth_str, 0) + 1
                
                # Format page data
                page_data = {
                    "url": page_result.url,
                    "depth": depth,
                    "title": page_result.metadata.get('title', '') if hasattr(page_result, 'metadata') else "",
                    "content": page_result.markdown or "",
                    "success": page_result.success,
                    "metadata": {
                        "crawl_time": datetime.now(timezone.utc).isoformat(),
                        "score": getattr(page_result, 'score', 0.0)
                    }
                }
                pages.append(page_data)
            
            return json.dumps({
                "success": True,
                "streaming": streaming,
                "crawl_summary": {
                    "total_pages": len(pages),
                    "strategy_used": getattr(result, 'strategy_used', 'bfs'),
                    "max_depth_reached": max_depth,
                    "pages_by_depth": pages_by_depth
                },
                "pages": pages
            })
        
        elif hasattr(result, 'url'):
            # Single page result
            return json.dumps({
                "success": True,
                "streaming": streaming,
                "crawl_summary": {
                    "total_pages": 1,
                    "strategy_used": "bfs",
                    "max_depth_reached": 0,
                    "pages_by_depth": {"0": 1}
                },
                "pages": [{
                    "url": result.url,
                    "depth": 0,
                    "title": result.metadata.get('title', '') if hasattr(result, 'metadata') else "",
                    "content": result.markdown or "",
                    "success": result.success,
                    "metadata": {
                        "crawl_time": datetime.now(timezone.utc).isoformat(),
                        "score": getattr(result, 'score', 0.0)
                    }
                }]
            })
        
        else:
            # Fallback for unknown result format
            return json.dumps({
                "success": False,
                "error": "Unknown result format",
                "streaming": streaming,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
    except Exception as e:
        logger.error(f"Error formatting crawl result: {e}")
        return json.dumps({
            "success": False,
            "error": f"Result formatting failed: {str(e)}",
            "streaming": streaming,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })


def sanitize_error_message(error_message: str) -> str:
    """Sanitize error message using actual sanitizer."""
    try:
        from tools.error_sanitizer import sanitize_error_message as real_sanitizer
        return real_sanitizer(error_message)
    except ImportError:
        # Fallback if sanitizer not available
        return error_message


async def domain_deep_crawl_impl(params: DomainDeepCrawlParams) -> str:
    """Implementation of domain deep crawling."""
    try:
        # Configure browser for silent operation
        browser_config = create_browser_config()
        
        # Build filter chain
        filter_chain = build_filter_chain(
            domain_url=params.domain_url,
            include_external=params.include_external,
            url_patterns=params.url_patterns,
            exclude_patterns=params.exclude_patterns
        )
        
        # Create strategy
        strategy = create_crawl_strategy(
            strategy_name=params.crawl_strategy,
            max_depth=params.max_depth,
            max_pages=params.max_pages,
            filter_chain=filter_chain,
            keywords=params.keywords
        )
        
        # Configure crawler
        run_config = create_run_config(
            strategy=strategy,
            stream_results=params.stream_results,
            memory_threshold=70.0
        )
        
        # Execute crawl
        async with AsyncWebCrawler(config=browser_config) as crawler:
            if params.stream_results:
                return await handle_streaming_crawl(crawler, params.domain_url, run_config, strategy)
            else:
                return await handle_batch_crawl(crawler, params.domain_url, run_config, strategy)
                
    except Exception as e:
        sanitized_error = sanitize_error_message(str(e))
        logger.error(f"Domain crawl failed for {params.domain_url}: {sanitized_error}")
        return json.dumps({
            "success": False,
            "error": sanitized_error,
            "domain": params.domain_url,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })