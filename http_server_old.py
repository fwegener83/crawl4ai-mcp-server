"""HTTP wrapper for the MCP server to provide REST API endpoints."""
import asyncio
import json
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import MCP tools directly
from tools.web_extract import web_content_extract
from tools.mcp_domain_tools import domain_deep_crawl, domain_link_preview
from tools.sqlite_collection_manager import create_collection_manager
import os

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import RAG tools
try:
    from tools.knowledge_base.dependencies import is_rag_available
    if is_rag_available():
        from tools.knowledge_base.rag_tools import (
            store_crawl_results,
            search_knowledge_base,
            list_collections,
            delete_collection
        )
        from tools.vector_sync_api import VectorSyncAPI
        from tools.knowledge_base.intelligent_sync_manager import IntelligentSyncManager
        from tools.knowledge_base.vector_store import VectorStore
        RAG_AVAILABLE = True
        
        # Initialize Vector Sync API components
        try:
            vector_store = VectorStore()
            sync_manager = IntelligentSyncManager(
                vector_store=vector_store,
                collection_manager=None  # Will be set later
            )
            vector_sync_api = VectorSyncAPI(
                sync_manager=sync_manager,
                vector_store=vector_store,
                collection_manager=None  # Will be set later
            )
        except Exception as e:
            logger.warning(f"Failed to initialize Vector Sync API: {e}")
            vector_sync_api = None
    else:
        RAG_AVAILABLE = False
        vector_sync_api = None
except ImportError as e:
    logger.warning(f"RAG dependencies not available: {e}")
    RAG_AVAILABLE = False
    vector_sync_api = None

# Configure logging (already done above)

# Initialize Collection Manager (SQLite by default, configurable via environment)
use_sqlite = os.getenv('CRAWL4AI_USE_SQLITE', 'true').lower() == 'true'
collection_manager = create_collection_manager(use_sqlite=use_sqlite)

# Set collection manager for vector sync components if available
if RAG_AVAILABLE and vector_sync_api:
    try:
        # Update the sync manager and vector sync API with the collection manager
        vector_sync_api.sync_manager.collection_manager = collection_manager
        vector_sync_api.collection_manager = collection_manager
        logger.info("Vector Sync API initialized successfully with collection manager")
    except Exception as e:
        logger.warning(f"Failed to set collection manager for Vector Sync API: {e}")
        vector_sync_api = None

# FastAPI app
app = FastAPI(title="Crawl4AI HTTP API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class ExtractRequest(BaseModel):
    url: str

class DeepCrawlRequest(BaseModel):
    domain_url: str
    max_depth: int = 1
    crawl_strategy: str = "bfs"
    max_pages: int = 10
    include_external: bool = False
    url_patterns: Optional[list] = None
    exclude_patterns: Optional[list] = None
    keywords: Optional[list] = None

class LinkPreviewRequest(BaseModel):
    domain_url: str
    include_external: bool = False

class StoreRequest(BaseModel):
    crawl_result: str
    collection_name: str = "default"

class SearchRequest(BaseModel):
    query: str
    collection_name: str = "default"
    n_results: int = 5
    similarity_threshold: Optional[float] = None

# File collection management models
class CreateCollectionRequest(BaseModel):
    name: str
    description: str = ""

class SaveFileRequest(BaseModel):
    filename: str
    content: str
    folder: str = ""

class UpdateFileRequest(BaseModel):
    content: str

class CrawlToCollectionRequest(BaseModel):
    url: str
    folder: str = ""

# Vector sync models
class SyncCollectionRequest(BaseModel):
    force_reprocess: bool = False
    chunking_strategy: str = "auto"  # auto, baseline, markdown_intelligent

class VectorSearchRequest(BaseModel):
    query: str
    collection_name: Optional[str] = None
    limit: int = 20

# Health check
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "rag_available": RAG_AVAILABLE}

@app.get("/api/status")
async def get_status():
    tools_count = 3 + (4 if RAG_AVAILABLE else 0)
    return {
        "status": "running",
        "tools_available": tools_count,
        "rag_enabled": RAG_AVAILABLE
    }

# Basic crawling endpoints
@app.post("/api/extract")
async def extract_content(request: ExtractRequest):
    try:
        from tools.web_extract import WebExtractParams
        content = await web_content_extract(WebExtractParams(url=request.url))
        return {"content": content}
    except Exception as e:
        logger.error(f"Extract failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/deep-crawl")
