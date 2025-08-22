"""Test force resync API functionality."""

import pytest
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def vector_service():
    """Create a vector sync service for testing."""
    from services.vector_sync_service import VectorSyncService
    service = VectorSyncService()
    return service


@pytest.mark.asyncio
async def test_force_resync_deletes_existing_vectors(vector_service):
    """Test that force resync deletes existing vectors before reprocessing."""
    if not vector_service.vector_available:
        pytest.skip("Vector dependencies not available")
    
    collection_name = "test_force_resync"
    
    # Test scenario:
    # 1. Create collection with some content
    # 2. Sync normally (should create vectors)
    # 3. Force resync (should delete old vectors and create new ones)
    # 4. Verify vector count and content consistency
    
    try:
        # Create test collection
        from services.collection_management_service import CollectionManagementService
        collection_service = CollectionManagementService()
        
        await collection_service.create_collection({
            "name": collection_name,
            "description": "Test collection for force resync"
        })
        
        # Add test content
        test_content = """# Test Document
        
        This is test content for force resync testing.
        
        ## Section 1
        Content that should generate vectors.
        
        ## Section 2  
        More content for comprehensive testing.
        """
        
        await collection_service.create_file(
            collection_name,
            "test_document.md", 
            test_content
        )
        
        # Initial sync
        initial_status = await vector_service.sync_collection(collection_name)
        assert initial_status.sync_status != "error", f"Initial sync failed: {initial_status.error_message}"
        
        # Get initial vector count (if available)
        initial_search = await vector_service.search_vectors(
            query="test content",
            collection_name=collection_name,
            limit=100
        )
        initial_count = len(initial_search.results)
        assert initial_count > 0, "Initial sync should create vectors"
        
        # Force resync - this should delete all existing vectors and recreate them
        force_config = {
            "force_delete_vectors": True,  # New parameter for force resync
            "force_reprocess": True
        }
        
        force_status = await vector_service.sync_collection(collection_name, force_config)
        assert force_status.sync_status != "error", f"Force resync failed: {force_status.error_message}"
        
        # Verify vectors were recreated
        final_search = await vector_service.search_vectors(
            query="test content",
            collection_name=collection_name,
            limit=100
        )
        final_count = len(final_search.results)
        
        # Should have same number of vectors (content didn't change)
        # but they should be recreated (potentially with updated embeddings)
        assert final_count > 0, "Force resync should recreate vectors"
        
        # Verify search quality is good with new model
        similarity_scores = [result.similarity for result in final_search.results]
        max_similarity = max(similarity_scores) if similarity_scores else 0
        assert max_similarity > 0.3, f"Search quality should be decent, got max similarity {max_similarity}"
        
    finally:
        # Cleanup
        try:
            await collection_service.delete_collection(collection_name)
        except Exception as e:
            print(f"Cleanup error: {e}")


@pytest.mark.asyncio
async def test_force_resync_configuration_options(vector_service):
    """Test force resync with different configuration options."""
    if not vector_service.vector_available:
        pytest.skip("Vector dependencies not available")
        
    collection_name = "test_force_config"
    
    try:
        from services.collection_management_service import CollectionManagementService
        collection_service = CollectionManagementService()
        
        await collection_service.create_collection({
            "name": collection_name,
            "description": "Test collection for force resync config"
        })
        
        # Test different force resync configurations
        test_configs = [
            {"force_delete_vectors": True, "force_reprocess": True},
            {"force_delete_vectors": True, "chunking_strategy": "auto"},
            {"force_delete_vectors": True, "force_reprocess": True, "chunking_strategy": "markdown_intelligent"}
        ]
        
        for config in test_configs:
            status = await vector_service.sync_collection(collection_name, config)
            
            # Should handle the configuration without errors
            if status.sync_status == "error":
                # Some configs might not be supported yet, but shouldn't crash
                assert "not supported" in status.error_message.lower() or \
                       "not implemented" in status.error_message.lower(), \
                       f"Unexpected error for config {config}: {status.error_message}"
            else:
                assert status.sync_status in ["success", "completed", "in_sync"], \
                       f"Force resync should succeed with config {config}, got status: {status.sync_status}"
                       
    finally:
        try:
            await collection_service.delete_collection(collection_name)
        except Exception as e:
            print(f"Cleanup error: {e}")


def test_force_resync_request_model():
    """Test the request model for force resync API."""
    from tools.vector_sync_api import SyncCollectionRequest
    
    # Test default values
    default_request = SyncCollectionRequest()
    assert default_request.force_reprocess == False
    assert default_request.chunking_strategy is None
    
    # Test force resync configuration
    force_request = SyncCollectionRequest(
        force_reprocess=True,
        chunking_strategy="auto"
    )
    assert force_request.force_reprocess == True
    assert force_request.chunking_strategy == "auto"
    
    # Test serialization
    request_dict = force_request.model_dump()
    assert request_dict["force_reprocess"] == True
    assert request_dict["chunking_strategy"] == "auto"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])