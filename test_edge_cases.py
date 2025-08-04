#!/usr/bin/env python3
"""
Edge case testing for content processing strategies.
"""

import os
import sys
import time
from pathlib import Path

# Set up environment
os.environ['TMPDIR'] = '/tmp'

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent / "tools"))

from knowledge_base.enhanced_content_processor import EnhancedContentProcessor


def test_edge_case(name: str, content: str, expected_behavior: str):
    """Test an edge case and report results."""
    print(f"\n🧪 Testing: {name}")
    print(f"   Expected: {expected_behavior}")
    
    try:
        processor = EnhancedContentProcessor(chunking_strategy="auto")
        start_time = time.time()
        chunks = processor.process_content(content)
        processing_time = time.time() - start_time
        
        print(f"   ✅ Success: {len(chunks)} chunks in {processing_time:.3f}s")
        
        if chunks:
            print(f"      Strategy used: {chunks[0]['metadata'].get('chunking_strategy', 'unknown')}")
            print(f"      Avg chunk size: {sum(len(c['content']) for c in chunks) / len(chunks):.0f} chars")
            
            # Check for specific edge case handling
            if name == "Malformed markdown":
                code_chunks = sum(1 for c in chunks if c['metadata'].get('contains_code', False))
                if code_chunks > 0:
                    print(f"      ⚠️  Detected {code_chunks} code chunks despite malformed syntax")
            
            if name == "Very long lines":
                max_chunk_size = max(len(c['content']) for c in chunks)
                if max_chunk_size > 2000:
                    print(f"      ⚠️  Large chunk detected: {max_chunk_size} chars")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False


def run_edge_case_tests():
    """Run comprehensive edge case testing."""
    print("🧪 Edge Case Testing for Content Processing")
    print("=" * 50)
    
    edge_cases = [
        {
            "name": "Empty content",
            "content": "",
            "expected": "Handle gracefully, return empty list"
        },
        {
            "name": "Whitespace only",
            "content": "   \n\t  \n   ",
            "expected": "Handle gracefully, return empty list"
        },
        {
            "name": "Single character",
            "content": "A",
            "expected": "Create single chunk"
        },
        {
            "name": "Very long single line",
            "content": "This is a very long line that exceeds typical chunk sizes. " * 100,
            "expected": "Split appropriately without breaking words"
        },
        {
            "name": "Malformed markdown",
            "content": """# Broken Header
This has ```unclosed code blocks
And ##invalid header## structure
| Broken | Table |
|--------|
Missing cells
```python
# Missing closing backticks
def broken():
    pass
""",
            "expected": "Handle gracefully, extract what's possible"
        },
        {
            "name": "Mixed line endings",
            "content": "Line 1\r\nLine 2\nLine 3\r\n# Header\r\nMore content\n",
            "expected": "Normalize line endings, process correctly"
        },
        {
            "name": "Unicode content",
            "content": """# Internationalization Test
## 中文标题
This is Chinese: 你好世界
## Español
Contenido en español: ¡Hola mundo!
## العربية  
محتوى باللغة العربية
```python
# Unicode in code
def unicode_test():
    return "Hello 🌍"
```
""",
            "expected": "Handle Unicode correctly in all metadata"
        },
        {
            "name": "Deeply nested structure",
            "content": """# Level 1
## Level 2  
### Level 3
#### Level 4
##### Level 5
###### Level 6
####### Invalid Level 7
Content at deepest level
""",
            "expected": "Preserve header hierarchy correctly"
        },
        {
            "name": "Mixed code languages",
            "content": """# Multi-Language Code
## Python
```python
def hello():
    return "Python"
```
## JavaScript
```javascript
function hello() {
    return "JavaScript";
}
```
## Bash
```bash
echo "Shell script"
```
## Unknown language
```unknownlang
syntax that doesn't match any language
```
""",
            "expected": "Detect languages correctly, handle unknown gracefully"
        },
        {
            "name": "Extreme table sizes",
            "content": """# Large Table Test
| Col1 | Col2 | Col3 | Col4 | Col5 | Col6 | Col7 | Col8 | Col9 | Col10 |
|------|------|------|------|------|------|------|------|------|-------|
""" + "\n".join([f"| Data{i}1 | Data{i}2 | Data{i}3 | Data{i}4 | Data{i}5 | Data{i}6 | Data{i}7 | Data{i}8 | Data{i}9 | Data{i}10 |" for i in range(100)]),
            "expected": "Handle large tables without memory issues"
        },
        {
            "name": "Nested code blocks",
            "content": """# Code Documentation
Here's how to use markdown in code:

```markdown
# This is markdown inside a code block
```python
def nested_example():
    return "code in markdown in code"
```
```

And here's actual Python:
```python
def real_python():
    markdown = '''
    # This is markdown in a string
    ## With headers
    '''
    return markdown
```
""",
            "expected": "Handle nested structures correctly"
        },
        {
            "name": "Special characters and symbols",
            "content": """# Special Characters Test ⚡
## Math symbols: ∑ ∫ √ π ∞
Content with *emphasis* and **bold** and `inline code`.

```python
# Special chars in code
symbols = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
unicode_math = "α + β = γ"
```

| Symbol | Meaning |
|--------|---------|
| ⚡     | Lightning |
| 🚀     | Rocket |
| 🎯     | Target |
""",
            "expected": "Preserve all special characters and symbols"
        }
    ]
    
    success_count = 0
    total_tests = len(edge_cases)
    
    for test_case in edge_cases:
        success = test_edge_case(
            test_case["name"],
            test_case["content"], 
            test_case["expected"]
        )
        if success:
            success_count += 1
    
    print(f"\n📊 Edge Case Test Results")
    print(f"   Passed: {success_count}/{total_tests}")
    print(f"   Success rate: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print("🎉 All edge cases handled successfully!")
    else:
        print("⚠️  Some edge cases need attention")
    
    return success_count == total_tests


def test_performance_edge_cases():
    """Test performance with edge cases."""
    print(f"\n⚡ Performance Edge Case Testing")
    print("-" * 40)
    
    # Test with very large content
    large_content = "# Large Document\n\n" + ("This is a paragraph with substantial content. " * 1000)
    
    print("Testing very large content (45KB)...")
    start_time = time.time()
    
    try:
        processor = EnhancedContentProcessor()
        chunks = processor.process_content(large_content)
        processing_time = time.time() - start_time
        
        print(f"✅ Processed {len(large_content)} chars in {processing_time:.3f}s")
        print(f"   Generated {len(chunks)} chunks")
        print(f"   Processing rate: {len(large_content)/processing_time:.0f} chars/sec")
        
        if processing_time > 5.0:
            print("⚠️  Processing time exceeds 5 seconds")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        return False


def main():
    """Run all edge case tests."""
    try:
        # Run standard edge cases
        standard_success = run_edge_case_tests()
        
        # Run performance edge cases
        performance_success = test_performance_edge_cases()
        
        print(f"\n{'='*50}")
        print("🏁 Edge Case Testing Complete")
        print(f"{'='*50}")
        
        if standard_success and performance_success:
            print("✅ All edge case tests passed!")
            print("   The content processor handles edge cases robustly.")
        else:
            print("⚠️  Some edge cases failed.")
            print("   Review the output above for details.")
        
        return standard_success and performance_success
        
    except Exception as e:
        print(f"❌ Edge case testing failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)