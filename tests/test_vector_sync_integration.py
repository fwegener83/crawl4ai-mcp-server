"""
Integration tests for Vector Sync Infrastructure.

Tests the complete integration between file collections, vector storage,
and the intelligent sync manager.
"""
import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

# Check if RAG dependencies are available
try:
    from tools.knowledge_base.dependencies import is_rag_available
    RAG_AVAILABLE = is_rag_available()
except ImportError:
    RAG_AVAILABLE = False

# Conditionally import components to test
if RAG_AVAILABLE:
    from tools.knowledge_base.vector_sync_schemas import (
        VectorSyncStatus, SyncConfiguration, SyncResult, SyncStatus, SyncOperation
    )
    from tools.knowledge_base.intelligent_sync_manager import IntelligentSyncManager
    from tools.vector_sync_api import VectorSyncAPI, SyncCollectionRequest, VectorSearchRequest
    from tools.collection_manager import CollectionFileManager
else:
    # Skip all tests in this module if RAG is not available
    pytestmark = pytest.mark.skip(reason="RAG dependencies not available")


# Fixtures
@pytest.fixture
def temp_collections_dir():
    """Create temporary directory for collections."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def collection_manager(temp_collections_dir):
    """Create collection file manager."""
    return CollectionFileManager(base_dir=temp_collections_dir)


@pytest.fixture
def mock_vector_store():
    """Create mock vector store."""
    mock_store = Mock()
    mock_store.add_documents = Mock()
    mock_store.delete_documents = Mock()
    mock_store.similarity_search = Mock(return_value=[])
    mock_store.get_or_create_collection = Mock()
    return mock_store


@pytest.fixture
def mock_content_processor():
    """Create mock content processor."""
    with patch('tools.knowledge_base.intelligent_sync_manager.EnhancedContentProcessor') as mock_processor_class:
        mock_processor = Mock()
        mock_processor.process_content = Mock(return_value=[
            {
                'id': 'test_chunk_1',
                'content': 'Test content chunk 1',
                'metadata': {
                    'chunk_index': 0,
                    'total_chunks': 2,
                    'chunk_type': 'paragraph',
                    'header_hierarchy': [],
                    'contains_code': False,
                    'word_count': 4,
                    'created_at': datetime.now(timezone.utc).isoformat()
                }
            },
            {
                'id': 'test_chunk_2',
                'content': 'Test content chunk 2',
                'metadata': {
                    'chunk_index': 1,
                    'total_chunks': 2,
                    'chunk_type': 'paragraph',
                    'header_hierarchy': [],
                    'contains_code': False,
                    'word_count': 4,
                    'created_at': datetime.now(timezone.utc).isoformat()
                }
            }
        ])
        mock_processor_class.return_value = mock_processor
        yield mock_processor


@pytest.fixture
def sync_config():
    """Create sync configuration."""
    return SyncConfiguration(
        enabled=True,
        batch_size=10,
        max_concurrent_files=2,
        chunking_strategy="markdown_intelligent"
    )


@pytest.fixture
def sync_manager(mock_vector_store, collection_manager, sync_config, mock_content_processor):
    """Create intelligent sync manager."""
    with patch('tools.knowledge_base.intelligent_sync_manager.is_rag_available', return_value=True):
        manager = IntelligentSyncManager(
            vector_store=mock_vector_store,
            collection_manager=collection_manager,
            config=sync_config
        )
        # Replace the content processor with our mock
        manager.content_processor = mock_content_processor
        return manager


@pytest.fixture
def sync_api(sync_manager, mock_vector_store, collection_manager):
    """Create vector sync API."""
    return VectorSyncAPI(
        sync_manager=sync_manager,
        vector_store=mock_vector_store,
        collection_manager=collection_manager
    )


class TestVectorSyncSchemas:
    """Test vector sync data models and schemas."""
    
    def test_vector_sync_status_creation(self):
        """Test VectorSyncStatus model creation."""
        status = VectorSyncStatus(
            collection_name="test_collection",
            sync_enabled=True,
            status=SyncStatus.NEVER_SYNCED
        )
        
        assert status.collection_name == "test_collection"
        assert status.sync_enabled is True
        assert status.status == SyncStatus.NEVER_SYNCED
        assert status.total_files == 0
        assert status.is_out_of_sync is False  # NEVER_SYNCED is not considered out of sync
        assert 0.0 <= status.sync_health_score <= 1.0
    
    def test_sync_health_score_calculation(self):
        """Test sync health score calculation for different statuses."""
        # Test IN_SYNC
        status = VectorSyncStatus(collection_name="test", status=SyncStatus.IN_SYNC)
        assert status.sync_health_score == 1.0
        
        # Test PARTIAL_SYNC
        status.status = SyncStatus.PARTIAL_SYNC
        assert status.sync_health_score == 0.7
        
        # Test OUT_OF_SYNC
        status.status = SyncStatus.OUT_OF_SYNC
        assert status.sync_health_score == 0.3
        
        # Test SYNC_ERROR
        status.status = SyncStatus.SYNC_ERROR
        assert status.sync_health_score == 0.1


class TestIntelligentSyncManager:
    """Test intelligent sync manager functionality."""
    
    def test_sync_manager_initialization(self, sync_manager):
        """Test sync manager initializes correctly."""
        assert sync_manager.config.enabled is True
        assert sync_manager.config.chunking_strategy == "markdown_intelligent"
        assert sync_manager.vector_store is not None
        assert sync_manager.collection_manager is not None
    
    def test_get_collection_sync_status(self, sync_manager):
        """Test getting collection sync status."""
        status = sync_manager.get_collection_sync_status("test_collection")
        
        assert status.collection_name == "test_collection"
        assert status.sync_enabled is True
        assert status.status == SyncStatus.NEVER_SYNCED
    
    def test_enable_disable_collection_sync(self, sync_manager):
        """Test enabling and disabling collection sync."""
        # Test enable
        sync_manager.enable_collection_sync("test_collection")
        status = sync_manager.get_collection_sync_status("test_collection")
        assert status.sync_enabled is True
        
        # Test disable
        sync_manager.disable_collection_sync("test_collection")
        status = sync_manager.get_collection_sync_status("test_collection")
        assert status.sync_enabled is False
    
    @pytest.mark.asyncio
    async def test_sync_nonexistent_collection(self, sync_manager):
        """Test syncing a collection that doesn't exist."""
        result = await sync_manager.sync_collection("nonexistent_collection")
        
        assert result.success is False
        assert "does not exist" in result.errors[0].lower()
    
    @pytest.mark.asyncio
    async def test_sync_empty_collection(self, sync_manager, collection_manager):
        """Test syncing an empty collection."""
        # Create empty collection
        collection_manager.create_collection("empty_collection", "Empty test collection")
        
        result = await sync_manager.sync_collection("empty_collection")
        
        assert result.success is True
        assert result.files_processed == 0
        assert result.chunks_created == 0
    
    @pytest.mark.asyncio
    async def test_sync_collection_with_files(self, sync_manager, collection_manager):
        """Test syncing a collection with files."""
        # Create collection with test files
        collection_manager.create_collection("test_collection", "Test collection")
        collection_manager.save_file("test_collection", "test1.md", "# Test Content 1\n\nThis is test content.")
        collection_manager.save_file("test_collection", "test2.md", "# Test Content 2\n\nThis is more test content.")
        
        result = await sync_manager.sync_collection("test_collection")
        
        assert result.success is True
        assert result.files_processed == 2
        assert result.chunks_created == 4  # 2 chunks per file based on mock
        
        # Verify vector store was called
        sync_manager.vector_store.add_documents.assert_called()
    
    @pytest.mark.asyncio
    async def test_incremental_sync(self, sync_manager, collection_manager):
        """Test incremental sync only processes changed files."""
        # Create collection and sync
        collection_manager.create_collection("test_collection", "Test collection")
        collection_manager.save_file("test_collection", "test1.md", "# Original Content")
        
        # First sync
        result1 = await sync_manager.sync_collection("test_collection")
        assert result1.success is True
        assert result1.files_processed == 1
        
        # Second sync without changes - should process 0 files
        result2 = await sync_manager.sync_collection("test_collection")
        assert result2.success is True
        assert result2.files_processed == 0
        
        # Modify file and sync again - should process 1 file
        collection_manager.save_file("test_collection", "test1.md", "# Modified Content")
        result3 = await sync_manager.sync_collection("test_collection")
        assert result3.success is True
        assert result3.files_processed == 1
    
    @pytest.mark.asyncio
    async def test_force_reprocess(self, sync_manager, collection_manager):
        """Test force reprocess ignores file hashes."""
        # Create collection and sync
        collection_manager.create_collection("test_collection", "Test collection")
        collection_manager.save_file("test_collection", "test1.md", "# Test Content")
        
        # First sync
        result1 = await sync_manager.sync_collection("test_collection")
        assert result1.success is True
        assert result1.files_processed == 1
        
        # Force reprocess should process files even without changes
        result2 = await sync_manager.sync_collection("test_collection", force_reprocess=True)
        assert result2.success is True
        assert result2.files_processed == 1


