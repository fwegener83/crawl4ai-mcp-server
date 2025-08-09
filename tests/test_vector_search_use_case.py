"""
Tests for vector search use-case layer.

This test file defines the behavior that both API and MCP endpoints must follow
after refactoring to use shared use-case functions.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import Optional, List, Dict, Any

# Import the exception we'll create
try:
    from application_layer.vector_search import ValidationError, search_vectors_use_case
    from services.interfaces import VectorSearchResult
except ImportError:
    # These don't exist yet - we'll create them after writing tests
    pass


class TestVectorSearchValidation:
    """Test validation rules that both API and MCP must follow."""

    @pytest.mark.asyncio
    async def test_missing_query_raises_validation_error(self):
        """Test that missing or empty query raises ValidationError with MISSING_QUERY code."""
        vector_service = AsyncMock()
        collection_service = AsyncMock()
        
        # Test empty string
        with pytest.raises(ValidationError) as exc_info:
            await search_vectors_use_case(
                vector_service, collection_service,
                query="", collection_name=None, limit=10, similarity_threshold=0.7
            )
        assert exc_info.value.code == "MISSING_QUERY"
        assert "required" in exc_info.value.message.lower()
        
        # Test whitespace-only string
        with pytest.raises(ValidationError) as exc_info:
            await search_vectors_use_case(
                vector_service, collection_service,
                query="   ", collection_name=None, limit=10, similarity_threshold=0.7
            )
        assert exc_info.value.code == "MISSING_QUERY"
    
    @pytest.mark.asyncio
    async def test_invalid_limit_raises_validation_error(self):
        """Test that invalid limit raises ValidationError with INVALID_LIMIT code."""
        vector_service = AsyncMock()
        collection_service = AsyncMock()
        
        # Test limit = 0
        with pytest.raises(ValidationError) as exc_info:
            await search_vectors_use_case(
                vector_service, collection_service,
                query="test", collection_name=None, limit=0, similarity_threshold=0.7
            )
        assert exc_info.value.code == "INVALID_LIMIT"
        assert "greater than 0" in exc_info.value.message.lower()
        
        # Test negative limit
        with pytest.raises(ValidationError) as exc_info:
            await search_vectors_use_case(
                vector_service, collection_service,
                query="test", collection_name=None, limit=-1, similarity_threshold=0.7
            )
        assert exc_info.value.code == "INVALID_LIMIT"
    
    @pytest.mark.asyncio
    async def test_invalid_threshold_raises_validation_error(self):
        """Test that invalid similarity threshold raises ValidationError with INVALID_THRESHOLD code."""
        vector_service = AsyncMock()
        collection_service = AsyncMock()
        
        # Test threshold < 0
        with pytest.raises(ValidationError) as exc_info:
            await search_vectors_use_case(
                vector_service, collection_service,
                query="test", collection_name=None, limit=10, similarity_threshold=-0.1
            )
        assert exc_info.value.code == "INVALID_THRESHOLD"
        assert "between 0 and 1" in exc_info.value.message.lower()
        
        # Test threshold > 1
        with pytest.raises(ValidationError) as exc_info:
            await search_vectors_use_case(
                vector_service, collection_service,
                query="test", collection_name=None, limit=10, similarity_threshold=1.1
            )
        assert exc_info.value.code == "INVALID_THRESHOLD"
    
    @pytest.mark.asyncio
    async def test_collection_not_found_raises_error(self):
        """Test that non-existent collection raises error when collection_name provided."""
        vector_service = AsyncMock()
        collection_service = AsyncMock()
        
        # Mock collection service to raise exception for non-existent collection
        collection_service.get_collection.side_effect = Exception("Collection 'nonexistent' does not exist")
        
        with pytest.raises(Exception) as exc_info:
            await search_vectors_use_case(
                vector_service, collection_service,
                query="test", collection_name="nonexistent", limit=10, similarity_threshold=0.7
            )
        assert "does not exist" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_service_unavailable_raises_runtime_error(self):
        """Test that unavailable vector service raises RuntimeError."""
        vector_service = AsyncMock()
        collection_service = AsyncMock()
        
        # Mock vector service as unavailable
        vector_service.vector_available = False
        
        with pytest.raises(RuntimeError) as exc_info:
            await search_vectors_use_case(
                vector_service, collection_service,
                query="test", collection_name=None, limit=10, similarity_threshold=0.7
            )
        assert "not available" in str(exc_info.value).lower()


class TestVectorSearchSuccessPath:
    """Test successful vector search behavior."""

    @pytest.mark.asyncio
    async def test_search_without_collection_name(self):
        """Test successful search without specifying collection name."""
        vector_service = AsyncMock()
        collection_service = AsyncMock()
        
        # Mock services as available and working
        vector_service.vector_available = True
        
        # Mock search results
        mock_result_1 = MagicMock()
        mock_result_1.model_dump.return_value = {
            "content": "AI fundamentals content",
            "metadata": {"filename": "ai.md"},
            "score": 0.85
        }
        mock_result_1.score = 0.85
        
        mock_result_2 = MagicMock()
        mock_result_2.model_dump.return_value = {
            "content": "Machine learning content", 
            "metadata": {"filename": "ml.md"},
            "score": 0.75
        }
        mock_result_2.score = 0.75
        
        vector_service.search_vectors.return_value = [mock_result_1, mock_result_2]
        
        # Execute use case
        results = await search_vectors_use_case(
            vector_service, collection_service,
            query="artificial intelligence", collection_name=None, limit=10, similarity_threshold=0.7
        )
        
        # Verify service was called correctly
        vector_service.search_vectors.assert_called_once_with(
            "artificial intelligence", None, 10, 0.7
        )
        
        # Verify result format
        assert len(results) == 2
        assert results[0]["content"] == "AI fundamentals content"
        assert results[0]["metadata"]["filename"] == "ai.md"
        assert results[0]["similarity_score"] == 0.85  # Transformed from score
        assert results[1]["content"] == "Machine learning content"
        assert results[1]["similarity_score"] == 0.75
    
    @pytest.mark.asyncio
    async def test_search_with_collection_name(self):
        """Test successful search with specific collection name."""
        vector_service = AsyncMock()
        collection_service = AsyncMock()
        
        # Mock services
        vector_service.vector_available = True
        collection_service.get_collection.return_value = MagicMock()  # Collection exists
        
        mock_result = MagicMock()
        mock_result.model_dump.return_value = {
            "content": "Collection-specific content",
            "metadata": {"collection": "test_collection", "filename": "doc.md"},
            "score": 0.9
        }
        mock_result.score = 0.9
        
        vector_service.search_vectors.return_value = [mock_result]
        
        # Execute use case
        results = await search_vectors_use_case(
            vector_service, collection_service,
            query="test query", collection_name="test_collection", limit=5, similarity_threshold=0.8
        )
        
        # Verify collection validation was called
        collection_service.get_collection.assert_called_once_with("test_collection")
        
        # Verify service was called correctly
        vector_service.search_vectors.assert_called_once_with(
            "test query", "test_collection", 5, 0.8
        )
        
        # Verify result format
        assert len(results) == 1
        assert results[0]["similarity_score"] == 0.9
        assert results[0]["metadata"]["collection"] == "test_collection"
    
    @pytest.mark.asyncio
    async def test_result_format_consistency(self):
        """Test that results are consistently formatted with similarity_score field."""
        vector_service = AsyncMock()
        collection_service = AsyncMock()
        
        vector_service.vector_available = True
        
        # Mock result with different field structure
        mock_result = MagicMock()
        mock_result.model_dump.return_value = {
            "content": "Test content",
            "metadata": {"test": "data"},
            "score": 0.95,
            "other_field": "value"
        }
        mock_result.score = 0.95
        
        vector_service.search_vectors.return_value = [mock_result]
        
        results = await search_vectors_use_case(
            vector_service, collection_service,
            query="test", collection_name=None, limit=10, similarity_threshold=0.7
        )
        
        # Verify consistent transformation
        assert len(results) == 1
        result = results[0]
        assert "similarity_score" in result
        assert result["similarity_score"] == 0.95
        assert result["content"] == "Test content"
        assert result["metadata"]["test"] == "data"
        assert result["other_field"] == "value"  # Other fields preserved
    
    @pytest.mark.asyncio
    async def test_empty_results_handled_correctly(self):
        """Test that empty search results are handled correctly."""
        vector_service = AsyncMock()
        collection_service = AsyncMock()
        
        vector_service.vector_available = True
        vector_service.search_vectors.return_value = []
        
        results = await search_vectors_use_case(
            vector_service, collection_service,
            query="no matches", collection_name=None, limit=10, similarity_threshold=0.7
        )
        
        assert isinstance(results, list)
        assert len(results) == 0


class TestValidationError:
    """Test the ValidationError exception class."""
    
    def test_validation_error_creation(self):
        """Test ValidationError can be created with code, message, and details."""
        error = ValidationError("TEST_CODE", "Test message", {"field": "value"})
        
        assert error.code == "TEST_CODE"
        assert error.message == "Test message"
        assert error.details == {"field": "value"}
    
    def test_validation_error_default_details(self):
        """Test ValidationError defaults to empty dict for details."""
        error = ValidationError("CODE", "Message")
        
        assert error.code == "CODE"
        assert error.message == "Message"
        assert error.details == {}