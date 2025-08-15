"""
Test suite for RAG Query use-case implementation.

Tests the RAG orchestration logic that integrates vector search 
with LLM response generation, including error handling, validation,
and graceful degradation scenarios.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from typing import Dict, Any, List

from application_layer.rag_query import (
    rag_query_use_case,
    RAGQueryRequest,
    RAGQueryResponse,
    RAGError,
    RAGValidationError,
    RAGUnavailableError
)
from application_layer.vector_search import ValidationError
from services.llm_service import LLMUnavailableError, LLMRateLimitError


class TestRAGQueryRequest:
    """Test RAG query request model validation."""
    
    def test_valid_request_minimal(self):
        """Test valid request with minimal parameters."""
        request = RAGQueryRequest(query="What is AI?")
        
        assert request.query == "What is AI?"
        assert request.collection_name is None
        assert request.max_chunks == 5
        assert request.similarity_threshold == 0.7
    
    def test_valid_request_full(self):
        """Test valid request with all parameters."""
        request = RAGQueryRequest(
            query="Explain machine learning",
            collection_name="ml_docs",
            max_chunks=10,
            similarity_threshold=0.8
        )
        
        assert request.query == "Explain machine learning"
        assert request.collection_name == "ml_docs"
        assert request.max_chunks == 10
        assert request.similarity_threshold == 0.8
    
    def test_invalid_empty_query(self):
        """Test validation error for empty query."""
        with pytest.raises(ValueError):
            RAGQueryRequest(query="")
    
    def test_invalid_whitespace_query(self):
        """Test validation error for whitespace-only query."""
        with pytest.raises(ValueError):
            RAGQueryRequest(query="   ")
    
    def test_invalid_max_chunks_zero(self):
        """Test validation error for zero max_chunks."""
        with pytest.raises(ValueError):
            RAGQueryRequest(query="test", max_chunks=0)
    
    def test_invalid_max_chunks_negative(self):
        """Test validation error for negative max_chunks."""
        with pytest.raises(ValueError):
            RAGQueryRequest(query="test", max_chunks=-1)
    
    def test_invalid_similarity_threshold_negative(self):
        """Test validation error for negative similarity threshold."""
        with pytest.raises(ValueError):
            RAGQueryRequest(query="test", similarity_threshold=-0.1)
    
    def test_invalid_similarity_threshold_over_one(self):
        """Test validation error for similarity threshold > 1."""
        with pytest.raises(ValueError):
            RAGQueryRequest(query="test", similarity_threshold=1.1)


class TestRAGQueryResponse:
    """Test RAG query response model."""
    
    def test_success_response(self):
        """Test successful RAG response structure."""
        sources = [
            {
                "content": "AI is artificial intelligence",
                "similarity_score": 0.9,
                "metadata": {"source": "ai_basics.md"}
            }
        ]
        
        response = RAGQueryResponse(
            success=True,
            answer="Artificial Intelligence (AI) is a technology...",
            sources=sources,
            metadata={
                "chunks_used": 1,
                "collection_searched": "ai_docs",
                "llm_provider": "openai",
                "response_time_ms": 1500
            }
        )
        
        assert response.success is True
        assert "Artificial Intelligence" in response.answer
        assert len(response.sources) == 1
        assert response.sources[0]["similarity_score"] == 0.9
        assert response.metadata["llm_provider"] == "openai"
    
    def test_error_response(self):
        """Test error RAG response structure."""
        response = RAGQueryResponse(
            success=False,
            error="LLM service unavailable"
        )
        
        assert response.success is False
        assert response.answer is None
        assert response.sources is None
        assert response.error == "LLM service unavailable"


class TestRAGQueryUseCase:
    """Test RAG query use-case orchestration."""
    
    @pytest.fixture
    def mock_vector_service(self):
        """Mock vector service."""
        service = AsyncMock()
        service.vector_available = True
        service.search_vectors = AsyncMock()
        return service
    
    @pytest.fixture
    def mock_collection_service(self):
        """Mock collection service."""
        service = AsyncMock()
        service.get_collection = AsyncMock()
        return service
    
    @pytest.fixture
    def mock_llm_service(self):
        """Mock LLM service."""
        service = AsyncMock()
        service.generate_response = AsyncMock()
        service.health_check = AsyncMock(return_value=True)
        return service
    
    @pytest.fixture
    def sample_vector_results(self):
        """Sample vector search results."""
        mock_result = Mock()
        mock_result.model_dump.return_value = {
            "content": "Machine learning is a subset of AI that involves training algorithms on data.",
            "metadata": {"source": "ml_intro.md", "created_at": "2024-01-01"},
            "collection_name": "ai_docs",
            "file_path": "docs/ml_intro.md"
        }
        mock_result.score = 0.85
        return [mock_result]
    
    @pytest.fixture
    def sample_llm_response(self):
        """Sample LLM response."""
        return {
            "success": True,
            "answer": "Machine learning is indeed a subset of artificial intelligence that focuses on training algorithms to learn from data and make predictions or decisions without being explicitly programmed for each task.",
            "provider": "openai",
            "model": "gpt-4o-mini",
            "token_usage": {"total": 95, "prompt": 70, "completion": 25},
            "response_time_ms": 1200
        }
    
    @pytest.mark.asyncio
    async def test_successful_rag_query(
        self, mock_vector_service, mock_collection_service, mock_llm_service,
        sample_vector_results, sample_llm_response
    ):
        """Test successful RAG query with vector search and LLM response."""
        # Arrange
        with patch('application_layer.rag_query.search_vectors_use_case') as mock_search:
            mock_search.return_value = [
                {
                    **sample_vector_results[0].model_dump(),
                    "similarity_score": sample_vector_results[0].score
                }
            ]
            mock_llm_service.generate_response.return_value = sample_llm_response
            
            request = RAGQueryRequest(
                query="What is machine learning?",
                collection_name="ai_docs",
                max_chunks=3,
                similarity_threshold=0.8
            )
            
            # Act
            with patch('time.time', side_effect=[1000.0, 1001.2]):  # 1.2 second duration
                response = await rag_query_use_case(
                    vector_service=mock_vector_service,
                    collection_service=mock_collection_service,
                    llm_service=mock_llm_service,
                    request=request
                )
            
            # Assert - Response structure
            assert response.success is True
            assert "Machine learning is indeed a subset" in response.answer
            assert len(response.sources) == 1
            assert response.sources[0]["similarity_score"] == 0.85
            assert response.error is None
            
            # Assert - Metadata
            assert response.metadata["chunks_used"] == 1
            assert response.metadata["collection_searched"] == "ai_docs"
            assert response.metadata["llm_provider"] == "openai"
            assert response.metadata["response_time_ms"] == 1200
            
            # Assert - Service calls
            mock_search.assert_called_once_with(
                vector_service=mock_vector_service,
                collection_service=mock_collection_service,
                query="What is machine learning?",
                collection_name="ai_docs",
                limit=3,
                similarity_threshold=0.8
            )
            
            mock_llm_service.generate_response.assert_called_once()
            llm_call_args = mock_llm_service.generate_response.call_args
            assert "What is machine learning?" in llm_call_args.kwargs['query']
            assert "Machine learning is a subset" in llm_call_args.kwargs['context']
    
    @pytest.mark.asyncio
    async def test_rag_query_no_collection(
        self, mock_vector_service, mock_collection_service, mock_llm_service,
        sample_vector_results, sample_llm_response
    ):
        """Test RAG query without specifying collection."""
        # Arrange
        with patch('application_layer.rag_query.search_vectors_use_case') as mock_search:
            mock_search.return_value = [
                {
                    **sample_vector_results[0].model_dump(),
                    "similarity_score": sample_vector_results[0].score
                }
            ]
            mock_llm_service.generate_response.return_value = sample_llm_response
            
            request = RAGQueryRequest(query="What is AI?")
            
            # Act
            response = await rag_query_use_case(
                vector_service=mock_vector_service,
                collection_service=mock_collection_service,
                llm_service=mock_llm_service,
                request=request
            )
            
            # Assert
            assert response.success is True
            assert response.metadata["collection_searched"] is None
            
            # Assert vector search called with None collection
            mock_search.assert_called_once_with(
                vector_service=mock_vector_service,
                collection_service=mock_collection_service,
                query="What is AI?",
                collection_name=None,
                limit=5,
                similarity_threshold=0.7
            )
    
    @pytest.mark.asyncio
    async def test_rag_query_no_vector_results(
        self, mock_vector_service, mock_collection_service, mock_llm_service
    ):
        """Test RAG query when vector search returns no results."""
        # Arrange
        with patch('application_layer.rag_query.search_vectors_use_case') as mock_search:
            mock_search.return_value = []  # No results
            
            request = RAGQueryRequest(query="What is quantum computing?")
            
            # Act
            response = await rag_query_use_case(
                vector_service=mock_vector_service,
                collection_service=mock_collection_service,
                llm_service=mock_llm_service,
                request=request
            )
            
            # Assert
            assert response.success is False
            assert response.answer is None
            assert response.sources == []
            assert "No relevant information found" in response.error
            assert response.metadata["chunks_used"] == 0
    
    @pytest.mark.asyncio
    async def test_rag_query_vector_search_validation_error(
        self, mock_vector_service, mock_collection_service, mock_llm_service
    ):
        """Test RAG query with vector search validation error."""
        # Arrange
        with patch('application_layer.rag_query.search_vectors_use_case') as mock_search:
            mock_search.side_effect = ValidationError("MISSING_QUERY", "Query parameter is required")
            
            request = RAGQueryRequest(query="test")
            
            # Act & Assert
            with pytest.raises(RAGValidationError) as exc_info:
                await rag_query_use_case(
                    vector_service=mock_vector_service,
                    collection_service=mock_collection_service,
                    llm_service=mock_llm_service,
                    request=request
                )
            
            assert "Query parameter is required" in str(exc_info.value)
            assert exc_info.value.code == "MISSING_QUERY"
    
    @pytest.mark.asyncio
    async def test_rag_query_vector_service_unavailable(
        self, mock_vector_service, mock_collection_service, mock_llm_service
    ):
        """Test RAG query when vector service is unavailable."""
        # Arrange
        with patch('application_layer.rag_query.search_vectors_use_case') as mock_search:
            mock_search.side_effect = RuntimeError("Vector sync service is not available")
            
            request = RAGQueryRequest(query="test")
            
            # Act & Assert
            with pytest.raises(RAGUnavailableError) as exc_info:
                await rag_query_use_case(
                    vector_service=mock_vector_service,
                    collection_service=mock_collection_service,
                    llm_service=mock_llm_service,
                    request=request
                )
            
            assert "Vector sync service is not available" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_rag_query_llm_unavailable_graceful_degradation(
        self, mock_vector_service, mock_collection_service, mock_llm_service,
        sample_vector_results
    ):
        """Test RAG query graceful degradation when LLM is unavailable."""
        # Arrange
        with patch('application_layer.rag_query.search_vectors_use_case') as mock_search:
            mock_search.return_value = [
                {
                    **sample_vector_results[0].model_dump(),
                    "similarity_score": sample_vector_results[0].score
                }
            ]
            mock_llm_service.generate_response.side_effect = LLMUnavailableError(
                "OpenAI API connection failed", provider="openai"
            )
            
            request = RAGQueryRequest(query="What is machine learning?")
            
            # Act
            response = await rag_query_use_case(
                vector_service=mock_vector_service,
                collection_service=mock_collection_service,
                llm_service=mock_llm_service,
                request=request
            )
            
            # Assert - Graceful degradation to vector search only
            assert response.success is True
            assert response.answer is None  # No LLM-generated answer
            assert len(response.sources) == 1  # But vector results are returned
            assert "LLM temporarily unavailable" in response.error
            assert response.metadata["llm_provider"] is None
    
    @pytest.mark.asyncio
    async def test_rag_query_llm_rate_limit_error(
        self, mock_vector_service, mock_collection_service, mock_llm_service,
        sample_vector_results
    ):
        """Test RAG query handling of LLM rate limit errors."""
        # Arrange
        with patch('application_layer.rag_query.search_vectors_use_case') as mock_search:
            mock_search.return_value = [
                {
                    **sample_vector_results[0].model_dump(),
                    "similarity_score": sample_vector_results[0].score
                }
            ]
            mock_llm_service.generate_response.side_effect = LLMRateLimitError(
                "Rate limit exceeded", provider="openai", retry_after=60
            )
            
            request = RAGQueryRequest(query="What is AI?")
            
            # Act
            response = await rag_query_use_case(
                vector_service=mock_vector_service,
                collection_service=mock_collection_service,
                llm_service=mock_llm_service,
                request=request
            )
            
            # Assert - Rate limit handled gracefully
            assert response.success is True
            assert response.answer is None
            assert len(response.sources) == 1
            assert "Rate limit exceeded" in response.error
            assert "retry after 60 seconds" in response.error.lower()
    
    @pytest.mark.asyncio
    async def test_rag_query_multiple_vector_results(
        self, mock_vector_service, mock_collection_service, mock_llm_service,
        sample_llm_response
    ):
        """Test RAG query with multiple vector search results."""
        # Arrange
        with patch('application_layer.rag_query.search_vectors_use_case') as mock_search:
            # Multiple vector results
            vector_results = [
                {
                    "content": "AI is artificial intelligence",
                    "similarity_score": 0.9,
                    "metadata": {"source": "ai_basics.md"},
                    "collection_name": "docs",
                    "file_path": "ai_basics.md"
                },
                {
                    "content": "Machine learning is a subset of AI",
                    "similarity_score": 0.85,
                    "metadata": {"source": "ml_intro.md"},
                    "collection_name": "docs", 
                    "file_path": "ml_intro.md"
                },
                {
                    "content": "Deep learning uses neural networks",
                    "similarity_score": 0.8,
                    "metadata": {"source": "deep_learning.md"},
                    "collection_name": "docs",
                    "file_path": "deep_learning.md"
                }
            ]
            
            mock_search.return_value = vector_results
            mock_llm_service.generate_response.return_value = sample_llm_response
            
            request = RAGQueryRequest(query="What is AI?", max_chunks=3)
            
            # Act
            response = await rag_query_use_case(
                vector_service=mock_vector_service,
                collection_service=mock_collection_service,
                llm_service=mock_llm_service,
                request=request
            )
            
            # Assert
            assert response.success is True
            assert len(response.sources) == 3
            assert response.sources[0]["similarity_score"] == 0.9
            assert response.sources[1]["similarity_score"] == 0.85
            assert response.sources[2]["similarity_score"] == 0.8
            assert response.metadata["chunks_used"] == 3
            
            # Assert LLM received combined context
            llm_call_args = mock_llm_service.generate_response.call_args
            context = llm_call_args.kwargs['context']
            assert "AI is artificial intelligence" in context
            assert "Machine learning is a subset" in context
            assert "Deep learning uses neural networks" in context
    
    @pytest.mark.asyncio
    async def test_rag_query_collection_not_found(
        self, mock_vector_service, mock_collection_service, mock_llm_service
    ):
        """Test RAG query when specified collection doesn't exist."""
        # Arrange
        with patch('application_layer.rag_query.search_vectors_use_case') as mock_search:
            mock_search.side_effect = Exception("Collection 'nonexistent' not found")
            
            request = RAGQueryRequest(query="test", collection_name="nonexistent")
            
            # Act & Assert
            with pytest.raises(RAGError) as exc_info:
                await rag_query_use_case(
                    vector_service=mock_vector_service,
                    collection_service=mock_collection_service,
                    llm_service=mock_llm_service,
                    request=request
                )
            
            assert "Collection 'nonexistent' not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_rag_query_performance_metadata(
        self, mock_vector_service, mock_collection_service, mock_llm_service,
        sample_vector_results, sample_llm_response
    ):
        """Test RAG query performance metadata tracking."""
        # Arrange
        with patch('application_layer.rag_query.search_vectors_use_case') as mock_search:
            mock_search.return_value = [
                {
                    **sample_vector_results[0].model_dump(),
                    "similarity_score": sample_vector_results[0].score
                }
            ]
            mock_llm_service.generate_response.return_value = sample_llm_response
            
            request = RAGQueryRequest(query="Performance test")
            
            # Act
            with patch('time.time', side_effect=[1000.0, 1001.5]):  # 1.5 second duration
                response = await rag_query_use_case(
                    vector_service=mock_vector_service,
                    collection_service=mock_collection_service,
                    llm_service=mock_llm_service,
                    request=request
                )
            
            # Assert performance tracking
            assert response.metadata["response_time_ms"] == 1500
            assert response.metadata["chunks_used"] == 1
            assert response.metadata["llm_provider"] == "openai"


class TestRAGErrorHandling:
    """Test RAG error hierarchy and handling."""
    
    def test_rag_error_base(self):
        """Test base RAG error."""
        error = RAGError("Test RAG error")
        
        assert str(error) == "Test RAG error"
        assert isinstance(error, Exception)
    
    def test_rag_validation_error(self):
        """Test RAG validation error."""
        error = RAGValidationError("Invalid input", code="INVALID_QUERY", details={"field": "query"})
        
        assert str(error) == "Invalid input"
        assert error.code == "INVALID_QUERY"
        assert error.details["field"] == "query"
        assert isinstance(error, RAGError)
    
    def test_rag_unavailable_error(self):
        """Test RAG unavailable error."""
        error = RAGUnavailableError("Service down", service="vector")
        
        assert str(error) == "Service down"
        assert error.service == "vector"
        assert isinstance(error, RAGError)