"""
Tests for Enhanced Vector Search Use Case.

Test-first implementation for multi-query orchestration, result deduplication,
and configuration-driven feature toggling in the enhanced vector search.
"""

import os
import pytest
from unittest.mock import AsyncMock, Mock, patch
from application_layer.vector_search import search_vectors_use_case, ValidationError
from services.query_expansion_service import QueryExpansionService


class MockVectorService:
    """Mock vector service for testing."""
    
    def __init__(self, results_per_query=None):
        self.vector_available = True
        self.search_calls = []
        self.results_per_query = results_per_query or {}
        
    async def search_vectors(self, query, collection_name, limit, threshold):
        self.search_calls.append({
            'query': query,
            'collection_name': collection_name,
            'limit': limit,
            'threshold': threshold
        })
        
        # Return predefined results or default mock results
        if query in self.results_per_query:
            return self.results_per_query[query]
        
        # Default mock results
        return [
            Mock(model_dump=lambda: {
                'content': f'Content for {query}',
                'metadata': {'source': f'doc_{query.replace(" ", "_")}.md'},
                'collection_name': collection_name,
                'file_path': f'/path/to/{query.replace(" ", "_")}.md'
            }, score=0.8),
            Mock(model_dump=lambda: {
                'content': f'More content for {query}',
                'metadata': {'source': f'doc2_{query.replace(" ", "_")}.md'},
                'collection_name': collection_name,
                'file_path': f'/path/to/doc2_{query.replace(" ", "_")}.md'
            }, score=0.7)
        ]


class MockCollectionService:
    """Mock collection service for testing."""
    
    def __init__(self, collections=None):
        self.collections = collections or ['test_collection']
        
    async def get_collection(self, name):
        if name not in self.collections:
            raise Exception(f"Collection {name} not found")
        return {'name': name}


class MockQueryExpansionService:
    """Mock query expansion service for testing."""
    
    def __init__(self, expansions=None):
        self.expansions = expansions or {}
        self.call_count = 0
        
    async def expand_query_intelligently(self, query, collection_context=None, max_expansions=3, temperature=0.3):
        self.call_count += 1
        
        if query in self.expansions:
            return self.expansions[query]
            
        # Default expansions
        return [query, f"{query} alternative", f"{query} variant"]


