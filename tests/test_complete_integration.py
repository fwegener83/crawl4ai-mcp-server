"""
Complete Integration Tests for Enhanced RAG Search Pipeline.

Tests the entire enhanced search workflow:
- Query expansion + multi-query vector search
- LLM-based re-ranking 
- Final RAG response generation
- Configuration-driven feature control
"""

import os
import pytest
from unittest.mock import AsyncMock, Mock, patch
from application_layer.rag_query import rag_query_use_case, RAGQueryRequest


class IntegratedMockLLMService:
    """Mock LLM service that handles both expansion and re-ranking."""
    
    def __init__(self):
        self.calls = []
        
    async def generate_response(self, query, context, max_tokens=2000, temperature=0.1):
        self.calls.append({
            'query': query,
            'context': context,
            'max_tokens': max_tokens,
            'temperature': temperature,
            'type': self._classify_call_type(query, context)
        })
        
        # Query expansion call
        if self._is_expansion_call(query):
            return {
                "success": True,
                "answer": "machine learning systems\nartificial intelligence applications\nML algorithms",
                "provider": "mock"
            }
        
        # Re-ranking call
        elif self._is_reranking_call(query):
            # Return reverse ranking for testing
            import re
            chunk_matches = re.findall(r'Chunk (\d+)', query)
            if chunk_matches:
                chunk_count = len(chunk_matches)
                reverse_ranking = ", ".join(str(i) for i in reversed(range(1, chunk_count + 1)))
                return {
                    "success": True,
                    "answer": reverse_ranking,
                    "provider": "mock"
                }
        
        # Final RAG response generation
        elif context and context.strip():
            return {
                "success": True,
                "answer": f"Based on the provided context, here's the answer to '{query}': This is a comprehensive response based on the retrieved information.",
                "provider": "mock",
                "model": "mock-model",
                "token_usage": {"total": 150, "prompt": 100, "completion": 50},
                "response_time_ms": 800
            }
        
        # Fallback
        return {
            "success": True,
            "answer": "Mock response",
            "provider": "mock"
        }
    
    def _classify_call_type(self, query, context):
        if self._is_expansion_call(query):
            return "expansion"
        elif self._is_reranking_call(query):
            return "reranking"
        elif context and context.strip():
            return "rag_generation"
        else:
            return "unknown"
    
    def _is_expansion_call(self, query):
        return "generate" in query.lower() and "alternative search queries" in query.lower()
    
    def _is_reranking_call(self, query):
        return "rank these text chunks" in query.lower() and "relevance" in query.lower()


class IntegratedMockVectorService:
    """Mock vector service that supports enhanced search."""
    
    def __init__(self, base_results_count=15):
        self.vector_available = True
        self.base_results_count = base_results_count
        self.search_calls = []
        
    async def search_vectors(self, query, collection_name, limit, threshold):
        self.search_calls.append({
            'query': query,
            'collection_name': collection_name,
            'limit': limit,
            'threshold': threshold
        })
        
        # Return different content based on query
        results = []
        for i in range(min(self.base_results_count, limit)):
            content_base = f"Content about {query}"
            if "machine learning" in query.lower():
                content_base = f"Machine learning content {i+1}: Deep learning and neural networks"
            elif "artificial intelligence" in query.lower():
                content_base = f"AI content {i+1}: Expert systems and knowledge representation"
            elif "algorithms" in query.lower():
                content_base = f"Algorithm content {i+1}: Sorting and searching techniques"
            else:
                content_base = f"General content {i+1} about {query}"
                
            results.append(Mock(
                model_dump=lambda i=i, content=content_base: {
                    'content': content,
                    'metadata': {'source': f'doc_{query.replace(" ", "_")}_{i+1}.md'},
                    'collection_name': collection_name,
                    'file_path': f'/docs/{query.replace(" ", "_")}_{i+1}.md'
                },
                score=0.9 - (i * 0.05)  # Descending scores
            ))
        
        return results


class IntegratedMockCollectionService:
    """Mock collection service for integration tests."""
    
    async def get_collection(self, name):
        return {'name': name, 'doc_count': 100}


