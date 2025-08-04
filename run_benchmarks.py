#!/usr/bin/env python3
"""
Standalone benchmark script for content processing strategies.
"""

import os
import sys
import time
import json
import statistics
from pathlib import Path
from datetime import datetime, timezone

# Set up environment
os.environ['TMPDIR'] = '/tmp'

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent / "tools"))

from knowledge_base.enhanced_content_processor import EnhancedContentProcessor


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n--- {title} ---")


def create_test_content():
    """Create test content for benchmarking."""
    return {
        "simple_text": """
This is a simple text document without any special formatting.
It contains multiple paragraphs and sentences to test basic text splitting.
The content is straightforward and should be handled well by any chunking strategy.
""",
        
        "structured_markdown": """# Complete API Guide

## Overview
This guide covers all aspects of our REST API.

### Authentication
All requests require API authentication:

```bash
curl -H "Authorization: Bearer TOKEN" https://api.example.com
```

## Core Endpoints

### Users Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | /users   | List users  |
| POST   | /users   | Create user |
| PUT    | /users/{id} | Update user |
| DELETE | /users/{id} | Delete user |

#### Create User Example

```python
import requests

def create_user(name: str, email: str):
    \"\"\"Create a new user via API.\"\"\"
    payload = {
        "name": name,
        "email": email,
        "active": True
    }
    
    response = requests.post(
        "https://api.example.com/users",
        json=payload,
        headers={"Authorization": f"Bearer {API_TOKEN}"}
    )
    
    return response.json()
```

### Data Processing

The API supports various data formats:

1. **JSON**: Standard format for all endpoints
2. **XML**: Legacy support for older systems
3. **CSV**: Bulk data operations

#### Error Handling

```javascript
// Handle API errors properly
try {
    const response = await fetch('/api/endpoint');
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    const data = await response.json();
    return data;
} catch (error) {
    console.error('API Error:', error.message);
    throw error;
}
```

### Rate Limiting

| Plan     | Requests/Hour | Burst Limit |
|----------|---------------|-------------|
| Free     | 1,000         | 100         |
| Pro      | 10,000        | 500         |
| Enterprise | 100,000     | 2,000       |

## Advanced Features

### Webhooks

Configure webhooks for real-time notifications:

```json
{
    "url": "https://your-app.com/webhook",
    "events": ["user.created", "user.updated"],
    "secret": "webhook-secret-key"
}
```
""",
        
        "code_heavy": """# Code Examples Collection

## Python Examples

### Data Processing

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

def preprocess_data(df):
    \"\"\"Comprehensive data preprocessing pipeline.\"\"\"
    # Handle missing values
    df = df.fillna(df.mean())
    
    # Remove outliers using IQR
    Q1 = df.quantile(0.25)
    Q3 = df.quantile(0.75)
    IQR = Q3 - Q1
    df = df[~((df < (Q1 - 1.5 * IQR)) | (df > (Q3 + 1.5 * IQR))).any(axis=1)]
    
    return df
```

### Machine Learning Pipeline

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

class MLPipeline:
    def __init__(self, model=None):
        self.model = model or RandomForestClassifier()
        self.is_fitted = False
    
    def fit(self, X, y):
        \"\"\"Train the model.\"\"\"
        self.model.fit(X, y)
        self.is_fitted = True
        return self
    
    def predict(self, X):
        \"\"\"Make predictions.\"\"\"
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        return self.model.predict(X)
```

## JavaScript Examples

### Async Data Fetching

```javascript
class APIClient {
    constructor(baseURL, apiKey) {
        this.baseURL = baseURL;
        this.apiKey = apiKey;
    }
    
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Authorization': `Bearer ${this.apiKey}`,
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };
        
        try {
            const response = await fetch(url, config);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`API request failed: ${error.message}`);
            throw error;
        }
    }
}
```
"""
    }


def benchmark_strategy(content: str, strategy: str) -> dict:
    """Benchmark a specific strategy on content."""
    try:
        processor = EnhancedContentProcessor(
            chunking_strategy=strategy,
            enable_ab_testing=False
        )
        
        start_time = time.time()
        chunks = processor.process_content(content)
        processing_time = time.time() - start_time
        
        if not chunks:
            return {
                "error": "No chunks generated",
                "processing_time": processing_time
            }
        
        # Calculate metrics
        avg_chunk_size = sum(len(c['content']) for c in chunks) / len(chunks)
        code_chunks = sum(1 for c in chunks if c['metadata'].get('contains_code', False))
        header_chunks = sum(1 for c in chunks if c['metadata'].get('header_hierarchy'))
        
        return {
            "success": True,
            "chunks_generated": len(chunks),
            "processing_time": processing_time,
            "avg_chunk_size": avg_chunk_size,
            "code_chunks": code_chunks,
            "header_chunks": header_chunks,
            "strategy_used": chunks[0]['metadata'].get('chunking_strategy', strategy)
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "processing_time": 0
        }