class TestEnhancedVectorSearchUseCase:
    """Test suite for enhanced vector search use case."""
    
    @pytest.mark.asyncio
    async def test_enhanced_search_with_expansion_enabled(self):
        """Test enhanced search when query expansion is enabled."""
        
        # Setup mocks
        vector_service = MockVectorService({
            'machine learning': [Mock(model_dump=lambda: {'content': 'ML content', 'metadata': {'source': 'ml.md'}}, score=0.9)],
            'machine learning alternative': [Mock(model_dump=lambda: {'content': 'ML alt content', 'metadata': {'source': 'ml_alt.md'}}, score=0.8)],
            'machine learning variant': [Mock(model_dump=lambda: {'content': 'ML variant content', 'metadata': {'source': 'ml_var.md'}}, score=0.7)]
        })
        collection_service = MockCollectionService()
        
        with patch.dict(os.environ, {'RAG_QUERY_EXPANSION_ENABLED': 'true'}):
            with patch('application_layer.vector_search.LLMServiceFactory') as mock_llm_factory:
                with patch('application_layer.vector_search.QueryExpansionService') as mock_expansion_class:
                    mock_expansion_service = MockQueryExpansionService({
                        'machine learning': ['machine learning', 'machine learning alternative', 'machine learning variant']
                    })
                    mock_expansion_class.return_value = mock_expansion_service
                    mock_llm_factory.create_service.return_value = Mock()
                
                    results = await search_vectors_use_case(
                        vector_service=vector_service,
                        collection_service=collection_service,
                        query='machine learning',
                        collection_name='test_collection',
                        limit=5,
                        similarity_threshold=0.2
                    )
        
        # Should have called vector search for each expanded query
        assert len(vector_service.search_calls) == 3
        assert vector_service.search_calls[0]['query'] == 'machine learning'
        assert vector_service.search_calls[1]['query'] == 'machine learning alternative'
        assert vector_service.search_calls[2]['query'] == 'machine learning variant'
        
        # Should have expansion service call
        assert mock_expansion_service.call_count == 1
        
        # Results should be deduplicated and combined
        assert len(results) >= 1  # At least some results

    @pytest.mark.asyncio
    async def test_enhanced_search_with_expansion_disabled(self):
        """Test that search works normally when expansion is disabled."""
        
        vector_service = MockVectorService()
        collection_service = MockCollectionService()
        
        with patch.dict(os.environ, {'RAG_QUERY_EXPANSION_ENABLED': 'false'}):
            results = await search_vectors_use_case(
                vector_service=vector_service,
                collection_service=collection_service,
                query='test query',
                collection_name='test_collection',
                limit=5,
                similarity_threshold=0.2
            )
        
        # Should only call vector search once with original query
        assert len(vector_service.search_calls) == 1
        assert vector_service.search_calls[0]['query'] == 'test query'
        
        # Should have normal results
        assert len(results) == 2  # Mock returns 2 results

    @pytest.mark.asyncio
    async def test_result_deduplication(self):
        """Test that duplicate results from different queries are deduplicated."""
        
        # Create identical content from different queries to test deduplication
        duplicate_result = Mock(model_dump=lambda: {
            'content': 'Same content appearing twice',
            'metadata': {'source': 'same_doc.md'},
            'collection_name': 'test_collection'
        }, score=0.8)
        
        vector_service = MockVectorService({
            'original query': [duplicate_result],
            'alternative query': [duplicate_result],  # Same result
            'variant query': [Mock(model_dump=lambda: {
                'content': 'Different content',
                'metadata': {'source': 'different_doc.md'},
                'collection_name': 'test_collection'
            }, score=0.7)]
        })
        collection_service = MockCollectionService()
        
        with patch.dict(os.environ, {'RAG_QUERY_EXPANSION_ENABLED': 'true'}):
            with patch('application_layer.vector_search.LLMServiceFactory') as mock_llm_factory:
                with patch('application_layer.vector_search.QueryExpansionService') as mock_expansion_class:
                    mock_expansion_service = MockQueryExpansionService({
                        'test query': ['original query', 'alternative query', 'variant query']
                    })
                    mock_expansion_class.return_value = mock_expansion_service
                    mock_llm_factory.create_service.return_value = Mock()
                    
                    results = await search_vectors_use_case(
                        vector_service=vector_service,
                        collection_service=collection_service,
                        query='test query',
                        collection_name='test_collection',
                        limit=10,
                        similarity_threshold=0.2
                    )
        
        # Should have deduplicated the identical results
        # We expect 2 unique results (the duplicate + the different one)
        unique_contents = set(result['content'] for result in results)
        assert len(unique_contents) == 2
        assert 'Same content appearing twice' in unique_contents
        assert 'Different content' in unique_contents

    @pytest.mark.asyncio
    async def test_configuration_driven_max_expansions(self):
        """Test that max expansions configuration is respected."""
        
        vector_service = MockVectorService()
        collection_service = MockCollectionService()
        
        with patch.dict(os.environ, {
            'RAG_QUERY_EXPANSION_ENABLED': 'true',
            'RAG_MAX_QUERY_VARIANTS': '2'  # Limit to 2 variants total (original + 1 expansion)
        }):
            with patch('application_layer.vector_search.LLMServiceFactory') as mock_llm_factory:
                with patch('application_layer.vector_search.QueryExpansionService') as mock_expansion_class:
                    mock_expansion_service = MockQueryExpansionService({
                        'test': ['test', 'test alternative']  # Only 2 total
                    })
                    mock_expansion_class.return_value = mock_expansion_service
                    mock_llm_factory.create_service.return_value = Mock()
                    
                    results = await search_vectors_use_case(
                        vector_service=vector_service,
                        collection_service=collection_service,
                        query='test',
                        collection_name='test_collection',
                        limit=5,
                        similarity_threshold=0.2
                    )
        
        # Should have called vector search only 2 times (not 3)
        assert len(vector_service.search_calls) == 2

    @pytest.mark.asyncio
    async def test_expansion_service_failure_fallback(self):
        """Test graceful fallback when expansion service fails."""
        
        vector_service = MockVectorService()
        collection_service = MockCollectionService()
        
        with patch.dict(os.environ, {'RAG_QUERY_EXPANSION_ENABLED': 'true'}):
            with patch('application_layer.vector_search.LLMServiceFactory') as mock_llm_factory:
                with patch('application_layer.vector_search.QueryExpansionService') as mock_expansion_class:
                    # Mock expansion service that fails
                    mock_expansion_service = Mock()
                    mock_expansion_service.expand_query_intelligently = AsyncMock(side_effect=Exception("Expansion failed"))
                    mock_expansion_class.return_value = mock_expansion_service
                    mock_llm_factory.create_service.return_value = Mock()
                
                    results = await search_vectors_use_case(
                        vector_service=vector_service,
                        collection_service=collection_service,
                        query='test query',
                        collection_name='test_collection',
                        limit=5,
                        similarity_threshold=0.2
                    )
        
        # Should fallback to original query only
        assert len(vector_service.search_calls) == 1
        assert vector_service.search_calls[0]['query'] == 'test query'
        
        # Should still return results
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_existing_validation_still_works(self):
        """Test that existing validation logic still works with enhancements."""
        
        vector_service = MockVectorService()
        collection_service = MockCollectionService()
        
        with patch.dict(os.environ, {'RAG_QUERY_EXPANSION_ENABLED': 'false'}):
            # Test empty query validation
            with pytest.raises(ValidationError) as exc_info:
                await search_vectors_use_case(
                    vector_service=vector_service,
                    collection_service=collection_service,
                    query='',
                    collection_name='test_collection',
                    limit=5,
                    similarity_threshold=0.2
                )
            assert exc_info.value.code == "MISSING_QUERY"
            
            # Test invalid limit
            with pytest.raises(ValidationError) as exc_info:
                await search_vectors_use_case(
                    vector_service=vector_service,
                    collection_service=collection_service,
                    query='test',
                    collection_name='test_collection',
                    limit=0,
                    similarity_threshold=0.2
                )
            assert exc_info.value.code == "INVALID_LIMIT"
            
            # Test invalid threshold
            with pytest.raises(ValidationError) as exc_info:
                await search_vectors_use_case(
                    vector_service=vector_service,
                    collection_service=collection_service,
                    query='test',
                    collection_name='test_collection',
                    limit=5,
                    similarity_threshold=1.5
                )
            assert exc_info.value.code == "INVALID_THRESHOLD"

    @pytest.mark.asyncio
    async def test_collection_context_passing(self):
        """Test that collection context is passed to expansion service."""
        
        vector_service = MockVectorService()
        collection_service = MockCollectionService(['test_collection', 'documentation_collection'])
        
        with patch.dict(os.environ, {'RAG_QUERY_EXPANSION_ENABLED': 'true'}):
            with patch('application_layer.vector_search.LLMServiceFactory') as mock_llm_factory:
                with patch('application_layer.vector_search.QueryExpansionService') as mock_expansion_class:
                    mock_expansion_service = Mock()
                    mock_expansion_service.expand_query_intelligently = AsyncMock(return_value=['test', 'test alt'])
                    mock_expansion_class.return_value = mock_expansion_service
                    mock_llm_factory.create_service.return_value = Mock()
                    
                    await search_vectors_use_case(
                        vector_service=vector_service,
                        collection_service=collection_service,
                        query='test',
                        collection_name='documentation_collection',
                        limit=5,
                        similarity_threshold=0.2
                    )
        
        # Check that collection context was passed to expansion service
        mock_expansion_service.expand_query_intelligently.assert_called_once()
        call_args = mock_expansion_service.expand_query_intelligently.call_args
        
        # Should pass collection name as context
        assert call_args[1]['collection_context'] == 'documentation_collection'

    @pytest.mark.asyncio
    async def test_response_format_unchanged(self):
        """Test that enhanced search returns same format as original."""
        
        vector_service = MockVectorService()
        collection_service = MockCollectionService()
        
        with patch.dict(os.environ, {'RAG_QUERY_EXPANSION_ENABLED': 'false'}):
            results = await search_vectors_use_case(
                vector_service=vector_service,
                collection_service=collection_service,
                query='test query',
                collection_name='test_collection',
                limit=5,
                similarity_threshold=0.2
            )
        
        # Results should maintain original format
        assert isinstance(results, list)
        for result in results:
            assert 'content' in result
            assert 'metadata' in result
            assert 'similarity_score' in result  # Renamed from 'score'
            assert 'collection_name' in result


