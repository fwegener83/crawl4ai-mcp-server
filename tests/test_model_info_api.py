"""Test model info API functionality."""

import pytest
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.knowledge_base.dependencies import is_rag_available
from services.vector_sync_service import VectorSyncService


@pytest.mark.asyncio
async def test_get_model_info_with_rag_available():
    """Test model info when RAG dependencies are available."""
    if not is_rag_available():
        pytest.skip("RAG dependencies not available")
    
    service = VectorSyncService()
    assert service.vector_available is True
    
    model_info = await service.get_model_info()
    
    # Verify response structure
    assert isinstance(model_info, dict)
    assert "model_name" in model_info
    assert "device" in model_info
    assert "model_dimension" in model_info
    assert "model_properties" in model_info
    assert "error_message" in model_info
    
    # Verify successful response
    assert model_info["error_message"] is None
    assert model_info["model_name"] is not None
    assert model_info["device"] is not None
    assert model_info["model_dimension"] is not None
    assert isinstance(model_info["model_dimension"], int)
    assert model_info["model_dimension"] > 0
    
    # Verify model properties
    assert isinstance(model_info["model_properties"], dict)
    if "max_sequence_length" in model_info["model_properties"]:
        assert isinstance(model_info["model_properties"]["max_sequence_length"], int)


@pytest.mark.asyncio 
async def test_get_model_info_without_rag():
    """Test model info when RAG dependencies are not available."""
    service = VectorSyncService()
    
    # Temporarily disable vector availability
    original_vector_available = service.vector_available
    service.vector_available = False
    
    try:
        model_info = await service.get_model_info()
        
        # Verify error response structure
        assert isinstance(model_info, dict)
        assert model_info["model_name"] is None
        assert model_info["device"] is None  
        assert model_info["model_dimension"] is None
        assert model_info["error_message"] == "Vector dependencies not available"
        
    finally:
        # Restore original state
        service.vector_available = original_vector_available


@pytest.mark.asyncio
async def test_model_info_api_response_format():
    """Test that model info matches expected API response format."""
    if not is_rag_available():
        pytest.skip("RAG dependencies not available")
    
    service = VectorSyncService()
    model_info = await service.get_model_info()
    
    # Simulate API endpoint response structure
    api_response = {
        "success": True,
        "data": {
            "vector_service_available": service.vector_available,
            **model_info
        }
    }
    
    # Verify API response structure
    assert api_response["success"] is True
    assert "data" in api_response
    assert api_response["data"]["vector_service_available"] is True
    
    # Verify all model info is included
    expected_fields = ["model_name", "device", "model_dimension", "model_properties", "error_message"]
    for field in expected_fields:
        assert field in api_response["data"]


def test_model_info_multilingual_model():
    """Test that the multilingual model is correctly loaded."""
    if not is_rag_available():
        pytest.skip("RAG dependencies not available")
    
    # Run test synchronously
    async def check_multilingual_model():
        service = VectorSyncService()
        model_info = await service.get_model_info()
        
        # Verify multilingual model is loaded (from Phase 1 fix)
        assert model_info["model_name"] == "distiluse-base-multilingual-cased-v1"
        assert model_info["model_dimension"] == 512  # Multilingual model dimension
        
        return model_info
    
    # Run the test
    asyncio.run(check_multilingual_model())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])