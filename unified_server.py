"""
Unified server implementation for Crawl4AI MCP Server.

This server combines both MCP (stdio) and HTTP (REST) protocols in a single process,
using shared service layer for consistent business logic. It replaces the dual-server
architecture with a clean, maintainable unified approach.
"""
import asyncio
import json
import logging
import sys
import os
from typing import Dict, Any, Optional

# FastMCP for MCP protocol
from fastmcp import FastMCP

# FastAPI for HTTP protocol  
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Our service layer
from services.containers import get_container
from services.interfaces import (
    CrawlResult, DeepCrawlConfig, LinkPreview,
    CollectionInfo, FileInfo, VectorSyncStatus, VectorSearchResult
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UnifiedServer:
    """
    Unified server that handles both MCP and HTTP protocols.
    
    Uses dependency injection container to provide shared services
    to both protocol handlers, ensuring consistent behavior and
    shared state management.
    """
    
    def __init__(self):
        """Initialize the unified server."""
        logger.info("Initializing UnifiedServer")
        
        # Get dependency injection container
        self.container = get_container()
        
        # Initialize protocol handlers
        self.mcp_server = None
        self.http_app = None
        
        # Server state
        self.running = False
    
    def setup_mcp_server(self) -> FastMCP:
        """
        Set up MCP protocol handler with tool adapters.
        
        Returns:
            Configured FastMCP server instance
        """
        logger.info("Setting up MCP protocol handler")
        
        # Create FastMCP server
        mcp_server = FastMCP("Crawl4AI-Unified")
        
        # Get services from container
        web_service = self.container.web_crawling_service()
        collection_service = self.container.collection_service()
        vector_service = self.container.vector_sync_service()
        
        # ===== WEB CRAWLING TOOLS =====
        
        @mcp_server.tool()
        async def web_content_extract(url: str) -> str:
            """Extract content from a single web page."""
            try:
                result = await web_service.extract_content(url)
                if result.error:
                    return f"Error extracting content: {result.error}"
                return result.content
            except Exception as e:
                logger.error(f"MCP web_content_extract error: {e}")
                return f"Error extracting content: {str(e)}"
        
        @mcp_server.tool()
        async def domain_deep_crawl_tool(
            domain_url: str,
            max_depth: int = 1,
            max_pages: int = 10,
            crawl_strategy: str = "bfs",
            include_external: bool = False,
            url_patterns: Optional[list] = None,
            exclude_patterns: Optional[list] = None
        ) -> str:
            """Perform deep crawling of a domain."""
            try:
                config = DeepCrawlConfig(
                    domain_url=domain_url,
                    max_depth=max_depth,
                    max_pages=max_pages,
                    crawl_strategy=crawl_strategy,
                    include_external=include_external,
                    url_patterns=url_patterns,
                    exclude_patterns=exclude_patterns
                )
                results = await web_service.deep_crawl(config)
                return {
                    "success": True,
                    "pages": [result.model_dump() for result in results]
                }
            except Exception as e:
                logger.error(f"MCP domain_deep_crawl error: {e}")
                return {"success": False, "error": str(e)}
        
        @mcp_server.tool()
        async def domain_link_preview_tool(domain_url: str, include_external: bool = False) -> str:
            """Preview available links on a domain."""
            try:
                result = await web_service.preview_links(domain_url, include_external)
                return result.model_dump_json()
            except Exception as e:
                logger.error(f"MCP domain_link_preview error: {e}")
                return LinkPreview(domain=domain_url, links=[], metadata={"error": str(e)}).model_dump_json()
        
        # ===== COLLECTION MANAGEMENT TOOLS =====
        
        @mcp_server.tool()
        async def list_file_collections() -> str:
            """List all file collections."""
            try:
                from application_layer.collection_management import list_collections_use_case
                collections = await list_collections_use_case(collection_service)
                return json.dumps({
                    "success": True,
                    "collections": [col.model_dump() for col in collections]
                })
            except Exception as e:
                logger.error(f"MCP list_file_collections error: {e}")
                return json.dumps({"success": False, "error": str(e)})
        
        @mcp_server.tool()
        async def create_collection(name: str, description: str = "") -> str:
            """Create a new file collection."""
            try:
                from application_layer.collection_management import create_collection_use_case, ValidationError
                collection = await create_collection_use_case(collection_service, name, description)
                return json.dumps({
                    "success": True,
                    "collection": collection.model_dump()
                })
            except ValidationError as e:
                logger.error(f"MCP create_collection validation error: {e}")
                return json.dumps({"success": False, "error": e.message, "code": e.code})
            except Exception as e:
                logger.error(f"MCP create_collection error: {e}")
                return json.dumps({"success": False, "error": str(e)})
        
        @mcp_server.tool()
        async def get_collection_info(collection_name: str) -> str:
            """Get information about a specific collection."""
            try:
                from application_layer.collection_management import get_collection_use_case, ValidationError
                collection = await get_collection_use_case(collection_service, collection_name)
                return json.dumps({
                    "success": True,
                    "collection": collection.model_dump()
                })
            except ValidationError as e:
                logger.error(f"MCP get_collection_info validation error: {e}")
                return json.dumps({"success": False, "error": e.message, "code": e.code})
            except Exception as e:
                logger.error(f"MCP get_collection_info error: {e}")
                return json.dumps({"success": False, "error": str(e)})
        
        @mcp_server.tool()
        async def delete_file_collection(collection_name: str) -> str:
            """Delete a file collection."""
            try:
                from application_layer.collection_management import delete_collection_use_case, ValidationError
                result = await delete_collection_use_case(collection_service, collection_name)
                return json.dumps(result)  # Use-case already returns proper format
            except ValidationError as e:
                logger.error(f"MCP delete_file_collection validation error: {e}")
                return json.dumps({"success": False, "error": e.message, "code": e.code})
            except Exception as e:
                logger.error(f"MCP delete_file_collection error: {e}")
                return json.dumps({"success": False, "error": str(e)})
        
        @mcp_server.tool()
        async def save_to_collection(
            collection_name: str,
            filename: str,
            content: str,
            folder: str = ""
        ) -> str:
            """Save content to a file in a collection."""
            try:
                file_info = await collection_service.save_file(collection_name, filename, content, folder)
                return {
                    "success": True,
                    "file": file_info.model_dump()
                }
            except Exception as e:
                logger.error(f"MCP save_to_collection error: {e}")
                return {"success": False, "error": str(e)}
        
        @mcp_server.tool()
        async def read_from_collection(
            collection_name: str,
            filename: str,
            folder: str = ""
        ) -> str:
            """Read content from a file in a collection."""
            try:
                file_info = await collection_service.get_file(collection_name, filename, folder)
                return {
                    "success": True,
                    "file": file_info.model_dump()
                }
            except Exception as e:
                logger.error(f"MCP read_from_collection error: {e}")
                return {"success": False, "error": str(e)}
        
        # ===== VECTOR SYNC TOOLS =====
        
        @mcp_server.tool()
        async def sync_collection_to_vectors(
            collection_name: str,
            force_reprocess: bool = False,
            chunking_strategy: Optional[str] = None
        ) -> str:
            """Synchronize a collection with the vector database."""
            try:
                config = {}
                if force_reprocess:
                    config["force_reprocess"] = True
                if chunking_strategy:
                    config["chunking_strategy"] = chunking_strategy
                
                status = await vector_service.sync_collection(collection_name, config)
                return json.dumps({
                    "success": True,
                    "sync_result": status.model_dump()
                })
            except Exception as e:
                logger.error(f"MCP sync_collection_to_vectors error: {e}")
                return json.dumps({"success": False, "error": str(e)})
        
        @mcp_server.tool()
        async def get_collection_sync_status(collection_name: str) -> str:
            """Get synchronization status for a collection."""
            try:
                status = await vector_service.get_sync_status(collection_name)
                return json.dumps({
                    "success": True,
                    "status": status.model_dump()
                })
            except Exception as e:
                logger.error(f"MCP get_collection_sync_status error: {e}")
                return json.dumps({"success": False, "error": str(e)})
        
        @mcp_server.tool()
        async def search_collection_vectors(
            query: str,
            collection_name: Optional[str] = None,
            limit: int = 10,
            similarity_threshold: float = 0.7
        ) -> str:
            """Search vectors using semantic similarity."""
            try:
                # Import and use the shared use-case function
                from application_layer.vector_search import search_vectors_use_case
                
                # Use shared use-case function (same as API)
                results = await search_vectors_use_case(
                    vector_service, collection_service,
                    query, collection_name, limit, similarity_threshold
                )
                
                return json.dumps({
                    "success": True,
                    "results": results  # Results already transformed with similarity_score
                })
            except Exception as e:
                logger.error(f"MCP search_collection_vectors error: {e}")
                return json.dumps({"success": False, "error": str(e)})
        
        self.mcp_server = mcp_server
        logger.info("MCP protocol handler configured with service layer adapters")
        return mcp_server
    
    def setup_http_app(self) -> FastAPI:
        """
        Set up HTTP protocol handler with REST endpoints.
        
        Returns:
            Configured FastAPI application instance
        """
        logger.info("Setting up HTTP protocol handler")
        
        # Create FastAPI app
        app = FastAPI(
            title="Crawl4AI Unified Server",
            description="Web crawling and collection management with vector sync",
            version="1.0.0"
        )
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Get services from container
        web_service = self.container.web_crawling_service()
        collection_service = self.container.collection_service()
        vector_service = self.container.vector_sync_service()
        
        # ===== HEALTH AND STATUS ENDPOINTS =====
        
        @app.get("/api/health")
        async def health_check():
            """Health check endpoint."""
            return {"status": "healthy", "server": "unified"}
        
        @app.get("/api/status")
        async def server_status():
            """Server status endpoint."""
            return {
                "status": "running",
                "server_type": "unified",
                "protocols": ["mcp", "http"],
                "services": ["web_crawling", "collection_management", "vector_sync"]
            }
        
        # ===== WEB CRAWLING ENDPOINTS =====
        
        @app.post("/api/extract")
        async def extract_content(request: dict):
            """Extract content from a single web page."""
            try:
                url = request.get("url")
                if not url:
                    raise HTTPException(status_code=400, detail="URL is required")
                
                result = await web_service.extract_content(url)
                return {
                    "success": result.error is None,
                    "content": result.content,
                    "metadata": result.metadata,
                    "error": result.error
                }
            except HTTPException:
                raise  # Re-raise HTTPExceptions without wrapping
            except Exception as e:
                logger.error(f"HTTP extract_content error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.post("/api/deep-crawl")
        async def deep_crawl(request: dict):
            """Perform deep crawling of a domain."""
            try:
                config = DeepCrawlConfig(**request)
                results = await web_service.deep_crawl(config)
                
                return {
                    "success": True,
                    "pages": [
                        {
                            "url": result.url,
                            "title": result.metadata.get("title", ""),
                            "content": result.content,
                            "success": result.error is None,
                            "depth": result.metadata.get("depth", 0),
                            "metadata": {
                                "crawl_time": result.metadata.get("crawl_time", ""),
                                "score": result.metadata.get("score", 0.0)
                            },
                            "error": result.error
                        }
                        for result in results
                    ]
                }
            except Exception as e:
                logger.error(f"HTTP deep_crawl error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.post("/api/link-preview")
        async def link_preview(request: dict):
            """Preview available links on a domain."""
            try:
                domain_url = request.get("domain_url")
                include_external = request.get("include_external", False)
                
                if not domain_url:
                    raise HTTPException(status_code=400, detail="domain_url is required")
                
                result = await web_service.preview_links(domain_url, include_external)
                return {
                    "success": True,
                    "domain": result.domain,
                    "links": result.links,
                    "external_links": result.external_links,
                    "metadata": result.metadata
                }
            except HTTPException:
                raise  # Re-raise HTTPExceptions without wrapping
            except Exception as e:
                logger.error(f"HTTP link_preview error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # ===== COLLECTION MANAGEMENT ENDPOINTS =====
        
        @app.get("/api/file-collections")
        async def list_collections():
            """List all file collections."""
            try:
                from application_layer.collection_management import list_collections_use_case
                collections = await list_collections_use_case(collection_service)
                return {
                    "success": True,
                    "collections": [col.model_dump() for col in collections]
                }
            except Exception as e:
                logger.error(f"HTTP list_collections error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.post("/api/file-collections")
        async def create_collection_endpoint(request: dict):
            """Create a new file collection."""
            try:
                from application_layer.collection_management import create_collection_use_case, ValidationError
                name = request.get("name")
                description = request.get("description", "")
                
                collection = await create_collection_use_case(collection_service, name, description)
                return {
                    "success": True,
                    "data": collection.model_dump()
                }
            except ValidationError as e:
                logger.error(f"HTTP create_collection validation error: {e}")
                raise HTTPException(status_code=400, detail=e.message)
            except Exception as e:
                logger.error(f"HTTP create_collection error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/api/file-collections/{collection_id}")
        async def get_collection(collection_id: str):
            """Get information about a specific collection."""
            try:
                from application_layer.collection_management import get_collection_use_case, ValidationError
                collection = await get_collection_use_case(collection_service, collection_id)
                return {
                    "success": True,
                    "data": collection.model_dump()
                }
            except ValidationError as e:
                logger.error(f"HTTP get_collection validation error: {e}")
                raise HTTPException(status_code=400, detail=e.message)
            except Exception as e:
                logger.error(f"HTTP get_collection error: {e}")
                raise HTTPException(status_code=404, detail=str(e))
        
        @app.delete("/api/file-collections/{collection_id}")
        async def delete_collection(collection_id: str):
            """Delete a file collection."""
            try:
                from application_layer.collection_management import delete_collection_use_case, ValidationError
                result = await delete_collection_use_case(collection_service, collection_id)
                return result
            except ValidationError as e:
                logger.error(f"HTTP delete_collection validation error: {e}")
                raise HTTPException(status_code=400, detail=e.message)
            except Exception as e:
                logger.error(f"HTTP delete_collection error: {e}")
                # RESTful error handling - 404 for collection not found
                if "not found" in str(e).lower() or "does not exist" in str(e).lower():
                    raise HTTPException(status_code=404, detail=str(e))
                else:
                    raise HTTPException(status_code=500, detail=str(e))
        
        # ===== FILE MANAGEMENT ENDPOINTS =====
        
        @app.get("/api/file-collections/{collection_id}/files")
        async def list_files_in_collection(collection_id: str):
            """List all files and folders in a collection."""
            try:
                from urllib.parse import unquote
                decoded_collection_id = unquote(collection_id)
                
                files = await collection_service.list_files_in_collection(decoded_collection_id)
                # Transform files to include filename field for backward compatibility
                files_data = []
                for f in files:
                    file_dict = f.model_dump()
                    file_dict["filename"] = file_dict.get("name", file_dict.get("path", ""))
                    files_data.append(file_dict)
                
                return {
                    "success": True,
                    "data": {
                        "files": files_data,
                        "folders": [],  # Placeholder - implement if needed
                        "total_files": len(files),
                        "total_folders": 0
                    }
                }
            except Exception as e:
                logger.error(f"HTTP list_files_in_collection error: {e}")
                # RESTful error handling - 404 for collection not found
                if "not found" in str(e).lower() or "does not exist" in str(e).lower():
                    raise HTTPException(status_code=404, detail=str(e))
                else:
                    raise HTTPException(status_code=500, detail=str(e))
        
        @app.post("/api/file-collections/{collection_id}/files")
        async def save_file_to_collection_endpoint(collection_id: str, request: dict):
            """Save a file to a collection."""
            try:
                from urllib.parse import unquote
                decoded_collection_id = unquote(collection_id)
                
                filename = request.get("filename")
                content = request.get("content")
                folder = request.get("folder", "")
                
                if not filename:
                    raise HTTPException(status_code=400, detail="Filename is required")
                if not content:
                    raise HTTPException(status_code=400, detail="Content is required")
                
                file_info = await collection_service.save_file(decoded_collection_id, filename, content, folder)
                return {
                    "success": True,
                    "data": file_info.model_dump()
                }
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"HTTP save_file_to_collection error: {e}")
                # RESTful error handling - 404 for collection not found
                if "not found" in str(e).lower() or "does not exist" in str(e).lower():
                    raise HTTPException(status_code=404, detail=str(e))
                else:
                    raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/api/file-collections/{collection_id}/files/{filename}")
        async def read_file_from_collection_endpoint(collection_id: str, filename: str, folder: str = ""):
            """Read a file from a collection."""
            try:
                from urllib.parse import unquote
                decoded_collection_id = unquote(collection_id)
                decoded_filename = unquote(filename)
                
                file_info = await collection_service.get_file(decoded_collection_id, decoded_filename, folder)
                return {
                    "success": True,
                    "data": {
                        "content": file_info.content,
                        "filename": decoded_filename,
                        "path": file_info.path,
                        "created_at": file_info.created_at,
                        "updated_at": file_info.updated_at
                    }
                }
            except Exception as e:
                logger.error(f"HTTP read_file_from_collection error: {e}")
                raise HTTPException(status_code=404, detail=str(e))
        
        @app.put("/api/file-collections/{collection_id}/files/{filename}")
        async def update_file_in_collection_endpoint(collection_id: str, filename: str, request: dict, folder: str = ""):
            """Update a file in a collection."""
            try:
                from urllib.parse import unquote
                decoded_collection_id = unquote(collection_id)
                decoded_filename = unquote(filename)
                
                content = request.get("content")
                if not content:
                    raise HTTPException(status_code=400, detail="Content is required")
                
                file_info = await collection_service.save_file(decoded_collection_id, decoded_filename, content, folder)
                return {
                    "success": True,
                    "data": file_info.model_dump()
                }
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"HTTP update_file_in_collection error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.delete("/api/file-collections/{collection_id}/files/{filename}")
        async def delete_file_from_collection_endpoint(collection_id: str, filename: str, folder: str = ""):
            """Delete a file from a collection."""
            try:
                from urllib.parse import unquote
                decoded_collection_id = unquote(collection_id)
                decoded_filename = unquote(filename)
                
                await collection_service.delete_file(decoded_collection_id, decoded_filename, folder)
                return {"success": True}
            except Exception as e:
                logger.error(f"HTTP delete_file_from_collection error: {e}")
                # RESTful error handling - 404 for collection or file not found
                if "not found" in str(e).lower() or "does not exist" in str(e).lower():
                    raise HTTPException(status_code=404, detail=str(e))
                else:
                    raise HTTPException(status_code=500, detail=str(e))
        
        @app.post("/api/crawl/single/{collection_id}")
        async def crawl_single_page_to_collection(collection_id: str, request: dict):
            """Crawl a single page and save to collection."""
            try:
                from urllib.parse import unquote, urlparse
                
                # URL decode the collection_id to handle names with spaces
                decoded_collection_id = unquote(collection_id)
                
                # Extract required fields from request
                url = request.get("url")
                folder = request.get("folder", "")
                
                if not url:
                    raise HTTPException(status_code=400, detail="URL is required")
                
                # Extract content from URL using web service
                content_result = await web_service.extract_content(url)
                
                if content_result.error:
                    raise HTTPException(status_code=400, detail=f"Failed to crawl URL: {content_result.error}")
                
                # Generate filename from URL
                parsed_url = urlparse(url)
                domain = parsed_url.netloc.replace("www.", "")
                path_parts = [p for p in parsed_url.path.split("/") if p]
                if path_parts:
                    filename = f"{domain}_{path_parts[-1]}.md"
                else:
                    filename = f"{domain}_index.md"
                
                # Clean filename
                import re
                filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
                
                # Save to collection using collection service
                file_info = await collection_service.save_file(
                    decoded_collection_id, 
                    filename, 
                    content_result.content, 
                    folder
                )
                
                return {
                    "success": True,
                    "file": {
                        "filename": filename,
                        "collection_id": decoded_collection_id
                    },
                    "url": url,
                    "folder": folder,
                    "content_length": len(content_result.content),
                    "message": f"Successfully saved content from {url} to {decoded_collection_id}/{folder if folder else ''}{filename}"
                }
                
            except HTTPException:
                raise  # Re-raise HTTPExceptions without wrapping
            except Exception as e:
                logger.error(f"HTTP crawl_single_page_to_collection error: {e}")
                error_str = str(e)
                
                # Handle specific error cases
                if "does not exist" in error_str or "not found" in error_str.lower():
                    raise HTTPException(status_code=404, detail=error_str)
                else:
                    raise HTTPException(status_code=500, detail=error_str)
        
        # ===== VECTOR SYNC ENDPOINTS =====
        
        async def _validate_collection_exists(collection_name: str):
            """Validate that a collection exists, raise 404 HTTPException if not."""
            try:
                await collection_service.get_collection(collection_name)
            except Exception as e:
                error_msg = str(e).lower()
                if "not found" in error_msg or "does not exist" in error_msg:
                    raise HTTPException(
                        status_code=404, 
                        detail={
                            "error": {
                                "code": "COLLECTION_NOT_FOUND",
                                "message": f"Collection '{collection_name}' does not exist",
                                "details": {"collection_name": collection_name}
                            }
                        }
                    )
                raise  # Re-raise other exceptions
        
        @app.post("/api/vector-sync/collections/{collection_id}/sync")
        async def sync_collection(collection_id: str, request: dict = None):
            """Synchronize a collection with the vector database."""
            try:
                # Validate collection exists first
                await _validate_collection_exists(collection_id)
                
                config = request or {}
                status = await vector_service.sync_collection(collection_id, config)
                
                # Check if vector dependencies are available
                if not vector_service.vector_available:
                    raise HTTPException(
                        status_code=503,
                        detail={
                            "error": {
                                "code": "SERVICE_UNAVAILABLE",
                                "message": "Vector sync service is not available - RAG dependencies not installed",
                                "details": {"service": "vector_sync"}
                            }
                        }
                    )
                
                # Check sync result
                if status.sync_status == "error":
                    # General sync error
                    raise HTTPException(
                        status_code=500,
                        detail={
                            "error": {
                                "code": "SYNC_FAILED",
                                "message": status.error_message,
                                "details": {"collection_name": collection_id}
                            }
                        }
                    )
                
                # Success case
                return {
                    "success": True,
                    "sync_result": status.model_dump()
                }
                
            except HTTPException:
                raise  # Re-raise HTTPExceptions without wrapping
            except Exception as e:
                logger.error(f"HTTP sync_collection error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/api/vector-sync/collections/{collection_id}/status")
        async def get_sync_status(collection_id: str):
            """Get synchronization status for a collection."""
            try:
                # Validate collection exists first
                await _validate_collection_exists(collection_id)
                
                status = await vector_service.get_sync_status(collection_id)
                
                # Check if vector dependencies are available
                if not vector_service.vector_available:
                    raise HTTPException(
                        status_code=503,
                        detail={
                            "error": {
                                "code": "SERVICE_UNAVAILABLE",
                                "message": "Vector sync service is not available - RAG dependencies not installed",
                                "details": {"service": "vector_sync"}
                            }
                        }
                    )
                
                return {
                    "success": True,
                    "status": status.model_dump()
                }
            except HTTPException:
                raise  # Re-raise HTTPExceptions without wrapping
            except Exception as e:
                logger.error(f"HTTP get_sync_status error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/api/vector-sync/collections/statuses")
        async def list_all_sync_statuses():
            """Get synchronization status for all collections."""
            try:
                statuses = await vector_service.list_sync_statuses()
                return {
                    "success": True,
                    "statuses": {status.collection_name: status.model_dump() for status in statuses}
                }
            except Exception as e:
                logger.error(f"HTTP list_all_sync_statuses error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.post("/api/vector-sync/search")
        async def search_vectors(request: dict):
            """Search vectors using semantic similarity."""
            try:
                # Import the shared use-case function
                from application_layer.vector_search import search_vectors_use_case, ValidationError
                
                # Extract parameters from request
                query = request.get("query")
                collection_name = request.get("collection_name")
                limit = request.get("limit", 10)
                similarity_threshold = request.get("similarity_threshold", 0.7)
                
                # Use shared use-case function
                results = await search_vectors_use_case(
                    vector_service, collection_service,
                    query, collection_name, limit, similarity_threshold
                )
                
                return {
                    "success": True,
                    "results": results
                }
                
            except ValidationError as ve:
                # Map ValidationError to HTTPException with exact same format as before
                if ve.code == "MISSING_QUERY":
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error": {
                                "code": "MISSING_QUERY",
                                "message": "Query parameter is required",
                                "details": {"missing_field": "query"}
                            }
                        }
                    )
                elif ve.code == "INVALID_LIMIT":
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error": {
                                "code": "INVALID_LIMIT",
                                "message": "Limit must be greater than 0",
                                "details": {"limit": limit}
                            }
                        }
                    )
                elif ve.code == "INVALID_THRESHOLD":
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error": {
                                "code": "INVALID_THRESHOLD",
                                "message": "Similarity threshold must be between 0 and 1",
                                "details": {"similarity_threshold": similarity_threshold}
                            }
                        }
                    )
                else:
                    # Generic validation error mapping
                    raise HTTPException(status_code=400, detail=str(ve))
                    
            except RuntimeError as re:
                # Map RuntimeError (service unavailable) to 503
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error": {
                            "code": "SERVICE_UNAVAILABLE",
                            "message": "Vector search service is not available - RAG dependencies not installed", 
                            "details": {"service": "vector_search"}
                        }
                    }
                )
                
            except Exception as e:
                # Handle collection not found and other service errors
                error_msg = str(e).lower()
                if "not found" in error_msg or "does not exist" in error_msg:
                    # Extract collection name for proper error response
                    collection_name_for_error = collection_name or "unknown"
                    raise HTTPException(
                        status_code=404,
                        detail={
                            "error": {
                                "code": "COLLECTION_NOT_FOUND",
                                "message": f"Collection '{collection_name_for_error}' does not exist",
                                "details": {"collection_name": collection_name_for_error}
                            }
                        }
                    )
                else:
                    # Generic error handling
                    logger.error(f"HTTP search_vectors error: {e}")
                    raise HTTPException(status_code=500, detail=str(e))
        
        # ===== ADDITIONAL VECTOR SYNC ENDPOINTS =====
        
        @app.delete("/api/vector-sync/collections/{collection_id}/vectors")
        async def delete_collection_vectors(collection_id: str):
            """Delete all vectors for a collection."""
            try:
                # Validate collection exists first
                await _validate_collection_exists(collection_id)
                
                # Check if vector service is available
                if not vector_service.vector_available:
                    raise HTTPException(
                        status_code=503,
                        detail={
                            "error": {
                                "code": "SERVICE_UNAVAILABLE",
                                "message": "Vector sync service is not available - RAG dependencies not installed",
                                "details": {"service": "vector_sync"}
                            }
                        }
                    )
                
                # Delete vectors (implement in vector service)
                result = await vector_service.delete_collection_vectors(collection_id)
                return {"success": True, "message": f"Deleted vectors for collection '{collection_id}'", "deleted_count": result.get("deleted_count", 0)}
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"HTTP delete_collection_vectors error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        self.http_app = app
        logger.info("HTTP protocol handler configured with service layer controllers")
        return app
    
    async def run_mcp_server(self):
        """Run the MCP server (stdio protocol)."""
        logger.info("Starting MCP server (stdio)")
        if not self.mcp_server:
            self.setup_mcp_server()
        
        # Run MCP server
        await self.mcp_server.run()
    
    async def run_http_server(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the HTTP server."""
        logger.info(f"Starting HTTP server on {host}:{port}")
        if not self.http_app:
            self.setup_http_app()
        
        # Import uvicorn here to avoid import issues
        import uvicorn
        
        # Run HTTP server
        config = uvicorn.Config(
            self.http_app,
            host=host,
            port=port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
    
    async def run_unified(self):
        """
        Run both MCP and HTTP servers concurrently.
        
        This is the main entry point for unified server operation.
        """
        logger.info("Starting unified server with both MCP and HTTP protocols")
        
        # Setup both protocol handlers
        self.setup_mcp_server()
        self.setup_http_app()
        
        self.running = True
        
        # Determine run mode based on environment or command line
        run_mode = os.getenv("UNIFIED_SERVER_MODE", "auto")
        
        if run_mode == "mcp" or (run_mode == "auto" and len(sys.argv) == 1):
            # MCP mode (stdio) - default for Claude Desktop
            logger.info("Running in MCP mode (stdio)")
            await self.run_mcp_server()
        elif run_mode == "http":
            # HTTP mode only
            logger.info("Running in HTTP mode only")
            await self.run_http_server()
        else:
            # Dual mode - both protocols (for development/testing)
            logger.info("Running in dual mode (MCP + HTTP)")
            await asyncio.gather(
                self.run_mcp_server(),
                self.run_http_server()
            )


async def main():
    """Main entry point for unified server."""
    try:
        server = UnifiedServer()
        await server.run_unified()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())