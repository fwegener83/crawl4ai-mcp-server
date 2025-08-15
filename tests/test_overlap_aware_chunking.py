"""
Test suite for overlap-aware chunking functionality.

This module provides comprehensive tests for:
1. Overlap calculation algorithms (20-30% configurable overlap)
2. Chunk relationship tracking (parent/sibling references)
3. Metadata enhancement for overlapped chunks
4. Performance benchmarks for storage efficiency

Following the plan's test-first development approach.
"""

import pytest
import hashlib
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timezone

# Test data and fixtures
SAMPLE_MARKDOWN_CONTENT = """# Main Title

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

@dataclass
class TestChunkMetadata:
    """Test metadata structure for chunked content."""
    chunk_index: int
    total_chunks: int
    chunk_type: str
    content_hash: str
    header_hierarchy: List[str]
    contains_code: bool
    programming_language: Optional[str]
    word_count: int
    character_count: int
    created_at: str
    # Enhanced fields for overlap tracking
    overlap_sources: List[str]
    overlap_regions: List[tuple]
    previous_chunk_id: Optional[str]
    next_chunk_id: Optional[str]
    context_expansion_eligible: bool

@dataclass
class TestOverlapConfig:
    """Configuration for overlap testing."""
    chunk_size: int
    chunk_overlap: int
    overlap_percentage: float
    preserve_code_blocks: bool
    preserve_tables: bool

class TestOverlapCalculation:
    """Test suite for overlap calculation algorithms."""
    
    def test_overlap_percentage_calculation(self):
        """Test calculation of 20-30% overlap between consecutive chunks."""
        config = TestOverlapConfig(
            chunk_size=1000,
            chunk_overlap=250,  # 25% overlap
            overlap_percentage=0.25,
            preserve_code_blocks=True,
            preserve_tables=True
        )
        
        # Test overlap percentage calculation
        calculated_overlap = (config.chunk_overlap / config.chunk_size)
        assert 0.2 <= calculated_overlap <= 0.3, f"Overlap percentage {calculated_overlap} not in 20-30% range"
        
        # Test that overlap is less than chunk size
        assert config.chunk_overlap < config.chunk_size, "Overlap must be less than chunk size"
        
        # Test minimum viable overlap
        min_overlap = config.chunk_size * 0.1  # 10% minimum
        assert config.chunk_overlap >= min_overlap, f"Overlap {config.chunk_overlap} below minimum {min_overlap}"
    
    def test_overlap_region_detection(self):
        """Test detection of overlapping regions between chunks."""
        # Sample chunks with known overlap
        chunk1 = "This is the first chunk with some content that overlaps with the next chunk."
        chunk2 = "some content that overlaps with the next chunk. This is additional content in the second chunk."
        
        # Expected overlap region
        expected_overlap = "some content that overlaps with the next chunk."
        
        # Test overlap detection algorithm
        overlap_start_1 = chunk1.find(expected_overlap)
        overlap_end_1 = overlap_start_1 + len(expected_overlap)
        
        overlap_start_2 = chunk2.find(expected_overlap)
        overlap_end_2 = overlap_start_2 + len(expected_overlap)
        
        # Verify overlap regions are detected correctly
        assert overlap_start_1 != -1, "Overlap not found in first chunk"
        assert overlap_start_2 != -1, "Overlap not found in second chunk"
        assert overlap_start_2 == 0, "Overlap should start at beginning of second chunk"
        
        # Test overlap region metadata
        overlap_region_1 = (overlap_start_1, overlap_end_1)
        overlap_region_2 = (overlap_start_2, overlap_end_2)
        
        assert overlap_region_1[1] - overlap_region_1[0] == len(expected_overlap)
        assert overlap_region_2[1] - overlap_region_2[0] == len(expected_overlap)
    
    def test_chunk_boundary_preservation(self):
        """Test that important boundaries (sentences, paragraphs) are preserved in overlaps."""
        # Content with clear sentence boundaries
        content = "First sentence here. Second sentence continues. Third sentence concludes the paragraph."
        
        # Test sentence boundary detection
        sentences = content.split('. ')
        assert len(sentences) >= 2, "Should have multiple sentences for boundary testing"
        
        # Test that overlap respects sentence boundaries
        # When creating overlap, should prefer breaking at sentence boundaries
        sentence_boundaries = []
        current_pos = 0
        for sentence in sentences[:-1]:  # Exclude last as it doesn't end with '. '
            boundary_pos = current_pos + len(sentence) + 2  # +2 for '. '
            sentence_boundaries.append(boundary_pos)
            current_pos = boundary_pos
        
        assert len(sentence_boundaries) > 0, "Should identify sentence boundaries"
        
        # Verify boundaries are within content length
        for boundary in sentence_boundaries:
            assert 0 <= boundary <= len(content), f"Boundary {boundary} outside content range"
    
    def test_overlap_with_code_blocks(self):
        """Test overlap behavior around code blocks (should preserve code integrity)."""
        content_with_code = """