def run_ab_comparison(content: str) -> dict:
    """Run A/B comparison between strategies."""
    try:
        processor = EnhancedContentProcessor(enable_ab_testing=True)
        comparison = processor.compare_strategies(content)
        
        return {
            "success": True,
            "baseline_chunks": comparison.baseline_chunks,
            "enhanced_chunks": comparison.enhanced_chunks,
            "baseline_time": comparison.baseline_time,
            "enhanced_time": comparison.enhanced_time,
            "baseline_avg_size": comparison.baseline_avg_size,
            "enhanced_avg_size": comparison.enhanced_avg_size,
            "semantic_score": comparison.semantic_preservation_score,
            "quality_improvement": comparison.quality_improvement_ratio,
            "performance_ratio": comparison.performance_ratio,
            "recommendation": comparison.recommendation
        }
    except Exception as e:
        return {"error": str(e)}


def main():
    """Run comprehensive benchmarks."""
    print_header("Content Processing Benchmarks")
    
    test_content = create_test_content()
    strategies = ["baseline", "markdown_intelligent", "auto"]
    
    results = {}
    
    # Test individual strategies
    for content_name, content in test_content.items():
        print_section(f"Testing: {content_name}")
        print(f"Content size: {len(content)} characters")
        
        results[content_name] = {}
        
        for strategy in strategies:
            print(f"  Testing {strategy}...")
            result = benchmark_strategy(content, strategy)
            results[content_name][strategy] = result
            
            if result.get('success'):
                print(f"    ✅ {result['chunks_generated']} chunks in {result['processing_time']:.3f}s")
                print(f"       Avg chunk size: {result['avg_chunk_size']:.0f} chars")
                print(f"       Code chunks: {result['code_chunks']}")
                print(f"       Header chunks: {result['header_chunks']}")
            else:
                print(f"    ❌ Error: {result.get('error', 'Unknown error')}")
    
    # Run A/B comparisons
    print_section("A/B Comparisons")
    
    for content_name, content in test_content.items():
        if content_name == "simple_text":
            continue  # Skip simple text for A/B testing
            
        print(f"  A/B testing: {content_name}")
        ab_result = run_ab_comparison(content)
        results[content_name]["ab_comparison"] = ab_result
        
        if ab_result.get('success'):
            print(f"    Baseline: {ab_result['baseline_chunks']} chunks, {ab_result['baseline_time']:.3f}s")
            print(f"    Enhanced: {ab_result['enhanced_chunks']} chunks, {ab_result['enhanced_time']:.3f}s")
            print(f"    Quality improvement: {ab_result['quality_improvement']:.3f}")
            print(f"    Recommendation: {ab_result['recommendation']}")
        else:
            print(f"    ❌ Error: {ab_result.get('error', 'Unknown error')}")
    
    # Generate summary
    print_section("Performance Summary")
    
    successful_results = []
    for content_name, content_results in results.items():
        for strategy, result in content_results.items():
            if strategy != "ab_comparison" and result.get('success'):
                successful_results.append((content_name, strategy, result))
    
    if successful_results:
        # Group by strategy
        by_strategy = {}
        for content_name, strategy, result in successful_results:
            if strategy not in by_strategy:
                by_strategy[strategy] = []
            by_strategy[strategy].append(result)
        
        for strategy, strategy_results in by_strategy.items():
            avg_time = statistics.mean(r['processing_time'] for r in strategy_results)
            avg_chunks = statistics.mean(r['chunks_generated'] for r in strategy_results)
            avg_size = statistics.mean(r['avg_chunk_size'] for r in strategy_results)
            
            print(f"{strategy.upper()}:")
            print(f"  Average processing time: {avg_time:.4f}s")
            print(f"  Average chunks generated: {avg_chunks:.1f}")
            print(f"  Average chunk size: {avg_size:.1f} chars")
    
    # Save detailed results
    output_file = Path("benchmark_results.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📁 Detailed results saved to: {output_file}")
    print("\n✅ Benchmark completed successfully!")


if __name__ == "__main__":
    main()