"""Web content extraction tool using crawl4ai."""
import asyncio
import logging
from typing import Dict, Any
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator, ConfigDict
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

# Configure logging
logger = logging.getLogger(__name__)


class WebExtractParams(BaseModel):
    """Parameters for web content extraction."""
    
    model_config = ConfigDict(frozen=True)
    
    url: str = Field(..., description="URL of the webpage to crawl")
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        """Validate URL format."""
        if not v or not v.strip():
            raise ValueError("URL cannot be empty")
        
        # Basic URL validation
        parsed = urlparse(v)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid URL format")
        
        if parsed.scheme not in ['http', 'https']:
            raise ValueError("URL must use HTTP or HTTPS protocol")
        
        return v.strip()


async def web_content_extract(params: WebExtractParams) -> str:
    """Extract clean text content from a webpage.
    
    Args:
        params: WebExtractParams containing the URL to crawl
        
    Returns:
        str: Extracted content in markdown format, or error message
    """
    try:
        # Configure browser to run silently
        browser_config = BrowserConfig(
            headless=True,
            verbose=False  # Disable browser-level verbose output
        )
        
        # Configure crawler to run silently
        run_config = CrawlerRunConfig(
            verbose=False,  # Disable crawler-level verbose output (critical for eliminating progress output)
            stream=False,   # Ensure no streaming output
            log_console=False  # Disable console logging
        )
        
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=params.url, config=run_config)
            
            # Handle case where markdown is None
            if result.markdown is None:
                return ""
            
            return result.markdown
            
    except Exception as e:
        logger.error(f"Content extraction failed for {params.url}: {str(e)}")
        return f"Error extracting content: {str(e)}"


async def safe_extract(url: str) -> Dict[str, Any]:
    """Safely extract content with comprehensive error handling.
    
    Args:
        url: URL to extract content from
        
    Returns:
        Dict containing success status, content, and metadata
    """
    try:
        # Configure browser to run silently
        browser_config = BrowserConfig(
            headless=True,
            verbose=False  # Disable browser-level verbose output
        )
        
        # Configure crawler to run silently
        run_config = CrawlerRunConfig(
            verbose=False,  # Disable crawler-level verbose output (critical for eliminating progress output)
            stream=False,   # Ensure no streaming output
            log_console=False  # Disable console logging
        )
        
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=url, config=run_config)
            
            return {
                "success": True,
                "content": result.markdown or "",
                "url": url,
                "title": getattr(result, 'title', 'No title') or "No title"
            }
            
    except Exception as e:
        logger.error(f"Content extraction failed for {url}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "url": url,
            "content": None
        }