async def deep_crawl(request: DeepCrawlRequest):
    try:
        results_json = await domain_deep_crawl(
            domain_url=request.domain_url,
            max_depth=request.max_depth,
            crawl_strategy=request.crawl_strategy,
            max_pages=request.max_pages,
            include_external=request.include_external,
            url_patterns=request.url_patterns,
            exclude_patterns=request.exclude_patterns,
            keywords=request.keywords
        )
        # Parse the JSON string returned by MCP tool
        results = json.loads(results_json) if isinstance(results_json, str) else results_json
        return {"results": results}
    except Exception as e:
        logger.error(f"Deep crawl failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/link-preview")
async def link_preview(request: LinkPreviewRequest):
    try:
        preview = await domain_link_preview(
            domain_url=request.domain_url,
            include_external=request.include_external
        )
        return preview
    except Exception as e:
        logger.error(f"Link preview failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# File Collection Management Endpoints

@app.post("/api/file-collections")
async def create_file_collection(request: CreateCollectionRequest):
    """Create a new file collection."""
    try:
        result = collection_manager.create_collection(request.name, request.description)
        if isinstance(result, str):
            result = json.loads(result)
            
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to create collection"))
            
        # Transform to match frontend expected format
        from datetime import datetime, timezone
        return {
            "success": True,
            "data": {
                "name": request.name,
                "description": request.description,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "file_count": 0,
                "folders": [],
                "metadata": {
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "description": request.description,
                    "last_modified": datetime.now(timezone.utc).isoformat(),
                    "file_count": 0,
                    "total_size": 0
                },
                "path": result.get("path")
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create file collection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/file-collections")
async def list_file_collections():
    """List all file collections."""
    try:
        result = collection_manager.list_collections()
        if isinstance(result, str):
            result = json.loads(result)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to list collections"))
            
        # Transform to match frontend expected format
        return {
            "success": True,
            "data": {
                "collections": result.get("collections", [])
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List file collections failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/file-collections/{collection_id}")
async def get_file_collection_info(collection_id: str):
    """Get detailed information about a file collection."""
    try:
        # URL decode the collection_id to handle names with spaces
        from urllib.parse import unquote
        decoded_collection_id = unquote(collection_id)
        result = collection_manager.get_collection_info(decoded_collection_id)
        if isinstance(result, str):
            result = json.loads(result)
        if not result.get("success"):
            if "not found" in result.get("error", "").lower():
                raise HTTPException(status_code=404, detail=f"Collection '{collection_id}' not found")
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to get collection info"))
        
        # Transform to match frontend expected format
        return {
            "success": True,
            "data": result.get("collection", {})
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get file collection info failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/file-collections/{collection_id}/files")
async def list_files_in_collection(collection_id: str):
    """List all files and folders in a collection."""
    try:
        # URL decode the collection_id to handle names with spaces
        from urllib.parse import unquote
        decoded_collection_id = unquote(collection_id)
        
        result = collection_manager.list_files_in_collection(decoded_collection_id)
        if isinstance(result, str):
            result = json.loads(result)
        
        if not result.get("success"):
            if "not found" in result.get("error", "").lower():
                raise HTTPException(status_code=404, detail=f"Collection '{decoded_collection_id}' not found")
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to list files"))
        
        return {
            "success": True,
            "data": {
                "files": result.get("files", []),
                "folders": result.get("folders", []),
                "total_files": result.get("total_files", 0),
                "total_folders": result.get("total_folders", 0)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List files in collection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/file-collections/{collection_id}")
async def delete_file_collection(collection_id: str):
    """Delete a file collection and all its files."""
    try:
        # URL decode the collection_id to handle names with spaces
        from urllib.parse import unquote
        decoded_collection_id = unquote(collection_id)
        result = collection_manager.delete_collection(decoded_collection_id)
        if isinstance(result, str):
            result = json.loads(result)
        if not result.get("success"):
            if "not found" in result.get("error", "").lower():
                raise HTTPException(status_code=404, detail=f"Collection '{collection_id}' not found")
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to delete collection"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete file collection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/file-collections/{collection_id}/files")
async def save_file_to_collection(collection_id: str, request: SaveFileRequest):
    """Save a file to a collection."""
    try:
        # URL decode the collection_id to handle names with spaces
        from urllib.parse import unquote
        decoded_collection_id = unquote(collection_id)
        
        # Ensure collection exists
        collection_info = collection_manager.get_collection_info(decoded_collection_id)
        if isinstance(collection_info, str):
            collection_info = json.loads(collection_info)
        
        if not collection_info.get("success"):
            if "not found" in collection_info.get("error", "").lower():
                # Auto-create collection if it doesn't exist
                logger.info(f"Collection '{decoded_collection_id}' doesn't exist, creating it")
                create_result = collection_manager.create_collection(decoded_collection_id)
                if isinstance(create_result, str):
                    create_result = json.loads(create_result)
                if not create_result.get("success"):
                    raise HTTPException(status_code=400, detail=f"Failed to create collection: {create_result.get('error')}")
        
        result = collection_manager.save_file(decoded_collection_id, request.filename, request.content, request.folder)
        if isinstance(result, str):
            result = json.loads(result)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to save file"))
        
        # Transform to match frontend expected format
        return {
            "success": True,
            "data": {
                "filename": request.filename,
                "folder_path": request.folder or "",
                "path": result.get("path")
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Save file to collection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/file-collections/{collection_id}/files/{file_path:path}")
async def read_file_from_collection(collection_id: str, file_path: str, folder: str = ""):
    """Read a file from a collection."""
    try:
        # URL decode the collection_id to handle names with spaces
        from urllib.parse import unquote
        decoded_collection_id = unquote(collection_id)
        result = collection_manager.read_file(decoded_collection_id, file_path, folder)
        if isinstance(result, str):
            result = json.loads(result)
        
        if not result.get("success"):
            if "not found" in result.get("error", "").lower():
                raise HTTPException(status_code=404, detail=f"File '{file_path}' not found in collection '{decoded_collection_id}'")
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to read file"))
        
        # Transform to match frontend expected format
        return {
            "success": True,
            "data": {
                "content": result.get("content", "")
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Read file from collection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/file-collections/{collection_id}/files/{file_path:path}")
async def update_file_in_collection(collection_id: str, file_path: str, request: UpdateFileRequest, folder: str = ""):
    """Update a file in a collection."""
    try:
        # URL decode the collection_id to handle names with spaces
        from urllib.parse import unquote
        decoded_collection_id = unquote(collection_id)
        result = collection_manager.save_file(decoded_collection_id, file_path, request.content, folder)
        if isinstance(result, str):
            result = json.loads(result)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to update file"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update file in collection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/file-collections/{collection_id}/files/{file_path:path}")
async def delete_file_from_collection(collection_id: str, file_path: str, folder: str = ""):
    """Delete a file from a collection."""
    try:
        # URL decode the collection_id to handle names with spaces
        from urllib.parse import unquote
        decoded_collection_id = unquote(collection_id)
        
        # Build full file path
        collection_path = collection_manager.base_dir / decoded_collection_id
        if not collection_path.exists():
            raise HTTPException(status_code=404, detail=f"Collection '{decoded_collection_id}' not found")
        
        if folder:
            file_full_path = collection_path / folder / file_path
        else:
            file_full_path = collection_path / file_path
            
        if not file_full_path.exists():
            raise HTTPException(status_code=404, detail=f"File '{file_path}' not found in collection '{decoded_collection_id}'")
        
        # Delete the file
        file_full_path.unlink()
        logger.info(f"Successfully deleted '{file_path}' from collection '{decoded_collection_id}'")
        
        return {
            "success": True,
            "message": f"File '{file_path}' deleted successfully",
            "collection_name": decoded_collection_id,
            "filename": file_path,
            "folder": folder
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete file from collection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/crawl/single/{collection_id}")
async def crawl_single_page_to_collection(collection_id: str, request: CrawlToCollectionRequest):
    """Crawl a single page and save to collection."""
    try:
        # URL decode the collection_id to handle names with spaces
        from urllib.parse import unquote
        decoded_collection_id = unquote(collection_id)
        
        # Extract content from URL
        from tools.web_extract import WebExtractParams
        content = await web_content_extract(WebExtractParams(url=request.url))
        content_str = str(content)
        
        if content_str.startswith("Error extracting content"):
            raise HTTPException(status_code=400, detail=f"Failed to crawl URL: {content_str}")
        
        # Generate filename from URL
        from urllib.parse import urlparse
        parsed_url = urlparse(request.url)
        domain = parsed_url.netloc.replace("www.", "")
        path_parts = [p for p in parsed_url.path.split("/") if p]
        if path_parts:
            filename = f"{domain}_{path_parts[-1]}.md"
        else:
            filename = f"{domain}_index.md"
        
        # Save to collection using the decoded collection ID
        result = collection_manager.save_file(decoded_collection_id, filename, content_str, request.folder)
        if isinstance(result, str):
            result = json.loads(result)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to save crawled content"))
        
        # Add crawl metadata to result
        result["url"] = request.url
        result["content_length"] = len(content_str)
        result["message"] = f"Page crawled and saved as '{filename}'"
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Crawl single page to collection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# RAG endpoints (if available)
if RAG_AVAILABLE:
    @app.post("/api/collections")
    async def store_content(request: StoreRequest):
        try:
            result_json = await store_crawl_results(
                crawl_result=request.crawl_result,
                collection_name=request.collection_name
            )
            # Parse the JSON string returned by MCP tool
            result = json.loads(result_json) if isinstance(result_json, str) else result_json
            return result
        except Exception as e:
            logger.error(f"Store failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/collections")
    async def get_collections():
        try:
            collections_json = await list_collections()
            # Parse the JSON string returned by MCP tool
            collections = json.loads(collections_json) if isinstance(collections_json, str) else collections_json
            return collections
        except Exception as e:
            logger.error(f"List collections failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/api/collections/{collection_name}")
    async def delete_collection_endpoint(collection_name: str):
        try:
            result_json = await delete_collection(collection_name)
            # Parse the JSON string returned by MCP tool
            result = json.loads(result_json) if isinstance(result_json, str) else result_json
            return result
        except Exception as e:
            logger.error(f"Delete collection failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/search")
    async def search_collections(
        query: str,
        collection_name: str = "default",
        n_results: int = 5,
        similarity_threshold: Optional[float] = None
    ):
        try:
            results_json = await search_knowledge_base(
                query=query,
                collection_name=collection_name,
                n_results=n_results,
                similarity_threshold=similarity_threshold
            )
            # Parse the JSON string returned by MCP tool
            results = json.loads(results_json) if isinstance(results_json, str) else results_json
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
else:
    # Stub endpoints when RAG is not available
    @app.post("/api/collections")
    async def store_content_stub(request: StoreRequest):
        raise HTTPException(status_code=503, detail="RAG functionality not available")

    @app.get("/api/collections")
    async def get_collections_stub():
        raise HTTPException(status_code=503, detail="RAG functionality not available")

    @app.delete("/api/collections/{collection_name}")
    async def delete_collection_stub(collection_name: str):
        raise HTTPException(status_code=503, detail="RAG functionality not available")

    @app.get("/api/search")
    async def search_stub():
        raise HTTPException(status_code=503, detail="RAG functionality not available")

# ===== VECTOR SYNC ENDPOINTS =====

if RAG_AVAILABLE and vector_sync_api:
    @app.get("/api/vector-sync/collections/{collection_name}/status")
    async def get_collection_sync_status(collection_name: str):
        """Get vector sync status for a collection."""
        try:
            status = await vector_sync_api.get_collection_sync_status(collection_name)
            return {
                "success": True,
                "status": status.model_dump()
            }
        except Exception as e:
            logger.error(f"Get sync status failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/vector-sync/collections/statuses")
    async def list_collection_sync_statuses():
        """Get vector sync status for all collections."""
        try:
            response = await vector_sync_api.list_collection_sync_statuses()
            
            # Handle the case where the response is a dict with success/error structure
            if isinstance(response, dict):
                if response.get('success'):
                    return {
                        "success": True,
                        "statuses": response.get('statuses', {})
                    }
                else:
                    return {
                        "success": False,
                        "statuses": {},
                        "error": response.get('error', 'Unknown error')
                    }
            else:
                # Fallback for unexpected response format
                return {
                    "success": True,
                    "statuses": {}
                }
        except Exception as e:
            logger.error(f"List sync statuses failed: {e}")
            return {
                "success": False,
                "statuses": {},
                "error": str(e)
            }

    @app.post("/api/vector-sync/collections/{collection_name}/sync")
    async def sync_collection(collection_name: str, request: SyncCollectionRequest):
        """Sync a collection to vector store."""
        try:
            from tools.vector_sync_api import SyncCollectionRequest as APISyncRequest
            
            api_request = APISyncRequest(
                force_reprocess=request.force_reprocess,
                chunking_strategy=request.chunking_strategy
            )
            
            response = await vector_sync_api.sync_collection(collection_name, api_request)
            return response.model_dump()
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Sync collection failed: {error_msg}")
            
            # Handle specific HTTP status codes
            if "409:" in error_msg:
                return {
                    "success": False,
                    "error": "Collection is already syncing",
                    "status_code": 409
                }
            elif "404:" in error_msg:
                return {
                    "success": False,
                    "error": "Collection not found",
                    "status_code": 404
                }
            else:
                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": 500
                }

    @app.post("/api/vector-sync/collections/{collection_name}/enable")
    async def enable_collection_sync(collection_name: str):
        """Enable vector sync for a collection."""
        try:
            result = await vector_sync_api.enable_collection_sync(collection_name)
            return result
        except Exception as e:
            logger.error(f"Enable sync failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/vector-sync/collections/{collection_name}/disable")
    async def disable_collection_sync(collection_name: str):
        """Disable vector sync for a collection."""
        try:
            result = await vector_sync_api.disable_collection_sync(collection_name)
            return result
        except Exception as e:
            logger.error(f"Disable sync failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/api/vector-sync/collections/{collection_name}/vectors")
    async def delete_collection_vectors(collection_name: str):
        """Delete all vectors for a collection."""
        try:
            result = await vector_sync_api.delete_collection_vectors(collection_name)
            return result
        except Exception as e:
            logger.error(f"Delete vectors failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/vector-sync/search")
    async def search_vectors(request: VectorSearchRequest):
        """Search vectors across collections."""
        try:
            from tools.vector_sync_api import VectorSearchRequest as APISearchRequest
            
            api_request = APISearchRequest(
                query=request.query,
                collection_name=request.collection_name,
                limit=request.limit
            )
            
            response = await vector_sync_api.search_vectors(api_request)
            return response.model_dump()
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

else:
    # Stub endpoints when RAG is not available
    @app.get("/api/vector-sync/collections/{collection_name}/status")
    async def get_collection_sync_status_stub(collection_name: str):
        raise HTTPException(status_code=503, detail="Vector sync functionality not available - RAG dependencies not installed")

    @app.get("/api/vector-sync/collections/statuses")
    async def list_collection_sync_statuses_stub():
        raise HTTPException(status_code=503, detail="Vector sync functionality not available - RAG dependencies not installed")

    @app.post("/api/vector-sync/collections/{collection_name}/sync")
    async def sync_collection_stub(collection_name: str, request: SyncCollectionRequest):
        raise HTTPException(status_code=503, detail="Vector sync functionality not available - RAG dependencies not installed")

    @app.post("/api/vector-sync/collections/{collection_name}/enable")
    async def enable_collection_sync_stub(collection_name: str):
        raise HTTPException(status_code=503, detail="Vector sync functionality not available - RAG dependencies not installed")

    @app.post("/api/vector-sync/collections/{collection_name}/disable")
    async def disable_collection_sync_stub(collection_name: str):
        raise HTTPException(status_code=503, detail="Vector sync functionality not available - RAG dependencies not installed")

    @app.delete("/api/vector-sync/collections/{collection_name}/vectors")
    async def delete_collection_vectors_stub(collection_name: str):
        raise HTTPException(status_code=503, detail="Vector sync functionality not available - RAG dependencies not installed")

    @app.post("/api/vector-sync/search")
    async def search_vectors_stub(request: VectorSearchRequest):
        raise HTTPException(status_code=503, detail="Vector sync functionality not available - RAG dependencies not installed")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Crawl4AI HTTP API",
        "version": "1.0.0",
        "docs": "/docs",
        "rag_available": RAG_AVAILABLE
    }

if __name__ == "__main__":
    logger.info("Starting Crawl4AI HTTP Server on port 8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")