class TestVectorSyncAPI:
    """Test vector sync API functionality."""
    
    @pytest.mark.asyncio
    async def test_sync_collection_request(self, sync_api, collection_manager):
        """Test syncing collection via API."""
        # Create test collection
        collection_manager.create_collection("api_test_collection", "API test collection")
        collection_manager.save_file("api_test_collection", "test.md", "# API Test Content")
        
        request = SyncCollectionRequest(force_reprocess=False)
        response = await sync_api.sync_collection("api_test_collection", request)
        
        assert response.success is True
        assert response.job_id is not None
        assert "api_test_collection" in response.message
        assert response.sync_result is not None
    
    @pytest.mark.asyncio
    async def test_sync_collection_not_found(self, sync_api):
        """Test syncing non-existent collection returns error."""
        request = SyncCollectionRequest()
        
        response = await sync_api.sync_collection("nonexistent", request)
        assert response.success is False
        assert "does not exist" in response.error.lower() or "not found" in response.error.lower()
    
    @pytest.mark.asyncio
    async def test_get_collection_sync_status_api(self, sync_api, collection_manager):
        """Test getting collection sync status via API."""
        # Create test collection
        collection_manager.create_collection("status_test_collection", "Status test collection")
        
        response = await sync_api.get_collection_sync_status("status_test_collection")
        
        assert response.success is True
        assert response.status['collection_name'] == "status_test_collection"
        assert 'status' in response.status
        assert 'sync_enabled' in response.status
    
    @pytest.mark.asyncio
    async def test_list_collection_sync_statuses(self, sync_api, collection_manager):
        """Test listing all collection sync statuses."""
        # Create test collections
        collection_manager.create_collection("collection1", "Test collection 1")
        collection_manager.create_collection("collection2", "Test collection 2")
        
        response = await sync_api.list_collection_sync_statuses()
        
        assert response['success'] is True
        assert 'statuses' in response
        assert 'summary' in response
    
    @pytest.mark.asyncio
    async def test_enable_disable_collection_sync_api(self, sync_api, collection_manager):
        """Test enabling/disabling collection sync via API."""
        # Create test collection
        collection_manager.create_collection("toggle_test_collection", "Toggle test collection")
        
        # Test disable
        response = await sync_api.disable_collection_sync("toggle_test_collection")
        assert response['success'] is True
        
        # Test enable
        response = await sync_api.enable_collection_sync("toggle_test_collection")
        assert response['success'] is True
    
    @pytest.mark.asyncio
    async def test_vector_search(self, sync_api):
        """Test vector search functionality."""
        # Mock search results
        sync_api.vector_store.similarity_search.return_value = [
            {
                'id': 'test_chunk_1',
                'content': 'Test search result content',
                'metadata': {
                    'collection_name': 'test_collection',
                    'source_file': 'test.md',
                    'chunk_index': 0
                },
                'score': 0.9
            }
        ]
        
        request = VectorSearchRequest(
            query="test search query",
            limit=5,
            similarity_threshold=0.7
        )
        
        response = await sync_api.search_vectors(request)
        
        assert response.success is True
        assert len(response.results) == 1
        assert response.results[0]['content'] == 'Test search result content'
        assert response.results[0]['similarity_score'] == 0.9  # Use similarity_score instead of score
        assert response.query_time > 0


