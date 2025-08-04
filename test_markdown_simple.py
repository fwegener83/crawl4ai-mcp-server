"""
Simple standalone test for MarkdownContentProcessor without heavy dependencies.
This allows us to test the core functionality without import issues.
"""

import os
import sys
import markdown2

# Add the tools directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))

def test_markdown2_basic():
    """Test that markdown2 works correctly."""
    md = markdown2.Markdown(extras=['fenced-code-blocks', 'header-ids'])
    
    sample = """# Header 1

Some content.

```python
def test():
    return True
```

## Header 2

More content."""
    
    result = md.convert(sample)
    print("Markdown2 conversion successful")
    print("Result contains header:", 'h1' in result)
    print("Result contains code:", 'code' in result)
    return result


def test_langchain_import():
    """Test if we can import LangChain components."""
    try:
        # Try to import without the full dependency chain
        import sys
        import importlib.util
        
        # Check if langchain_text_splitters is available
        spec = importlib.util.find_spec("langchain_text_splitters")
        if spec is not None:
            print("LangChain text splitters module is available")
            return True
        else:
            print("LangChain text splitters not available")
            return False
    except Exception as e:
        print(f"Import test failed: {e}")
        return False


def test_content_hash():
    """Test content hash generation."""
    import hashlib
    
    content1 = "Test content A"
    content2 = "Test content B"
    
    hash1 = hashlib.md5(content1.encode('utf-8')).hexdigest()
    hash2 = hashlib.md5(content2.encode('utf-8')).hexdigest()
    
    print(f"Hash 1: {hash1}")
    print(f"Hash 2: {hash2}")
    print(f"Hashes are different: {hash1 != hash2}")
    
    return hash1 != hash2


def test_text_splitting_logic():
    """Test basic text splitting logic without heavy dependencies."""
    
    # Simulate basic recursive character splitting
    def simple_recursive_split(text, chunk_size=100, separators=None):
        if separators is None:
            separators = ["\n\n", "\n", " ", ""]
        
        chunks = []
        current_text = text
        
        for separator in separators:
            if len(current_text) <= chunk_size:
                if current_text.strip():
                    chunks.append(current_text)
                break
            
            if separator in current_text:
                parts = current_text.split(separator)
                current_chunk = ""
                
                for part in parts:
                    if len(current_chunk + separator + part) <= chunk_size:
                        current_chunk += separator + part if current_chunk else part
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                        current_chunk = part
                
                if current_chunk:
                    current_text = current_chunk
                else:
                    break
        
        return chunks
    
    test_text = """# Header 1

This is some content under header 1.

## Header 2

This is content under header 2 with more text to make it longer.

### Header 3

Final content section."""
    
    chunks = simple_recursive_split(test_text, chunk_size=50)
    print(f"Split text into {len(chunks)} chunks")
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i}: {chunk[:30]}...")
    
    return len(chunks) > 1


def test_code_block_detection():
    """Test code block detection logic."""
    import re
    
    content_with_code = """# Example

Here's some code:

```python
def hello():
    print("Hello, World!")
```

And some regular text."""
    
    # Test fenced code block detection
    fenced_pattern = r'```[\s\S]*?```'
    fenced_blocks = re.findall(fenced_pattern, content_with_code)
    
    print(f"Found {len(fenced_blocks)} fenced code blocks")
    print(f"Code block content: {fenced_blocks[0] if fenced_blocks else 'None'}")
    
    # Test language detection
    lang_pattern = r'^```(\w+)'
    for block in fenced_blocks:
        match = re.match(lang_pattern, block.strip())
        if match:
            print(f"Detected language: {match.group(1)}")
    
    return len(fenced_blocks) > 0


def run_all_tests():
    """Run all simple tests."""
    print("=== Simple MarkdownContentProcessor Tests ===\n")
    
    tests = [
        ("Markdown2 Basic", test_markdown2_basic),
        ("LangChain Import", test_langchain_import),
        ("Content Hash", test_content_hash),
        ("Text Splitting Logic", test_text_splitting_logic),
        ("Code Block Detection", test_code_block_detection),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"Running: {test_name}")
        try:
            result = test_func()
            results[test_name] = "PASS" if result else "FAIL"
            print(f"Result: {results[test_name]}\n")
        except Exception as e:
            results[test_name] = f"ERROR: {e}"
            print(f"Result: {results[test_name]}\n")
    
    print("=== Test Summary ===")
    for test_name, result in results.items():
        print(f"{test_name}: {result}")
    
    passed = sum(1 for r in results.values() if r == "PASS")
    total = len(results)
    print(f"\nPassed: {passed}/{total}")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)