Text before code block.

```python
def test_function():
    return "code content"
```

Text after code block.
"""
        
        # Test code block detection
        code_start = content_with_code.find('```python')
        code_end = content_with_code.find('```', code_start + 1) + 3
        
        assert code_start != -1, "Should find code block start"
        assert code_end != -1, "Should find code block end"
        assert code_end > code_start, "Code block end should be after start"
        
        # Test that overlap doesn't break code blocks
        code_block = content_with_code[code_start:code_end]
        assert 'def test_function()' in code_block, "Code block should contain function definition"
        assert code_block.count('```') == 2, "Code block should have opening and closing markers"
    
    def test_overlap_performance_impact(self):
        """Test storage efficiency with overlapped chunks."""
        config = TestOverlapConfig(
            chunk_size=1000,
            chunk_overlap=250,
            overlap_percentage=0.25,
            preserve_code_blocks=True,
            preserve_tables=True
        )
        
        # Simulate chunk creation with overlap
        content_length = 5000  # 5KB of content
        estimated_chunks_without_overlap = content_length // config.chunk_size  # ~5 chunks
        estimated_chunks_with_overlap = content_length // (config.chunk_size - config.chunk_overlap)  # ~6-7 chunks
        
        # Test storage increase calculation
        storage_increase_ratio = estimated_chunks_with_overlap / estimated_chunks_without_overlap
        
        # Should be within acceptable limits (plan specifies max 40% increase)
        assert storage_increase_ratio <= 1.4, f"Storage increase {storage_increase_ratio} exceeds 40% limit"
        
        # Test memory efficiency - overlap regions shouldn't double storage
        overlap_storage_overhead = (estimated_chunks_with_overlap * config.chunk_overlap) / content_length
        assert overlap_storage_overhead <= 0.4, f"Overlap overhead {overlap_storage_overhead} too high"

class TestChunkRelationshipTracking:
    """Test suite for chunk relationship tracking functionality."""
    
    def test_parent_child_relationships(self):
        """Test tracking of parent document to child chunks relationships."""
        # Sample document metadata
        document_id = "test_doc_001"
        document_hash = hashlib.md5(SAMPLE_MARKDOWN_CONTENT.encode()).hexdigest()
        
        # Simulate chunk creation
        chunk_ids = [f"chunk_{document_id}_{i}" for i in range(3)]
        
        # Test parent-child relationship structure
        for i, chunk_id in enumerate(chunk_ids):
            metadata = TestChunkMetadata(
                chunk_index=i,
                total_chunks=len(chunk_ids),
                chunk_type="header_section",
                content_hash=hashlib.md5(f"chunk_content_{i}".encode()).hexdigest(),
                header_hierarchy=["# Main Title", "## Section 1"],
                contains_code=False,
                programming_language=None,
                word_count=100,
                character_count=500,
                created_at=datetime.now(timezone.utc).isoformat(),
                overlap_sources=[],
                overlap_regions=[],
                previous_chunk_id=chunk_ids[i-1] if i > 0 else None,
                next_chunk_id=chunk_ids[i+1] if i < len(chunk_ids)-1 else None,
                context_expansion_eligible=True
            )
            
            # Verify relationship consistency
            assert metadata.chunk_index == i, "Chunk index should match position"
            assert metadata.total_chunks == len(chunk_ids), "Total chunks should be consistent"
            
            # Test bidirectional linking
            if i > 0:
                assert metadata.previous_chunk_id is not None, "Should have previous chunk reference"
            else:
                assert metadata.previous_chunk_id is None, "First chunk shouldn't have previous"
                
            if i < len(chunk_ids) - 1:
                assert metadata.next_chunk_id is not None, "Should have next chunk reference"
            else:
                assert metadata.next_chunk_id is None, "Last chunk shouldn't have next"
    
    def test_sibling_chunk_relationships(self):
        """Test tracking of sibling relationships within same section."""
        # Simulate chunks from the same header section
        section_chunks = [
            {"id": "chunk_section1_0", "header": "## Section 1", "subsection": None},
            {"id": "chunk_section1_1", "header": "## Section 1", "subsection": "### Subsection 1.1"},
            {"id": "chunk_section1_2", "header": "## Section 1", "subsection": "### Subsection 1.1"},
        ]
        
        # Test sibling identification
        section1_siblings = [chunk for chunk in section_chunks if chunk["header"] == "## Section 1"]
        assert len(section1_siblings) == 3, "Should identify all siblings in same section"
        
        subsection_siblings = [chunk for chunk in section_chunks 
                             if chunk["subsection"] == "### Subsection 1.1"]
        assert len(subsection_siblings) == 2, "Should identify subsection siblings"
        
        # Test hierarchy preservation
        for chunk in section_chunks:
            assert chunk["header"] is not None, "All chunks should have header reference"
            
    def test_overlap_source_tracking(self):
        """Test tracking which chunks contribute to overlap regions."""
        # Sample overlapped chunks
        chunk1_id = "chunk_001"
        chunk2_id = "chunk_002"
        chunk3_id = "chunk_003"
        
        # Test overlap source metadata
        chunk2_metadata = TestChunkMetadata(
            chunk_index=1,
            total_chunks=3,
            chunk_type="paragraph",
            content_hash="hash_002",
            header_hierarchy=["# Title"],
            contains_code=False,
            programming_language=None,
            word_count=80,
            character_count=400,
            created_at=datetime.now(timezone.utc).isoformat(),
            overlap_sources=[chunk1_id],  # Overlaps with previous chunk
            overlap_regions=[(0, 50)],  # First 50 characters are overlap
            previous_chunk_id=chunk1_id,
            next_chunk_id=chunk3_id,
            context_expansion_eligible=True
        )
        
        # Verify overlap source tracking
        assert chunk1_id in chunk2_metadata.overlap_sources, "Should track overlap source"
        assert len(chunk2_metadata.overlap_regions) == 1, "Should have one overlap region"
        assert chunk2_metadata.overlap_regions[0][0] == 0, "Overlap should start at beginning"
        assert chunk2_metadata.overlap_regions[0][1] > 0, "Overlap should have positive length"
    
    def test_context_expansion_eligibility(self):
        """Test marking chunks as eligible for context expansion."""
        # Test chunks with different eligibility criteria
        test_cases = [
            {"chunk_type": "header_section", "word_count": 50, "expected": True},  # Short, good for expansion
            {"chunk_type": "code_block", "word_count": 200, "expected": False},     # Code blocks shouldn't expand
            {"chunk_type": "paragraph", "word_count": 500, "expected": False},     # Long chunks don't need expansion
            {"chunk_type": "list", "word_count": 100, "expected": True},           # Medium lists can expand
        ]
        
        for case in test_cases:
            # Simulate chunk eligibility determination
            is_eligible = (
                case["chunk_type"] not in ["code_block"] and
                case["word_count"] < 300 and  # Arbitrary threshold for testing
                case["chunk_type"] in ["header_section", "paragraph", "list"]
            )
            
            assert is_eligible == case["expected"], \
                f"Chunk type {case['chunk_type']} with {case['word_count']} words should be {case['expected']}"

class TestOverlapMetadataEnhancement:
    """Test suite for enhanced metadata in overlapped chunks."""
    
    def test_content_hash_consistency(self):
        """Test that content hashes are consistent and unique."""
        content1 = "This is test content for hashing."
        content2 = "This is different test content for hashing."
        
        hash1 = hashlib.md5(content1.encode()).hexdigest()
        hash2 = hashlib.md5(content2.encode()).hexdigest()
        hash1_repeat = hashlib.md5(content1.encode()).hexdigest()
        
        # Test hash consistency
        assert hash1 == hash1_repeat, "Same content should produce same hash"
        assert hash1 != hash2, "Different content should produce different hashes"
        assert len(hash1) == 32, "MD5 hash should be 32 characters"
        assert len(hash2) == 32, "MD5 hash should be 32 characters"
    
    def test_header_hierarchy_preservation(self):
        """Test preservation of markdown header hierarchy in metadata."""
        # Sample markdown with nested headers
        content = """# Main Title
