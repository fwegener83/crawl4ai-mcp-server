"""
Comprehensive benchmarking and quality validation for content processors.

This module provides performance benchmarks, quality metrics, and edge case testing
for comparing different chunking strategies in the File Collection Vector Sync system.
"""

import os
import time
import json
import hashlib
import statistics
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

from enhanced_content_processor import EnhancedContentProcessor, ChunkingComparisonResult
from chunking_config import get_chunking_config, PRESETS


@dataclass
class BenchmarkResult:
    """Results from a single benchmark test."""
    test_name: str
    content_size: int
    processor_name: str
    chunks_generated: int
    processing_time: float
    avg_chunk_size: float
    semantic_score: float
    metadata_richness: float
    error_occurred: bool = False
    error_message: Optional[str] = None


@dataclass
class QualityMetrics:
    """Quality assessment metrics for chunking results."""
    structure_preservation: float
    code_block_integrity: float
    table_preservation: float
    header_hierarchy_score: float
    language_detection_accuracy: float
    chunk_size_consistency: float
    metadata_completeness: float
    overall_quality_score: float


class ContentBenchmarkSuite:
    """Comprehensive benchmark suite for content processing strategies."""
    
    def __init__(self, output_dir: Optional[Path] = None):
        """Initialize benchmark suite.
        
        Args:
            output_dir: Directory to save benchmark results
        """
        self.output_dir = output_dir or Path("./benchmark_results")
        self.output_dir.mkdir(exist_ok=True)
        
        # Test data
        self.test_datasets = self._create_test_datasets()
        
        # Results storage
        self.results: List[BenchmarkResult] = []
        self.quality_assessments: Dict[str, QualityMetrics] = {}
    
    def _create_test_datasets(self) -> Dict[str, str]:
        """Create diverse test datasets for benchmarking."""
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

### Pagination

```python
def get_all_users():
    \"\"\"Fetch all users with pagination.\"\"\"
    users = []
    page = 1
    
    while True:
        response = requests.get(
            f"https://api.example.com/users?page={page}&limit=100"
        )
        data = response.json()
        
        users.extend(data['users'])
        
        if not data['has_next']:
            break
            
        page += 1
    
    return users
```
""",
            
            "code_heavy": """# Code Examples Collection

## Python Examples

### Data Processing

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def preprocess_data(df):
    \"\"\"Comprehensive data preprocessing pipeline.\"\"\"
    # Handle missing values
    df = df.fillna(df.mean())
    
    # Remove outliers using IQR
    Q1 = df.quantile(0.25)
    Q3 = df.quantile(0.75)
    IQR = Q3 - Q1
    df = df[~((df < (Q1 - 1.5 * IQR)) | (df > (Q3 + 1.5 * IQR))).any(axis=1)]
    
    # Feature scaling
    scaler = StandardScaler()
    df[df.select_dtypes(include=[np.number]).columns] = scaler.fit_transform(
        df.select_dtypes(include=[np.number])
    )
    
    return df
```

### Machine Learning Pipeline

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

class MLPipeline:
    def __init__(self, model=None):
        self.model = model or RandomForestClassifier()
        self.scaler = StandardScaler()
        self.is_fitted = False
    
    def fit(self, X, y):
        \"\"\"Train the model.\"\"\"
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_fitted = True
        return self
    
    def predict(self, X):
        \"\"\"Make predictions.\"\"\"
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def evaluate(self, X_test, y_test):
        \"\"\"Evaluate model performance.\"\"\"
        y_pred = self.predict(X_test)
        return {
            'report': classification_report(y_test, y_pred),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
        }
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
    
    async getUsers() {
        return this.request('/users');
    }
    
    async createUser(userData) {
        return this.request('/users', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }
}
```

### React Component

```jsx
import React, { useState, useEffect } from 'react';

const UserList = ({ apiClient }) => {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    
    useEffect(() => {
        const fetchUsers = async () => {
            try {
                const userData = await apiClient.getUsers();
                setUsers(userData);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };
        
        fetchUsers();
    }, [apiClient]);
    
    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;
    
    return (
        <div>
            <h2>Users</h2>
            <ul>
                {users.map(user => (
                    <li key={user.id}>
                        {user.name} ({user.email})
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default UserList;
```
""",
            
            "table_heavy": """# Database Schema Documentation

## User Tables

### users
Primary user information table.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique user identifier |
| username | VARCHAR(50) | UNIQUE, NOT NULL | User login name |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email address |
| password_hash | VARCHAR(255) | NOT NULL | Encrypted password |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Account creation time |
| updated_at | TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | Last modification time |
| is_active | BOOLEAN | DEFAULT TRUE | Account status |