class TestEnhancedSearchHelpers:
    """Test helper functions for enhanced search."""
    
    def test_environment_variable_parsing(self):
        """Test parsing of environment variables for feature flags."""
        
        # Test boolean parsing
        with patch.dict(os.environ, {'RAG_QUERY_EXPANSION_ENABLED': 'true'}):
            assert os.getenv('RAG_QUERY_EXPANSION_ENABLED', 'false').lower() == 'true'
            
        with patch.dict(os.environ, {'RAG_QUERY_EXPANSION_ENABLED': 'false'}):
            assert os.getenv('RAG_QUERY_EXPANSION_ENABLED', 'false').lower() == 'false'
            
        # Test integer parsing
        with patch.dict(os.environ, {'RAG_MAX_QUERY_VARIANTS': '5'}):
            assert int(os.getenv('RAG_MAX_QUERY_VARIANTS', '3')) == 5
            
        # Test default values
        with patch.dict(os.environ, {}, clear=True):
            assert os.getenv('RAG_QUERY_EXPANSION_ENABLED', 'false').lower() == 'false'
            assert int(os.getenv('RAG_MAX_QUERY_VARIANTS', '3')) == 3

    def test_result_deduplication_logic(self):
        """Test the result deduplication algorithm logic."""
        
        # Create test results with some duplicates
        results = [
            {'content': 'Content A', 'metadata': {'source': 'doc1.md'}, 'similarity_score': 0.9},
            {'content': 'Content B', 'metadata': {'source': 'doc2.md'}, 'similarity_score': 0.8},
            {'content': 'Content A', 'metadata': {'source': 'doc1.md'}, 'similarity_score': 0.85},  # Duplicate
            {'content': 'Content C', 'metadata': {'source': 'doc3.md'}, 'similarity_score': 0.7},
        ]
        
        # Simple deduplication by content (this logic will be in the implementation)
        seen_content = set()
        deduplicated = []
        
        for result in results:
            content_key = result['content']
            if content_key not in seen_content:
                seen_content.add(content_key)
                deduplicated.append(result)
        
        assert len(deduplicated) == 3  # Should remove 1 duplicate
        contents = [r['content'] for r in deduplicated]
        assert 'Content A' in contents
        assert 'Content B' in contents
        assert 'Content C' in contents
        
        # Should keep the higher scoring duplicate (0.9 vs 0.85)
        content_a_result = next(r for r in deduplicated if r['content'] == 'Content A')
        assert content_a_result['similarity_score'] == 0.9