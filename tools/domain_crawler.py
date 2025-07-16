"""
Domain deep crawler implementation.
This module provides domain-based deep crawling capabilities for MCP tools.
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List
from urllib.parse import urlparse


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