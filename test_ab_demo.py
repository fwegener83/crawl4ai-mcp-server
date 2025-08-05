#!/usr/bin/env python3
"""
A/B Testing Demo for Enhanced Content Processor

This script demonstrates the intelligent chunking capabilities and A/B testing
framework comparing baseline RecursiveCharacterTextSplitter with the new
MarkdownContentProcessor.
"""

import os
import json
import time
from pathlib import Path

# Set up environment
os.environ['TMPDIR'] = '/tmp'

from tools.knowledge_base.enhanced_content_processor import EnhancedContentProcessor
from tools.knowledge_base.chunking_config import get_chunking_config, PRESETS


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n--- {title} ---")


def format_metrics(metrics: dict) -> str:
    """Format metrics for display."""
    return json.dumps(metrics, indent=2, default=str)


def demo_basic_processing():
    """Demonstrate basic content processing with different strategies."""
    print_header("Basic Content Processing Demo")
    
    # Sample content with various markdown features
    sample_content = """# API Documentation

## Authentication

All API requests require authentication using an API key.

```python
import requests

headers = {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
}
```

## Endpoints

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | /users   | List users  |
| POST   | /users   | Create user |

#### Get User

```python
def get_user(user_id: int):
    \"\"\"Retrieve a specific user.\"\"\"
    response = requests.get(
        f'https://api.example.com/users/{user_id}',
        headers=headers
    )
    return response.json()
```

### Posts

Content management endpoints:

1. **Create Post**: Submit new content
2. **Update Post**: Modify existing content  
3. **Delete Post**: Remove content

```javascript
// Example POST request
fetch('https://api.example.com/posts', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer ' + apiKey,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        title: 'My Post',
        content: 'Post content here...'
    })
});
```

## Error Handling

The API returns standard HTTP status codes:

- `200`: Success
- `400`: Bad Request  
- `401`: Unauthorized
- `404`: Not Found
- `500`: Internal Server Error
"""
    
    processor = EnhancedContentProcessor(
        chunking_strategy="auto",
        enable_ab_testing=True
    )
    
    print_section("Processing with Auto Strategy")
    start_time = time.time()
    chunks = processor.process_content(sample_content)
    processing_time = time.time() - start_time
    
    print(f"Content length: {len(sample_content)} characters")
    print(f"Generated chunks: {len(chunks)}")
    print(f"Processing time: {processing_time:.3f}s")
    print(f"Selected strategy: {chunks[0]['metadata']['chunking_strategy']}")
    
    print_section("Sample Chunks")
    for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
        print(f"\nChunk {i+1}:")
        print(f"  Content: {chunk['content'][:100]}...")
        print(f"  Type: {chunk['metadata'].get('chunk_type', 'N/A')}")
        print(f"  Contains code: {chunk['metadata'].get('contains_code', False)}")
        print(f"  Language: {chunk['metadata'].get('programming_language', 'N/A')}")
        print(f"  Size: {chunk['metadata'].get('character_count', len(chunk['content']))} chars")


