"""Main MCP server with FastMCP and crawl4ai integration."""
import asyncio
import json
import logging
import os
from typing import Dict, Any, Optional, List

from fastmcp import FastMCP
from dotenv import load_dotenv

from tools.web_extract import WebExtractParams, web_content_extract
from tools.mcp_domain_tools import domain_deep_crawl, domain_link_preview
from tools.collection_manager import CollectionFileManager

# Try to import RAG tools, but don't fail if dependencies are missing
try:
    from tools.knowledge_base.dependencies import is_rag_available
    if is_rag_available():
        from tools.knowledge_base.rag_tools import (
            store_crawl_results as rag_store_crawl_results,
            search_knowledge_base as rag_search_knowledge_base,
            list_collections as rag_list_collections,
            delete_collection as rag_delete_collection
        )
        RAG_TOOLS_AVAILABLE = True
    else:
        RAG_TOOLS_AVAILABLE = False
except ImportError as e:
    logger.warning(f"RAG tools not available: {e}")
    RAG_TOOLS_AVAILABLE = False

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
    max_depth: int = 1,
    crawl_strategy: str = "bfs",
    max_pages: int = 10,
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
    logger.info(f"Starting domain crawl for {domain_url} (max_depth={max_depth}, max_pages={max_pages})")
    
    try:
        # Add timeout protection
        result = await asyncio.wait_for(
            domain_deep_crawl(
                domain_url=domain_url,
                max_depth=max_depth,
                crawl_strategy=crawl_strategy,
                max_pages=max_pages,
                include_external=include_external,
                url_patterns=url_patterns,
                exclude_patterns=exclude_patterns,
                keywords=keywords,
                stream_results=stream_results
            ),
            timeout=60.0  # 60 second timeout
        )
        logger.info(f"Domain crawl completed for {domain_url}")
        return result
    except asyncio.TimeoutError:
        error_msg = f"Domain crawl timed out after 60 seconds for {domain_url}"
        logger.error(error_msg)
        return f"{{\"success\": false, \"error\": \"Crawl timed out - try reducing max_pages or max_depth\", \"domain\": \"{domain_url}\"}}"
    except Exception as e:
        error_msg = f"Domain crawl failed for {domain_url}: {str(e)}"
        logger.error(error_msg)
        return f"{{\"success\": false, \"error\": \"{str(e)}\", \"domain\": \"{domain_url}\"}}"


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


# RAG Knowledge Base Tools (conditional registration)
def register_rag_tools():
    """Register RAG tools if dependencies are available."""
    
    @mcp.tool()
    async def store_crawl_results(
        crawl_result: str,
        collection_name: str = "default"
    ) -> str:
        """Store crawl results in RAG knowledge base."""
        logger.info(f"Storing crawl results in collection: {collection_name}")
        
        try:
            result = await rag_store_crawl_results(crawl_result, collection_name)
            logger.info("Crawl results stored successfully")
            return result
        except Exception as e:
            error_msg = f"Failed to store crawl results: {str(e)}"
            logger.error(error_msg)
            return f'{{"success": false, "message": "{str(e)}", "chunks_stored": 0}}'

    @mcp.tool()
    async def search_knowledge_base(
        query: str,
        collection_name: str = "default",
        n_results: int = 5,
        similarity_threshold: float = None
    ) -> str:
        """Search the RAG knowledge base for relevant content."""
        logger.info(f"Searching knowledge base: '{query[:50]}...' in collection '{collection_name}'")
        
        try:
            result = await rag_search_knowledge_base(
                query=query,
                collection_name=collection_name,
                n_results=n_results,
                similarity_threshold=similarity_threshold
            )
            logger.info("Search completed successfully")
            return result
        except Exception as e:
            error_msg = f"Search failed: {str(e)}"
            logger.error(error_msg)
            return f'{{"success": false, "query": "{query}", "message": "{str(e)}", "results": []}}'

    @mcp.tool()
    async def list_collections() -> str:
        """List all available collections in the knowledge base."""
        logger.info("Listing knowledge base collections")
        
        try:
            result = await rag_list_collections()
            logger.info("Collections listed successfully")
            return result
        except Exception as e:
            error_msg = f"Failed to list collections: {str(e)}"
            logger.error(error_msg)
            return f'{{"success": false, "message": "{str(e)}", "collections": []}}'

    @mcp.tool()
    async def delete_collection(collection_name: str) -> str:
        """Delete a collection from the knowledge base."""
        logger.info(f"Deleting collection: {collection_name}")
        
        try:
            result = await rag_delete_collection(collection_name)
            logger.info(f"Collection '{collection_name}' deleted successfully")
            return result
        except Exception as e:
            error_msg = f"Failed to delete collection: {str(e)}"
            logger.error(error_msg)
            return f'{{"success": false, "message": "{str(e)}", "collection_name": "{collection_name}"}}'


if RAG_TOOLS_AVAILABLE:
    register_rag_tools()
    logger.info("RAG tools registered successfully")
else:
    logger.info("RAG tools not available - install dependencies to enable: pip install chromadb sentence-transformers langchain-text-splitters numpy")


# Initialize Collection File Manager
collection_manager = CollectionFileManager()


