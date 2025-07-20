"""Main MCP server with FastMCP and crawl4ai integration."""
import asyncio
import logging
import os
from typing import Dict, Any, Optional, List

from fastmcp import FastMCP
from dotenv import load_dotenv

from tools.web_extract import WebExtractParams, web_content_extract
from tools.mcp_domain_tools import domain_deep_crawl, domain_link_preview

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_environment():
    """Load environment variables from .env file."""
    load_dotenv()
    
    # Log configuration (without sensitive values)
    logger.info("Environment configuration loaded")
    
    # Optional: Set crawl4ai specific environment variables
    if os.getenv("CRAWL4AI_USER_AGENT"):
        logger.info(f"Using custom user agent: {os.getenv('CRAWL4AI_USER_AGENT')}")
    
    if os.getenv("CRAWL4AI_TIMEOUT"):
        logger.info(f"Using custom timeout: {os.getenv('CRAWL4AI_TIMEOUT')}")


# Load environment variables
load_environment()

# Initialize FastMCP server
mcp = FastMCP("Crawl4AI-MCP-Server")

# Register logging for server events
logger.info("Initializing Crawl4AI MCP Server")


@mcp.tool()
async def web_content_extract(url: str) -> str:
    """Extract clean text content from a webpage.
    
    This tool crawls a webpage and extracts its content in markdown format,
    suitable for AI processing and analysis.
    
    Args:
        url: URL of the webpage to crawl
        
    Returns:
        str: Extracted content in markdown format, or error message
    """
    logger.info(f"Extracting content from URL: {url}")
    
    try:
        # Create params object for the extraction function
        params = WebExtractParams(url=url)
        
        # Import here to avoid circular imports in tests
        from tools.web_extract import web_content_extract as extract_func
        
        result = await extract_func(params)
        
        # Ensure result is a proper string (convert from StringCompatibleMarkdown if needed)
        result_str = str(result)
        
        if result_str.startswith("Error extracting content"):
            logger.error(f"Content extraction failed: {result_str}")
        else:
            logger.info(f"Successfully extracted {len(result_str)} characters from {url}")
        
        return result_str
        
    except Exception as e:
        error_msg = f"Unexpected error during content extraction: {str(e)}"
        logger.error(error_msg)
        return f"Error extracting content: {str(e)}"


@mcp.tool()
async def domain_deep_crawl_tool(
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
    """Crawl a complete domain with configurable depth and strategies.
    
    This tool performs deep crawling of a domain using various strategies 
    (BFS, DFS, BestFirst) with configurable filtering and scoring.
    
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
        str: JSON string with crawl results or error information
    """
    return await domain_deep_crawl(
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


@mcp.tool()
async def domain_link_preview_tool(
    domain_url: str,
    include_external: bool = False
) -> str:
    """Get a quick preview of links available on a domain.
    
    This tool provides a fast overview of available links on a domain
    without performing full crawling.
    
    Args:
        domain_url: The base URL/domain to analyze
        include_external: Whether to include external links
        
    Returns:
        str: JSON string with link preview or error information
    """
    return await domain_link_preview(
        domain_url=domain_url,
        include_external=include_external
    )


if __name__ == "__main__":
    logger.info("Starting Crawl4AI MCP Server")
    
    try:
        # Let FastMCP handle the event loop internally with anyio.run()
        # Don't wrap in asyncio.run() as it creates nested event loops
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise
    finally:
        logger.info("Server shutdown complete")