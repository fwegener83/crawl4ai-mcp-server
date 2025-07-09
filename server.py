"""Main MCP server with FastMCP and crawl4ai integration."""
import asyncio
import logging
import os
from typing import Dict, Any

from fastmcp import FastMCP
from dotenv import load_dotenv

from tools.web_extract import WebExtractParams, web_content_extract

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


@mcp.tool
async def web_content_extract(url: str) -> str:
    """Extract clean text content from a webpage.
    
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
        
        if result.startswith("Error extracting content"):
            logger.error(f"Content extraction failed: {result}")
        else:
            logger.info(f"Successfully extracted {len(result)} characters from {url}")
        
        return result
        
    except Exception as e:
        error_msg = f"Unexpected error during content extraction: {str(e)}"
        logger.error(error_msg)
        return f"Error extracting content: {str(e)}"


async def main():
    """Main entry point for the server."""
    logger.info("Starting Crawl4AI MCP Server")
    
    try:
        # Start the server
        await mcp.run()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise
    finally:
        logger.info("Server shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())