## Section 1
### Subsection 1.1
#### Detail Level
Content here."""
        
        # Extract header hierarchy
        lines = content.split('\n')
        headers = [line for line in lines if line.strip().startswith('#')]
        
        expected_hierarchy = [
            "# Main Title",
            "## Section 1", 
            "### Subsection 1.1",
            "#### Detail Level"
        ]
        
        assert headers == expected_hierarchy, "Should preserve exact header hierarchy"
        
        # Test hierarchy depth tracking
        hierarchy_depths = [len(h.split(' ')[0]) for h in headers]  # Count # characters
        assert hierarchy_depths == [1, 2, 3, 4], "Should track correct hierarchy depths"
    
    def test_programming_language_detection(self):
        """Test detection and tracking of programming languages in code blocks."""
        test_cases = [
            {"content": "```python\ndef test():\n    pass\n```", "expected": "python"},
            {"content": "```javascript\nfunction test() {}\n```", "expected": "javascript"},
            {"content": "```sql\nSELECT * FROM table;\n```", "expected": "sql"},
            {"content": "```\ngeneric code\n```", "expected": None},  # No language specified
            {"content": "No code blocks here", "expected": None},     # No code blocks
        ]
        
        for case in test_cases:
            # Extract language from code block
            if '```' in case["content"]:
                code_start = case["content"].find('```') + 3
                first_line = case["content"][code_start:case["content"].find('\n', code_start)]
                detected_language = first_line.strip() if first_line.strip() else None
            else:
                detected_language = None
            
            assert detected_language == case["expected"], \
                f"Should detect language '{case['expected']}' in content: {case['content'][:50]}..."
    
    def test_timestamp_consistency(self):
        """Test consistent timestamp generation for chunk metadata."""
        timestamp1 = datetime.now(timezone.utc).isoformat()
        timestamp2 = datetime.now(timezone.utc).isoformat()
        
        # Test timestamp format
        assert 'T' in timestamp1, "Timestamp should be in ISO format"
        assert timestamp1.endswith('+00:00') or timestamp1.endswith('Z'), "Should include timezone"
        
        # Test that timestamps are very close (within reasonable execution time)
        dt1 = datetime.fromisoformat(timestamp1.replace('Z', '+00:00'))
        dt2 = datetime.fromisoformat(timestamp2.replace('Z', '+00:00'))
        time_diff = abs((dt2 - dt1).total_seconds())
        assert time_diff < 2.0, "Timestamps should be within 2 seconds for rapid execution"

class TestOverlapPerformanceBenchmarks:
    """Test suite for performance benchmarks with overlapped chunks."""
    
    def test_storage_efficiency_benchmarks(self):
        """Test storage efficiency meets plan requirements (max 40% increase)."""
        # Test configuration matching plan requirements
        base_content_size = 10000  # 10KB
        chunk_size = 1000
        chunk_overlap = 250  # 25% overlap
        
        # Calculate storage impact
        chunks_without_overlap = base_content_size // chunk_size  # ~10 chunks
        effective_chunk_size = chunk_size - chunk_overlap  # 750 bytes per unique content
        chunks_with_overlap = base_content_size // effective_chunk_size  # ~13 chunks
        
        storage_increase = (chunks_with_overlap / chunks_without_overlap) - 1
        
        # Should meet plan requirement (max 40% increase)
        assert storage_increase <= 0.4, \
            f"Storage increase {storage_increase:.2%} exceeds 40% limit from plan"
        
        # Test that overlap provides value (some storage increase expected)
        assert storage_increase > 0.1, \
            f"Storage increase {storage_increase:.2%} too low, overlap may not be effective"
    
    def test_memory_usage_during_processing(self):
        """Test memory usage during chunk processing with overlap."""
        # Simulate memory usage for processing
        chunk_size = 1000
        chunk_overlap = 250
        max_concurrent_chunks = 3  # Processing 3 chunks simultaneously
        
        # Estimate memory usage
        base_memory = chunk_size * max_concurrent_chunks  # Without overlap
        overlap_memory = chunk_overlap * (max_concurrent_chunks - 1)  # Overlap storage
        total_memory = base_memory + overlap_memory
        
        memory_increase = (total_memory / base_memory) - 1
        
        # Should meet plan requirement (max 25% memory increase)
        assert memory_increase <= 0.25, \
            f"Memory increase {memory_increase:.2%} exceeds 25% limit from plan"
    
    def test_processing_time_benchmarks(self):
        """Test processing time impact of overlap calculation."""
        import time
        
        # Simulate processing time for different approaches
        base_content = SAMPLE_MARKDOWN_CONTENT * 10  # Larger content for timing
        
        # Test basic chunking time (simulated)
        start_time = time.time()
        basic_chunks = len(base_content) // 1000  # Simple calculation
        basic_time = time.time() - start_time
        
        # Test overlap chunking time (simulated with additional processing)
        start_time = time.time()
        overlap_chunks = len(base_content) // 750  # Overlap calculation
        overlap_processing = sum(len(base_content[i:i+250]) for i in range(0, len(base_content), 750))  # Overlap processing
        overlap_time = time.time() - start_time
        
        # Processing time increase should be reasonable (plan allows 25% query latency increase)
        if basic_time > 0:  # Avoid division by zero
            time_increase = (overlap_time / basic_time) - 1
            assert time_increase <= 0.5, \
                f"Processing time increase {time_increase:.2%} too high for overlap calculation"

@pytest.mark.parametrize("chunk_size,overlap_percentage", [
    (500, 0.2),   # 20% overlap
    (1000, 0.25), # 25% overlap  
    (1500, 0.3),  # 30% overlap
])
def test_overlap_configuration_flexibility(chunk_size, overlap_percentage):
    """Test that overlap system works with different configurations."""
    chunk_overlap = int(chunk_size * overlap_percentage)
    
    config = TestOverlapConfig(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        overlap_percentage=overlap_percentage,
        preserve_code_blocks=True,
        preserve_tables=True
    )
    
    # Test configuration validity
    assert config.chunk_overlap < config.chunk_size, "Overlap must be less than chunk size"
    assert 0.2 <= config.overlap_percentage <= 0.3, "Overlap percentage must be 20-30%"
    
    # Test that configuration produces reasonable chunk counts
    content_length = 5000
    estimated_chunks = content_length // (config.chunk_size - config.chunk_overlap)
    assert estimated_chunks > 0, "Should produce at least one chunk"
    assert estimated_chunks < 50, "Shouldn't produce excessive chunks for test content"

# Integration test with mocked components
class TestOverlapIntegrationMocks:
    """Integration tests with mocked components for overlap functionality."""
    
    def test_overlap_with_markdown_processor_interface(self):
        """Test overlap functionality integrates with MarkdownContentProcessor interface."""
        # Mock the expected interface from the existing processor
        class MockMarkdownProcessor:
            def __init__(self, chunk_size=1000, chunk_overlap=200):
                self.chunk_size = chunk_size
                self.chunk_overlap = chunk_overlap
                
            def split_markdown_intelligently(self, content, source_metadata=None):
                """Mock implementation of intelligent splitting."""
                # Simulate chunk creation with overlap
                chunks = []
                overlap_start = 0
                
                while overlap_start < len(content):
                    chunk_end = min(overlap_start + self.chunk_size, len(content))
                    chunk_content = content[overlap_start:chunk_end]
                    
                    # Create mock chunk with overlap metadata
                    chunk = {
                        "content": chunk_content,
                        "metadata": {
                            "chunk_index": len(chunks),
                            "chunk_type": "paragraph",
                            "overlap_start": overlap_start,
                            "overlap_end": chunk_end,
                            "has_overlap": len(chunks) > 0,
                        }
                    }
                    chunks.append(chunk)
                    
                    # Move to next chunk with overlap
                    overlap_start = chunk_end - self.chunk_overlap
                    if overlap_start >= len(content):
                        break
                
                return chunks
        
        # Test the mock processor
        processor = MockMarkdownProcessor(chunk_size=500, chunk_overlap=100)
        chunks = processor.split_markdown_intelligently(SAMPLE_MARKDOWN_CONTENT)
        
        # Verify overlap behavior
        assert len(chunks) > 1, "Should create multiple chunks for test content"
        
        for i, chunk in enumerate(chunks[1:], 1):  # Skip first chunk
            assert chunk["metadata"]["has_overlap"], f"Chunk {i} should have overlap"
            
        # Verify chunk content overlap
        if len(chunks) >= 2:
            chunk1_content = chunks[0]["content"]
            chunk2_content = chunks[1]["content"]
            
            # Find overlapping region
            overlap_region = chunk1_content[-100:]  # Last 100 chars of first chunk
            assert overlap_region in chunk2_content, "Should find overlap region in second chunk"
    
    def test_overlap_with_vector_store_interface(self):
        """Test overlap functionality integrates with VectorStore interface."""
        # Mock vector store operations for overlapped chunks
        class MockVectorStore:
            def __init__(self):
                self.stored_chunks = []
                
            def add_chunks_with_relationships(self, chunks_with_metadata):
                """Mock method for storing chunks with relationship metadata."""
                for chunk_data in chunks_with_metadata:
                    # Validate required relationship metadata
                    metadata = chunk_data.get("metadata", {})
                    required_fields = ["chunk_index", "overlap_sources", "previous_chunk_id", "next_chunk_id"]
                    
                    for field in required_fields:
                        assert field in metadata, f"Missing required metadata field: {field}"
                    
                    self.stored_chunks.append(chunk_data)
                
                return len(self.stored_chunks)
            
            def query_with_context_expansion(self, query, expand_context=True):
                """Mock method for querying with context expansion."""
                # Simulate finding relevant chunks
                relevant_chunks = [chunk for chunk in self.stored_chunks if "test" in chunk.get("content", "")]
                
                if expand_context and relevant_chunks:
                    # Simulate context expansion by adding neighbor chunks
                    expanded_chunks = []
                    for chunk in relevant_chunks:
                        expanded_chunks.append(chunk)
                        
                        # Add previous/next chunks if available
                        prev_id = chunk["metadata"].get("previous_chunk_id")
                        next_id = chunk["metadata"].get("next_chunk_id")
                        
                        if prev_id:
                            # Find previous chunk (simplified mock)
                            prev_chunk = {"content": f"Previous chunk content for {prev_id}", "id": prev_id}
                            expanded_chunks.append(prev_chunk)
                        
                        if next_id:
                            # Find next chunk (simplified mock)
                            next_chunk = {"content": f"Next chunk content for {next_id}", "id": next_id}
                            expanded_chunks.append(next_chunk)
                    
                    return expanded_chunks
                
                return relevant_chunks
        
        # Test mock vector store
        vector_store = MockVectorStore()
        
        # Sample chunks with overlap metadata
        test_chunks = [
            {
                "content": "First chunk with test content",
                "metadata": {
                    "chunk_index": 0,
                    "overlap_sources": [],
                    "previous_chunk_id": None,
                    "next_chunk_id": "chunk_001",
                }
            },
            {
                "content": "Second chunk with more test content",
                "metadata": {
                    "chunk_index": 1,
                    "overlap_sources": ["chunk_000"],
                    "previous_chunk_id": "chunk_000",
                    "next_chunk_id": None,
                }
            }
        ]
        
        # Test storing chunks with relationships
        stored_count = vector_store.add_chunks_with_relationships(test_chunks)
        assert stored_count == 2, "Should store both chunks"
        
        # Test querying with context expansion
        results = vector_store.query_with_context_expansion("test query", expand_context=True)
        assert len(results) > len(test_chunks), "Context expansion should return more chunks"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])