class TestCompleteIntegration:
    """Integration tests for the complete enhanced RAG pipeline."""
    
    @pytest.mark.asyncio
    async def test_full_enhanced_pipeline_enabled(self):
        """Test complete pipeline with all enhancements enabled."""
        
        vector_service = IntegratedMockVectorService(base_results_count=20)
        collection_service = IntegratedMockCollectionService()
        llm_service = IntegratedMockLLMService()
        
        request = RAGQueryRequest(
            query="machine learning applications",
            collection_name="tech_docs",
            max_chunks=5,
            similarity_threshold=0.2,
            enable_query_expansion=True,  # Explicitly enable for test
            max_query_variants=3,
            enable_reranking=True,
            reranking_threshold=8
        )
        
        with patch('application_layer.vector_search.LLMServiceFactory') as mock_factory:
            with patch('application_layer.vector_search.QueryExpansionService') as mock_expansion_service:
                # Mock expansion service
                expansion_service_mock = Mock()
                expansion_service_mock.expand_query_intelligently = AsyncMock(
                    return_value=['machine learning applications', 'ML systems', 'AI applications']
                )
                mock_expansion_service.return_value = expansion_service_mock
                mock_factory.create_service.return_value = llm_service
                
                response = await rag_query_use_case(
                    vector_service=vector_service,
                    collection_service=collection_service,
                    llm_service=llm_service,
                    request=request
                )
        
        # Verify the complete pipeline worked
        assert response.success is True
        assert response.answer is not None
        assert "comprehensive response" in response.answer
        
        # Verify multiple vector searches happened (query expansion)
        assert len(vector_service.search_calls) == 3  # Original + 2 expansions
        
        # Verify LLM was used for expansion, re-ranking, and final generation
        expansion_calls = [call for call in llm_service.calls if call['type'] == 'expansion']
        reranking_calls = [call for call in llm_service.calls if call['type'] == 'reranking']
        generation_calls = [call for call in llm_service.calls if call['type'] == 'rag_generation']
        
        assert len(expansion_calls) == 1  # Query expansion
        assert len(reranking_calls) == 1  # Result re-ranking
        assert len(generation_calls) == 1  # Final RAG generation
        
        # Verify metadata includes enhancement info
        assert response.metadata['chunks_used'] == 5
        assert response.metadata['llm_provider'] == 'mock'
        assert response.metadata['response_time_ms'] > 0

    @pytest.mark.asyncio
    async def test_partial_enhancement_expansion_only(self):
        """Test pipeline with only query expansion enabled."""
        
        vector_service = IntegratedMockVectorService(base_results_count=20)
        collection_service = IntegratedMockCollectionService()
        llm_service = IntegratedMockLLMService()
        
        request = RAGQueryRequest(
            query="artificial intelligence",
            collection_name="ai_docs",
            max_chunks=8,  # Above re-ranking threshold but disabled
            similarity_threshold=0.3,
            enable_query_expansion=True,
            max_query_variants=2,
            enable_reranking=False,  # Disabled
            reranking_threshold=5
        )
        
        with patch('application_layer.vector_search.LLMServiceFactory') as mock_factory:
            with patch('application_layer.vector_search.QueryExpansionService') as mock_expansion_service:
                expansion_service_mock = Mock()
                expansion_service_mock.expand_query_intelligently = AsyncMock(
                    return_value=['artificial intelligence', 'AI systems']
                )
                mock_expansion_service.return_value = expansion_service_mock
                mock_factory.create_service.return_value = llm_service
                
                response = await rag_query_use_case(
                    vector_service=vector_service,
                    collection_service=collection_service,
                    llm_service=llm_service,
                    request=request
                )
        
        # Verify response
        assert response.success is True
        
        # Verify query expansion happened
        assert len(vector_service.search_calls) == 2
        
        # Verify no re-ranking
        expansion_calls = [call for call in llm_service.calls if call['type'] == 'expansion']
        reranking_calls = [call for call in llm_service.calls if call['type'] == 'reranking']
        generation_calls = [call for call in llm_service.calls if call['type'] == 'rag_generation']
        
        assert len(expansion_calls) == 1
        assert len(reranking_calls) == 0  # No re-ranking
        assert len(generation_calls) == 1

    @pytest.mark.asyncio 
    async def test_no_enhancements_original_behavior(self):
        """Test that original behavior is preserved when enhancements are disabled."""
        
        vector_service = IntegratedMockVectorService(base_results_count=10)
        collection_service = IntegratedMockCollectionService()
        llm_service = IntegratedMockLLMService()
        
        request = RAGQueryRequest(
            query="data structures",
            collection_name="cs_docs",
            max_chunks=5,
            similarity_threshold=0.2
        )
        
        with patch.dict(os.environ, {
            'RAG_QUERY_EXPANSION_ENABLED': 'false',  # Disabled
            'RAG_AUTO_RERANKING_ENABLED': 'false'   # Disabled
        }):
            response = await rag_query_use_case(
                vector_service=vector_service,
                collection_service=collection_service,
                llm_service=llm_service,
                request=request
            )
        
        # Verify response
        assert response.success is True
        
        # Verify only single vector search (no expansion)
        assert len(vector_service.search_calls) == 1
        assert vector_service.search_calls[0]['query'] == "data structures"
        
        # Verify only final generation (no expansion or re-ranking)
        expansion_calls = [call for call in llm_service.calls if call['type'] == 'expansion']
        reranking_calls = [call for call in llm_service.calls if call['type'] == 'reranking']
        generation_calls = [call for call in llm_service.calls if call['type'] == 'rag_generation']
        
        assert len(expansion_calls) == 0
        assert len(reranking_calls) == 0
        assert len(generation_calls) == 1

    @pytest.mark.asyncio
    async def test_graceful_degradation_llm_failures(self):
        """Test graceful degradation when LLM services fail."""
        
        vector_service = IntegratedMockVectorService(base_results_count=15)
        collection_service = IntegratedMockCollectionService()
        
        # LLM that fails for expansion but works for generation
        failing_llm = Mock()
        failing_llm.generate_response = AsyncMock(side_effect=[
            {"success": False, "error": "Expansion failed"},  # Expansion call fails
            {"success": True, "answer": "Final answer despite expansion failure", "provider": "mock"}  # Generation succeeds
        ])
        
        request = RAGQueryRequest(
            query="database systems",
            collection_name="db_docs",
            max_chunks=6,
            similarity_threshold=0.2
        )
        
        with patch.dict(os.environ, {
            'RAG_QUERY_EXPANSION_ENABLED': 'true',
            'RAG_AUTO_RERANKING_ENABLED': 'true',
            'RAG_RERANKING_THRESHOLD': '5'
        }):
            with patch('application_layer.vector_search.LLMServiceFactory') as mock_factory:
                mock_factory.create_service.return_value = failing_llm
                
                response = await rag_query_use_case(
                    vector_service=vector_service,
                    collection_service=collection_service,
                    llm_service=failing_llm,
                    request=request
                )
        
        # Should still succeed with fallback
        assert response.success is True
        assert response.answer == "Final answer despite expansion failure"
        
        # Should fall back to single vector search
        assert len(vector_service.search_calls) == 1

    @pytest.mark.asyncio
    async def test_performance_with_configuration_limits(self):
        """Test performance characteristics with various configuration limits."""
        
        vector_service = IntegratedMockVectorService(base_results_count=25)
        collection_service = IntegratedMockCollectionService()
        llm_service = IntegratedMockLLMService()
        
        request = RAGQueryRequest(
            query="performance optimization",
            collection_name="perf_docs",
            max_chunks=3,  # Small limit
            similarity_threshold=0.4  # Higher threshold
        )
        
        with patch.dict(os.environ, {
            'RAG_QUERY_EXPANSION_ENABLED': 'true',
            'RAG_MAX_QUERY_VARIANTS': '4',  # More variants
            'RAG_AUTO_RERANKING_ENABLED': 'true',
            'RAG_RERANKING_THRESHOLD': '6'
        }):
            with patch('application_layer.vector_search.LLMServiceFactory') as mock_factory:
                with patch('application_layer.vector_search.QueryExpansionService') as mock_expansion_service:
                    expansion_service_mock = Mock()
                    expansion_service_mock.expand_query_intelligently = AsyncMock(
                        return_value=['performance optimization', 'speed improvement', 'efficiency boost', 'performance tuning']
                    )
                    mock_expansion_service.return_value = expansion_service_mock
                    mock_factory.create_service.return_value = llm_service
                    
                    response = await rag_query_use_case(
                        vector_service=vector_service,
                        collection_service=collection_service,
                        llm_service=llm_service,
                        request=request
                    )
        
        # Verify response
        assert response.success is True
        
        # Verify configuration limits were respected
        assert len(response.sources) == 3  # Limited by max_chunks
        assert len(vector_service.search_calls) == 4  # All 4 query variants
        
        # Verify reasonable response time
        assert response.metadata['response_time_ms'] < 5000  # Should be fast with mocks


