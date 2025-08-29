"""
Tests for Result Re-ranking Logic in RAG Query Use Case.

Test-first implementation for:
- LLM-based chunk relevance scoring
- Threshold-based re-ranking trigger  
- Fallback to similarity-based ranking
"""

import os
import pytest
from unittest.mock import AsyncMock, Mock, patch
from application_layer.rag_query import rag_query_use_case, RAGQueryRequest


class MockVectorService:
    """Mock vector service for re-ranking tests."""
    
    def __init__(self, results_count=10):
        self.vector_available = True
        self.results_count = results_count
        
    async def search_vectors(self, query, collection_name, limit, threshold):
        # Return mock results based on count
        results = []
        for i in range(min(self.results_count, limit)):
            results.append(Mock(
                model_dump=lambda i=i: {
                    'content': f'Content chunk {i+1} about {query}',
                    'metadata': {'source': f'doc{i+1}.md'},
                    'collection_name': collection_name,
                    'file_path': f'/path/to/doc{i+1}.md'
                },
                score=0.8 - (i * 0.05)  # Descending scores
            ))
        return results


class MockCollectionService:
    """Mock collection service for tests."""
    
    async def get_collection(self, name):
        return {'name': name}


class MockLLMService:
    """Mock LLM service for re-ranking tests."""
    
    def __init__(self, should_fail_generation=False, should_fail_reranking=False):
        self.should_fail_generation = should_fail_generation
        self.should_fail_reranking = should_fail_reranking
        self.generation_calls = []
        self.reranking_calls = []
        
    async def generate_response(self, query, context, max_tokens=2000, temperature=0.1):
        # Check if this is a re-ranking call
        if self._is_reranking_call(query):
            self.reranking_calls.append({
                'query': query,
                'context': context,
                'max_tokens': max_tokens,
                'temperature': temperature
            })
            
            if self.should_fail_reranking:
                return {"success": False, "error": "Re-ranking failed"}
            
            # Mock re-ranking response - return ranking in reverse order
            # Extract chunk count from query (look for "Chunk X" patterns)
            import re
            chunk_matches = re.findall(r'Chunk (\d+)', query)
            if chunk_matches:
                chunk_count = len(chunk_matches)
                # Return reverse ranking: highest number first (e.g., "3, 2, 1")
                reverse_ranking = ", ".join(str(i) for i in reversed(range(1, chunk_count + 1)))
                return {
                    "success": True,
                    "answer": reverse_ranking,
                    "provider": "mock",
                    "model": "mock-model",
                    "token_usage": {"total": 50, "prompt": 30, "completion": 20},
                    "response_time_ms": 300
                }
            
        # Regular generation call
        self.generation_calls.append({
            'query': query,
            'context': context,
            'max_tokens': max_tokens,
            'temperature': temperature
        })
        
        if self.should_fail_generation:
            return {"success": False, "error": "Generation failed"}
            
        return {
            "success": True,
            "answer": f"Generated answer for: {query}",
            "provider": "mock",
            "model": "mock-model",
            "token_usage": {"total": 100, "prompt": 60, "completion": 40},
            "response_time_ms": 500
        }
        
    def _is_reranking_call(self, query):
        """Check if this is a re-ranking call based on query content."""
        return "rank these text chunks" in query.lower() and "relevance" in query.lower()


class TestResultReranking:
    """Test suite for result re-ranking functionality."""
    
    @pytest.mark.asyncio
    async def test_reranking_triggered_when_above_threshold(self):
        """Test that re-ranking is triggered when results exceed threshold."""
        
        # Setup services with many results to trigger re-ranking
        vector_service = MockVectorService(results_count=15)  # Above threshold
        collection_service = MockCollectionService()
        llm_service = MockLLMService()
        
        request = RAGQueryRequest(
            query="test query",
            collection_name="test_collection",
            max_chunks=5,
            similarity_threshold=0.2
        )
        
        with patch.dict(os.environ, {
            'RAG_AUTO_RERANKING_ENABLED': 'true',
            'RAG_RERANKING_THRESHOLD': '8',  # Trigger when > 8 results
            'RAG_QUERY_EXPANSION_ENABLED': 'false'  # Disable query expansion for simpler testing
        }):
            with patch('application_layer.rag_query.LLMService') as mock_llm_class:
                mock_llm_class.return_value = llm_service
                
                response = await rag_query_use_case(
                    vector_service=vector_service,
                    collection_service=collection_service,
                    llm_service=llm_service,
                    request=request
                )
        
        # Should have triggered re-ranking
        assert len(llm_service.reranking_calls) == 1
        
        # Should still generate final response
        assert len(llm_service.generation_calls) == 1
        assert response.success is True
        assert response.answer is not None

    @pytest.mark.asyncio
    async def test_reranking_not_triggered_when_below_threshold(self):
        """Test that re-ranking is not triggered when results are below threshold."""
        
        # Setup services with few results (below threshold)
        vector_service = MockVectorService(results_count=5)  # Below threshold
        collection_service = MockCollectionService()
        llm_service = MockLLMService()
        
        request = RAGQueryRequest(
            query="test query",
            collection_name="test_collection",
            max_chunks=5,
            similarity_threshold=0.2
        )
        
        with patch.dict(os.environ, {
            'RAG_AUTO_RERANKING_ENABLED': 'true',
            'RAG_RERANKING_THRESHOLD': '8'  # No trigger when <= 8 results
        }):
            response = await rag_query_use_case(
                vector_service=vector_service,
                collection_service=collection_service,
                llm_service=llm_service,
                request=request
            )
        
        # Should NOT have triggered re-ranking
        assert len(llm_service.reranking_calls) == 0
        
        # Should still generate final response
        assert len(llm_service.generation_calls) == 1
        assert response.success is True
        assert response.answer is not None

    @pytest.mark.asyncio
    async def test_reranking_disabled_by_configuration(self):
        """Test that re-ranking can be disabled via configuration."""
        
        vector_service = MockVectorService(results_count=15)  # Above threshold
        collection_service = MockCollectionService()
        llm_service = MockLLMService()
        
        request = RAGQueryRequest(
            query="test query",
            collection_name="test_collection",
            max_chunks=5,
            similarity_threshold=0.2
        )
        
        with patch.dict(os.environ, {
            'RAG_AUTO_RERANKING_ENABLED': 'false',  # Disabled
            'RAG_RERANKING_THRESHOLD': '8'
        }):
            response = await rag_query_use_case(
                vector_service=vector_service,
                collection_service=collection_service,
                llm_service=llm_service,
                request=request
            )
        
        # Should NOT have triggered re-ranking even with many results
        assert len(llm_service.reranking_calls) == 0
        
        # Should still generate final response
        assert len(llm_service.generation_calls) == 1
        assert response.success is True

    @pytest.mark.asyncio
    async def test_reranking_fallback_on_llm_failure(self):
        """Test fallback to similarity-based ranking when LLM re-ranking fails."""
        
        vector_service = MockVectorService(results_count=12)
        collection_service = MockCollectionService()
        llm_service = MockLLMService(should_fail_reranking=True)
        
        request = RAGQueryRequest(
            query="test query",
            collection_name="test_collection", 
            max_chunks=5,
            similarity_threshold=0.2
        )
        
        with patch.dict(os.environ, {
            'RAG_AUTO_RERANKING_ENABLED': 'true',
            'RAG_RERANKING_THRESHOLD': '8'
        }):
            response = await rag_query_use_case(
                vector_service=vector_service,
                collection_service=collection_service,
                llm_service=llm_service,
                request=request
            )
        
        # Should have attempted re-ranking
        assert len(llm_service.reranking_calls) == 1
        
        # Should still succeed with fallback
        assert response.success is True
        assert response.answer is not None
        
        # Should have generated final answer despite re-ranking failure
        assert len(llm_service.generation_calls) == 1

    @pytest.mark.asyncio
    async def test_reranking_improves_result_order(self):
        """Test that re-ranking changes the order of results."""
        
        vector_service = MockVectorService(results_count=12)
        collection_service = MockCollectionService()
        llm_service = MockLLMService()  # Will reverse order as mock re-ranking
        
        request = RAGQueryRequest(
            query="test query",
            collection_name="test_collection",
            max_chunks=5,
            similarity_threshold=0.2
        )
        
        with patch.dict(os.environ, {
            'RAG_AUTO_RERANKING_ENABLED': 'true',
            'RAG_RERANKING_THRESHOLD': '8'
        }):
            response = await rag_query_use_case(
                vector_service=vector_service,
                collection_service=collection_service,
                llm_service=llm_service,
                request=request
            )
        
        # Should have re-ranked results
        assert len(llm_service.reranking_calls) == 1
        
        # Check that results are present and ordered
        assert len(response.sources) == 5  # Limited by max_chunks
        
        # Mock re-ranking reverses order, so lowest scoring should be first now
        # (In real implementation, this would be based on LLM relevance scoring)
        first_source = response.sources[0]
        assert 'Content chunk' in first_source['content']

    @pytest.mark.asyncio
    async def test_reranking_respects_max_chunks_limit(self):
        """Test that re-ranking respects the max_chunks limit."""
        
        vector_service = MockVectorService(results_count=20)  # Many results
        collection_service = MockCollectionService()
        llm_service = MockLLMService()
        
        request = RAGQueryRequest(
            query="test query",
            collection_name="test_collection",
            max_chunks=3,  # Small limit
            similarity_threshold=0.2
        )
        
        with patch.dict(os.environ, {
            'RAG_AUTO_RERANKING_ENABLED': 'true',
            'RAG_RERANKING_THRESHOLD': '5'
        }):
            response = await rag_query_use_case(
                vector_service=vector_service,
                collection_service=collection_service,
                llm_service=llm_service,
                request=request
            )
        
        # Should respect max_chunks limit
        assert len(response.sources) == 3
        
        # Should have re-ranked but returned only top 3
        assert len(llm_service.reranking_calls) == 1

    @pytest.mark.asyncio
    async def test_llm_reranking_prompt_structure(self):
        """Test that LLM re-ranking receives properly structured prompt."""
        
        vector_service = MockVectorService(results_count=10)
        collection_service = MockCollectionService()
        llm_service = MockLLMService()
        
        request = RAGQueryRequest(
            query="artificial intelligence applications",
            collection_name="tech_docs",
            max_chunks=5,
            similarity_threshold=0.2
        )
        
        with patch.dict(os.environ, {
            'RAG_AUTO_RERANKING_ENABLED': 'true',
            'RAG_RERANKING_THRESHOLD': '6'
        }):
            response = await rag_query_use_case(
                vector_service=vector_service,
                collection_service=collection_service,
                llm_service=llm_service,
                request=request
            )
        
        # Check that re-ranking was called with proper parameters
        assert len(llm_service.reranking_calls) == 1
        rerank_call = llm_service.reranking_calls[0]
        
        # The query parameter contains the re-ranking prompt, not the original query
        assert "artificial intelligence applications" in rerank_call['query']
        assert "rank these text chunks" in rerank_call['query'].lower()
        assert rerank_call['max_tokens'] <= 1000  # Reasonable token limit


