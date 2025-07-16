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
        def __init__(self, deep_crawl_strategy=None, stream=False, verbose=False, 
                     log_console=False, memory_threshold_percent=70.0, **kwargs):
            self.deep_crawl_strategy = deep_crawl_strategy
            self.stream = stream
            self.verbose = verbose
            self.log_console = log_console
            self.memory_threshold_percent = memory_threshold_percent
            # Accept any additional arguments for flexibility

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


# Mock strategy classes for testing (will be replaced with real Crawl4AI strategies later)
class MockCrawlStrategy:
    """Mock base crawl strategy for testing."""
    
    def __init__(self, strategy_type: str, max_depth: int, max_pages: int, 
                 filter_chain: Optional[Any] = None, keywords: Optional[List[str]] = None):
        self.strategy_type = strategy_type
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.filter_chain = filter_chain
        self.keywords = keywords or []
        self.url_scorer = None
        
        # Set up URL scorer for best_first strategy
        if strategy_type == "best_first" and keywords:
            self.url_scorer = create_keyword_scorer(keywords, weight=0.8)


class MockFilterChain:
    """Mock filter chain for testing."""
    
    def __init__(self, domain: str, include_external: bool = False):
        self.domain = domain
        self.include_external = include_external
        self.filters = []
        self.include_patterns = []
        self.exclude_patterns = []
        
        # Add domain filter
        self.filters.append("domain_filter")
        
    def add_pattern_filter(self, include_patterns: List[str], exclude_patterns: List[str]):
        """Add pattern filters."""
        if include_patterns:
            self.include_patterns.extend(include_patterns)
            self.filters.append("include_pattern_filter")
        if exclude_patterns:
            self.exclude_patterns.extend(exclude_patterns)
            self.filters.append("exclude_pattern_filter")


class MockKeywordScorer:
    """Mock keyword scorer for testing."""
    
    def __init__(self, keywords: List[str], weight: float):
        self.keywords = [kw.lower() for kw in keywords]  # Normalize to lowercase
        self.weight = weight


def create_crawl_strategy(
    strategy_name: str,
    max_depth: int,
    max_pages: int,
    filter_chain: Optional[Any],
    keywords: List[str]
) -> MockCrawlStrategy:
    """Create a crawl strategy based on strategy name."""
    
    valid_strategies = ['bfs', 'dfs', 'best_first']
    if strategy_name not in valid_strategies:
        raise ValueError(f"Unknown strategy: {strategy_name}")
    
    return MockCrawlStrategy(
        strategy_type=strategy_name,
        max_depth=max_depth,
        max_pages=max_pages,
        filter_chain=filter_chain,
        keywords=keywords
    )


def build_filter_chain(
    domain_url: str,
    include_external: bool,
    url_patterns: List[str],
    exclude_patterns: List[str]
) -> MockFilterChain:
    """Build filter chain for URL filtering."""
    
    # Extract domain from URL
    parsed = urlparse(domain_url)
    domain = parsed.netloc
    
    # Create filter chain
    filter_chain = MockFilterChain(domain=domain, include_external=include_external)
    
    # Add pattern filters if provided
    if url_patterns or exclude_patterns:
        filter_chain.add_pattern_filter(url_patterns, exclude_patterns)
    
    return filter_chain


def create_keyword_scorer(keywords: List[str], weight: float) -> Optional[MockKeywordScorer]:
    """Create keyword scorer for BestFirst strategy."""
    
    if not keywords:
        return None
    
    return MockKeywordScorer(keywords=keywords, weight=weight)


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
        deep_crawl_strategy=strategy,
        stream=stream_results,
        verbose=False,
        log_console=False,
        memory_threshold_percent=memory_threshold
    )


async def handle_streaming_crawl(crawler: AsyncWebCrawler, domain_url: str, config: CrawlerRunConfig) -> str:
    """Handle streaming crawl mode."""
    # Mock implementation for testing
    return json.dumps({
        "success": True,
        "streaming": True,
        "crawl_summary": {
            "total_pages": 1,
            "strategy_used": "bfs",
            "max_depth_reached": 0,
            "pages_by_depth": {"0": 1}
        },
        "pages": [
            {
                "url": domain_url,
                "depth": 0,
                "title": "Mock Page",
                "content": "Mock content",
                "success": True,
                "metadata": {
                    "crawl_time": datetime.now(timezone.utc).isoformat(),
                    "score": 1.0
                }
            }
        ]
    })


async def handle_batch_crawl(crawler: AsyncWebCrawler, domain_url: str, config: CrawlerRunConfig) -> str:
    """Handle batch crawl mode."""
    # Mock implementation for testing
    return json.dumps({
        "success": True,
        "streaming": False,
        "crawl_summary": {
            "total_pages": 1,
            "strategy_used": "bfs",
            "max_depth_reached": 0,
            "pages_by_depth": {"0": 1}
        },
        "pages": [
            {
                "url": domain_url,
                "depth": 0,
                "title": "Mock Page",
                "content": "Mock content",
                "success": True,
                "metadata": {
                    "crawl_time": datetime.now(timezone.utc).isoformat(),
                    "score": 1.0
                }
            }
        ]
    })


def sanitize_error_message(error_message: str) -> str:
    """Sanitize error message (placeholder - will use actual sanitizer)."""
    # This is a placeholder - will integrate with actual error sanitizer
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
                return await handle_streaming_crawl(crawler, params.domain_url, run_config)
            else:
                return await handle_batch_crawl(crawler, params.domain_url, run_config)
                
    except Exception as e:
        sanitized_error = sanitize_error_message(str(e))
        logger.error(f"Domain crawl failed for {params.domain_url}: {sanitized_error}")
        return json.dumps({
            "success": False,
            "error": sanitized_error,
            "domain": params.domain_url,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })