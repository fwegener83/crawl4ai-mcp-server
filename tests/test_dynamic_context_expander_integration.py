"""
Integration tests for DynamicContextExpander implementation.

Tests the actual DynamicContextExpander implementation against the test
specifications to ensure all functionality works correctly.
"""

import pytest
import time
from tools.knowledge_base.dynamic_context_expander import (
    DynamicContextExpander, 
    ExpansionStrategy,
    create_dynamic_context_expander
)
from tools.knowledge_base.dependencies import is_rag_available

# Skip all tests if RAG dependencies are not available
pytestmark = pytest.mark.skipif(not is_rag_available(), reason="RAG dependencies not available")

SAMPLE_CONTENT = """# Main Document

This is introductory content for testing dynamic context expansion.

## Section 1: Introduction

This section provides detailed introduction with sufficient content to test expansion behavior across chunk boundaries.

### Subsection 1.1: Details

Here we have detailed information that helps test the context expansion algorithms.

## Section 2: Implementation

This section contains implementation details with code examples.

```python
def example_function():
    return "This is a code block example"
```

More content follows to ensure proper context expansion testing.

## Section 3: Conclusion

Final section with concluding thoughts and additional test content."""


class TestDynamicContextExpanderImplementation:
    """Test the actual DynamicContextExpander implementation."""
    
    def test_expander_initialization(self):
        """Test DynamicContextExpander initializes with correct configuration."""
        expander = DynamicContextExpander(
            similarity_threshold=0.8,
            max_neighbors=3,
            max_expansion_depth=1,
            enable_caching=False,
            performance_budget_ms=30
        )
        
        assert expander.similarity_threshold == 0.8
        assert expander.max_neighbors == 3
        assert expander.max_expansion_depth == 1
        assert expander.enable_caching is False
        assert expander.performance_budget_ms == 30
    
    def test_factory_function(self):
        """Test factory function creates properly configured expander."""
        expander = create_dynamic_context_expander(
            similarity_threshold=0.65,
            max_neighbors=8
        )
        
        assert expander.similarity_threshold == 0.65
        assert expander.max_neighbors == 8
        assert expander.max_expansion_depth == 2  # Default
        assert expander.enable_caching is True  # Default
        assert expander.performance_budget_ms == 50  # Default
    
    def test_marginal_result_identification(self):
        """Test identification of marginal query results."""
        expander = DynamicContextExpander(similarity_threshold=0.75)
        
        # Sample query results with different scores
        query_results = [
            {
                'chunk_id': 'chunk_001',
                'content': 'High relevance content',
                'similarity_score': 0.9,
                'metadata': {'context_expansion_eligible': True}
            },
            {
                'chunk_id': 'chunk_002', 
                'content': 'Marginal relevance content',
                'similarity_score': 0.65,
                'metadata': {'context_expansion_eligible': True}
            },
            {
                'chunk_id': 'chunk_003',
                'content': '```python\ncode content\n```',
                'similarity_score': 0.6,
                'metadata': {'context_expansion_eligible': False, 'chunk_type': 'code_block'}
            }
        ]
        
        marginal_results = expander._identify_marginal_results(query_results)
        
        # Should identify only the marginal, eligible result
        assert len(marginal_results) == 1
        assert marginal_results[0]['chunk_id'] == 'chunk_002'
    
    def test_expansion_eligibility_logic(self):
        """Test expansion eligibility determination logic."""
        expander = DynamicContextExpander()
        
        # Test cases for different chunk types
        test_chunks = [
            {
                'content': 'Short paragraph text',
                'metadata': {'chunk_type': 'paragraph', 'context_expansion_eligible': True}
            },
            {
                'content': '```python\ndef test():\n    pass\n```',
                'metadata': {'chunk_type': 'code_block'}
            },
            {
                'content': 'Long paragraph with many words that exceeds the expansion threshold because it contains sufficient context',
                'metadata': {'chunk_type': 'paragraph'}
            }
        ]
        
        # Test explicit eligibility flag
        assert expander._is_expansion_eligible(test_chunks[0]) is True
        
        # Test code block detection
        assert expander._is_expansion_eligible(test_chunks[1]) is False
        
        # Test word count threshold (should be eligible as < 300 words)
        assert expander._is_expansion_eligible(test_chunks[2]) is True
    
    def test_sequential_expansion_strategy(self):
        """Test sequential expansion strategy implementation."""
        expander = DynamicContextExpander(max_neighbors=2)
        
        # Mock marginal results
        marginal_results = [
            {
                'chunk_id': 'chunk_main',
                'content': 'Main marginal content',
                'metadata': {
                    'previous_chunk_id': 'chunk_prev',
                    'next_chunk_id': 'chunk_next'
                }
            }
        ]
        
        # Mock available chunks
        available_chunks = {
            'chunk_prev': {
                'chunk_id': 'chunk_prev',
                'content': 'Previous chunk content',
                'embedding': [0.1] * 384  # Mock embedding
            },
            'chunk_next': {
                'chunk_id': 'chunk_next', 
                'content': 'Next chunk content',
                'embedding': [0.2] * 384  # Mock embedding
            }
        }
        
        # Test sequential expansion
        expanded_chunks = expander._apply_sequential_expansion(
            marginal_results, available_chunks, [0.15] * 384  # Mock query embedding
        )
        
        # Should include original chunk plus neighbors
        assert len(expanded_chunks) >= 1  # At least the original marginal result
        
        # Check if neighbors were added (depends on similarity calculation)
        chunk_ids = [chunk.get('chunk_id') for chunk in expanded_chunks]
        assert 'chunk_main' in chunk_ids  # Original should be included
    
    def test_multi_strategy_expansion(self):
        """Test multi-strategy expansion with prioritization."""
        expander = DynamicContextExpander(
            similarity_threshold=0.7,  # Lower threshold for testing
            max_neighbors=3
        )
        
        # Mock marginal result with multiple relationship types
        marginal_results = [
            {
                'chunk_id': 'chunk_comprehensive',
                'content': 'Comprehensive chunk with all relationships',
                'metadata': {
                    'previous_chunk_id': 'chunk_prev',
                    'next_chunk_id': 'chunk_next',
                    'section_siblings': ['chunk_sib1', 'chunk_sib2'],
                    'overlap_sources': ['chunk_overlap']
                }
            }
        ]
        
        # Mock available chunks
        available_chunks = {
            'chunk_prev': {'chunk_id': 'chunk_prev', 'content': 'Previous content'},
            'chunk_next': {'chunk_id': 'chunk_next', 'content': 'Next content'},
            'chunk_sib1': {'chunk_id': 'chunk_sib1', 'content': 'Sibling 1 content'},
            'chunk_sib2': {'chunk_id': 'chunk_sib2', 'content': 'Sibling 2 content'},
            'chunk_overlap': {'chunk_id': 'chunk_overlap', 'content': 'Overlap content'}
        }
        
        # Test multi-strategy expansion
        expanded_chunks = expander._apply_multi_strategy_expansion(
            marginal_results, available_chunks, None  # No query embedding
        )
        
        # Should include original chunk and some neighbors
        assert len(expanded_chunks) >= 1
        
        # Check expansion metadata
        for chunk in expanded_chunks:
            if chunk.get('chunk_id') != 'chunk_comprehensive':
                assert 'expansion_source' in chunk
                assert chunk['expansion_source'] == 'chunk_comprehensive'
                assert 'expansion_type' in chunk
                assert chunk['expansion_type'] == 'multi_strategy'
    
    def test_performance_metrics_tracking(self):
        """Test performance metrics tracking functionality."""
        expander = DynamicContextExpander(performance_budget_ms=100)
        
        # Initial metrics should be empty
        initial_stats = expander.get_expansion_statistics()
        assert initial_stats['performance']['total_expansions'] == 0
        assert initial_stats['performance']['total_expansion_time_ms'] == 0.0
        
        # Simulate expansion operation
        query_results = [
            {
                'chunk_id': 'test_chunk',
                'content': 'Test content',
                'similarity_score': 0.6,  # Below threshold
                'metadata': {'context_expansion_eligible': True}
            }
        ]
        
        available_chunks = {}  # Empty for simple test
        
        result = expander.expand_context_for_marginal_queries(
            query_results, available_chunks
        )
        
        # Check that metrics were updated
        updated_stats = expander.get_expansion_statistics()
        assert updated_stats['performance']['total_expansions'] == 1
        assert updated_stats['performance']['total_expansion_time_ms'] > 0
        
        # Check result structure
        assert result.original_chunks == query_results
        assert result.expansion_metadata['expansion_applied'] is True
        assert 'processing_time_ms' in result.expansion_metadata
    
    def test_similarity_score_calculation(self):
        """Test similarity score calculation with embeddings."""
        expander = DynamicContextExpander()
        
        # Test cosine similarity calculation
        embedding1 = [1.0, 0.0, 0.0]
        embedding2 = [0.0, 1.0, 0.0]  # Orthogonal
        embedding3 = [1.0, 0.0, 0.0]  # Identical
        
        # Test orthogonal vectors (should be low similarity)
        similarity_orthogonal = expander._cosine_similarity(embedding1, embedding2)
        assert 0.0 <= similarity_orthogonal <= 0.6  # Should be low
        
        # Test identical vectors (should be high similarity)
        similarity_identical = expander._cosine_similarity(embedding1, embedding3)
        assert 0.9 <= similarity_identical <= 1.0  # Should be high
        
        # Test calculation with actual neighbor chunk
        neighbor_chunk = {
            'content': 'Test neighbor content',
            'embedding': [0.5, 0.5, 0.0]
        }
        
        score = expander._calculate_similarity_score(
            embedding1, neighbor_chunk, 'test_neighbor'
        )
        
        assert 0.0 <= score <= 1.0  # Should be valid score
    
    def test_edge_case_handling(self):
        """Test handling of edge cases and error conditions."""
        expander = DynamicContextExpander()
        
        # Test with empty query results
        empty_result = expander.expand_context_for_marginal_queries([], {})
        assert empty_result.original_chunks == []
        assert empty_result.expanded_chunks == []
        assert empty_result.expansion_metadata['expansion_applied'] is False
        
        # Test with no marginal results (all above threshold)
        high_score_results = [
            {
                'chunk_id': 'high_chunk',
                'content': 'High relevance content',
                'similarity_score': 0.9,
                'metadata': {'context_expansion_eligible': True}
            }
        ]
        
        high_score_result = expander.expand_context_for_marginal_queries(
            high_score_results, {}
        )
        
        assert high_score_result.original_chunks == high_score_results
        assert high_score_result.expanded_chunks == high_score_results
        assert high_score_result.expansion_metadata['expansion_applied'] is False
        assert high_score_result.expansion_metadata['reason'] == 'no_marginal_results'
    
    def test_cache_functionality(self):
        """Test caching functionality for repeated queries."""
        expander = DynamicContextExpander(enable_caching=True)
        
        # Initial cache should be empty
        stats = expander.get_expansion_statistics()
        assert stats['caching']['cache_size'] == 0
        assert stats['caching']['cache_hits'] == 0
        assert stats['caching']['cache_misses'] == 0
        
        # Test cache clearing
        expander.clear_cache()  # Should not error on empty cache
        
        # Verify cache configuration
        assert expander.enable_caching is True
        assert expander._expansion_cache is not None
    
    def test_expansion_strategies_enum(self):
        """Test expansion strategies enumeration."""
        # Test all strategy types are available
        strategies = [
            ExpansionStrategy.SEQUENTIAL,
            ExpansionStrategy.HIERARCHICAL,
            ExpansionStrategy.OVERLAP_AWARE,
            ExpansionStrategy.MULTI_STRATEGY
        ]
        
        for strategy in strategies:
            assert isinstance(strategy, ExpansionStrategy)
            assert isinstance(strategy.value, str)
        
        # Test strategy values
        assert ExpansionStrategy.SEQUENTIAL.value == "sequential"
        assert ExpansionStrategy.HIERARCHICAL.value == "hierarchical"
        assert ExpansionStrategy.OVERLAP_AWARE.value == "overlap_aware"
        assert ExpansionStrategy.MULTI_STRATEGY.value == "multi_strategy"


