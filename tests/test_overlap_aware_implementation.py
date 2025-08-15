"""
Integration tests for OverlapAwareMarkdownProcessor implementation.

Tests the actual implementation against the comprehensive test suite to ensure
the overlap-aware processor meets all requirements from the plan.
"""

import pytest
from tools.knowledge_base.overlap_aware_processor import OverlapAwareMarkdownProcessor, create_overlap_aware_processor
from tools.knowledge_base.dependencies import is_rag_available

# Skip all tests if RAG dependencies are not available
pytestmark = pytest.mark.skipif(not is_rag_available(), reason="RAG dependencies not available")

SAMPLE_CONTENT = """# Main Title

This is an introductory paragraph with some basic content that will be used for testing overlap calculations.

## Section 1: Introduction

This section introduces the topic with detailed content that spans multiple sentences. We need enough content here to test proper overlap behavior when chunks are created. This paragraph contains sufficient text to validate that our overlap algorithms work correctly across chunk boundaries.

### Subsection 1.1: Details

Here we have more detailed information that will help us test the chunking behavior. This content is specifically designed to test edge cases in overlap calculation.

## Section 2: Implementation

This section contains implementation details. The content here should be sufficient to create multiple chunks when using our standard chunk sizes.

```python
def example_function():
    return "This is a code block that should be preserved"
```

More content follows the code block to ensure we test behavior around code boundaries.

## Section 3: Conclusion

Final section with concluding thoughts and additional content for testing purposes."""

class TestOverlapAwareProcessorImplementation:
    """Test the actual OverlapAwareMarkdownProcessor implementation."""
    
    def test_processor_initialization(self):
        """Test processor initializes with correct overlap configuration."""
        processor = OverlapAwareMarkdownProcessor(
            chunk_size=1000,
            overlap_percentage=0.25
        )
        
        assert processor.overlap_percentage == 0.25
        assert processor._chunk_size == 1000
        assert processor._chunk_overlap == 250  # 25% of 1000
        assert processor.context_expansion_threshold == 0.75
    
    def test_overlap_percentage_validation(self):
        """Test overlap percentage validation during initialization."""
        # Valid overlap percentages
        for percentage in [0.2, 0.25, 0.3]:
            processor = OverlapAwareMarkdownProcessor(overlap_percentage=percentage)
            assert processor.overlap_percentage == percentage
        
        # Invalid overlap percentages
        with pytest.raises(ValueError, match="must be between 0.2 and 0.3"):
            OverlapAwareMarkdownProcessor(overlap_percentage=0.1)
        
        with pytest.raises(ValueError, match="must be between 0.2 and 0.3"):
            OverlapAwareMarkdownProcessor(overlap_percentage=0.4)
    
    def test_chunk_overlap_validation(self):
        """Test that chunk overlap is less than chunk size."""
        # Valid configuration
        processor = OverlapAwareMarkdownProcessor(chunk_size=1000, chunk_overlap=200)
        assert processor._chunk_overlap < processor._chunk_size
        
        # Invalid configuration
        with pytest.raises(ValueError, match="must be less than chunk size"):
            OverlapAwareMarkdownProcessor(chunk_size=500, chunk_overlap=600)
    
    def test_basic_overlap_functionality(self):
        """Test basic overlap functionality with sample content."""
        processor = OverlapAwareMarkdownProcessor(
            chunk_size=500,  # Small chunks to force multiple chunks
            overlap_percentage=0.25
        )
        
        chunks = processor.split_markdown_intelligently_with_overlap(SAMPLE_CONTENT)
        
        # Should create multiple chunks for this content
        assert len(chunks) > 1, "Should create multiple chunks for test content"
        
        # Check chunk metadata structure
        for i, chunk in enumerate(chunks):
            assert 'content' in chunk
            assert 'metadata' in chunk
            assert 'chunk_id' in chunk
            
            metadata = chunk['metadata']
            assert 'overlap_sources' in metadata
            assert 'overlap_regions' in metadata
            assert 'overlap_percentage' in metadata
            assert 'chunk_index' in metadata
            assert metadata['chunk_index'] == i
    
    def test_overlap_between_consecutive_chunks(self):
        """Test that consecutive chunks have proper overlap."""
        processor = OverlapAwareMarkdownProcessor(
            chunk_size=300,  # Very small chunks to ensure overlap
            overlap_percentage=0.3
        )
        
        chunks = processor.split_markdown_intelligently_with_overlap(SAMPLE_CONTENT)
        
        if len(chunks) >= 2:
            # Check that at least some chunks have overlap metadata
            overlapped_chunks = 0
            for i in range(1, len(chunks)):
                chunk = chunks[i]
                metadata = chunk['metadata']
                
                # Count chunks with overlap
                if len(metadata['overlap_sources']) > 0:
                    overlapped_chunks += 1
                    assert len(metadata['overlap_regions']) > 0, f"Chunk {i} with sources should have regions"
                    
                    # Overlap percentage should be reasonable (wider range for small chunks)
                    assert 0.05 <= metadata['overlap_percentage'] <= 0.75, \
                        f"Chunk {i} overlap percentage {metadata['overlap_percentage']} not reasonable"
            
            # At least half of the chunks (after first) should have overlap
            assert overlapped_chunks >= max(1, (len(chunks) - 1) // 2), \
                f"Expected at least half of chunks to have overlap, got {overlapped_chunks}/{len(chunks)-1}"
    
    def test_chunk_relationships(self):
        """Test bidirectional chunk relationships."""
        processor = OverlapAwareMarkdownProcessor(
            chunk_size=400,
            overlap_percentage=0.25,
            enable_relationship_tracking=True
        )
        
        chunks = processor.split_markdown_intelligently_with_overlap(SAMPLE_CONTENT)
        
        if len(chunks) >= 2:
            for i, chunk in enumerate(chunks):
                metadata = chunk['metadata']
                
                # Check previous chunk relationship
                if i > 0:
                    assert metadata['previous_chunk_id'] is not None, f"Chunk {i} should have previous_chunk_id"
                    assert metadata['previous_chunk_id'] == chunks[i-1]['chunk_id']
                else:
                    assert metadata['previous_chunk_id'] is None, "First chunk shouldn't have previous_chunk_id"
                
                # Check next chunk relationship
                if i < len(chunks) - 1:
                    assert metadata['next_chunk_id'] is not None, f"Chunk {i} should have next_chunk_id"
                    assert metadata['next_chunk_id'] == chunks[i+1]['chunk_id']
                else:
                    assert metadata['next_chunk_id'] is None, "Last chunk shouldn't have next_chunk_id"
    
    def test_context_expansion_eligibility(self):
        """Test context expansion eligibility determination."""
        processor = OverlapAwareMarkdownProcessor(
            chunk_size=200,  # Small chunks to test eligibility
            overlap_percentage=0.25
        )
        
        chunks = processor.split_markdown_intelligently_with_overlap(SAMPLE_CONTENT)
        
        for chunk in chunks:
            metadata = chunk['metadata']
            
            # Check eligibility field exists
            assert 'context_expansion_eligible' in metadata
            assert isinstance(metadata['context_expansion_eligible'], bool)
            
            # Check expansion threshold
            assert metadata['expansion_threshold'] == 0.75
            
            # Code blocks should not be eligible for expansion
            if metadata.get('contains_code', False):
                assert not metadata['context_expansion_eligible'], \
                    "Code blocks should not be eligible for context expansion"
    
    def test_performance_metrics(self):
        """Test performance metrics tracking."""
        processor = OverlapAwareMarkdownProcessor(chunk_size=500, overlap_percentage=0.25)
        
        # Process content and check metrics
        chunks = processor.split_markdown_intelligently_with_overlap(SAMPLE_CONTENT)
        metrics = processor.get_performance_metrics()
        
        # Check metrics structure
        assert 'total_chunks_created' in metrics
        assert 'total_processing_time_ms' in metrics
        assert 'average_processing_time_ms' in metrics
        assert 'overlap_percentage' in metrics
        assert 'chunk_size' in metrics
        assert 'chunk_overlap' in metrics
        
        # Check metrics values
        assert metrics['total_chunks_created'] == len(chunks)
        assert metrics['overlap_percentage'] == 0.25
        assert metrics['chunk_size'] == 500
        assert metrics['chunk_overlap'] == 125  # 25% of 500
        
        # Processing time should be reasonable
        assert metrics['total_processing_time_ms'] > 0
        assert metrics['average_processing_time_ms'] > 0
        
        # Check per-chunk processing time
        for chunk in chunks:
            assert chunk['metadata']['processing_time_ms'] > 0
    
    def test_storage_efficiency_within_budget(self):
        """Test storage efficiency meets plan requirements (max 40% increase)."""
        processor = OverlapAwareMarkdownProcessor(chunk_size=1000, overlap_percentage=0.25)
        
        chunks = processor.split_markdown_intelligently_with_overlap(SAMPLE_CONTENT)
        
        # Calculate storage efficiency
        total_overlapped_content = sum(len(chunk['content']) for chunk in chunks)
        original_content_length = len(SAMPLE_CONTENT)
        
        storage_increase_ratio = (total_overlapped_content / original_content_length) - 1
        
        # Should meet plan requirement (max 40% increase)
        assert storage_increase_ratio <= 0.4, \
            f"Storage increase {storage_increase_ratio:.2%} exceeds 40% limit from plan"
        
        # Check per-chunk storage efficiency
        for chunk in chunks:
            efficiency = chunk['metadata']['storage_efficiency_ratio']
            assert 0.5 <= efficiency <= 1.0, \
                f"Storage efficiency {efficiency} out of reasonable range"
    
    def test_backward_compatibility(self):
        """Test backward compatibility with original interface."""
        processor = OverlapAwareMarkdownProcessor(chunk_size=800, overlap_percentage=0.25)
        
        # Use original method name
        chunks_original = processor.split_markdown_intelligently(SAMPLE_CONTENT)
        
        # Use new method name
        chunks_new = processor.split_markdown_intelligently_with_overlap(SAMPLE_CONTENT)
        
        # Should produce same results
        assert len(chunks_original) == len(chunks_new)
        
        for orig, new in zip(chunks_original, chunks_new):
            assert orig['content'] == new['content']
            assert orig['chunk_id'] == new['chunk_id']
    
    def test_factory_function(self):
        """Test factory function creates properly configured processor."""
        processor = create_overlap_aware_processor(
            chunk_size=800,
            overlap_percentage=0.3
        )
        
        assert processor._chunk_size == 800
        assert processor.overlap_percentage == 0.3
        assert processor._chunk_overlap == 240  # 30% of 800
        assert processor.enable_relationship_tracking is True
    
    def test_code_block_preservation(self):
        """Test that code blocks are preserved in overlap calculations."""
        code_content = """# Code Example

Here's some text before the code.

```python
def test_function():
    # This code should be preserved
    return "important code"
```

Text after the code block that continues."""
        
        processor = OverlapAwareMarkdownProcessor(
            chunk_size=200,  # Small to force chunking around code
            overlap_percentage=0.25,
            preserve_code_blocks=True
        )
        
        chunks = processor.split_markdown_intelligently_with_overlap(code_content)
        
        # Find chunk containing code
        code_chunk = None
        for chunk in chunks:
            if '```python' in chunk['content']:
                code_chunk = chunk
                break
        
        assert code_chunk is not None, "Should find chunk containing code block"
        
        # Code block should be complete
        assert 'def test_function():' in code_chunk['content']
        assert 'return "important code"' in code_chunk['content']
        assert code_chunk['content'].count('```') == 2, "Code block should have opening and closing markers"
        
        # Metadata should indicate contains code
        assert code_chunk['metadata']['contains_code'] is True
        assert code_chunk['metadata']['programming_language'] == 'python'
    
    def test_empty_content_handling(self):
        """Test handling of empty or whitespace-only content."""
        processor = OverlapAwareMarkdownProcessor(chunk_size=500, overlap_percentage=0.25)
        
        # Empty content
        chunks_empty = processor.split_markdown_intelligently_with_overlap("")
        assert chunks_empty == []
        
        # Whitespace-only content
        chunks_whitespace = processor.split_markdown_intelligently_with_overlap("   \n\n  ")
        assert chunks_whitespace == []
    
    def test_single_chunk_content(self):
        """Test content that fits in a single chunk."""
        short_content = "This is a short piece of content that fits in one chunk."
        
        processor = OverlapAwareMarkdownProcessor(chunk_size=1000, overlap_percentage=0.25)
        chunks = processor.split_markdown_intelligently_with_overlap(short_content)
        
        # Should create exactly one chunk
        assert len(chunks) == 1
        
        chunk = chunks[0]
        metadata = chunk['metadata']
        
        # No overlap for single chunk
        assert metadata['overlap_sources'] == []
        assert metadata['overlap_regions'] == []
        assert metadata['overlap_percentage'] == 0.0
        assert metadata['previous_chunk_id'] is None
        assert metadata['next_chunk_id'] is None


class TestOverlapAwareProcessorConfiguration:
    """Test different configuration scenarios for the overlap-aware processor."""
    
    @pytest.mark.parametrize("overlap_percentage", [0.2, 0.25, 0.3])
    def test_different_overlap_percentages(self, overlap_percentage):
        """Test processor with different valid overlap percentages."""
        processor = OverlapAwareMarkdownProcessor(
            chunk_size=1000,
            overlap_percentage=overlap_percentage
        )
        
        assert processor.overlap_percentage == overlap_percentage
        assert processor._chunk_overlap == int(1000 * overlap_percentage)
        
        chunks = processor.split_markdown_intelligently_with_overlap(SAMPLE_CONTENT)
        
        # Should work with all valid percentages
        assert len(chunks) > 0
        
        # Check overlap metadata
        overlapped_chunks = [c for c in chunks if c['metadata']['overlap_percentage'] > 0]
        if overlapped_chunks:
            for chunk in overlapped_chunks:
                # Achieved overlap should be reasonable for the configured percentage
                achieved = chunk['metadata']['overlap_percentage']
                assert 0.1 <= achieved <= 0.5, \
                    f"Achieved overlap {achieved} not reasonable for config {overlap_percentage}"
    
    @pytest.mark.parametrize("chunk_size", [300, 500, 800, 1000, 1500])
    def test_different_chunk_sizes(self, chunk_size):
        """Test processor with different chunk sizes."""
        processor = OverlapAwareMarkdownProcessor(
            chunk_size=chunk_size,
            overlap_percentage=0.25
        )
        
        chunks = processor.split_markdown_intelligently_with_overlap(SAMPLE_CONTENT)
        
        # Should work with all chunk sizes
        assert len(chunks) > 0
        
        # Smaller chunk sizes should create more chunks
        if chunk_size <= 500:
            assert len(chunks) >= 2, "Small chunk sizes should create multiple chunks"
    
    def test_relationship_tracking_disabled(self):
        """Test processor with relationship tracking disabled."""
        processor = OverlapAwareMarkdownProcessor(
            chunk_size=500,
            overlap_percentage=0.25,
            enable_relationship_tracking=False
        )
        
        chunks = processor.split_markdown_intelligently_with_overlap(SAMPLE_CONTENT)
        
        # Should still have overlap metadata but no relationships
        for chunk in chunks:
            metadata = chunk['metadata']
            assert 'overlap_sources' in metadata
            assert 'overlap_regions' in metadata
            # Relationships might be None or empty but should exist in structure
            assert 'previous_chunk_id' in metadata
            assert 'next_chunk_id' in metadata


if __name__ == "__main__":
    pytest.main([__file__, "-v"])