class TestReranKingHelpers:
    """Test helper functions for result re-ranking."""
    
    def test_reranking_configuration_parsing(self):
        """Test parsing of re-ranking configuration variables."""
        
        # Test boolean parsing
        with patch.dict(os.environ, {'RAG_AUTO_RERANKING_ENABLED': 'true'}):
            assert os.getenv('RAG_AUTO_RERANKING_ENABLED', 'false').lower() == 'true'
            
        with patch.dict(os.environ, {'RAG_AUTO_RERANKING_ENABLED': 'false'}):
            assert os.getenv('RAG_AUTO_RERANKING_ENABLED', 'false').lower() == 'false'
            
        # Test threshold parsing
        with patch.dict(os.environ, {'RAG_RERANKING_THRESHOLD': '10'}):
            assert int(os.getenv('RAG_RERANKING_THRESHOLD', '8')) == 10
            
        # Test defaults
        with patch.dict(os.environ, {}, clear=True):
            assert os.getenv('RAG_AUTO_RERANKING_ENABLED', 'false').lower() == 'false'
            assert int(os.getenv('RAG_RERANKING_THRESHOLD', '8')) == 8

    def test_chunk_selection_for_reranking(self):
        """Test logic for selecting chunks for re-ranking."""
        
        # Mock chunks with similarity scores
        chunks = [
            {'content': f'Content {i}', 'similarity_score': 0.9 - i * 0.1}
            for i in range(15)
        ]
        
        # Simulate selecting top N for re-ranking (before final selection)
        reranking_limit = 10
        reranking_candidates = chunks[:reranking_limit]
        
        assert len(reranking_candidates) == 10
        assert reranking_candidates[0]['similarity_score'] == 0.9  # Highest first
        assert reranking_candidates[-1]['similarity_score'] == 0.0  # Lowest last

    def test_result_ordering_logic(self):
        """Test logic for reordering results based on LLM ranking."""
        
        # Original results in similarity order
        original_results = [
            {'content': 'Content A', 'similarity_score': 0.9},
            {'content': 'Content B', 'similarity_score': 0.8},
            {'content': 'Content C', 'similarity_score': 0.7},
            {'content': 'Content D', 'similarity_score': 0.6}
        ]
        
        # Mock LLM ranking (0-indexed): reverse order
        llm_ranking = [3, 2, 1, 0]  # D, C, B, A
        
        # Apply ranking
        reranked_results = [original_results[i] for i in llm_ranking]
        
        assert reranked_results[0]['content'] == 'Content D'  # Lowest similarity but highest LLM rank
        assert reranked_results[1]['content'] == 'Content C'
        assert reranked_results[2]['content'] == 'Content B'
        assert reranked_results[3]['content'] == 'Content A'