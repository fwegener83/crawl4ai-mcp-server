"""
Vector Sync Schemas and Data Models

This module defines the core data structures for the Vector Sync Infrastructure,
enabling intelligent synchronization between file collections and vector storage.
"""

import hashlib
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, field_validator
from dataclasses import dataclass


class SyncStatus(Enum):
    """Vector sync status enumeration."""
    NEVER_SYNCED = "never_synced"
    IN_SYNC = "in_sync"
    OUT_OF_SYNC = "out_of_sync"
    SYNCING = "syncing"
    SYNC_ERROR = "sync_error"
    PARTIAL_SYNC = "partial_sync"


class ChunkType(Enum):
    """Chunk type classification."""
    HEADER_SECTION = "header_section"
    CODE_BLOCK = "code_block"
    TABLE = "table"
    LIST = "list"
    ORDERED_LIST = "ordered_list"
    BLOCKQUOTE = "blockquote"
    PARAGRAPH = "paragraph"


class SyncOperation(Enum):
    """Type of sync operation."""
    ADD = "add"
    UPDATE = "update"
    DELETE = "delete"
    VERIFY = "verify"


class VectorSyncStatus(BaseModel):
    """Collection-level vector sync status."""
    collection_name: str = Field(..., description="Name of the collection")
    sync_enabled: bool = Field(default=True, description="Whether sync is enabled for this collection")
    status: SyncStatus = Field(default=SyncStatus.NEVER_SYNCED, description="Current sync status")
    last_sync: Optional[datetime] = Field(None, description="Timestamp of last successful sync")
    last_sync_attempt: Optional[datetime] = Field(None, description="Timestamp of last sync attempt")
    
    # File tracking
    total_files: int = Field(default=0, description="Total files in collection")
    synced_files: int = Field(default=0, description="Number of files successfully synced")
    changed_files_count: int = Field(default=0, description="Files changed since last sync")
    
    # Chunk tracking
    total_chunks: int = Field(default=0, description="Total chunks in vector store")
    chunk_count: int = Field(default=0, description="Current chunk count")
    
    # Progress and error tracking
    sync_progress: Optional[float] = Field(None, description="Current sync progress (0.0-1.0)")
    errors: List[str] = Field(default_factory=list, description="Recent sync errors")
    warnings: List[str] = Field(default_factory=list, description="Recent sync warnings")
    
    # Performance metrics
    last_sync_duration: Optional[float] = Field(None, description="Duration of last sync in seconds")
    avg_sync_duration: Optional[float] = Field(None, description="Average sync duration")
    
    @property
    def is_out_of_sync(self) -> bool:
        """Check if collection is out of sync."""
        return self.status in [SyncStatus.OUT_OF_SYNC, SyncStatus.SYNC_ERROR, SyncStatus.PARTIAL_SYNC]
    
    @property
    def sync_health_score(self) -> float:
        """Calculate sync health score (0.0-1.0)."""
        if self.status == SyncStatus.IN_SYNC:
            return 1.0
        elif self.status == SyncStatus.PARTIAL_SYNC:
            return 0.7
        elif self.status == SyncStatus.OUT_OF_SYNC:
            return 0.3
        elif self.status == SyncStatus.SYNC_ERROR:
            return 0.1
        else:  # NEVER_SYNCED or SYNCING
            return 0.5


