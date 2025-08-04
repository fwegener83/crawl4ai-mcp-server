"""
Vector Sync API Endpoints

This module provides HTTP API endpoints for the Vector Sync Infrastructure,
enabling integration with the existing MCP server and frontend applications.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from fastapi import HTTPException
from pydantic import BaseModel, Field

from .knowledge_base.intelligent_sync_manager import IntelligentSyncManager
from .knowledge_base.vector_sync_schemas import (
    VectorSyncStatus, SyncConfiguration, SyncResult, SyncStatus
)
from .knowledge_base.vector_store import VectorStore
from .collection_manager import CollectionFileManager

logger = logging.getLogger(__name__)


# Request/Response Models for API
class SyncCollectionRequest(BaseModel):
    """Request model for syncing a collection."""
    force_reprocess: bool = Field(default=False, description="Force reprocessing of all files")
    chunking_strategy: Optional[str] = Field(None, description="Override chunking strategy")


class SyncCollectionResponse(BaseModel):
    """Response model for sync operations."""
    success: bool
    job_id: str
    message: str
    sync_result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class CollectionSyncStatusResponse(BaseModel):
    """Response model for collection sync status."""
    success: bool
    status: Dict[str, Any]
    error: Optional[str] = None


class VectorSearchRequest(BaseModel):
    """Request model for vector search."""
    query: str = Field(..., description="Search query")
    collection_name: Optional[str] = Field(None, description="Specific collection to search")
    limit: int = Field(default=10, description="Maximum number of results")
    similarity_threshold: float = Field(default=0.7, description="Minimum similarity score")


class VectorSearchResponse(BaseModel):
    """Response model for vector search."""
    success: bool
    results: List[Dict[str, Any]] = Field(default_factory=list)
    total_results: int = 0
    query_time: float = 0.0
    error: Optional[str] = None


class SyncConfigurationRequest(BaseModel):
    """Request model for updating sync configuration."""
    enabled: Optional[bool] = None
    batch_size: Optional[int] = None
    max_concurrent_files: Optional[int] = None
    chunking_strategy: Optional[str] = None


class VectorSyncAPI:
    """API handler for vector sync operations."""
    
    def __init__(
        self,
        sync_manager: IntelligentSyncManager,
        vector_store: VectorStore,
        collection_manager: CollectionFileManager
    ):
        """Initialize the API handler.
        
        Args:
            sync_manager: Intelligent sync manager instance
            vector_store: Vector storage instance
            collection_manager: Collection file manager
        """
        self.sync_manager = sync_manager
        self.vector_store = vector_store
        self.collection_manager = collection_manager
        
        # Progress tracking for async operations
        self.active_sync_jobs: Dict[str, Dict[str, Any]] = {}
        
        logger.info("VectorSyncAPI initialized")
    
    async def sync_collection(
        self,
        collection_name: str,
        request: SyncCollectionRequest
    ) -> SyncCollectionResponse:
        """
        Sync a collection with the vector store.
        
        Args:
            collection_name: Name of collection to sync
            request: Sync configuration request
            
        Returns:
            Sync operation response
        """
        try:
            # Validate collection exists
            if not self._collection_exists(collection_name):
                raise HTTPException(
                    status_code=404,
                    detail=f"Collection '{collection_name}' not found"
                )
            
            # Check if sync is enabled for this collection
            sync_status = self.sync_manager.get_collection_sync_status(collection_name)
            if not sync_status.sync_enabled:
                raise HTTPException(
                    status_code=400,
                    detail=f"Sync is disabled for collection '{collection_name}'"
                )
            
            # Check if already syncing
            if sync_status.status == SyncStatus.SYNCING:
                raise HTTPException(
                    status_code=409,
                    detail=f"Collection '{collection_name}' is already syncing"
                )
            
            # Override chunking strategy if specified
            if request.chunking_strategy:
                self.sync_manager.content_processor.chunking_strategy = request.chunking_strategy
            
            # Progress tracking
            job_progress = {'progress': 0.0, 'message': 'Starting sync...'}
            
            def progress_callback(progress: float, message: str):
                job_progress['progress'] = progress
                job_progress['message'] = message
                logger.debug(f"Sync progress for {collection_name}: {progress:.1%} - {message}")
            
            # Start sync operation
            logger.info(f"Starting sync for collection '{collection_name}'")
            sync_result = await self.sync_manager.sync_collection(
                collection_name=collection_name,
                force_reprocess=request.force_reprocess,
                progress_callback=progress_callback
            )
            
            # Store job for tracking
            self.active_sync_jobs[sync_result.job_id] = {
                'collection_name': collection_name,
                'started_at': sync_result.started_at.isoformat(),
                'status': 'completed' if sync_result.success else 'failed',
                'progress': job_progress
            }
            
            response = SyncCollectionResponse(
                success=sync_result.success,
                job_id=sync_result.job_id,
                message=f"Sync {'completed' if sync_result.success else 'failed'} for collection '{collection_name}'",
                sync_result={
                    'files_processed': sync_result.files_processed,
                    'chunks_created': sync_result.chunks_created,
                    'chunks_updated': sync_result.chunks_updated,
                    'total_duration': sync_result.total_duration,
                    'errors': sync_result.errors,
                    'warnings': sync_result.warnings,
                    'health_score': sync_result.health_score
                }
            )
            
            if not sync_result.success:
                response.error = f"Sync failed: {'; '.join(sync_result.errors[:3])}"
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error syncing collection '{collection_name}': {str(e)}")
            return SyncCollectionResponse(
                success=False,
                job_id="",
                message=f"Sync failed for collection '{collection_name}'",
                error=str(e)
            )
    
    async def get_collection_sync_status(
        self,
        collection_name: str
    ) -> CollectionSyncStatusResponse:
        """
        Get sync status for a collection.
        
        Args:
            collection_name: Name of collection
            
        Returns:
            Collection sync status
        """
        try:
            if not self._collection_exists(collection_name):
                raise HTTPException(
                    status_code=404,
                    detail=f"Collection '{collection_name}' not found"
                )
            
            sync_status = self.sync_manager.get_collection_sync_status(collection_name)
            
            return CollectionSyncStatusResponse(
                success=True,
                status={
                    'collection_name': sync_status.collection_name,
                    'sync_enabled': sync_status.sync_enabled,
                    'status': sync_status.status.value,
                    'last_sync': sync_status.last_sync.isoformat() if sync_status.last_sync else None,
                    'last_sync_attempt': sync_status.last_sync_attempt.isoformat() if sync_status.last_sync_attempt else None,
                    'total_files': sync_status.total_files,
                    'synced_files': sync_status.synced_files,
                    'changed_files_count': sync_status.changed_files_count,
                    'total_chunks': sync_status.total_chunks,
                    'chunk_count': sync_status.chunk_count,
                    'sync_progress': sync_status.sync_progress,
                    'is_out_of_sync': sync_status.is_out_of_sync,
                    'sync_health_score': sync_status.sync_health_score,
                    'errors': sync_status.errors,
                    'warnings': sync_status.warnings,
                    'last_sync_duration': sync_status.last_sync_duration,
                    'avg_sync_duration': sync_status.avg_sync_duration
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting sync status for '{collection_name}': {str(e)}")
            return CollectionSyncStatusResponse(
                success=False,
                status={},
                error=str(e)
            )
    
    async def list_collection_sync_statuses(self) -> Dict[str, Any]:
        """
        Get sync status for all collections.
        
        Returns:
            Dictionary of collection sync statuses
        """
        try:
            statuses = self.sync_manager.list_collection_sync_statuses()
            
            # Convert to API format
            status_data = {}
            for collection_name, sync_status in statuses.items():
                status_data[collection_name] = {
                    'collection_name': sync_status.collection_name,
                    'sync_enabled': sync_status.sync_enabled,
                    'status': sync_status.status.value,
                    'last_sync': sync_status.last_sync.isoformat() if sync_status.last_sync else None,
                    'total_files': sync_status.total_files,
                    'synced_files': sync_status.synced_files,
                    'changed_files_count': sync_status.changed_files_count,
                    'chunk_count': sync_status.chunk_count,
                    'is_out_of_sync': sync_status.is_out_of_sync,
                    'sync_health_score': sync_status.sync_health_score,
                    'sync_progress': sync_status.sync_progress
                }
            
            return {
                'success': True,
                'statuses': status_data,
                'summary': self.sync_manager.get_sync_statistics()
            }
            
        except Exception as e:
            logger.error(f"Error listing collection sync statuses: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def enable_collection_sync(self, collection_name: str) -> Dict[str, Any]:
        """Enable sync for a collection."""
        try:
            if not self._collection_exists(collection_name):
                raise HTTPException(
                    status_code=404,
                    detail=f"Collection '{collection_name}' not found"
                )
            
            self.sync_manager.enable_collection_sync(collection_name)
            
            return {
                'success': True,
                'message': f"Sync enabled for collection '{collection_name}'"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error enabling sync for '{collection_name}': {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def disable_collection_sync(self, collection_name: str) -> Dict[str, Any]:
        """Disable sync for a collection."""
        try:
            if not self._collection_exists(collection_name):
                raise HTTPException(
                    status_code=404,
                    detail=f"Collection '{collection_name}' not found"
                )
            
            self.sync_manager.disable_collection_sync(collection_name)
            
            return {
                'success': True,
                'message': f"Sync disabled for collection '{collection_name}'"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error disabling sync for '{collection_name}': {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def delete_collection_vectors(self, collection_name: str) -> Dict[str, Any]:
        """Delete all vectors for a collection."""
        try:
            if not self._collection_exists(collection_name):
                raise HTTPException(
                    status_code=404,
                    detail=f"Collection '{collection_name}' not found"
                )
            
            result = await self.sync_manager.delete_collection_vectors(collection_name)
            
            return {
                'success': result.success,
                'message': f"{'Deleted' if result.success else 'Failed to delete'} vectors for collection '{collection_name}'",
                'chunks_deleted': result.chunks_deleted,
                'errors': result.errors
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting vectors for '{collection_name}': {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def search_vectors(
        self,
        request: VectorSearchRequest
    ) -> VectorSearchResponse:
        """
        Search vectors across collections.
        
        Args:
            request: Search request parameters
            
        Returns:
            Search results with file location mapping
        """
        try:
            import time
            start_time = time.time()
            
            # Perform vector search
            results = self.vector_store.similarity_search(
                query=request.query,
                k=request.limit,
                score_threshold=request.similarity_threshold
            )
            
            query_time = time.time() - start_time
            
            # Enhance results with file location information
            enhanced_results = []
            for result in results:
                # Extract metadata
                metadata = result.get('metadata', {})
                
                # Filter by collection if specified
                if request.collection_name and metadata.get('collection_name') != request.collection_name:
                    continue
                
                enhanced_result = {
                    'content': result.get('content', ''),
                    'score': result.get('score', 0.0),
                    'chunk_id': result.get('id', ''),
                    'collection_name': metadata.get('collection_name', ''),
                    'source_file': metadata.get('source_file', ''),
                    'chunk_index': metadata.get('chunk_index', 0),
                    'chunk_type': metadata.get('chunk_type', ''),
                    'header_hierarchy': metadata.get('header_hierarchy', []),
                    'contains_code': metadata.get('contains_code', False),
                    'programming_language': metadata.get('programming_language'),
                    'word_count': metadata.get('word_count', 0),
                    'created_at': metadata.get('created_at'),
                    'file_location': {
                        'collection': metadata.get('collection_name', ''),
                        'file_path': metadata.get('source_file', ''),
                        'chunk_position': metadata.get('chunk_index', 0)
                    }
                }
                enhanced_results.append(enhanced_result)
            
            return VectorSearchResponse(
                success=True,
                results=enhanced_results,
                total_results=len(enhanced_results),
                query_time=query_time
            )
            
        except Exception as e:
            logger.error(f"Error performing vector search: {str(e)}")
            return VectorSearchResponse(
                success=False,
                error=str(e)
            )
    
    async def get_sync_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of a specific sync job."""
        try:
            if job_id not in self.active_sync_jobs:
                raise HTTPException(
                    status_code=404,
                    detail=f"Sync job '{job_id}' not found"
                )
            
            job_info = self.active_sync_jobs[job_id]
            
            return {
                'success': True,
                'job_id': job_id,
                'collection_name': job_info['collection_name'],
                'status': job_info['status'],
                'started_at': job_info['started_at'],
                'progress': job_info['progress']
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting job status for '{job_id}': {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_sync_statistics(self) -> Dict[str, Any]:
        """Get overall sync statistics."""
        try:
            stats = self.sync_manager.get_sync_statistics()
            
            return {
                'success': True,
                'statistics': stats,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting sync statistics: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _collection_exists(self, collection_name: str) -> bool:
        """Check if collection exists."""
        try:
            self.collection_manager.get_collection_info(collection_name)
            return True
        except Exception:
            return False


# Utility functions for MCP tool integration
def create_vector_sync_tools(sync_api: VectorSyncAPI) -> List[Dict[str, Any]]:
    """Create MCP tool definitions for vector sync operations."""
    
    tools = [
        {
            "name": "sync_collection_to_vectors",
            "description": "Sync a file collection to vector storage with intelligent chunking",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "collection_name": {
                        "type": "string",
                        "description": "Name of the collection to sync"
                    },
                    "force_reprocess": {
                        "type": "boolean",
                        "description": "Force reprocessing of all files (ignore hashes)",
                        "default": False
                    },
                    "chunking_strategy": {
                        "type": "string",
                        "description": "Chunking strategy override (baseline, markdown_intelligent, auto)",
                        "enum": ["baseline", "markdown_intelligent", "auto"]
                    }
                },
                "required": ["collection_name"]
            }
        },
        {
            "name": "get_collection_sync_status",
            "description": "Get vector sync status for a collection",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "collection_name": {
                        "type": "string",
                        "description": "Name of the collection"
                    }
                },
                "required": ["collection_name"]
            }
        },
        {
            "name": "list_collection_sync_statuses",
            "description": "Get vector sync status for all collections",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "search_collection_vectors",
            "description": "Search vectors across collections with file location mapping",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query text"
                    },
                    "collection_name": {
                        "type": "string",
                        "description": "Specific collection to search (optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 100
                    },
                    "similarity_threshold": {
                        "type": "number",
                        "description": "Minimum similarity score (0.0-1.0)",
                        "default": 0.7,
                        "minimum": 0.0,
                        "maximum": 1.0
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "enable_collection_sync",
            "description": "Enable vector sync for a collection",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "collection_name": {
                        "type": "string",
                        "description": "Name of the collection"
                    }
                },
                "required": ["collection_name"]
            }
        },
        {
            "name": "disable_collection_sync",
            "description": "Disable vector sync for a collection",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "collection_name": {
                        "type": "string",
                        "description": "Name of the collection"
                    }
                },
                "required": ["collection_name"]
            }
        },
        {
            "name": "delete_collection_vectors",
            "description": "Delete all vectors for a collection",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "collection_name": {
                        "type": "string",
                        "description": "Name of the collection"
                    }
                },
                "required": ["collection_name"]
            }
        }
    ]
    
    return tools