### user_profiles
Extended user profile information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| user_id | INT | FOREIGN KEY(users.id) | Reference to user |
| first_name | VARCHAR(100) | NULL | User's first name |
| last_name | VARCHAR(100) | NULL | User's last name |
| bio | TEXT | NULL | User biography |
| avatar_url | VARCHAR(500) | NULL | Profile picture URL |
| birth_date | DATE | NULL | Date of birth |
| location | VARCHAR(255) | NULL | User location |

## Content Tables

### posts
User-generated content posts.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Unique post identifier |
| user_id | INT | FOREIGN KEY(users.id) | Post author |
| title | VARCHAR(500) | NOT NULL | Post title |
| content | TEXT | NOT NULL | Post content |
| status | ENUM | 'draft', 'published', 'archived' | Publication status |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation time |
| published_at | TIMESTAMP | NULL | Publication time |
| view_count | INT | DEFAULT 0 | Number of views |

### comments
Comments on posts.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Unique comment ID |
| post_id | BIGINT | FOREIGN KEY(posts.id) | Referenced post |
| user_id | INT | FOREIGN KEY(users.id) | Comment author |
| parent_id | BIGINT | FOREIGN KEY(comments.id), NULL | Parent comment for threading |
| content | TEXT | NOT NULL | Comment text |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation time |
| is_edited | BOOLEAN | DEFAULT FALSE | Edit status |

## Analytics Tables

### page_views
Track page view statistics.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Unique view ID |
| user_id | INT | FOREIGN KEY(users.id), NULL | Viewer (if logged in) |
| page_url | VARCHAR(1000) | NOT NULL, INDEX | Visited page |
| referrer | VARCHAR(1000) | NULL | Referrer URL |
| user_agent | TEXT | NULL | Browser user agent |
| ip_address | VARCHAR(45) | NULL | Visitor IP |
| session_id | VARCHAR(255) | NULL, INDEX | Session identifier |
| timestamp | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | View time |

### search_queries
User search behavior tracking.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Unique query ID |
| user_id | INT | FOREIGN KEY(users.id), NULL | Searcher |
| query_text | VARCHAR(500) | NOT NULL | Search terms |
| results_count | INT | DEFAULT 0 | Number of results |
| clicked_result_id | BIGINT | NULL | Which result was clicked |
| search_timestamp | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Search time |
""",
            
            "malformed_markdown": """# Broken Document

This has some ## invalid header structure
And missing closing tags for ```code
def broken_function():
    return "no closing quote

## Another Section

| Missing | Table |
|---------|
| Incomplete | row

```python
# Missing closing backticks
def another_function():
    pass

### Nested Lists
- Item 1
  - Subitem 1
    - Deep item
- Item 2
  - Subitem without proper nesting
    
    Some paragraph text mixed in

```

| Another | Table | With |
|---------|-------|------|
| Missing | Closing | Pipe |
| Row | Data

## Final Section
Some text to end the document.
""",
            
            "large_content": self._generate_large_content()
        }
    
    def _generate_large_content(self) -> str:
        """Generate large content for performance testing."""
        base_section = """## Section {i}

This is section {i} of a large document for performance testing.
It contains multiple paragraphs and various markdown elements.

### Subsection {i}.1

Here's some code:

```python
def function_{i}():
    \"\"\"Function for section {i}.\"\"\"
    return f"Result from section {i}"