class TestDynamicContextExpanderConfiguration:
    """Test different configuration scenarios for DynamicContextExpander."""
    
    @pytest.mark.parametrize("threshold", [0.5, 0.75, 0.9])
    def test_different_similarity_thresholds(self, threshold):
        """Test expander with different similarity thresholds."""
        expander = DynamicContextExpander(similarity_threshold=threshold)
        assert expander.similarity_threshold == threshold
        
        # Test threshold affects marginal result identification
        test_result = {
            'chunk_id': 'test',
            'content': 'Test content',
            'similarity_score': 0.7,
            'metadata': {'context_expansion_eligible': True}
        }
        
        marginal_results = expander._identify_marginal_results([test_result])
        
        if threshold > 0.7:
            assert len(marginal_results) == 1  # Should be identified as marginal
        else:
            assert len(marginal_results) == 0  # Should not be marginal
    
    @pytest.mark.parametrize("max_neighbors", [1, 3, 5, 10])
    def test_different_max_neighbors(self, max_neighbors):
        """Test expander with different max neighbor limits."""
        expander = DynamicContextExpander(max_neighbors=max_neighbors)
        assert expander.max_neighbors == max_neighbors
        
        # The max_neighbors setting affects expansion behavior
        # This would be tested more thoroughly in integration tests
        # with actual expansion operations
    
    def test_performance_budget_configuration(self):
        """Test performance budget configuration and tracking."""
        budget_ms = 25
        expander = DynamicContextExpander(performance_budget_ms=budget_ms)
        
        assert expander.performance_budget_ms == budget_ms
        
        # Test budget tracking in metrics
        metrics = expander._get_performance_metrics(time.time())
        assert metrics['performance_budget_ms'] == budget_ms


if __name__ == "__main__":
    pytest.main([__file__, "-v"])