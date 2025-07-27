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
        RAG_AVAILABLE = True
    else:
        RAG_AVAILABLE = False
except ImportError:
    RAG_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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