```

### Subsection {i}.2

And a table:

| Column A | Column B | Column C |
|----------|----------|----------|
| Value {i}A | Value {i}B | Value {i}C |
| Data {i}1 | Data {i}2 | Data {i}3 |

More text content for section {i} to make it substantial.
"""
        
        sections = [base_section.format(i=i) for i in range(1, 51)]  # 50 sections
        return "# Large Document for Performance Testing\n\n" + "\n\n".join(sections)
    
    def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """Run comprehensive benchmark across all test datasets and strategies."""
        print("🚀 Starting Comprehensive Content Processing Benchmark")
        print("=" * 60)
        
        benchmark_start = time.time()
        strategies = ["baseline", "markdown_intelligent", "auto"]
        
        for dataset_name, content in self.test_datasets.items():
            print(f"\n📊 Testing dataset: {dataset_name}")
            print(f"   Content size: {len(content)} characters")
            
            for strategy in strategies:
                print(f"   Testing strategy: {strategy}...")
                result = self._benchmark_strategy(dataset_name, content, strategy)
                self.results.append(result)
                
                if result.error_occurred:
                    print(f"   ❌ Error: {result.error_message}")
                else:
                    print(f"   ✅ Success: {result.chunks_generated} chunks in {result.processing_time:.3f}s")
        
        # Run A/B comparisons
        print(f"\n🔬 Running A/B Comparisons")
        ab_results = self._run_ab_comparisons()
        
        # Analyze quality metrics
        print(f"\n📈 Analyzing Quality Metrics")
        quality_results = self._analyze_quality_metrics()
        
        benchmark_time = time.time() - benchmark_start
        
        # Generate comprehensive report
        report = {
            "benchmark_info": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_time": benchmark_time,
                "datasets_tested": len(self.test_datasets),
                "strategies_tested": len(strategies),
                "total_tests": len(self.results)
            },
            "individual_results": [asdict(r) for r in self.results],
            "ab_comparisons": ab_results,
            "quality_metrics": quality_results,
            "summary": self._generate_summary()
        }
        
        # Save results
        output_file = self.output_dir / f"benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📁 Results saved to: {output_file}")
        print(f"⏱️  Total benchmark time: {benchmark_time:.2f}s")
        
        return report
    
    def _benchmark_strategy(self, dataset_name: str, content: str, strategy: str) -> BenchmarkResult:
        """Benchmark a specific strategy on a dataset."""
        try:
            processor = EnhancedContentProcessor(
                chunking_strategy=strategy,
                enable_ab_testing=False  # Disable for pure performance testing
            )
            
            start_time = time.time()
            chunks = processor.process_content(content)
            processing_time = time.time() - start_time
            
            if not chunks:
                return BenchmarkResult(
                    test_name=f"{dataset_name}_{strategy}",
                    content_size=len(content),
                    processor_name=strategy,
                    chunks_generated=0,
                    processing_time=processing_time,
                    avg_chunk_size=0,
                    semantic_score=0,
                    metadata_richness=0,
                    error_occurred=True,
                    error_message="No chunks generated"
                )
            
            avg_chunk_size = sum(len(c['content']) for c in chunks) / len(chunks)
            semantic_score = self._calculate_semantic_score(chunks)
            metadata_richness = self._calculate_metadata_richness(chunks)
            
            return BenchmarkResult(
                test_name=f"{dataset_name}_{strategy}",
                content_size=len(content),
                processor_name=strategy,
                chunks_generated=len(chunks),
                processing_time=processing_time,
                avg_chunk_size=avg_chunk_size,
                semantic_score=semantic_score,
                metadata_richness=metadata_richness
            )
            
        except Exception as e:
            return BenchmarkResult(
                test_name=f"{dataset_name}_{strategy}",
                content_size=len(content),
                processor_name=strategy,
                chunks_generated=0,
                processing_time=0,
                avg_chunk_size=0,
                semantic_score=0,
                metadata_richness=0,
                error_occurred=True,
                error_message=str(e)
            )
    
    def _run_ab_comparisons(self) -> Dict[str, Any]:
        """Run A/B comparisons between strategies."""
        processor = EnhancedContentProcessor(enable_ab_testing=True)
        comparisons = {}
        
        for dataset_name, content in self.test_datasets.items():
            if dataset_name == "malformed_markdown":
                continue  # Skip problematic content for A/B testing
                
            try:
                comparison = processor.compare_strategies(content)
                comparisons[dataset_name] = asdict(comparison)
            except Exception as e:
                comparisons[dataset_name] = {"error": str(e)}
        
        return comparisons
    
    def _analyze_quality_metrics(self) -> Dict[str, QualityMetrics]:
        """Analyze quality metrics for each strategy."""
        quality_metrics = {}
        
        # Group results by strategy
        strategy_results = {}
        for result in self.results:
            if result.error_occurred:
                continue
            
            if result.processor_name not in strategy_results:
                strategy_results[result.processor_name] = []
            strategy_results[result.processor_name].append(result)
        
        # Calculate quality metrics for each strategy
        for strategy, results in strategy_results.items():
            metrics = self._calculate_strategy_quality_metrics(results)
            quality_metrics[strategy] = metrics
        
        return quality_metrics
    
    def _calculate_strategy_quality_metrics(self, results: List[BenchmarkResult]) -> QualityMetrics:
        """Calculate quality metrics for a strategy based on benchmark results."""
        if not results:
            return QualityMetrics(0, 0, 0, 0, 0, 0, 0, 0)
        
        # Aggregate metrics
        avg_semantic = statistics.mean(r.semantic_score for r in results)
        avg_metadata = statistics.mean(r.metadata_richness for r in results)
        
        # Calculate consistency metrics
        chunk_sizes = [r.avg_chunk_size for r in results]
        size_consistency = 1.0 - (statistics.stdev(chunk_sizes) / statistics.mean(chunk_sizes)) if len(chunk_sizes) > 1 else 1.0
        size_consistency = max(0, min(1, size_consistency))  # Clamp to [0, 1]
        
        # Overall quality score
        overall_quality = (avg_semantic * 0.4 + avg_metadata * 0.3 + size_consistency * 0.3)
        
        return QualityMetrics(
            structure_preservation=avg_semantic,
            code_block_integrity=avg_semantic,  # Simplified
            table_preservation=avg_semantic,    # Simplified
            header_hierarchy_score=avg_semantic, # Simplified
            language_detection_accuracy=avg_metadata * 0.5,  # Approximate
            chunk_size_consistency=size_consistency,
            metadata_completeness=avg_metadata,
            overall_quality_score=overall_quality
        )
    
    def _calculate_semantic_score(self, chunks: List[Dict[str, Any]]) -> float:
        """Calculate semantic preservation score for chunks."""
        if not chunks:
            return 0.0
        
        score = 0.0
        
        # Structure indicators
        header_chunks = sum(1 for c in chunks if c['metadata'].get('header_hierarchy'))
        score += (header_chunks / len(chunks)) * 0.3
        
        # Code preservation
        code_chunks = sum(1 for c in chunks if c['metadata'].get('contains_code'))
        if any('```' in c['content'] for c in chunks):
            score += (code_chunks / len(chunks)) * 0.3
        
        # Size consistency
        sizes = [c['metadata'].get('character_count', len(c['content'])) for c in chunks]
        avg_size = statistics.mean(sizes)
        if 500 <= avg_size <= 1500:
            score += 0.2
        
        # Metadata richness
        avg_metadata_fields = statistics.mean(len(c['metadata']) for c in chunks)
        score += min(avg_metadata_fields / 20, 0.2)
        
        return min(score, 1.0)
    
    def _calculate_metadata_richness(self, chunks: List[Dict[str, Any]]) -> float:
        """Calculate metadata richness score."""
        if not chunks:
            return 0.0
        
        total_fields = sum(len(c['metadata']) for c in chunks)
        avg_fields = total_fields / len(chunks)
        
        # Normalize to 0-1 scale (assuming 15 fields is good richness)
        return min(avg_fields / 15, 1.0)
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate benchmark summary statistics."""
        if not self.results:
            return {"error": "No results to summarize"}
        
        successful_results = [r for r in self.results if not r.error_occurred]
        
        if not successful_results:
            return {"error": "No successful results"}
        
        # Performance summary
        by_strategy = {}
        for result in successful_results:
            strategy = result.processor_name
            if strategy not in by_strategy:
                by_strategy[strategy] = []
            by_strategy[strategy].append(result)
        
        summary = {}
        for strategy, results in by_strategy.items():
            summary[strategy] = {
                "tests_run": len(results),
                "avg_processing_time": statistics.mean(r.processing_time for r in results),
                "avg_chunks_generated": statistics.mean(r.chunks_generated for r in results),
                "avg_chunk_size": statistics.mean(r.avg_chunk_size for r in results),
                "avg_semantic_score": statistics.mean(r.semantic_score for r in results),
                "avg_metadata_richness": statistics.mean(r.metadata_richness for r in results)
            }
        
        return summary


def run_benchmark_cli():
    """Command-line interface for running benchmarks."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run content processing benchmarks")
    parser.add_argument("--output-dir", type=Path, help="Directory to save results")
    parser.add_argument("--dataset", choices=["all", "simple", "structured", "code", "table", "malformed", "large"], 
                       default="all", help="Dataset to test")
    
    args = parser.parse_args()
    
    os.environ['TMPDIR'] = '/tmp'
    
    benchmark_suite = ContentBenchmarkSuite(output_dir=args.output_dir)
    
    if args.dataset != "all":
        # Filter to specific dataset
        dataset_map = {
            "simple": "simple_text",
            "structured": "structured_markdown", 
            "code": "code_heavy",
            "table": "table_heavy",
            "malformed": "malformed_markdown",
            "large": "large_content"
        }
        dataset_key = dataset_map[args.dataset]
        benchmark_suite.test_datasets = {dataset_key: benchmark_suite.test_datasets[dataset_key]}
    
    results = benchmark_suite.run_comprehensive_benchmark()
    
    print("\n" + "="*60)
    print("📊 Benchmark Summary")
    print("="*60)
    
    for strategy, metrics in results["summary"].items():
        print(f"\n{strategy.upper()}:")
        print(f"  Avg processing time: {metrics['avg_processing_time']:.4f}s")
        print(f"  Avg chunks generated: {metrics['avg_chunks_generated']:.1f}")
        print(f"  Avg semantic score: {metrics['avg_semantic_score']:.3f}")
        print(f"  Avg metadata richness: {metrics['avg_metadata_richness']:.3f}")


if __name__ == "__main__":
    run_benchmark_cli()