def demo_ab_testing():
    """Demonstrate A/B testing comparison between strategies."""
    print_header("A/B Testing Comparison Demo")
    
    # Test content with rich markdown structure
    test_content = """# Machine Learning Guide

## Introduction

Machine learning is a subset of artificial intelligence that focuses on algorithms.

```python
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

# Sample data
X = np.random.randn(100, 5)
y = np.random.randn(100)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
```

## Data Preprocessing

### Data Cleaning

Steps for data cleaning:

1. **Handle Missing Values**
   - Remove rows with missing values
   - Impute missing values
   - Use domain knowledge

2. **Outlier Detection**
   - Statistical methods
   - Visualization techniques

```python
def clean_data(df):
    \"\"\"Clean the dataset.\"\"\"
    # Remove missing values
    df = df.dropna()
    
    # Handle outliers using IQR
    Q1 = df.quantile(0.25)
    Q3 = df.quantile(0.75)
    IQR = Q3 - Q1
    
    # Filter outliers
    df = df[~((df < (Q1 - 1.5 * IQR)) | (df > (Q3 + 1.5 * IQR))).any(axis=1)]
    
    return df
```

### Feature Engineering

| Technique | Description | Use Case |
|-----------|-------------|----------|
| Scaling | Normalize features | Neural networks |
| Encoding | Convert categories | Decision trees |
| Selection | Choose relevant features | All models |

## Model Training

### Linear Regression

```python
# Create and train model
model = LinearRegression()
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate performance
from sklearn.metrics import mean_squared_error, r2_score

mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"MSE: {mse:.4f}")
print(f"R²: {r2:.4f}")
```

### Advanced Techniques

Consider these approaches:

- **Cross-validation**: K-fold validation for robust evaluation
- **Hyperparameter tuning**: Grid search or random search
- **Ensemble methods**: Random forests, gradient boosting
"""
    
    processor = EnhancedContentProcessor(enable_ab_testing=True)
    
    print_section("Running A/B Comparison")
    print("Comparing baseline vs. markdown-intelligent strategies...")
    
    start_time = time.time()
    comparison = processor.compare_strategies(test_content)
    comparison_time = time.time() - start_time
    
    print(f"Comparison completed in {comparison_time:.3f}s")
    
    print_section("Comparison Results")
    print(f"Baseline chunks: {comparison.baseline_chunks}")
    print(f"Enhanced chunks: {comparison.enhanced_chunks}")
    print(f"Baseline time: {comparison.baseline_time:.4f}s")
    print(f"Enhanced time: {comparison.enhanced_time:.4f}s")
    print(f"Baseline avg size: {comparison.baseline_avg_size:.1f} chars")
    print(f"Enhanced avg size: {comparison.enhanced_avg_size:.1f} chars")
    print(f"Semantic preservation score: {comparison.semantic_preservation_score:.3f}")
    print(f"Quality improvement ratio: {comparison.quality_improvement_ratio:.3f}")
    print(f"Performance ratio: {comparison.performance_ratio:.3f}")
    print(f"Recommendation: {comparison.recommendation}")
    
    print_section("Analysis")
    if comparison.recommendation == "markdown_intelligent":
        print("✅ Enhanced processing recommended!")
        print("  - Better structure preservation")
        print("  - Improved code block handling")
        print("  - Richer metadata generation")
    else:
        print("⚡ Baseline processing recommended!")
        print("  - Faster processing speed")
        print("  - Simpler content structure")
        print("  - Lower computational overhead")


def demo_configuration_presets():
    """Demonstrate different configuration presets."""
    print_header("Configuration Presets Demo")
    
    simple_content = """# Quick Test

This is a simple test document.

```bash
echo "Hello World"
```
"""
    
    for preset_name, config in PRESETS.items():
        print_section(f"Preset: {preset_name.upper()}")
        
        processor = EnhancedContentProcessor(
            chunking_strategy=config.default_strategy,
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            enable_ab_testing=config.enable_ab_testing,
            quality_threshold=config.quality_threshold
        )
        
        start_time = time.time()
        chunks = processor.process_content(simple_content)
        processing_time = time.time() - start_time
        
        print(f"Strategy: {config.default_strategy}")
        print(f"Chunk size: {config.chunk_size}")
        print(f"Generated chunks: {len(chunks)}")
        print(f"Processing time: {processing_time:.4f}s")
        print(f"A/B testing: {'Enabled' if config.enable_ab_testing else 'Disabled'}")


def demo_performance_stats():
    """Demonstrate performance statistics tracking."""
    print_header("Performance Statistics Demo")
    
    processor = EnhancedContentProcessor(chunking_strategy="auto")
    
    test_contents = [
        "# Simple document\nJust some text.",
        """# Complex Document
        
## Code Examples

```python
def example():
    return "test"
```

## Tables

| A | B |
|---|---|
| 1 | 2 |
""",
        "Plain text without any markdown formatting.",
        "# Another Document\nWith minimal structure."
    ]
    
    print_section("Processing Multiple Documents")
    for i, content in enumerate(test_contents, 1):
        print(f"Processing document {i}...")
        chunks = processor.process_content(content)
        print(f"  Generated {len(chunks)} chunks")
    
    print_section("Performance Statistics")
    stats = processor.get_performance_stats()
    
    print(f"Total processed: {stats['total_processed']}")
    print(f"Baseline used: {stats['baseline_used']}")
    print(f"Markdown used: {stats['markdown_used']}")
    print(f"Auto selected: {stats['auto_selected']}")
    print(f"Average processing time: {stats['avg_processing_time']:.4f}s")
    
    print_section("Configuration")
    config = stats['configuration']
    print(format_metrics(config))


def main():
    """Run all demo functions."""
    print_header("Enhanced Content Processor A/B Testing Demo")
    print("This demo showcases intelligent markdown chunking and A/B testing capabilities.")
    
    try:
        demo_basic_processing()
        demo_ab_testing()
        demo_configuration_presets()
        demo_performance_stats()
        
        print_header("Demo Complete")
        print("✅ All demonstrations completed successfully!")
        print("\nKey takeaways:")
        print("- Intelligent chunking preserves markdown structure")
        print("- A/B testing helps choose optimal strategies")
        print("- Configuration presets suit different use cases")
        print("- Performance tracking enables optimization")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        raise


if __name__ == "__main__":
    main()