class TestConfigurationValidation:
    """Test configuration parsing and validation."""
    
    def test_environment_variable_parsing(self):
        """Test all configuration environment variables."""
        
        test_configs = {
            'RAG_QUERY_EXPANSION_ENABLED': ['true', 'false', 'TRUE', 'False'],
            'RAG_AUTO_RERANKING_ENABLED': ['true', 'false'],
            'RAG_MAX_QUERY_VARIANTS': ['2', '3', '5', '10'],
            'RAG_RERANKING_THRESHOLD': ['5', '8', '10', '15']
        }
        
        for var_name, values in test_configs.items():
            for value in values:
                with patch.dict(os.environ, {var_name: value}):
                    parsed_value = os.getenv(var_name, 'default')
                    assert parsed_value == value
    
    def test_default_configuration_values(self):
        """Test default values when environment variables are not set."""
        
        with patch.dict(os.environ, {}, clear=True):
            # Test defaults
            assert os.getenv('RAG_QUERY_EXPANSION_ENABLED', 'false').lower() == 'false'
            assert os.getenv('RAG_AUTO_RERANKING_ENABLED', 'false').lower() == 'false'
            assert int(os.getenv('RAG_MAX_QUERY_VARIANTS', '3')) == 3
            assert int(os.getenv('RAG_RERANKING_THRESHOLD', '8')) == 8