async def handle_vector_sync_tool(
    tool_name: str,
    arguments: Dict[str, Any],
    sync_api: VectorSyncAPI
) -> Dict[str, Any]:
    """Handle vector sync MCP tool calls."""
    
    try:
        if tool_name == "sync_collection_to_vectors":
            request = SyncCollectionRequest(**arguments)
            response = await sync_api.sync_collection(
                collection_name=arguments["collection_name"],
                request=request
            )
            return response.dict()
        
        elif tool_name == "get_collection_sync_status":
            response = await sync_api.get_collection_sync_status(
                collection_name=arguments["collection_name"]
            )
            return response.dict()
        
        elif tool_name == "list_collection_sync_statuses":
            return await sync_api.list_collection_sync_statuses()
        
        elif tool_name == "search_collection_vectors":
            request = VectorSearchRequest(**arguments)
            response = await sync_api.search_vectors(request)
            return response.dict()
        
        elif tool_name == "enable_collection_sync":
            return await sync_api.enable_collection_sync(
                collection_name=arguments["collection_name"]
            )
        
        elif tool_name == "disable_collection_sync":
            return await sync_api.disable_collection_sync(
                collection_name=arguments["collection_name"]
            )
        
        elif tool_name == "delete_collection_vectors":
            return await sync_api.delete_collection_vectors(
                collection_name=arguments["collection_name"]
            )
        
        else:
            return {
                "success": False,
                "error": f"Unknown vector sync tool: {tool_name}"
            }
    
    except Exception as e:
        logger.error(f"Error handling vector sync tool '{tool_name}': {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }