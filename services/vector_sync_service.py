"""
Vector synchronization service implementation.

Implements IVectorSyncService interface with actual vector operations
extracted from existing vector sync tools. This service is protocol-agnostic
and focuses purely on vector synchronization business logic.

This service is optional and only operates when vector dependencies are available.
"""
import logging
from typing import Dict, Any, List, Optional
from .interfaces import IVectorSyncService, VectorSyncStatus, VectorSearchResult

logger = logging.getLogger(__name__)


class VectorSyncService(IVectorSyncService):
    """
    Implementation of vector synchronization service.
    
    Delegates to existing vector sync tools while providing a clean,
    protocol-agnostic interface for business logic. This service is
    optional and gracefully handles cases where vector dependencies
    are not available.
    """
    
    def __init__(self, vector_store=None, collection_service=None):
        """
        Initialize the vector sync service.
        
        Args:
            vector_store: Optional vector store instance
            collection_service: Optional collection service for file operations
        """
        logger.info("Initializing VectorSyncService")
        self.vector_store = vector_store
        self.collection_service = collection_service
        self.vector_available = self._check_vector_availability()
        # Cache sync managers to maintain status between calls
        self._sync_manager_cache = {}
    
    def _check_vector_availability(self) -> bool:
        """Check if vector dependencies are available."""
        try:
            from tools.knowledge_base.dependencies import is_rag_available
            return is_rag_available()
        except ImportError:
            logger.warning("Vector dependencies not available")
            return False
    
    async def sync_collection(self, collection_name: str, config: Optional[Dict[str, Any]] = None) -> VectorSyncStatus:
        """
        Synchronize a collection with the vector database.
        
        Args:
            collection_name: Name of the collection to sync
            config: Optional sync configuration
            
        Returns:
            VectorSyncStatus with sync results
        """
        if not self.vector_available:
            return VectorSyncStatus(
                collection_name=collection_name,
                is_enabled=False,
                sync_status="error",
                error_message="Vector dependencies not available"
            )
        
        try:
            logger.info(f"Syncing collection to vectors: {collection_name}")
            
            # Import vector sync tools
            from tools.vector_sync_api import VectorSyncAPI
            from tools.knowledge_base.intelligent_sync_manager import IntelligentSyncManager
            from tools.knowledge_base.vector_store import VectorStore
            
            # Initialize components if not provided
            if not self.vector_store:
                self.vector_store = VectorStore()
            
            # Use cached sync manager or create new one
            cache_key = f"sync_{collection_name}"
            if cache_key not in self._sync_manager_cache:
                self._sync_manager_cache[cache_key] = IntelligentSyncManager(
                    vector_store=self.vector_store,
                    collection_manager=self.collection_service.collection_manager if self.collection_service else None
                )
            sync_manager = self._sync_manager_cache[cache_key]
            
            vector_sync_api = VectorSyncAPI(
                sync_manager=sync_manager,
                vector_store=self.vector_store,
                collection_manager=self.collection_service.collection_manager if self.collection_service else None
            )
            
            # Prepare sync request
            from tools.vector_sync_api import SyncCollectionRequest
            sync_request = SyncCollectionRequest(
                force_reprocess=config.get("force_reprocess", False) if config else False,
                chunking_strategy=config.get("chunking_strategy") if config else None
            )
            
            # Perform sync operation
            result = await vector_sync_api.sync_collection(collection_name, sync_request)
            
            # Handle both string and object responses
            if isinstance(result, str):
                import json
                result_data = json.loads(result)
            elif hasattr(result, 'model_dump'):
                result_data = result.model_dump()
            else:
                result_data = result
            
            if result_data.get("success", False):
                sync_data = result_data.get("sync_result", {})
                return VectorSyncStatus(
                    collection_name=collection_name,
                    is_enabled=True,
                    last_sync=sync_data.get("completed_at", ""),
                    file_count=sync_data.get("files_processed", 0),
                    vector_count=sync_data.get("chunks_created", 0),  # Fixed: chunks_created not vectors_created
                    sync_status="completed"
                )
            else:
                return VectorSyncStatus(
                    collection_name=collection_name,
                    is_enabled=False,
                    sync_status="error",
                    error_message=result_data.get("error", "Sync failed")
                )
                
        except Exception as e:
            logger.error(f"Error syncing collection {collection_name}: {str(e)}")
            return VectorSyncStatus(
                collection_name=collection_name,
                is_enabled=False,
                sync_status="error",
                error_message=str(e)
            )
    
    async def get_sync_status(self, collection_name: str) -> VectorSyncStatus:
        """
        Get synchronization status for a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            VectorSyncStatus with current status
        """
        if not self.vector_available:
            return VectorSyncStatus(
                collection_name=collection_name,
                is_enabled=False,
                sync_status="error",
                error_message="Vector dependencies not available"
            )
        
        try:
            logger.info(f"Getting sync status for collection: {collection_name}")
            
            # Import vector sync tools
            from tools.vector_sync_api import VectorSyncAPI
            from tools.knowledge_base.intelligent_sync_manager import IntelligentSyncManager
            from tools.knowledge_base.vector_store import VectorStore
            
            # Initialize components if not provided
            if not self.vector_store:
                self.vector_store = VectorStore()
            
            # Use cached sync manager or create new one - REUSE THE SAME INSTANCE!
            cache_key = f"sync_{collection_name}"
            if cache_key not in self._sync_manager_cache:
                self._sync_manager_cache[cache_key] = IntelligentSyncManager(
                    vector_store=self.vector_store,
                    collection_manager=self.collection_service.collection_manager if self.collection_service else None
                )
            sync_manager = self._sync_manager_cache[cache_key]
            
            vector_sync_api = VectorSyncAPI(
                sync_manager=sync_manager,
                vector_store=self.vector_store,
                collection_manager=self.collection_service.collection_manager if self.collection_service else None
            )
            
            # Get sync status
            result = await vector_sync_api.get_collection_sync_status(collection_name)
            
            # Handle both string and object responses
            if isinstance(result, str):
                import json
                result_data = json.loads(result)
            elif hasattr(result, 'model_dump'):
                result_data = result.model_dump()
            else:
                result_data = result
            
            if result_data.get("success", False):
                status_data = result_data.get("status", {})
                return VectorSyncStatus(
                    collection_name=collection_name,
                    is_enabled=status_data.get("sync_enabled", False),
                    last_sync=status_data.get("last_sync", ""),
                    file_count=status_data.get("total_files", 0),
                    vector_count=status_data.get("chunk_count", 0),
                    sync_status=status_data.get("status", "idle")
                )
            else:
                return VectorSyncStatus(
                    collection_name=collection_name,
                    is_enabled=False,
                    sync_status="error",
                    error_message=result_data.get("error", "Failed to get status")
                )
                
        except Exception as e:
            logger.error(f"Error getting sync status for {collection_name}: {str(e)}")
            return VectorSyncStatus(
                collection_name=collection_name,
                is_enabled=False,
                sync_status="error",
                error_message=str(e)
            )
    
    async def list_sync_statuses(self) -> List[VectorSyncStatus]:
        """
        List synchronization statuses for all collections.
        
        Returns:
            List of VectorSyncStatus objects
        """
        if not self.vector_available:
            return []
        
        try:
            logger.info("Listing all sync statuses")
            
            # Import vector sync tools
            from tools.vector_sync_api import VectorSyncAPI
            from tools.knowledge_base.intelligent_sync_manager import IntelligentSyncManager
            from tools.knowledge_base.vector_store import VectorStore
            
            # Initialize components if not provided
            if not self.vector_store:
                self.vector_store = VectorStore()
            
            # Get all collections first to ensure cache entries exist
            collections = await self.collection_service.list_collections()
            all_statuses = []
            
            # For each collection, get or create cached sync manager
            for collection in collections:
                cache_key = f"sync_{collection.name}"
                if cache_key not in self._sync_manager_cache:
                    self._sync_manager_cache[cache_key] = IntelligentSyncManager(
                        vector_store=self.vector_store,
                        collection_manager=self.collection_service.collection_manager if self.collection_service else None
                    )
                
                # Get status for this specific collection
                status = await self.get_sync_status(collection.name)
                all_statuses.append(status)
            
            return all_statuses
            
        except Exception as e:
            logger.error(f"Error listing sync statuses: {str(e)}")
            return []
    
    async def enable_sync(self, collection_name: str) -> VectorSyncStatus:
        """
        Enable vector synchronization for a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            VectorSyncStatus after enabling sync
        """
        if not self.vector_available:
            return VectorSyncStatus(
                collection_name=collection_name,
                is_enabled=False,
                sync_status="error",
                error_message="Vector dependencies not available"
            )
        
        try:
            logger.info(f"Enabling sync for collection: {collection_name}")
            
            # Import vector sync tools
            from tools.vector_sync_api import VectorSyncAPI
            from tools.knowledge_base.intelligent_sync_manager import IntelligentSyncManager
            from tools.knowledge_base.vector_store import VectorStore
            
            # Initialize components if not provided
            if not self.vector_store:
                self.vector_store = VectorStore()
            
            sync_manager = IntelligentSyncManager(
                vector_store=self.vector_store,
                collection_manager=self.collection_service.collection_manager if self.collection_service else None
            )
            
            vector_sync_api = VectorSyncAPI(
                sync_manager=sync_manager,
                vector_store=self.vector_store,
                collection_manager=self.collection_service.collection_manager if self.collection_service else None
            )
            
            # Enable sync
            result = await vector_sync_api.enable_collection_sync(collection_name)
            
            # Parse JSON result if it's a string
            if isinstance(result, str):
                import json
                result = json.loads(result)
            
            if result.get("success", False):
                return VectorSyncStatus(
                    collection_name=collection_name,
                    is_enabled=True,
                    sync_status="enabled"
                )
            else:
                return VectorSyncStatus(
                    collection_name=collection_name,
                    is_enabled=False,
                    sync_status="error",
                    error_message=result.get("error", "Failed to enable sync")
                )
                
        except Exception as e:
            logger.error(f"Error enabling sync for {collection_name}: {str(e)}")
            return VectorSyncStatus(
                collection_name=collection_name,
                is_enabled=False,
                sync_status="error",
                error_message=str(e)
            )
    
    async def disable_sync(self, collection_name: str) -> VectorSyncStatus:
        """
        Disable vector synchronization for a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            VectorSyncStatus after disabling sync
        """
        if not self.vector_available:
            return VectorSyncStatus(
                collection_name=collection_name,
                is_enabled=False,
                sync_status="error",
                error_message="Vector dependencies not available"
            )
        
        try:
            logger.info(f"Disabling sync for collection: {collection_name}")
            
            # Import vector sync tools
            from tools.vector_sync_api import VectorSyncAPI
            from tools.knowledge_base.intelligent_sync_manager import IntelligentSyncManager
            from tools.knowledge_base.vector_store import VectorStore
            
            # Initialize components if not provided
            if not self.vector_store:
                self.vector_store = VectorStore()
            
            sync_manager = IntelligentSyncManager(
                vector_store=self.vector_store,
                collection_manager=self.collection_service.collection_manager if self.collection_service else None
            )
            
            vector_sync_api = VectorSyncAPI(
                sync_manager=sync_manager,
                vector_store=self.vector_store,
                collection_manager=self.collection_service.collection_manager if self.collection_service else None
            )
            
            # Disable sync
            result = await vector_sync_api.disable_collection_sync(collection_name)
            
            # Parse JSON result if it's a string
            if isinstance(result, str):
                import json
                result = json.loads(result)
            
            if result.get("success", False):
                return VectorSyncStatus(
                    collection_name=collection_name,
                    is_enabled=False,
                    sync_status="disabled"
                )
            else:
                return VectorSyncStatus(
                    collection_name=collection_name,
                    is_enabled=False,
                    sync_status="error",
                    error_message=result.get("error", "Failed to disable sync")
                )
                
        except Exception as e:
            logger.error(f"Error disabling sync for {collection_name}: {str(e)}")
            return VectorSyncStatus(
                collection_name=collection_name,
                is_enabled=False,
                sync_status="error",
                error_message=str(e)
            )
    
    async def delete_vectors(self, collection_name: str) -> Dict[str, Any]:
        """
        Delete all vectors for a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Status information about the deletion
        """
        if not self.vector_available:
            return {
                "success": False,
                "error": "Vector dependencies not available"
            }
        
        try:
            logger.info(f"Deleting vectors for collection: {collection_name}")
            
            # Import vector sync tools
            from tools.vector_sync_api import VectorSyncAPI
            from tools.knowledge_base.intelligent_sync_manager import IntelligentSyncManager
            from tools.knowledge_base.vector_store import VectorStore
            
            # Initialize components if not provided
            if not self.vector_store:
                self.vector_store = VectorStore()
            
            sync_manager = IntelligentSyncManager(
                vector_store=self.vector_store,
                collection_manager=self.collection_service.collection_manager if self.collection_service else None
            )
            
            vector_sync_api = VectorSyncAPI(
                sync_manager=sync_manager,
                vector_store=self.vector_store,
                collection_manager=self.collection_service.collection_manager if self.collection_service else None
            )
            
            # Delete vectors
            result = await vector_sync_api.delete_collection_vectors(collection_name)
            
            # Parse JSON result if it's a string
            if isinstance(result, str):
                import json
                result = json.loads(result)
            
            if result.get("success", False):
                return {
                    "success": True,
                    "message": f"Vectors deleted for collection {collection_name}",
                    "deleted_count": result.get("deleted_count", 0)
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Failed to delete vectors")
                }
                
        except Exception as e:
            logger.error(f"Error deleting vectors for {collection_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def search_vectors(self, query: str, collection_name: Optional[str] = None, limit: int = 10) -> List[VectorSearchResult]:
        """
        Search vectors using semantic similarity.
        
        Args:
            query: Search query text
            collection_name: Optional collection to search in
            limit: Maximum number of results
            
        Returns:
            List of VectorSearchResult objects
        """
        if not self.vector_available:
            return []
        
        try:
            logger.info(f"Searching vectors with query: {query}")
            
            # Import vector sync tools
            from tools.vector_sync_api import VectorSyncAPI
            from tools.knowledge_base.intelligent_sync_manager import IntelligentSyncManager
            from tools.knowledge_base.vector_store import VectorStore
            
            # Initialize components if not provided
            if not self.vector_store:
                self.vector_store = VectorStore()
            
            sync_manager = IntelligentSyncManager(
                vector_store=self.vector_store,
                collection_manager=self.collection_service.collection_manager if self.collection_service else None
            )
            
            vector_sync_api = VectorSyncAPI(
                sync_manager=sync_manager,
                vector_store=self.vector_store,
                collection_manager=self.collection_service.collection_manager if self.collection_service else None
            )
            
            # Prepare search request
            from tools.vector_sync_api import VectorSearchRequest
            search_request = VectorSearchRequest(
                query=query,
                collection_name=collection_name,
                limit=limit
            )
            
            # Perform vector search
            result = await vector_sync_api.search_vectors(search_request)
            
            # Handle both string and object responses
            if isinstance(result, str):
                import json
                result_data = json.loads(result)
            elif hasattr(result, 'model_dump'):
                result_data = result.model_dump()
            else:
                result_data = result
            
            search_results = []
            if result_data.get("success", False):
                results_data = result_data.get("results", [])
                for result_item in results_data:
                    search_result = VectorSearchResult(
                        content=result_item.get("content", ""),
                        metadata=result_item.get("metadata", {}),
                        score=result_item.get("score", 0.0),
                        collection_name=result_item.get("collection_name", collection_name or ""),
                        file_path=result_item.get("source_file", result_item.get("file_path", ""))
                    )
                    search_results.append(search_result)
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error searching vectors with query '{query}': {str(e)}")
            return []