class TestVectorSyncIntegration:
    """Test complete integration scenarios."""
    
    @pytest.mark.asyncio
    async def test_full_sync_workflow(self, sync_api, collection_manager):
        """Test complete sync workflow from collection creation to search."""
        collection_name = "integration_test_collection"
        
        # 1. Create collection with content
        collection_manager.create_collection(collection_name, "Integration test collection")
        collection_manager.save_file(collection_name, "doc1.md", "# Introduction\n\nThis is the introduction section.")
        collection_manager.save_file(collection_name, "doc2.md", "# Conclusion\n\nThis is the conclusion section.")
        
        # 2. Sync collection
        sync_request = SyncCollectionRequest(force_reprocess=False)
        sync_response = await sync_api.sync_collection(collection_name, sync_request)
        
        assert sync_response.success is True
        assert sync_response.sync_result['files_processed'] == 2
        assert sync_response.sync_result['chunks_created'] == 4
        
        # 3. Check sync status
        status_response = await sync_api.get_collection_sync_status(collection_name)
        assert status_response.success is True
        assert status_response.status['status'] == 'in_sync'
        
        # 4. Simulate search (with mocked results)
        sync_api.vector_store.similarity_search.return_value = [
            {
                'id': 'intro_chunk',
                'content': 'This is the introduction section.',
                'metadata': {
                    'collection_name': collection_name,
                    'source_file': 'doc1.md',
                    'chunk_index': 1
                },
                'score': 0.85
            }
        ]
        
        search_request = VectorSearchRequest(
            query="introduction",
            collection_name=collection_name,
            limit=10
        )
        search_response = await sync_api.search_vectors(search_request)
        
        assert search_response.success is True
        assert len(search_response.results) == 1
        assert search_response.results[0]['collection_name'] == collection_name
    
    @pytest.mark.asyncio 
    async def test_error_handling_workflow(self, sync_api, collection_manager):
        """Test error handling in sync workflow."""
        collection_name = "error_test_collection"
        
        # Create collection
        collection_manager.create_collection(collection_name, "Error test collection")
        collection_manager.save_file(collection_name, "test.md", "# Test Content")
        
        # Mock content processor to raise an error
        sync_api.sync_manager.content_processor.process_content.side_effect = Exception("Processing error")
        
        # Attempt sync - should handle error gracefully
        sync_request = SyncCollectionRequest()
        sync_response = await sync_api.sync_collection(collection_name, sync_request)
        
        # Should not crash but report error
        assert sync_response.success is False
        assert sync_response.error is not None
    
    @pytest.mark.asyncio
    async def test_large_collection_sync(self, sync_api, collection_manager):
        """Test syncing a larger collection with multiple files."""
        collection_name = "large_test_collection"
        
        # Create collection with multiple files
        collection_manager.create_collection(collection_name, "Large test collection")
        
        # Create 10 test files
        for i in range(10):
            content = f"# Document {i}\n\nThis is content for document {i}.\n\n## Section 1\n\nMore content here."
            collection_manager.save_file(collection_name, f"doc{i:02d}.md", content)
        
        # Sync collection
        sync_request = SyncCollectionRequest()
        sync_response = await sync_api.sync_collection(collection_name, sync_request)
        
        assert sync_response.success is True
        assert sync_response.sync_result['files_processed'] == 10
        # Each file should generate 2 chunks based on our mock
        assert sync_response.sync_result['chunks_created'] == 20
        
        # Verify batch processing worked
        assert sync_api.sync_manager.vector_store.add_documents.call_count > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])