"""
Comprehensive tests for the enhanced MarkdownContentProcessor.
"""

import pytest
import os
from tools.knowledge_base.markdown_content_processor import MarkdownContentProcessor
from tools.knowledge_base.content_processor import ContentProcessor


class TestMarkdownContentProcessor:
    """Test suite for MarkdownContentProcessor."""
    
    @pytest.fixture(autouse=True)
    def setup_environment(self):
        """Set up environment variables for tests."""
        os.environ['TMPDIR'] = '/tmp'
    
    @pytest.fixture
    def processor(self):
        """Create a MarkdownContentProcessor instance for testing."""
        return MarkdownContentProcessor(chunk_size=500, chunk_overlap=100)
    
    @pytest.fixture  
    def baseline_processor(self):
        """Create baseline ContentProcessor for comparison."""
        return ContentProcessor(chunk_size=500, chunk_overlap=100)

    def test_initialization(self, processor):
        """Test proper initialization of MarkdownContentProcessor."""
        assert processor.chunk_size == 500
        assert processor.chunk_overlap == 100
        assert processor.preserve_code_blocks is True
        assert processor.preserve_tables is True

    def test_basic_markdown_splitting(self, processor):
        """Test basic markdown splitting functionality."""
        sample = """# Header
        
Some content.

```python
def test():
    return True
```"""
        
        chunks = processor.split_markdown_intelligently(sample)
        
        assert len(chunks) > 0
        assert all('content' in chunk for chunk in chunks)
        assert all('metadata' in chunk for chunk in chunks)

    def test_code_block_preservation(self, processor):
        """Test that code blocks are preserved intact."""
        markdown_with_code = """# Code Examples

```python
def complex_function():
    '''This should stay together.'''
    return "complete"
```"""
        
        chunks = processor.split_markdown_intelligently(markdown_with_code)
        
        # Find chunks containing code
        code_chunks = [c for c in chunks if '```python' in c['content']]
        assert len(code_chunks) >= 1
        
        # Verify code block is intact
        code_chunk = code_chunks[0]
        assert 'def complex_function' in code_chunk['content']
        assert code_chunk['metadata']['contains_code'] is True
        assert code_chunk['metadata']['programming_language'] == 'python'

    def test_performance_vs_baseline(self, processor, baseline_processor):
        """Test performance comparison with baseline processor."""
        sample_text = """# API Documentation

## Authentication

Use API keys.

```python
headers = {'Authorization': 'Bearer KEY'}
```"""
        
        comparison = processor.compare_with_baseline(sample_text, baseline_processor)
        
        # Verify comparison metrics exist
        assert 'our_chunks' in comparison
        assert 'baseline_chunks' in comparison
        assert 'semantic_preservation_score' in comparison
        
        # Semantic score should be positive
        assert comparison['semantic_preservation_score'] > 0.0

    def test_empty_content_handling(self, processor):
        """Test handling of empty content."""
        chunks = processor.split_markdown_intelligently("")
        assert len(chunks) == 0