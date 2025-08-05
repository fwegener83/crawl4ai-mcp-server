"""
Unit tests for Vector Sync Schemas and Data Models.

Tests all data structures, validation, and utility functions
for the vector sync infrastructure.
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import patch

from tools.knowledge_base.vector_sync_schemas import (
    VectorSyncStatus, ChunkMetadata, FileVectorMapping, SyncConfiguration,
    SyncJobSpec, SyncResult, SyncStatus, ChunkType, SyncOperation,
    generate_chunk_id, generate_operation_id, calculate_file_hash,
    chunk_metadata_from_enhanced_chunk, validate_sync_configuration
)


class TestEnumTypes:
    """Test enum types for vector sync."""
    
    def test_sync_status_enum(self):
        """Test SyncStatus enum values."""
        assert SyncStatus.NEVER_SYNCED.value == "never_synced"
        assert SyncStatus.IN_SYNC.value == "in_sync"
        assert SyncStatus.OUT_OF_SYNC.value == "out_of_sync"
        assert SyncStatus.SYNCING.value == "syncing"
        assert SyncStatus.SYNC_ERROR.value == "sync_error"
        assert SyncStatus.PARTIAL_SYNC.value == "partial_sync"
    
    def test_chunk_type_enum(self):
        """Test ChunkType enum values."""
        assert ChunkType.HEADER_SECTION.value == "header_section"
        assert ChunkType.CODE_BLOCK.value == "code_block"
        assert ChunkType.TABLE.value == "table"
        assert ChunkType.LIST.value == "list"
        assert ChunkType.PARAGRAPH.value == "paragraph"
    
    def test_sync_operation_enum(self):
        """Test SyncOperation enum values."""
        assert SyncOperation.ADD.value == "add"
        assert SyncOperation.UPDATE.value == "update"
        assert SyncOperation.DELETE.value == "delete"
        assert SyncOperation.VERIFY.value == "verify"


class TestVectorSyncStatus:
    """Test VectorSyncStatus model."""
    
    def test_basic_creation(self):
        """Test basic VectorSyncStatus creation."""
        status = VectorSyncStatus(collection_name="test_collection")
        
        assert status.collection_name == "test_collection"
        assert status.sync_enabled is True
        assert status.status == SyncStatus.NEVER_SYNCED
        assert status.total_files == 0
        assert status.synced_files == 0
        assert status.chunk_count == 0
        assert status.errors == []
        assert status.warnings == []
    
    def test_creation_with_all_fields(self):
        """Test VectorSyncStatus creation with all fields."""
        now = datetime.now(timezone.utc)
        
        status = VectorSyncStatus(
            collection_name="full_test_collection",
            sync_enabled=False,
            status=SyncStatus.IN_SYNC,
            last_sync=now,
            last_sync_attempt=now,
            total_files=10,
            synced_files=8,
            changed_files_count=2,
            total_chunks=50,
            chunk_count=45,
            sync_progress=0.8,
            errors=["Test error"],
            warnings=["Test warning"],
            last_sync_duration=120.5,
            avg_sync_duration=100.0
        )
        
        assert status.collection_name == "full_test_collection"
        assert status.sync_enabled is False
        assert status.status == SyncStatus.IN_SYNC
        assert status.total_files == 10
        assert status.synced_files == 8
        assert status.changed_files_count == 2
        assert status.chunk_count == 45
        assert status.sync_progress == 0.8
        assert len(status.errors) == 1
        assert len(status.warnings) == 1
    
    def test_is_out_of_sync_property(self):
        """Test is_out_of_sync property logic."""
        status = VectorSyncStatus(collection_name="test")
        
        # Test statuses that are NOT out of sync
        status.status = SyncStatus.NEVER_SYNCED
        assert status.is_out_of_sync is False
        
        status.status = SyncStatus.IN_SYNC
        assert status.is_out_of_sync is False
        
        status.status = SyncStatus.SYNCING
        assert status.is_out_of_sync is False
        
        # Test statuses that ARE out of sync
        status.status = SyncStatus.OUT_OF_SYNC
        assert status.is_out_of_sync is True
        
        status.status = SyncStatus.SYNC_ERROR
        assert status.is_out_of_sync is True
        
        status.status = SyncStatus.PARTIAL_SYNC
        assert status.is_out_of_sync is True
    
    def test_sync_health_score_property(self):
        """Test sync_health_score property calculation."""
        status = VectorSyncStatus(collection_name="test")
        
        # Test different status scores
        status.status = SyncStatus.IN_SYNC
        assert status.sync_health_score == 1.0
        
        status.status = SyncStatus.PARTIAL_SYNC
        assert status.sync_health_score == 0.7
        
        status.status = SyncStatus.OUT_OF_SYNC
        assert status.sync_health_score == 0.3
        
        status.status = SyncStatus.SYNC_ERROR
        assert status.sync_health_score == 0.1
        
        status.status = SyncStatus.NEVER_SYNCED
        assert status.sync_health_score == 0.5
        
        status.status = SyncStatus.SYNCING
        assert status.sync_health_score == 0.5


class TestChunkMetadata:
    """Test ChunkMetadata model."""
    
    def test_basic_creation(self):
        """Test basic ChunkMetadata creation."""
        metadata = ChunkMetadata(
            collection_name="test_collection",
            source_file="test.md",
            file_hash="d41d8cd98f00b204e9800998ecf8427e",  # Valid MD5 hash
            chunk_id="chunk_001",
            chunk_index=0,
            total_chunks=5
        )
        
        assert metadata.collection_name == "test_collection"
        assert metadata.source_file == "test.md"
        assert metadata.file_hash == "d41d8cd98f00b204e9800998ecf8427e"
        assert metadata.chunk_id == "chunk_001"
        assert metadata.chunk_index == 0
        assert metadata.total_chunks == 5
        assert metadata.chunk_type == ChunkType.PARAGRAPH
        assert metadata.header_hierarchy == []
        assert metadata.contains_code is False
        assert metadata.word_count == 0
        assert metadata.sync_version == 1
    
    def test_creation_with_code_metadata(self):
        """Test ChunkMetadata creation with code-specific fields."""
        metadata = ChunkMetadata(
            collection_name="code_collection",
            source_file="script.py",
            file_hash="5d41402abc4b2a76b9719d911017c592",  # Valid MD5 hash
            chunk_id="code_chunk_001",
            chunk_index=2,
            total_chunks=10,
            chunk_type=ChunkType.CODE_BLOCK,
            contains_code=True,
            programming_language="python",
            word_count=50,
            character_count=300
        )
        
        assert metadata.chunk_type == ChunkType.CODE_BLOCK
        assert metadata.contains_code is True
        assert metadata.programming_language == "python"
        assert metadata.word_count == 50
        assert metadata.character_count == 300
    
    def test_datetime_defaults(self):
        """Test that datetime fields have proper defaults."""
        metadata = ChunkMetadata(
            collection_name="test",
            source_file="test.md",
            file_hash="d41d8cd98f00b204e9800998ecf8427e",  # Valid MD5 hash
            chunk_id="chunk_001",
            chunk_index=0,
            total_chunks=1
        )
        
        assert isinstance(metadata.created_at, datetime)
        assert isinstance(metadata.last_updated, datetime)
        assert metadata.created_at.tzinfo == timezone.utc
        assert metadata.last_updated.tzinfo == timezone.utc


class TestFileVectorMapping:
    """Test FileVectorMapping model."""
    
    def test_basic_creation(self):
        """Test basic FileVectorMapping creation."""
        mapping = FileVectorMapping(
            collection_name="test_collection",
            file_path="docs/test.md",
            file_hash="d41d8cd98f00b204e9800998ecf8427e"  # Valid MD5 hash
        )
        
        assert mapping.collection_name == "test_collection"
        assert mapping.file_path == "docs/test.md"
        assert mapping.file_hash == "d41d8cd98f00b204e9800998ecf8427e"
        assert mapping.chunk_ids == []
        assert mapping.chunk_count == 0
        assert mapping.sync_status == SyncStatus.NEVER_SYNCED
        assert mapping.sync_error is None
        assert isinstance(mapping.last_synced, datetime)
    
    def test_creation_with_chunks(self):
        """Test FileVectorMapping creation with chunk data."""
        chunk_ids = ["chunk_001", "chunk_002", "chunk_003"]
        
        mapping = FileVectorMapping(
            collection_name="test_collection",
            file_path="docs/test.md",
            file_hash="5d41402abc4b2a76b9719d911017c592",  # Valid MD5 hash
            chunk_ids=chunk_ids,
            chunk_count=3,
            sync_status=SyncStatus.IN_SYNC,
            processing_time=45.2,
            chunking_strategy="markdown_intelligent"
        )
        
        assert mapping.chunk_ids == chunk_ids
        assert mapping.chunk_count == 3
        assert mapping.sync_status == SyncStatus.IN_SYNC
        assert mapping.processing_time == 45.2
        assert mapping.chunking_strategy == "markdown_intelligent"
    
    def test_file_hash_validation(self):
        """Test file hash validation."""
        # Valid MD5 hash (32 characters)
        valid_hash = "d41d8cd98f00b204e9800998ecf8427e"
        mapping = FileVectorMapping(
            collection_name="test",
            file_path="test.md",
            file_hash=valid_hash
        )
        assert mapping.file_hash == valid_hash
        
        # Invalid hash length should raise validation error
        with pytest.raises(ValueError, match="File hash must be MD5 format"):
            FileVectorMapping(
                collection_name="test",
                file_path="test.md",
                file_hash="invalid_hash"
            )


class TestSyncConfiguration:
    """Test SyncConfiguration model."""
    
    def test_default_configuration(self):
        """Test default SyncConfiguration values."""
        config = SyncConfiguration()
        
        assert config.enabled is True
        assert config.auto_sync is False
        assert config.batch_size == 50
        assert config.max_concurrent_files == 5
        assert config.chunk_cache_size == 1000
        assert config.embedding_batch_size == 32
        assert config.min_chunk_size == 50
        assert config.max_chunk_size == 2000
        assert config.chunking_strategy == "auto"
        assert config.max_retries == 3
        assert config.retry_delay == 1.0
        assert config.error_threshold == 0.1
        assert config.enable_metrics is True
        assert config.log_level == "INFO"
    
    def test_custom_configuration(self):
        """Test SyncConfiguration with custom values."""
        config = SyncConfiguration(
            enabled=False,
            auto_sync=True,
            batch_size=100,
            max_concurrent_files=10,
            chunking_strategy="markdown_intelligent",
            max_retries=5,
            error_threshold=0.05,
            log_level="DEBUG"
        )
        
        assert config.enabled is False
        assert config.auto_sync is True
        assert config.batch_size == 100
        assert config.max_concurrent_files == 10
        assert config.chunking_strategy == "markdown_intelligent"
        assert config.max_retries == 5
        assert config.error_threshold == 0.05
        assert config.log_level == "DEBUG"


class TestSyncJobSpec:
    """Test SyncJobSpec dataclass."""
    
    def test_basic_job_spec(self):
        """Test basic SyncJobSpec creation."""
        job_spec = SyncJobSpec(
            collection_name="test_collection",
            operation_type=SyncOperation.UPDATE
        )
        
        assert job_spec.collection_name == "test_collection"
        assert job_spec.operation_type == SyncOperation.UPDATE
        assert job_spec.file_paths is None
        assert job_spec.priority == 1
        assert job_spec.batch_size is None
        assert job_spec.chunking_strategy is None
        assert job_spec.force_reprocess is False
    
    def test_detailed_job_spec(self):
        """Test SyncJobSpec with all options."""
        file_paths = ["doc1.md", "doc2.md"]
        
        job_spec = SyncJobSpec(
            collection_name="detailed_collection",
            operation_type=SyncOperation.ADD,
            file_paths=file_paths,
            priority=5,
            batch_size=25,
            chunking_strategy="baseline",
            force_reprocess=True,
            progress_callback="http://callback.example.com/progress",
            completion_callback="http://callback.example.com/complete"
        )
        
        assert job_spec.file_paths == file_paths
        assert job_spec.priority == 5
        assert job_spec.batch_size == 25
        assert job_spec.chunking_strategy == "baseline"
        assert job_spec.force_reprocess is True
        assert job_spec.progress_callback == "http://callback.example.com/progress"
        assert job_spec.completion_callback == "http://callback.example.com/complete"


class TestSyncResult:
    """Test SyncResult dataclass."""
    
    def test_basic_result(self):
        """Test basic SyncResult creation."""
        now = datetime.now(timezone.utc)
        
        result = SyncResult(
            job_id="job_123",
            collection_name="test_collection",
            operation_type=SyncOperation.UPDATE,
            success=True,
            started_at=now
        )
        
        assert result.job_id == "job_123"
        assert result.collection_name == "test_collection"
        assert result.operation_type == SyncOperation.UPDATE
        assert result.success is True
        assert result.started_at == now
        assert result.completed_at is None
        assert result.files_processed == 0
        assert result.chunks_created == 0
        assert result.errors == []
        assert result.warnings == []
    
    def test_detailed_result(self):
        """Test SyncResult with detailed metrics."""
        started = datetime.now(timezone.utc)
        completed = datetime.now(timezone.utc)
        
        result = SyncResult(
            job_id="detailed_job_456",
            collection_name="detailed_collection",
            operation_type=SyncOperation.ADD,
            success=True,
            started_at=started,
            completed_at=completed,
            files_processed=10,
            chunks_created=50,
            chunks_updated=5,
            chunks_deleted=2,
            total_duration=120.5,
            average_file_time=12.05,
            chunks_per_second=0.42,
            chunking_quality_score=0.85,
            embedding_quality_score=0.92,
            errors=["Minor error 1", "Minor error 2"],
            warnings=["Warning 1"]
        )
        
        assert result.files_processed == 10
        assert result.chunks_created == 50
        assert result.chunks_updated == 5
        assert result.chunks_deleted == 2
        assert result.total_duration == 120.5
        assert result.chunking_quality_score == 0.85
        assert result.embedding_quality_score == 0.92
        assert len(result.errors) == 2
        assert len(result.warnings) == 1
    
    def test_health_score_calculation(self):
        """Test health score calculation for SyncResult."""
        now = datetime.now(timezone.utc)
        
        # Perfect result
        result = SyncResult(
            job_id="perfect_job",
            collection_name="test",
            operation_type=SyncOperation.UPDATE,
            success=True,
            started_at=now
        )
        assert result.health_score == 1.0
        
        # Failed result
        result.success = False
        assert result.health_score == 0.0
        
        # Result with errors
        result.success = True
        result.errors = ["Error 1", "Error 2"]
        expected_score = 1.0 - (2 * 0.1)  # Deduct 0.1 per error
        assert result.health_score == expected_score
        
        # Result with warnings
        result.errors = []
        result.warnings = ["Warning 1", "Warning 2", "Warning 3"]
        expected_score = 1.0 - (3 * 0.05)  # Deduct 0.05 per warning
        assert result.health_score == expected_score
        
        # Result with quality scores
        result.warnings = []
        result.chunking_quality_score = 0.8
        expected_score = (1.0 + 0.8) / 2  # Average with quality score
        assert result.health_score == expected_score


class TestUtilityFunctions:
    """Test utility functions for vector sync schemas."""
    
    def test_generate_chunk_id(self):
        """Test chunk ID generation."""
        chunk_id = generate_chunk_id(
            collection_name="test_collection",
            file_path="docs/test.md",
            chunk_index=0,
            content_hash="abc123"
        )
        
        assert isinstance(chunk_id, str)
        assert len(chunk_id) == 32  # MD5 hash length
        
        # Same inputs should generate same ID
        chunk_id2 = generate_chunk_id(
            collection_name="test_collection",
            file_path="docs/test.md",
            chunk_index=0,
            content_hash="abc123"
        )
        assert chunk_id == chunk_id2
        
        # Different inputs should generate different IDs
        chunk_id3 = generate_chunk_id(
            collection_name="test_collection",
            file_path="docs/test.md",
            chunk_index=1,  # Different index
            content_hash="abc123"
        )
        assert chunk_id != chunk_id3
    
    def test_generate_operation_id(self):
        """Test operation ID generation."""
        with patch('tools.knowledge_base.vector_sync_schemas.datetime') as mock_datetime:
            # Mock datetime to get consistent results
            mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T00:00:00+00:00"
            mock_datetime.now.return_value = mock_datetime.now.return_value
            
            operation_id = generate_operation_id("test_collection", SyncOperation.UPDATE)
            
            assert isinstance(operation_id, str)
            assert len(operation_id) == 16  # Truncated MD5 hash
            
            # Same inputs should generate same ID (with same timestamp)
            operation_id2 = generate_operation_id("test_collection", SyncOperation.UPDATE)
            assert operation_id == operation_id2
    
    def test_calculate_file_hash(self):
        """Test file content hash calculation."""
        content1 = "This is test content for hashing."
        content2 = "This is different test content."
        
        hash1 = calculate_file_hash(content1)
        hash2 = calculate_file_hash(content2)
        
        assert isinstance(hash1, str)
        assert isinstance(hash2, str)
        assert len(hash1) == 32  # MD5 hash length
        assert len(hash2) == 32
        assert hash1 != hash2
        
        # Same content should produce same hash
        hash1_repeat = calculate_file_hash(content1)
        assert hash1 == hash1_repeat
    
    def test_validate_sync_configuration(self):
        """Test sync configuration validation."""
        # Valid configuration
        config_data = {
            "enabled": True,
            "batch_size": 100,
            "chunking_strategy": "markdown_intelligent"
        }
        
        config = validate_sync_configuration(config_data)
        assert isinstance(config, SyncConfiguration)
        assert config.enabled is True
        assert config.batch_size == 100
        assert config.chunking_strategy == "markdown_intelligent"
        
        # Invalid configuration should raise validation error
        invalid_config_data = {
            "batch_size": "invalid"  # Should be int
        }
        
        with pytest.raises(Exception):  # Pydantic validation error
            validate_sync_configuration(invalid_config_data)
    
    def test_chunk_metadata_from_enhanced_chunk(self):
        """Test conversion from enhanced chunk to ChunkMetadata."""
        enhanced_chunk = {
            'id': 'test_chunk_123',
            'content': 'This is test chunk content.',
            'metadata': {
                'chunk_index': 0,
                'total_chunks': 3,
                'chunk_type': 'code_block',
                'header_hierarchy': ['Introduction', 'Setup'],
                'contains_code': True,
                'programming_language': 'python',
                'word_count': 25,
                'created_at': '2024-01-01T10:00:00+00:00'
            }
        }
        
        metadata = chunk_metadata_from_enhanced_chunk(
            chunk=enhanced_chunk,
            collection_name="test_collection",
            file_path="test.py",
            file_hash="d41d8cd98f00b204e9800998ecf8427e"
        )
        
        assert isinstance(metadata, ChunkMetadata)
        assert metadata.collection_name == "test_collection"
        assert metadata.source_file == "test.py"
        assert metadata.file_hash == "d41d8cd98f00b204e9800998ecf8427e"
        assert metadata.chunk_id == "test_chunk_123"
        assert metadata.chunk_index == 0
        assert metadata.total_chunks == 3
        assert metadata.chunk_type == ChunkType.CODE_BLOCK
        assert metadata.header_hierarchy == ['Introduction', 'Setup']
        assert metadata.contains_code is True
        assert metadata.programming_language == "python"
        assert metadata.word_count == 25
        assert metadata.character_count == len(enhanced_chunk['content'])
        assert metadata.sync_version == 1
    
    def test_chunk_metadata_from_minimal_chunk(self):
        """Test conversion with minimal chunk data."""
        minimal_chunk = {
            'id': 'minimal_chunk',
            'content': 'Minimal content.',
            'metadata': {}
        }
        
        metadata = chunk_metadata_from_enhanced_chunk(
            chunk=minimal_chunk,
            collection_name="minimal_collection",
            file_path="minimal.md",
            file_hash="5d41402abc4b2a76b9719d911017c592"
        )
        
        assert metadata.collection_name == "minimal_collection"
        assert metadata.source_file == "minimal.md"
        assert metadata.file_hash == "5d41402abc4b2a76b9719d911017c592"
        assert metadata.chunk_id == "minimal_chunk"
        assert metadata.chunk_index == 0  # Default
        assert metadata.total_chunks == 1  # Default
        assert metadata.chunk_type == ChunkType.PARAGRAPH  # Default
        assert metadata.header_hierarchy == []  # Default
        assert metadata.contains_code is False  # Default
        assert metadata.programming_language is None  # Default
        assert metadata.word_count == 0  # Default
        assert metadata.character_count == len(minimal_chunk['content'])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])