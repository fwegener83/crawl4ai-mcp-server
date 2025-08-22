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
# Import centralized configuration
from config.paths import Context42Config

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
        logger.info("Initializing VectorSyncService with ~/.context42/ configuration")
        
        # Ensure directory structure exists for vector operations
        Context42Config.ensure_directory_structure()
        Context42Config.migrate_legacy_data()
        
        self.vector_store = vector_store
        self.collection_service = collection_service
        self.vector_available = self._check_vector_availability()
        
        # Get centralized database path
        self.collections_db_path = str(Context42Config.get_collections_db_path())
        logger.info(f"Using collections database: {self.collections_db_path}")
        
        # Limited cache to prevent memory leaks - fixes unbounded cache issue
        from tools.knowledge_base.persistent_sync_manager import LimitedCache
        self._sync_manager_cache = LimitedCache(max_size=50)
    
    def _check_vector_availability(self) -> bool:
        """Check if vector dependencies are available."""
        try:
            from tools.knowledge_base.dependencies import is_rag_available
            return is_rag_available()
        except ImportError:
            logger.warning("Vector dependencies not available")
            return False
    
    async def sync_collection(self, collection_id: str, config: Optional[Dict[str, Any]] = None) -> VectorSyncStatus:
        """
        Synchronize a collection with the vector database.
        
        Args:
            collection_id: ID of the collection to sync
            config: Optional sync configuration
            
        Returns:
            VectorSyncStatus with sync results
        """
        if not self.vector_available:
            return VectorSyncStatus(
                collection_name=collection_id,
                is_enabled=False,
                sync_status="error",
                error_message="Vector dependencies not available"
            )
        
        try:
            logger.info(f"=== SYNC OPERATION: collection_id='{collection_id}' ====")
            print(f"DEBUG VECTOR_SERVICE: SYNC collection_id='{collection_id}' type={type(collection_id)}")
            
            # Import vector sync tools
            from tools.vector_sync_api import VectorSyncAPI
            from tools.knowledge_base.intelligent_sync_manager import IntelligentSyncManager
            from tools.knowledge_base.vector_store import VectorStore
            
            # Initialize components if not provided
            if not self.vector_store:
                # Use centralized vector database path
                vector_db_path = str(Context42Config.get_vector_db_path())
                self.vector_store = VectorStore(persist_directory=vector_db_path)
            
            # DEBUG: Log the VectorStore instance ID to verify it's shared
            logger.debug(f"VectorStore instance id: {id(self.vector_store)}")
            logger.debug(f"VectorStore DB path: {self.vector_store.persist_directory if hasattr(self.vector_store, 'persist_directory') else 'no persist_directory'}")
            
            # Use cached sync manager or create new one
            cache_key = f"sync_{collection_id}"
            sync_manager = self._sync_manager_cache.get(cache_key)
            if sync_manager is None:
                # Create database-only collection manager with centralized path
                from tools.knowledge_base.database_collection_adapter import DatabaseCollectionAdapter
                db_collection_manager = DatabaseCollectionAdapter(self.collections_db_path)
                
                sync_manager = IntelligentSyncManager(
                    vector_store=self.vector_store,
                    collection_manager=db_collection_manager,
                    persistent_db_path=self.collections_db_path  # Use centralized path
                )
                self._sync_manager_cache.set(cache_key, sync_manager)
            
            vector_sync_api = VectorSyncAPI(
                sync_manager=sync_manager,
                vector_store=self.vector_store,
                collection_manager=self.collection_service.collection_manager if self.collection_service else None
            )
            
            # Handle force vector deletion if requested
            force_delete_vectors = config.get("force_delete_vectors", False) if config else False
            if force_delete_vectors:
                logger.info(f"Force resync requested - deleting all vectors for collection '{collection_id}'")
                await self._delete_collection_vectors(collection_id, vector_sync_api.vector_store)
            
            # Prepare sync request
            from tools.vector_sync_api import SyncCollectionRequest
            sync_request = SyncCollectionRequest(
                force_reprocess=config.get("force_reprocess", False) if config else False,
                chunking_strategy=config.get("chunking_strategy") if config else None,
                force_delete_vectors=force_delete_vectors
            )
            
            # Perform sync operation
            logger.debug(f"Starting vector sync for collection '{collection_id}'")
            result = await vector_sync_api.sync_collection(collection_id, sync_request)
            logger.debug(f"Vector sync completed with result type: {type(result)}")
            
            # Handle both string and object responses
            if isinstance(result, str):
                import json
                result_data = json.loads(result)
            elif hasattr(result, 'model_dump'):
                result_data = result.model_dump()
            else:
                result_data = result
            
            logger.debug(f"Parsed result_data keys: {list(result_data.keys()) if isinstance(result_data, dict) else 'not a dict'}")
            if result_data.get("success", False):
                sync_data = result_data.get("sync_result", {})
                logger.debug(f"Extracted sync_data keys: {list(sync_data.keys()) if isinstance(sync_data, dict) else 'not a dict'}")
                return VectorSyncStatus(
                    collection_name=collection_id,
                    is_enabled=True,
                    last_sync=sync_data.get("completed_at", ""),
                    file_count=sync_data.get("files_processed", 0),
                    vector_count=sync_data.get("chunks_created", 0),  # Fixed: chunks_created not vectors_created
                    sync_status="in_sync"  # Fixed: should be 'in_sync' not 'completed'
                )
            else:
                return VectorSyncStatus(
                    collection_name=collection_id,
                    is_enabled=False,
                    sync_status="error",
                    error_message=result_data.get("error", "Sync failed")
                )
                
        except Exception as e:
            logger.error(f"Error syncing collection {collection_id}: {str(e)}")
            return VectorSyncStatus(
                collection_name=collection_id,
                is_enabled=False,
                sync_status="error",
                error_message=str(e)
            )
    
    async def get_sync_status(self, collection_id: str) -> VectorSyncStatus:
        """
        Get synchronization status for a collection.
        
        Args:
            collection_id: ID of the collection
            
        Returns:
            VectorSyncStatus with current status
        """
        if not self.vector_available:
            return VectorSyncStatus(
                collection_name=collection_id,
                is_enabled=False,
                sync_status="error",
                error_message="Vector dependencies not available"
            )
        
        try:
            logger.info(f"Getting sync status for collection: {collection_id}")
            
            # Import vector sync tools
            from tools.vector_sync_api import VectorSyncAPI
            from tools.knowledge_base.intelligent_sync_manager import IntelligentSyncManager
            from tools.knowledge_base.vector_store import VectorStore
            
            # Initialize components if not provided
            if not self.vector_store:
                self.vector_store = VectorStore()
            
            # Use cached sync manager or create new one - REUSE THE SAME INSTANCE!
            cache_key = f"sync_{collection_id}"
            sync_manager = self._sync_manager_cache.get(cache_key)
            if sync_manager is None:
                # Create database-only collection manager with centralized path
                from tools.knowledge_base.database_collection_adapter import DatabaseCollectionAdapter
                db_collection_manager = DatabaseCollectionAdapter(self.collections_db_path)
                
                sync_manager = IntelligentSyncManager(
                    vector_store=self.vector_store,
                    collection_manager=db_collection_manager,
                    persistent_db_path=self.collections_db_path  # Use centralized path
                )
                self._sync_manager_cache.set(cache_key, sync_manager)
            
            vector_sync_api = VectorSyncAPI(
                sync_manager=sync_manager,
                vector_store=self.vector_store,
                collection_manager=self.collection_service.collection_manager if self.collection_service else None
            )
            
            # Get sync status
            result = await vector_sync_api.get_collection_sync_status(collection_id)
            
            # Handle both string and object responses
            if isinstance(result, str):
                import json
                result_data = json.loads(result)
            elif hasattr(result, 'model_dump'):
                result_data = result.model_dump()
            else:
                result_data = result
            
            logger.debug(f"Get status result_data keys: {list(result_data.keys()) if isinstance(result_data, dict) else 'not a dict'}")
            if result_data.get("success", False):
                status_data = result_data.get("status", {})
                logger.debug(f"Extracted status_data keys: {list(status_data.keys()) if isinstance(status_data, dict) else 'not a dict'}")
                
                # Handle enum to string conversion for sync_status
                sync_status_value = status_data.get("status", "idle")
                if hasattr(sync_status_value, 'value'):
                    sync_status_value = sync_status_value.value
                # Do NOT map in_sync to completed - API expects 'in_sync'
                
                return VectorSyncStatus(
                    collection_name=collection_id,
                    is_enabled=status_data.get("sync_enabled", False),
                    last_sync=status_data.get("last_sync", ""),
                    file_count=status_data.get("total_files", 0),
                    vector_count=status_data.get("chunk_count", 0),
                    sync_status=sync_status_value
                )
            else:
                return VectorSyncStatus(
                    collection_name=collection_id,
                    is_enabled=False,
                    sync_status="error",
                    error_message=result_data.get("error", "Failed to get status")
                )
                
        except Exception as e:
            logger.error(f"Error getting sync status for {collection_id}: {str(e)}")
            return VectorSyncStatus(
                collection_name=collection_id,
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
                sync_manager = self._sync_manager_cache.get(cache_key)
                if sync_manager is None:
                    sync_manager = IntelligentSyncManager(
                        vector_store=self.vector_store,
                        collection_manager=self.collection_service.collection_manager if self.collection_service else None,
                        persistent_db_path=self.collections_db_path  # Use centralized path
                    )
                    self._sync_manager_cache.set(cache_key, sync_manager)
                
                # Get status for this specific collection
                status = await self.get_sync_status(collection.name)
                all_statuses.append(status)
            
            return all_statuses
            
        except Exception as e:
            logger.error(f"Error listing sync statuses: {str(e)}")
            return []
    
    async def search_vectors(
        self, 
        query: str, 
        collection_id: Optional[str] = None, 
        limit: int = 10, 
        similarity_threshold: float = 0.2,
        enable_context_expansion: bool = False,
        relationship_filter: Optional[Dict[str, Any]] = None
    ) -> List[VectorSearchResult]:
        """
        Search vectors using semantic similarity.
        
        Args:
            query: Search query text
            collection_id: Optional collection to search in
            limit: Maximum number of results
            
        Returns:
            List of VectorSearchResult objects
        """
        if not self.vector_available:
            logger.debug("Vector service not available, returning empty results")
            return []
        
        try:
            logger.info(f"=== SEARCH OPERATION: collection_id='{collection_id}' query='{query}' ===")
            print(f"DEBUG VECTOR_SERVICE: SEARCH collection_id='{collection_id}' type={type(collection_id)}")
            logger.debug(f"VectorSyncService.search_vectors called with query='{query}', collection='{collection_id}', limit={limit}")
            
            # Import vector sync tools
            from tools.vector_sync_api import VectorSyncAPI
            from tools.knowledge_base.intelligent_sync_manager import IntelligentSyncManager
            from tools.knowledge_base.vector_store import VectorStore
            
            # CRITICAL FIX: Reuse the SAME VectorStore instance that was used for sync
            # Initialize components if not provided, but ensure we use cached instances
            if not self.vector_store:
                self.vector_store = VectorStore()
            
            # DEBUG: Log the VectorStore instance ID to verify it's shared
            logger.debug(f"Search VectorStore instance id: {id(self.vector_store)}")
            logger.debug(f"Search VectorStore DB path: {getattr(self.vector_store, 'persist_directory', 'no persist_directory')}")
            
            # CRITICAL FIX: Use the EXACT SAME cache key pattern as sync operations
            # This ensures sync and search operations share the same ChromaDB connection
            if collection_id:
                # For specific collection searches, use the same key as sync operations
                cache_key = f"sync_{collection_id}"
                sync_manager = self._sync_manager_cache.get(cache_key)
                if sync_manager is None:
                    sync_manager = IntelligentSyncManager(
                        vector_store=self.vector_store,  # Use the SAME instance
                        collection_manager=self.collection_service.collection_manager if self.collection_service else None,
                        persistent_db_path=self.collections_db_path  # Use centralized path
                    )
                    self._sync_manager_cache.set(cache_key, sync_manager)
            else:
                # For global searches (no specific collection), create a dedicated global manager
                # but still use the same VectorStore instance
                cache_key = f"sync_global"
                sync_manager = self._sync_manager_cache.get(cache_key)
                if sync_manager is None:
                    sync_manager = IntelligentSyncManager(
                        vector_store=self.vector_store,  # Use the SAME instance
                        collection_manager=self.collection_service.collection_manager if self.collection_service else None,
                        persistent_db_path=self.collections_db_path  # Use centralized path
                    )
                    self._sync_manager_cache.set(cache_key, sync_manager)
            
            # Use the same vector_store instance for VectorSyncAPI
            vector_sync_api = VectorSyncAPI(
                sync_manager=sync_manager,
                vector_store=self.vector_store,  # Use the SAME instance
                collection_manager=self.collection_service.collection_manager if self.collection_service else None
            )
            
            # Prepare search request
            from tools.vector_sync_api import VectorSearchRequest
            search_request = VectorSearchRequest(
                query=query,
                collection_name=collection_id,
                limit=limit,
                similarity_threshold=similarity_threshold,
                enable_context_expansion=enable_context_expansion,
                relationship_filter=relationship_filter
            )
            
            # Perform vector search using the shared instance
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
                        score=result_item.get("similarity_score", result_item.get("score", 0.0)),  # Handle both field names
                        collection_name=result_item.get("collection_name", collection_id or ""),
                        file_path=result_item.get("source_file", result_item.get("file_path", ""))
                    )
                    search_results.append(search_result)
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error searching vectors with query '{query}': {str(e)}")
            return []
    
    async def delete_collection_vectors(self, collection_id: str) -> Dict[str, Any]:
        """
        Delete all vectors associated with a collection.
        
        Args:
            collection_id: ID of the collection
            
        Returns:
            Dictionary with deletion results including count
        """
        if not self.vector_available:
            return {
                "success": False,
                "error": "Vector dependencies not available",
                "deleted_count": 0
            }
        
        try:
            logger.info(f"Deleting vectors for collection: {collection_id}")
            
            # Import vector sync tools
            from tools.vector_sync_api import VectorSyncAPI
            from tools.knowledge_base.intelligent_sync_manager import IntelligentSyncManager
            from tools.knowledge_base.vector_store import VectorStore
            
            # Initialize components if not provided
            if not self.vector_store:
                self.vector_store = VectorStore()
            
            # Use cached sync manager or create new one
            cache_key = f"sync_{collection_id}"
            sync_manager = self._sync_manager_cache.get(cache_key)
            if sync_manager is None:
                # Create database-only collection manager with centralized path
                from tools.knowledge_base.database_collection_adapter import DatabaseCollectionAdapter
                db_collection_manager = DatabaseCollectionAdapter(self.collections_db_path)
                
                sync_manager = IntelligentSyncManager(
                    vector_store=self.vector_store,
                    collection_manager=db_collection_manager,
                    persistent_db_path=self.collections_db_path  # Use centralized path
                )
                self._sync_manager_cache.set(cache_key, sync_manager)
            
            vector_sync_api = VectorSyncAPI(
                sync_manager=sync_manager,
                vector_store=self.vector_store,
                collection_manager=self.collection_service.collection_manager if self.collection_service else None
            )
            
            # Delete vectors for collection
            result = await vector_sync_api.delete_collection_vectors(collection_id)
            
            # Handle both string and object responses
            if isinstance(result, str):
                import json
                result_data = json.loads(result)
            elif hasattr(result, 'model_dump'):
                result_data = result.model_dump()
            else:
                result_data = result
            
            if result_data.get("success", False):
                deleted_count = result_data.get("deleted_count", 0)
                # Clear the cached sync manager for this collection (no direct delete method in LimitedCache)
                # The cache will eventually evict old entries automatically
                
                return {
                    "success": True,
                    "deleted_count": deleted_count,
                    "message": f"Deleted {deleted_count} vectors for collection '{collection_id}'"
                }
            else:
                return {
                    "success": False,
                    "error": result_data.get("error", "Failed to delete vectors"),
                    "deleted_count": 0
                }
                
        except Exception as e:
            logger.error(f"Error deleting vectors for collection {collection_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "deleted_count": 0
            }
    
    async def _delete_collection_vectors(self, collection_id: str, vector_store=None):
        """
        Internal helper to delete all vectors for a collection.
        Used by force resync functionality.
        
        Args:
            collection_id: ID of the collection
            vector_store: Optional vector store instance
        """
        try:
            logger.info(f"Deleting all vectors for collection '{collection_id}'")
            
            # Use provided vector store or default
            if not vector_store and not self.vector_store:
                from tools.knowledge_base.vector_store import VectorStore
                # Use centralized vector database path
                vector_db_path = str(Context42Config.get_vector_db_path())
                vector_store = VectorStore(persist_directory=vector_db_path)
            else:
                vector_store = vector_store or self.vector_store
            
            # Try to delete collection from ChromaDB
            try:
                # Get or create collection client
                client = vector_store.get_chroma_client()
                
                # Delete collection if it exists
                try:
                    client.delete_collection(name=collection_id)
                    logger.info(f"Successfully deleted ChromaDB collection '{collection_id}'")
                except Exception as e:
                    if "does not exist" in str(e).lower():
                        logger.info(f"Collection '{collection_id}' doesn't exist in ChromaDB - nothing to delete")
                    else:
                        logger.warning(f"Error deleting ChromaDB collection '{collection_id}': {e}")
                        
            except Exception as e:
                logger.error(f"Error accessing ChromaDB for collection '{collection_id}': {e}")
                # Don't fail the entire operation if ChromaDB access fails
                
        except Exception as e:
            logger.error(f"Error in _delete_collection_vectors for '{collection_id}': {e}")
            # Don't raise exception - let sync continue even if vector deletion fails
    
    async def get_model_info(self) -> dict:
        """
        Get information about the current embedding model and configuration.
        
        Returns:
            Dict with model information including name, device, dimension, etc.
        """
        if not self.vector_available:
            return {
                "model_name": None,
                "device": None,
                "model_dimension": None,
                "error_message": "Vector dependencies not available"
            }
        
        try:
            # Create embedding service to get model information
            from tools.knowledge_base.embeddings import EmbeddingService
            
            try:
                embedding_service = EmbeddingService()
            except Exception as e:
                return {
                    "model_name": None,
                    "device": None,
                    "model_dimension": None,
                    "error_message": f"Could not initialize embedding service: {str(e)}"
                }
            
            # Get model information
            model_name = embedding_service.model_name
            device = embedding_service.device
            
            # Try to get model dimension
            model_dimension = None
            if embedding_service.model:
                try:
                    # Get dimension from the model's configuration or by encoding a test string
                    test_embedding = embedding_service.encode_text("test")
                    model_dimension = len(test_embedding) if test_embedding else None
                except Exception as e:
                    logger.warning(f"Could not determine model dimension: {e}")
                    model_dimension = None
            
            # Get additional model properties if available
            model_properties = {}
            if embedding_service.model:
                try:
                    # Try to get model max sequence length
                    if hasattr(embedding_service.model, 'max_seq_length'):
                        model_properties['max_sequence_length'] = embedding_service.model.max_seq_length
                    
                    # Try to get model name from the loaded model
                    if hasattr(embedding_service.model, 'model_name'):
                        model_properties['loaded_model_name'] = embedding_service.model.model_name
                        
                except Exception as e:
                    logger.debug(f"Could not get additional model properties: {e}")
            
            return {
                "model_name": model_name,
                "device": device,
                "model_dimension": model_dimension,
                "model_properties": model_properties,
                "error_message": None
            }
            
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {
                "model_name": None,
                "device": None,
                "model_dimension": None,
                "error_message": f"Error retrieving model information: {str(e)}"
            }