# Collection Management Tools
@mcp.tool()
async def create_collection(name: str, description: str = "") -> str:
    """Create a new collection for organizing crawled content.
    
    Creates a directory-based collection with metadata for storing 
    crawled web content as editable Markdown files.
    
    Args:
        name: Collection name (will be sanitized for filesystem safety)
        description: Optional description of the collection's purpose
        
    Returns:
        str: JSON string with operation result including success status and path
    """
    logger.info(f"Creating collection: {name}")
    
    try:
        result = collection_manager.create_collection(name, description)
        
        if result["success"]:
            logger.info(f"Successfully created collection '{name}' at {result['path']}")
        else:
            logger.error(f"Failed to create collection '{name}': {result.get('error', 'Unknown error')}")
            
        return json.dumps(result)
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": f"Unexpected error creating collection '{name}'"
        }
        logger.error(f"Unexpected error creating collection '{name}': {str(e)}")
        return json.dumps(error_result)


@mcp.tool()
async def save_to_collection(
    collection_name: str, 
    filename: str, 
    content: str, 
    folder: str = ""
) -> str:
    """Save crawled content to a collection as a Markdown file.
    
    Saves content to a specified collection with optional folder organization.
    Files are stored as UTF-8 encoded text with automatic metadata tracking.
    
    Args:
        collection_name: Name of the target collection
        filename: Name of the file (must have .md, .txt, or .json extension)
        content: Content to save (typically Markdown from web crawling)
        folder: Optional subfolder path for hierarchical organization
        
    Returns:
        str: JSON string with operation result including success status and file path
    """
    logger.info(f"Saving file '{filename}' to collection '{collection_name}'")
    
    try:
        # Ensure collection exists, create if needed
        collection_path = collection_manager.base_dir / collection_name
        if not collection_path.exists():
            logger.info(f"Collection '{collection_name}' doesn't exist, creating it")
            create_result = collection_manager.create_collection(collection_name)
            if not create_result["success"]:
                return json.dumps(create_result)
        
        result = collection_manager.save_file(collection_name, filename, content, folder)
        
        if result["success"]:
            logger.info(f"Successfully saved '{filename}' to collection '{collection_name}'")
        else:
            logger.error(f"Failed to save '{filename}': {result.get('error', 'Unknown error')}")
            
        return json.dumps(result)
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": f"Unexpected error saving file '{filename}' to collection '{collection_name}'"
        }
        logger.error(f"Unexpected error saving to collection: {str(e)}")
        return json.dumps(error_result)


@mcp.tool()
async def list_file_collections() -> str:
    """List all available collections.
    
    Returns information about all collections including names, descriptions,
    file counts, and folder structures.
    
    Returns:
        str: JSON string with list of collections and metadata
    """
    logger.info("Listing all collections")
    
    try:
        result = collection_manager.list_collections()
        
        if result["success"]:
            logger.info(f"Found {result['total']} collections")
        else:
            logger.error(f"Failed to list collections: {result.get('error', 'Unknown error')}")
            
        return json.dumps(result)
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "Unexpected error listing collections"
        }
        logger.error(f"Unexpected error listing collections: {str(e)}")
        return json.dumps(error_result)


@mcp.tool()
async def get_collection_info(collection_name: str) -> str:
    """Get detailed information about a specific collection.
    
    Returns comprehensive metadata including file count, folder structure,
    creation date, and description.
    
    Args:
        collection_name: Name of the collection to inspect
        
    Returns:
        str: JSON string with detailed collection information
    """
    logger.info(f"Getting info for collection: {collection_name}")
    
    try:
        result = collection_manager.get_collection_info(collection_name)
        
        if result["success"]:
            logger.info(f"Retrieved info for collection '{collection_name}'")
        else:
            logger.error(f"Failed to get collection info: {result.get('error', 'Unknown error')}")
            
        return json.dumps(result)
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": f"Unexpected error getting info for collection '{collection_name}'"
        }
        logger.error(f"Unexpected error getting collection info: {str(e)}")
        return json.dumps(error_result)


@mcp.tool()
async def read_from_collection(
    collection_name: str, 
    filename: str, 
    folder: str = ""
) -> str:
    """Read content from a file in a collection.
    
    Retrieves the content of a previously saved file from a collection.
    
    Args:
        collection_name: Name of the collection containing the file
        filename: Name of the file to read
        folder: Optional subfolder path where the file is located
        
    Returns:
        str: JSON string with file content and metadata
    """
    logger.info(f"Reading file '{filename}' from collection '{collection_name}'")
    
    try:
        result = collection_manager.read_file(collection_name, filename, folder)
        
        if result["success"]:
            content_length = len(result.get("content", ""))
            logger.info(f"Successfully read '{filename}' ({content_length} characters)")
        else:
            logger.error(f"Failed to read file: {result.get('error', 'Unknown error')}")
            
        return json.dumps(result)
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": f"Unexpected error reading file '{filename}' from collection '{collection_name}'"
        }
        logger.error(f"Unexpected error reading from collection: {str(e)}")
        return json.dumps(error_result)


@mcp.tool()
async def delete_file_collection(collection_name: str) -> str:
    """Delete a collection and all its files.
    
    WARNING: This operation is irreversible and will delete all files 
    and folders within the specified collection.
    
    Args:
        collection_name: Name of the collection to delete
        
    Returns:
        str: JSON string with operation result
    """
    logger.warning(f"Deleting collection: {collection_name}")
    
    try:
        result = collection_manager.delete_collection(collection_name)
        
        if result["success"]:
            logger.info(f"Successfully deleted collection '{collection_name}'")
        else:
            logger.error(f"Failed to delete collection: {result.get('error', 'Unknown error')}")
            
        return json.dumps(result)
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": f"Unexpected error deleting collection '{collection_name}'"
        }
        logger.error(f"Unexpected error deleting collection: {str(e)}")
        return json.dumps(error_result)


logger.info("Collection management tools registered successfully")


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