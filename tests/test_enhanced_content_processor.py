"""
Comprehensive tests for EnhancedContentProcessor and A/B testing framework.
"""

import pytest
import os

# Check if RAG dependencies are available
try:
    from tools.knowledge_base.dependencies import is_rag_available
    RAG_AVAILABLE = is_rag_available()
except ImportError:
    RAG_AVAILABLE = False

# Conditionally import components to test
if RAG_AVAILABLE:
    from tools.knowledge_base.enhanced_content_processor import (
        EnhancedContentProcessor, 
        ChunkingComparisonResult
    )
else:
    # Skip all tests in this module if RAG is not available
    pytestmark = pytest.mark.skip(reason="RAG dependencies not available")


class TestEnhancedContentProcessor:
    """Test suite for EnhancedContentProcessor."""
    
    @pytest.fixture(autouse=True)
    def setup_environment(self):
        """Set up environment variables for tests."""
        os.environ['TMPDIR'] = '/tmp'
    
    @pytest.fixture
    def processor(self):
        """Create an EnhancedContentProcessor instance for testing."""
        return EnhancedContentProcessor(
            chunking_strategy="auto",
            chunk_size=500,
            chunk_overlap=100,
            enable_ab_testing=True
        )
    
    @pytest.fixture
    def baseline_processor(self):
        """Create baseline-only processor for comparison."""
        return EnhancedContentProcessor(
            chunking_strategy="baseline",
            chunk_size=500,
            chunk_overlap=100,
            enable_ab_testing=True
        )
    
    @pytest.fixture
    def markdown_processor(self):
        """Create markdown-only processor for testing."""
        return EnhancedContentProcessor(
            chunking_strategy="markdown_intelligent",
            chunk_size=500,
            chunk_overlap=100,
            enable_ab_testing=True
        )

    def test_initialization(self, processor):
        """Test proper initialization of EnhancedContentProcessor."""
        assert processor.chunking_strategy == "auto"
        assert processor.chunk_size == 500
        assert processor.chunk_overlap == 100
        assert processor.enable_ab_testing is True
        assert processor.quality_threshold == 0.7
        
        # Check that both processors are initialized
        assert processor.baseline_processor is not None
        assert processor.markdown_processor is not None

    def test_basic_content_processing(self, processor):
        """Test basic content processing functionality."""
        sample_content = """# Test Document
        
This is a simple test document with some content.

## Section 1
        
Here's some text in the first section.

```python
def test_function():
    return "Hello World"
```

## Section 2

More content in the second section."""

        chunks = processor.process_content(sample_content)
        
        # Verify chunks are created
        assert len(chunks) > 0
        assert all('content' in chunk for chunk in chunks)
        assert all('metadata' in chunk for chunk in chunks)
        assert all('id' in chunk for chunk in chunks)
        
        # Verify enhanced metadata
        for chunk in chunks:
            metadata = chunk['metadata']
            assert 'chunking_strategy' in metadata
            assert 'processing_time' in metadata
            assert 'processor_version' in metadata
            assert metadata['processor_version'] == 'enhanced'

    def test_strategy_selection(self, processor):
        """Test automatic strategy selection logic."""
        # Test markdown content (should select markdown_intelligent)
        markdown_content = """# Header 1
        
## Header 2

```python
code_block = "test"
```

### Header 3

| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |
"""
        
        chunks = processor.process_content(markdown_content)
        # Should have selected markdown_intelligent for structured content
        assert chunks[0]['metadata']['chunking_strategy'] == 'markdown_intelligent'
        
        # Test simple text (should select baseline)
        simple_content = "This is just plain text without any special formatting or structure."
        chunks = processor.process_content(simple_content)
        # Should have selected baseline for simple text
        assert chunks[0]['metadata']['chunking_strategy'] == 'baseline'

    def test_forced_strategy_override(self, processor):
        """Test forcing specific strategies via parameters."""
        content = """# Test
Some content here."""
        
        # Force baseline strategy
        chunks = processor.process_content(content, force_strategy="baseline")
        assert chunks[0]['metadata']['chunking_strategy'] == 'baseline'
        
        # Force markdown strategy
        chunks = processor.process_content(content, force_strategy="markdown_intelligent")
        assert chunks[0]['metadata']['chunking_strategy'] == 'markdown_intelligent'

    def test_ab_testing_comparison(self, processor):
        """Test A/B testing framework."""
        test_content = """# API Documentation

## Authentication

Use API keys for authentication.

```python
headers = {
    'Authorization': 'Bearer YOUR_API_KEY'
}
```

## Usage Examples

### Basic Request

```python
import requests

response = requests.get('https://api.example.com/data', headers=headers)
```

### Error Handling

Handle errors appropriately:

```python
try:
    response = requests.get('https://api.example.com/data')
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
```
"""
        
        comparison = processor.compare_strategies(test_content)
        
        # Verify comparison result structure
        assert isinstance(comparison, ChunkingComparisonResult)
        assert comparison.baseline_chunks > 0
        assert comparison.enhanced_chunks > 0
        assert comparison.baseline_time > 0
        assert comparison.enhanced_time > 0
        assert comparison.baseline_avg_size > 0
        assert comparison.enhanced_avg_size > 0
        assert 0.0 <= comparison.semantic_preservation_score <= 1.0
        assert comparison.quality_improvement_ratio > 0
        assert comparison.performance_ratio > 0
        assert comparison.recommendation in ["baseline", "markdown_intelligent"]

    def test_ab_testing_disabled(self):
        """Test behavior when A/B testing is disabled."""
        processor = EnhancedContentProcessor(enable_ab_testing=False)
        
        with pytest.raises(ValueError, match="A/B testing is disabled"):
            processor.compare_strategies("Test content")

    def test_performance_stats_tracking(self, processor):
        """Test performance statistics tracking."""
        # Initial stats
        initial_stats = processor.get_performance_stats()
        assert initial_stats["total_processed"] == 0
        assert initial_stats["baseline_used"] == 0
        assert initial_stats["markdown_used"] == 0
        assert initial_stats["auto_selected"] == 0
        
        # Process some content
        processor.process_content("# Test\nSome content")
        processor.process_content("Simple text content")
        
        # Check updated stats
        updated_stats = processor.get_performance_stats()
        assert updated_stats["total_processed"] == 2
        assert updated_stats["avg_processing_time"] > 0
        
        # Verify configuration is included
        config = updated_stats["configuration"]
        assert config["strategy"] == "auto"
        assert config["chunk_size"] == 500
        assert config["ab_testing_enabled"] is True

    def test_backward_compatibility(self, processor):
        """Test backward compatibility with ContentProcessor API."""
        content = "This is test content for backward compatibility testing."
        
        # Test split_text method
        chunks = processor.split_text(content)
        assert isinstance(chunks, list)
        assert all(isinstance(chunk, str) for chunk in chunks)
        assert len(chunks) > 0
        
        # Test extract_metadata method
        metadata = processor.extract_metadata(
            content=content,
            url="https://example.com",
            title="Test Document"
        )
        assert isinstance(metadata, dict)
        assert metadata["url"] == "https://example.com"
        assert metadata["title"] == "Test Document"

    def test_empty_content_handling(self, processor):
        """Test handling of empty or whitespace-only content."""
        # Empty string
        chunks = processor.process_content("")
        assert len(chunks) == 0
        
        # Whitespace only
        chunks = processor.process_content("   \n\t  ")
        assert len(chunks) == 0
        
        # A/B testing with empty content should raise error
        with pytest.raises(ValueError, match="Cannot compare strategies with empty content"):
            processor.compare_strategies("")

    def test_source_metadata_integration(self, processor):
        """Test integration of source metadata into chunks."""
        content = "# Test Document\nSome content here."
        source_metadata = {
            "url": "https://example.com/doc",
            "title": "Test Document",
            "author": "Test Author",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        chunks = processor.process_content(content, source_metadata=source_metadata)
        
        # Verify source metadata is preserved
        for chunk in chunks:
            metadata = chunk['metadata']
            assert metadata.get("url") == "https://example.com/doc"
            assert metadata.get("title") == "Test Document"
            assert metadata.get("author") == "Test Author"
            assert metadata.get("timestamp") == "2024-01-01T00:00:00Z"

    def test_strategy_recommendation_logic(self, processor):
        """Test strategy recommendation logic in A/B testing."""
        # Content that should favor markdown processing
        structured_content = """# Main Title

## Section 1
Content here.

### Subsection 1.1
More content.

```python
def example():
    return "structured"
```

## Section 2

| Column | Value |
|--------|-------|
| A      | 1     |
| B      | 2     |

### Subsection 2.1

```javascript
function test() {
    return "more code";
}
```
"""
        
        comparison = processor.compare_strategies(structured_content)
        
        # For highly structured content, should recommend markdown_intelligent
        # (assuming quality improvement meets threshold)
        assert comparison.recommendation in ["markdown_intelligent", "baseline"]
        assert comparison.semantic_preservation_score > 0
        
        # Simple content test
        simple_content = "This is just a simple paragraph with no special structure or formatting."
        comparison_simple = processor.compare_strategies(simple_content)
        
        # For simple content, baseline might be recommended due to performance
        assert comparison_simple.recommendation in ["baseline", "markdown_intelligent"]

    def test_concurrent_processing(self, processor):
        """Test that processor handles multiple concurrent processing calls."""
        contents = [
            "# Document 1\nContent for first document.",
            "# Document 2\nContent for second document.",
            "Simple text document without markdown.",
            "# Document 4\n```python\ncode = 'test'\n```"
        ]
        
        # Process multiple contents
        all_chunks = []
        for content in contents:
            chunks = processor.process_content(content)
            all_chunks.extend(chunks)
        
        # Verify all processed successfully
        assert len(all_chunks) > 0
        
        # Check that stats were updated correctly
        stats = processor.get_performance_stats()
        assert stats["total_processed"] == len(contents)

    def test_chunk_id_uniqueness(self, processor):
        """Test that chunk IDs are unique across processing calls."""
        content1 = "# Document 1\nFirst document content."
        content2 = "# Document 2\nSecond document content."
        
        chunks1 = processor.process_content(content1)
        chunks2 = processor.process_content(content2)
        
        all_ids = [chunk['id'] for chunk in chunks1 + chunks2]
        unique_ids = set(all_ids)
        
        # All IDs should be unique
        assert len(all_ids) == len(unique_ids)