class ChunkMetadata(BaseModel):
    """Enhanced metadata for vector chunks with file mapping."""
    # Source identification
    collection_name: str = Field(..., description="Source collection name")
    source_file: str = Field(..., description="Source file path within collection")
    file_hash: str = Field(..., description="Hash of source file content")
    
    # Chunk identification
    chunk_id: str = Field(..., description="Unique chunk identifier")
    chunk_index: int = Field(..., description="Index within source file")
    total_chunks: int = Field(..., description="Total chunks from source file")
    
    # Content classification
    chunk_type: ChunkType = Field(default=ChunkType.PARAGRAPH, description="Type of content chunk")
    header_hierarchy: List[str] = Field(default_factory=list, description="Header hierarchy path")
    
    # Code-specific metadata
    contains_code: bool = Field(default=False, description="Whether chunk contains code")
    programming_language: Optional[str] = Field(None, description="Detected programming language")
    
    # Content metrics
    word_count: int = Field(default=0, description="Word count in chunk")
    character_count: int = Field(default=0, description="Character count in chunk")
    
    # Sync tracking
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sync_version: int = Field(default=1, description="Version counter for sync tracking")
    
    # Quality metrics
    semantic_density: Optional[float] = Field(None, description="Semantic information density")
    embedding_quality_score: Optional[float] = Field(None, description="Embedding quality assessment")


class FileVectorMapping(BaseModel):
    """Mapping between files and their vector representations."""
    collection_name: str = Field(..., description="Collection containing the file")
    file_path: str = Field(..., description="Path to file within collection")
    file_hash: str = Field(..., description="Content hash of source file")
    
    # Vector metadata
    chunk_ids: List[str] = Field(default_factory=list, description="List of chunk IDs from this file")
    chunk_count: int = Field(default=0, description="Number of chunks generated")
    
    # Sync tracking
    last_synced: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sync_status: SyncStatus = Field(default=SyncStatus.NEVER_SYNCED)
    sync_error: Optional[str] = Field(None, description="Last sync error if any")
    
    # Processing metadata
    processing_time: Optional[float] = Field(None, description="Time taken to process file")
    chunking_strategy: Optional[str] = Field(None, description="Strategy used for chunking")
    
    @field_validator('file_hash')
    @classmethod
    def validate_file_hash(cls, v):
        """Validate file hash format."""
        if v and len(v) != 32:  # MD5 hash length
            raise ValueError("File hash must be MD5 format (32 characters)")
        return v


class SyncOperationRecord(BaseModel):
    """Individual sync operation record."""
    operation_id: str = Field(..., description="Unique operation identifier")
    collection_name: str = Field(..., description="Target collection")
    operation_type: SyncOperation = Field(..., description="Type of sync operation")
    
    # Target identification
    file_path: Optional[str] = Field(None, description="Target file path")
    chunk_ids: List[str] = Field(default_factory=list, description="Affected chunk IDs")
    
    # Operation details
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    duration: Optional[float] = Field(None, description="Operation duration in seconds")
    
    # Result tracking
    success: Optional[bool] = Field(None, description="Operation success status")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    chunks_processed: int = Field(default=0, description="Number of chunks processed")
    
    # Performance metrics
    processing_rate: Optional[float] = Field(None, description="Chunks processed per second")
    memory_usage: Optional[int] = Field(None, description="Peak memory usage in bytes")


class SyncConfiguration(BaseModel):
    """Configuration for vector sync operations."""
    # Sync behavior
    enabled: bool = Field(default=True, description="Whether sync is enabled")
    auto_sync: bool = Field(default=False, description="Enable automatic sync on file changes")
    batch_size: int = Field(default=50, description="Number of chunks to process in batch")
    
    # Performance tuning
    max_concurrent_files: int = Field(default=5, description="Max files to process concurrently")
    chunk_cache_size: int = Field(default=1000, description="Number of chunks to cache")
    embedding_batch_size: int = Field(default=32, description="Batch size for embedding generation")
    
    # Quality control
    min_chunk_size: int = Field(default=50, description="Minimum chunk size in characters")
    max_chunk_size: int = Field(default=2000, description="Maximum chunk size in characters")
    chunking_strategy: str = Field(default="auto", description="Chunking strategy to use")
    
    # Error handling
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_delay: float = Field(default=1.0, description="Delay between retries in seconds")
    error_threshold: float = Field(default=0.1, description="Error rate threshold (0.0-1.0)")
    
    # Monitoring
    enable_metrics: bool = Field(default=True, description="Enable performance metrics collection")
    log_level: str = Field(default="INFO", description="Logging level for sync operations")


