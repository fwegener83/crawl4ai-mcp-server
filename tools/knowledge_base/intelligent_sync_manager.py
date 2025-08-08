"""
Intelligent Sync Manager for Vector Collection Synchronization

This module provides intelligent, user-triggered synchronization between file collections
and vector storage, with incremental processing and comprehensive error handling.
"""

import os
import asyncio
import logging
import time
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Set, Tuple, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

from .vector_sync_schemas import (
    VectorSyncStatus, ChunkMetadata, FileVectorMapping, SyncOperation,
    SyncConfiguration, SyncJobSpec, SyncResult, SyncStatus, SyncOperation as SyncOp,
    generate_chunk_id, generate_operation_id, calculate_file_hash,
    chunk_metadata_from_enhanced_chunk
)
from .enhanced_content_processor import EnhancedContentProcessor
from .vector_store import VectorStore
from .dependencies import is_rag_available
from ..collection_manager import CollectionFileManager

logger = logging.getLogger(__name__)


class IntelligentSyncManager:
    """
    Intelligent synchronization manager for vector collections.
    
    Features:
    - User-triggered collection-level sync
    - Intelligent incremental processing (only changed files)
    - Content hash comparison for change detection
    - Comprehensive error handling and retry logic
    - Progress tracking and status reporting
    - Background processing for large collections
    """
    
    def __init__(
        self,
        vector_store: VectorStore,
        collection_manager: CollectionFileManager,
        config: Optional[SyncConfiguration] = None
    ):
        """Initialize the sync manager.
        
        Args:
            vector_store: Vector storage instance
            collection_manager: File collection manager
            config: Sync configuration (uses defaults if None)
        """
        if not is_rag_available():
            raise ImportError("RAG dependencies required for vector sync")
        
        self.vector_store = vector_store
        self.collection_manager = collection_manager
        self.config = config or SyncConfiguration()
        
        # Content processor for intelligent chunking
        self.content_processor = EnhancedContentProcessor(
            chunking_strategy=self.config.chunking_strategy,
            enable_ab_testing=False  # Disable A/B testing for production sync
        )
        
        # State tracking
        self.sync_status: Dict[str, VectorSyncStatus] = {}
        self.file_mappings: Dict[str, Dict[str, FileVectorMapping]] = {}  # collection -> file_path -> mapping
        self.active_jobs: Dict[str, SyncJobSpec] = {}
        
        # Thread pool for concurrent processing
        self.executor = ThreadPoolExecutor(max_workers=self.config.max_concurrent_files)
        
        # Progress callbacks
        self.progress_callbacks: Dict[str, Callable] = {}
        
        logger.info(f"IntelligentSyncManager initialized with config: {self.config.model_dump()}")
    
    def get_collection_sync_status(self, collection_name: str) -> VectorSyncStatus:
        """Get current sync status for a collection."""
        if collection_name not in self.sync_status:
            # Initialize status for new collection
            self.sync_status[collection_name] = VectorSyncStatus(
                collection_name=collection_name,
                sync_enabled=self.config.enabled
            )
        
        return self.sync_status[collection_name]
    
    def list_collection_sync_statuses(self) -> Dict[str, VectorSyncStatus]:
        """Get sync status for all collections."""
        # Update with any collections we haven't seen yet
        try:
            collections = self.collection_manager.list_collections()
            for collection_info in collections:
                collection_name = collection_info.get('name', '')
                if collection_name and collection_name not in self.sync_status:
                    self.sync_status[collection_name] = VectorSyncStatus(
                        collection_name=collection_name,
                        sync_enabled=self.config.enabled
                    )
        except Exception as e:
            logger.warning(f"Could not list collections for status update: {e}")
        
        return self.sync_status.copy()
    
    async def sync_collection(
        self,
        collection_name: str,
        force_reprocess: bool = False,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> SyncResult:
        """
        Sync a collection with intelligent incremental processing.
        
        Args:
            collection_name: Name of collection to sync
            force_reprocess: If True, ignore file hashes and reprocess everything
            progress_callback: Optional callback for progress updates
            
        Returns:
            SyncResult with operation details
        """
        job_id = generate_operation_id(collection_name, SyncOp.UPDATE)
        
        logger.info(f"Starting sync for collection '{collection_name}' (job_id: {job_id})")
        
        # Initialize sync status
        sync_status = self.get_collection_sync_status(collection_name)
        sync_status.status = SyncStatus.SYNCING
        sync_status.last_sync_attempt = datetime.now(timezone.utc)
        sync_status.errors.clear()
        sync_status.warnings.clear()
        
        # Create sync result
        result = SyncResult(
            job_id=job_id,
            collection_name=collection_name,
            operation_type=SyncOp.UPDATE,
            success=False,
            started_at=datetime.now(timezone.utc)
        )
        
        try:
            # Check if collection exists
            if not self._collection_exists(collection_name):
                result.errors.append(f"Collection '{collection_name}' does not exist")
                return result
            
            # Get collection info and files
            collection_info = self.collection_manager.get_collection_info(collection_name)
            files_info = self._get_collection_files(collection_name)
            
            if not files_info:
                logger.warning(f"Collection '{collection_name}' has no files to sync")
                sync_status.status = SyncStatus.IN_SYNC
                result.success = True
                return result
            
            # Update sync status with file counts
            sync_status.total_files = len(files_info)
            
            # Determine which files need processing
            files_to_process = await self._identify_changed_files(
                collection_name, files_info, force_reprocess
            )
            
            if not files_to_process:
                logger.info(f"No files need processing in collection '{collection_name}'")
                sync_status.status = SyncStatus.IN_SYNC
                result.success = True
                return result
            
            logger.info(f"Processing {len(files_to_process)} files in collection '{collection_name}'")
            sync_status.changed_files_count = len(files_to_process)
            
            # Process files in batches
            total_chunks_created = 0
            total_chunks_updated = 0
            processed_files = 0
            
            for batch_start in range(0, len(files_to_process), self.config.batch_size):
                batch_end = min(batch_start + self.config.batch_size, len(files_to_process))
                batch_files = files_to_process[batch_start:batch_end]
                
                # Process batch
                batch_result = await self._process_file_batch(
                    collection_name, batch_files, progress_callback
                )
                
                total_chunks_created += batch_result['chunks_created']
                total_chunks_updated += batch_result['chunks_updated']
                processed_files += len(batch_files)
                
                # Update progress
                progress = processed_files / len(files_to_process)
                sync_status.sync_progress = progress
                
                if progress_callback:
                    progress_callback(progress, f"Processed {processed_files}/{len(files_to_process)} files")
                
                # Add any batch errors to result
                result.errors.extend(batch_result.get('errors', []))
                result.warnings.extend(batch_result.get('warnings', []))
            
            # Update final results
            result.files_processed = processed_files
            result.chunks_created = total_chunks_created
            result.chunks_updated = total_chunks_updated
            result.completed_at = datetime.now(timezone.utc)
            result.total_duration = (result.completed_at - result.started_at).total_seconds()
            
            # Update sync status
            sync_status.synced_files = sync_status.total_files
            sync_status.changed_files_count = 0
            sync_status.chunk_count = await self._count_collection_chunks(collection_name)
            sync_status.total_chunks = sync_status.chunk_count
            sync_status.last_sync = datetime.now(timezone.utc)
            sync_status.last_sync_duration = result.total_duration
            sync_status.sync_progress = 1.0
            
            # Determine final status
            if result.errors:
                sync_status.status = SyncStatus.SYNC_ERROR if len(result.errors) > len(files_to_process) * 0.5 else SyncStatus.PARTIAL_SYNC
                sync_status.errors = result.errors[-10:]  # Keep last 10 errors
            else:
                sync_status.status = SyncStatus.IN_SYNC
            
            result.success = sync_status.status in [SyncStatus.IN_SYNC, SyncStatus.PARTIAL_SYNC]
            
            if result.success:
                logger.info(f"Sync completed for collection '{collection_name}': "
                           f"{result.files_processed} files, {result.chunks_created} chunks created, "
                           f"{result.chunks_updated} chunks updated")
            else:
                logger.error(f"Sync failed for collection '{collection_name}': {len(result.errors)} errors")
            
        except Exception as e:
            logger.error(f"Sync failed for collection '{collection_name}': {str(e)}")
            result.errors.append(str(e))
            sync_status.status = SyncStatus.SYNC_ERROR
            sync_status.errors.append(str(e))
            
        finally:
            # Clean up progress tracking
            sync_status.sync_progress = None
            if progress_callback:
                progress_callback(1.0, "Sync completed" if result.success else "Sync failed")
        
        return result
    
    async def _identify_changed_files(
        self,
        collection_name: str,
        files_info: List[Dict[str, Any]],
        force_reprocess: bool
    ) -> List[Dict[str, Any]]:
        """Identify files that need processing based on content hash comparison."""
        if force_reprocess:
            logger.info(f"Force reprocess enabled - processing all {len(files_info)} files")
            # Still need to read content for all files even when force reprocessing
            changed_files = []
            for file_info in files_info:
                file_path = file_info.get('path', '')
                if not file_path:
                    continue
                    
                try:
                    # Read file content and calculate hash
                    read_result = self.collection_manager.read_file(
                        collection_name, file_info['name'], file_info.get('folder', '')
                    )
                    
                    if not read_result.get('success'):
                        logger.warning(f"Failed to read file {file_path}: {read_result.get('error', 'Unknown error')}")
                        continue
                    
                    content = read_result.get('content', '')
                    
                    if not content:
                        logger.warning(f"Empty content for file {file_path}")
                        continue
                    
                    current_hash = calculate_file_hash(content)
                    file_info['content'] = content
                    file_info['current_hash'] = current_hash
                    changed_files.append(file_info)
                    logger.debug(f"Force reprocess: {file_path}")
                    
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {str(e)}")
                    continue
            
            return changed_files
        
        # Get existing file mappings
        collection_mappings = self.file_mappings.get(collection_name, {})
        
        changed_files = []
        
        for file_info in files_info:
            file_path = file_info.get('path', '')
            if not file_path:
                continue
            
            try:
                # Read file content and calculate hash
                read_result = self.collection_manager.read_file(
                    collection_name, file_info['name'], file_info.get('folder', '')
                )
                
                if not read_result.get('success'):
                    logger.warning(f"Failed to read file {file_path}: {read_result.get('error', 'Unknown error')}")
                    continue
                
                content = read_result.get('content', '')
                
                if not content:
                    logger.warning(f"Empty content for file {file_path}")
                    continue
                
                current_hash = calculate_file_hash(content)
                
                # Check if file has changed
                existing_mapping = collection_mappings.get(file_path)
                if not existing_mapping or existing_mapping.file_hash != current_hash:
                    file_info['content'] = content
                    file_info['current_hash'] = current_hash
                    changed_files.append(file_info)
                    
                    if existing_mapping:
                        logger.debug(f"File changed: {file_path}")
                    else:
                        logger.debug(f"New file: {file_path}")
                
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {str(e)}")
                continue
        
        logger.info(f"Found {len(changed_files)} changed files out of {len(files_info)} total")
        return changed_files
    
    async def _process_file_batch(
        self,
        collection_name: str,
        files: List[Dict[str, Any]],
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Process a batch of files concurrently."""
        batch_result = {
            'chunks_created': 0,
            'chunks_updated': 0,
            'errors': [],
            'warnings': []
        }
        
        # Process files concurrently
        futures = []
        for file_info in files:
            future = self.executor.submit(self._process_single_file, collection_name, file_info)
            futures.append((future, file_info))
        
        # Collect results
        for future, file_info in futures:
            try:
                result = future.result(timeout=300)  # 5 minute timeout per file
                batch_result['chunks_created'] += result.get('chunks_created', 0)
                batch_result['chunks_updated'] += result.get('chunks_updated', 0)
                
                if result.get('errors'):
                    batch_result['errors'].extend(result['errors'])
                if result.get('warnings'):
                    batch_result['warnings'].extend(result['warnings'])
                    
            except Exception as e:
                error_msg = f"Failed to process file {file_info.get('path', 'unknown')}: {str(e)}"
                logger.error(error_msg)
                batch_result['errors'].append(error_msg)
        
        return batch_result
    
    def _process_single_file(self, collection_name: str, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single file and update vector store."""
        file_path = file_info.get('path', '')
        content = file_info.get('content', '')
        current_hash = file_info.get('current_hash', '')
        
        result = {
            'chunks_created': 0,
            'chunks_updated': 0,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Process content with enhanced processor
            chunks = self.content_processor.process_content(
                content,
                source_metadata={
                    'collection_name': collection_name,
                    'file_path': file_path,
                    'source_url': file_info.get('source_url'),
                    'file_hash': current_hash
                }
            )
            
            if not chunks:
                result['warnings'].append(f"No chunks generated for file {file_path}")
                return result
            
            # Convert chunks to vector format and store
            vector_chunks = []
            chunk_metadatas = []
            
            for chunk in chunks:
                # Generate chunk metadata
                chunk_meta = chunk_metadata_from_enhanced_chunk(
                    chunk, collection_name, file_path, current_hash
                )
                
                # Prepare for vector storage - serialize enums to strings for vector DB compatibility
                metadata_dict = chunk_meta.model_dump()
                
                # Convert all non-primitive values to compatible types for vector DB (ChromaDB)
                def serialize_for_vector_db(obj):
                    """Recursively convert non-primitive values to ChromaDB compatible types.
                    
                    ChromaDB only accepts: str, int, float, bool
                    ChromaDB REJECTS: None, empty lists [], complex objects
                    """
                    from datetime import datetime
                    
                    if isinstance(obj, dict):
                        # Clean dictionary - remove None values and empty lists
                        result = {}
                        for k, v in obj.items():
                            serialized_v = serialize_for_vector_db(v)
                            # Skip None values and empty lists - ChromaDB rejects them
                            if serialized_v is not None:
                                if isinstance(serialized_v, list) and len(serialized_v) == 0:
                                    # Skip empty lists entirely
                                    continue
                                else:
                                    result[k] = serialized_v
                        return result
                    elif isinstance(obj, list):
                        if len(obj) == 0:
                            # Return None for empty lists, will be filtered out by dict handling
                            return None
                        # ChromaDB does NOT accept lists at all - convert to string
                        # Process list items first, then join as string
                        processed_items = []
                        for item in obj:
                            processed_item = serialize_for_vector_db(item)
                            if processed_item is not None:
                                processed_items.append(str(processed_item))
                        # Join list elements into a single string
                        return " > ".join(processed_items) if processed_items else None
                    elif obj is None:
                        # Return None as-is, will be filtered out by dict handling
                        return None
                    elif hasattr(obj, 'value'):  # Enum object
                        return obj.value
                    elif isinstance(obj, datetime):  # DateTime objects
                        return obj.isoformat()
                    elif isinstance(obj, bool):  # Explicit bool handling
                        return obj
                    elif isinstance(obj, (str, int, float)):  # Primitive types
                        return obj
                    elif hasattr(obj, '__dict__'):  # Complex object, convert to string
                        return str(obj)
                    else:
                        return obj
                
                metadata_dict = serialize_for_vector_db(metadata_dict)
                
                vector_chunks.append({
                    'id': chunk['id'],
                    'content': chunk['content'],
                    'metadata': metadata_dict
                })
                chunk_metadatas.append(chunk_meta)
            
            # Remove old chunks for this file if they exist
            existing_mapping = self.file_mappings.get(collection_name, {}).get(file_path)
            if existing_mapping and existing_mapping.chunk_ids:
                try:
                    self.vector_store.delete_documents(existing_mapping.chunk_ids)
                    result['chunks_updated'] = len(existing_mapping.chunk_ids)
                except Exception as e:
                    logger.warning(f"Could not delete old chunks for {file_path}: {str(e)}")
            
            # Add new chunks to vector store
            print(f"DEBUG SYNC: About to store {len(vector_chunks)} chunks for collection '{collection_name}'")
            for i, chunk in enumerate(vector_chunks):
                print(f"DEBUG SYNC: Chunk {i} metadata: {chunk['metadata']}")
            
            self.vector_store.add_documents(
                [chunk['content'] for chunk in vector_chunks],
                metadatas=[chunk['metadata'] for chunk in vector_chunks],
                ids=[chunk['id'] for chunk in vector_chunks]
            )
            
            print(f"DEBUG SYNC: Successfully stored {len(vector_chunks)} chunks in ChromaDB")
            
            # IMMEDIATE TEST: Check if we can find what we just stored
            try:
                immediate_search = self.vector_store.similarity_search(
                    query="artificial intelligence",
                    k=10,
                    score_threshold=0.0,
                    filter={'collection_name': collection_name}
                )
                print(f"DEBUG SYNC: IMMEDIATE search for collection '{collection_name}' found {len(immediate_search)} results")
                for i, result in enumerate(immediate_search):
                    print(f"  -> Result {i}: {result.get('metadata', {}).get('collection_name')}")
            except Exception as e:
                print(f"DEBUG SYNC: IMMEDIATE search error: {e}")
            
            result['chunks_created'] = len(vector_chunks)
            
            # Update file mapping
            file_mapping = FileVectorMapping(
                collection_name=collection_name,
                file_path=file_path,
                file_hash=current_hash,
                chunk_ids=[chunk['id'] for chunk in vector_chunks],
                chunk_count=len(vector_chunks),
                last_synced=datetime.now(timezone.utc),
                sync_status=SyncStatus.IN_SYNC,
                processing_time=time.time(),  # Simple timing
                chunking_strategy=self.config.chunking_strategy
            )
            
            # Store mapping
            if collection_name not in self.file_mappings:
                self.file_mappings[collection_name] = {}
            self.file_mappings[collection_name][file_path] = file_mapping
            
            logger.debug(f"Processed file {file_path}: {len(vector_chunks)} chunks")
            
        except Exception as e:
            error_msg = f"Error processing file {file_path}: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
        
        return result
    
    def _collection_exists(self, collection_name: str) -> bool:
        """Check if collection exists."""
        try:
            result = self.collection_manager.get_collection_info(collection_name)
            return result.get('success', False)
        except Exception:
            return False
    
    def _get_collection_files(self, collection_name: str) -> List[Dict[str, Any]]:
        """Get list of files in collection."""
        try:
            result = self.collection_manager.list_files_in_collection(collection_name)
            if result.get('success'):
                return result.get('files', [])
            return []
        except Exception as e:
            logger.error(f"Error listing files for collection {collection_name}: {str(e)}")
            return []
    
    async def _count_collection_chunks(self, collection_name: str) -> int:
        """Count total chunks for a collection in vector store."""
        try:
            # Query vector store for collection chunks
            # This is a simplified implementation - actual implementation would depend on vector store capabilities
            collection_mappings = self.file_mappings.get(collection_name, {})
            return sum(mapping.chunk_count for mapping in collection_mappings.values())
        except Exception as e:
            logger.error(f"Error counting chunks for collection {collection_name}: {str(e)}")
            return 0
    
    def enable_collection_sync(self, collection_name: str) -> None:
        """Enable sync for a collection."""
        sync_status = self.get_collection_sync_status(collection_name)
        sync_status.sync_enabled = True
        logger.info(f"Sync enabled for collection '{collection_name}'")
    
    def disable_collection_sync(self, collection_name: str) -> None:
        """Disable sync for a collection."""
        sync_status = self.get_collection_sync_status(collection_name)
        sync_status.sync_enabled = False
        logger.info(f"Sync disabled for collection '{collection_name}'")
    
    async def delete_collection_vectors(self, collection_name: str) -> SyncResult:
        """Delete all vectors for a collection."""
        job_id = generate_operation_id(collection_name, SyncOp.DELETE)
        
        result = SyncResult(
            job_id=job_id,
            collection_name=collection_name,
            operation_type=SyncOp.DELETE,
            success=False,
            started_at=datetime.now(timezone.utc)
        )
        
        try:
            # Get all chunk IDs for this collection
            collection_mappings = self.file_mappings.get(collection_name, {})
            all_chunk_ids = []
            for mapping in collection_mappings.values():
                all_chunk_ids.extend(mapping.chunk_ids)
            
            if all_chunk_ids:
                # Delete from vector store
                self.vector_store.delete_documents(all_chunk_ids)
                result.chunks_deleted = len(all_chunk_ids)
                logger.info(f"Deleted {len(all_chunk_ids)} chunks for collection '{collection_name}'")
            
            # Clear mappings
            if collection_name in self.file_mappings:
                del self.file_mappings[collection_name]
            
            # Reset sync status
            if collection_name in self.sync_status:
                sync_status = self.sync_status[collection_name]
                sync_status.status = SyncStatus.NEVER_SYNCED
                sync_status.synced_files = 0
                sync_status.chunk_count = 0
                sync_status.total_chunks = 0
                sync_status.last_sync = None
            
            result.success = True
            result.completed_at = datetime.now(timezone.utc)
            
        except Exception as e:
            logger.error(f"Error deleting vectors for collection '{collection_name}': {str(e)}")
            result.errors.append(str(e))
        
        return result
    
    def get_sync_statistics(self) -> Dict[str, Any]:
        """Get overall sync statistics."""
        stats = {
            'total_collections': len(self.sync_status),
            'collections_in_sync': 0,
            'collections_out_of_sync': 0,
            'collections_never_synced': 0,
            'total_files': 0,
            'total_chunks': 0,
            'avg_sync_health': 0.0
        }
        
        health_scores = []
        
        for sync_status in self.sync_status.values():
            if sync_status.status == SyncStatus.IN_SYNC:
                stats['collections_in_sync'] += 1
            elif sync_status.status == SyncStatus.NEVER_SYNCED:
                stats['collections_never_synced'] += 1
            else:
                stats['collections_out_of_sync'] += 1
            
            stats['total_files'] += sync_status.total_files
            stats['total_chunks'] += sync_status.total_chunks
            health_scores.append(sync_status.sync_health_score)
        
        if health_scores:
            stats['avg_sync_health'] = sum(health_scores) / len(health_scores)
        
        return stats
    
    def shutdown(self):
        """Shutdown the sync manager and clean up resources."""
        logger.info("Shutting down IntelligentSyncManager")
        self.executor.shutdown(wait=True)