@dataclass
class SyncJobSpec:
    """Specification for a sync job."""
    collection_name: str
    operation_type: SyncOperation
    file_paths: Optional[List[str]] = None  # None means all files
    priority: int = 1  # Higher numbers = higher priority
    
    # Configuration overrides
    batch_size: Optional[int] = None
    chunking_strategy: Optional[str] = None
    force_reprocess: bool = False  # Ignore file hashes and reprocess everything
    
    # Callback information
    progress_callback: Optional[str] = None  # Callback URL for progress updates
    completion_callback: Optional[str] = None  # Callback URL for completion


@dataclass
class SyncResult:
    """Result of a sync operation."""
    job_id: str
    collection_name: str
    operation_type: SyncOperation
    
    # Status
    success: bool
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    # Statistics
    files_processed: int = 0
    chunks_created: int = 0
    chunks_updated: int = 0
    chunks_deleted: int = 0
    
    # Performance
    total_duration: Optional[float] = None
    average_file_time: Optional[float] = None
    chunks_per_second: Optional[float] = None
    
    # Quality metrics
    chunking_quality_score: Optional[float] = None
    embedding_quality_score: Optional[float] = None
    
    # Errors and warnings
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
    
    @property
    def health_score(self) -> float:
        """Overall health score for the sync operation."""
        if not self.success:
            return 0.0
        
        score = 1.0
        
        # Deduct for errors
        if self.errors:
            score -= len(self.errors) * 0.1
        
        # Deduct for warnings
        if self.warnings:
            score -= len(self.warnings) * 0.05
        
        # Factor in quality scores
        if self.chunking_quality_score:
            score = (score + self.chunking_quality_score) / 2
        
        return max(0.0, min(1.0, score))


def generate_chunk_id(collection_name: str, file_path: str, chunk_index: int, content_hash: str) -> str:
    """Generate a unique chunk ID."""
    id_string = f"{collection_name}:{file_path}:{chunk_index}:{content_hash}"
    return hashlib.md5(id_string.encode('utf-8')).hexdigest()


def generate_operation_id(collection_name: str, operation_type: SyncOperation) -> str:
    """Generate a unique operation ID."""
    timestamp = datetime.now(timezone.utc).isoformat()
    id_string = f"{collection_name}:{operation_type.value}:{timestamp}"
    return hashlib.md5(id_string.encode('utf-8')).hexdigest()[:16]


def calculate_file_hash(content: str) -> str:
    """Calculate MD5 hash of file content."""
    return hashlib.md5(content.encode('utf-8')).hexdigest()


# Utility functions for schema validation and conversion
def validate_sync_configuration(config: Dict[str, Any]) -> SyncConfiguration:
    """Validate and create sync configuration from dict."""
    return SyncConfiguration(**config)


def chunk_metadata_from_enhanced_chunk(
    chunk: Dict[str, Any], 
    collection_name: str, 
    file_path: str, 
    file_hash: str
) -> ChunkMetadata:
    """Convert enhanced chunk to ChunkMetadata."""
    metadata = chunk.get('metadata', {})
    
    return ChunkMetadata(
        collection_name=collection_name,
        source_file=file_path,
        file_hash=file_hash,
        chunk_id=chunk.get('id', ''),
        chunk_index=metadata.get('chunk_index', 0),
        total_chunks=metadata.get('total_chunks', 1),
        chunk_type=ChunkType(metadata.get('chunk_type', 'paragraph')),
        header_hierarchy=metadata.get('header_hierarchy', []),
        contains_code=metadata.get('contains_code', False),
        programming_language=metadata.get('programming_language'),
        word_count=metadata.get('word_count', 0),
        character_count=metadata.get('character_count', len(chunk.get('content', ''))),
        created_at=datetime.fromisoformat(metadata.get('created_at', datetime.now(timezone.utc).isoformat())),
        last_updated=datetime.now(timezone.utc),
        sync_version=1
    )