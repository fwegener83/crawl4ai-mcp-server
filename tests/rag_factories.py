"""Mock factories and test data for RAG knowledge base testing."""
import tempfile
import shutil
import os
from typing import Dict, Any, List, Optional, Union
from unittest.mock import MagicMock, AsyncMock, patch
import numpy as np
import json


class RAGTestData:
    """Factory for creating realistic test documents and crawl results."""
    
    # Sample documents for testing
    SAMPLE_DOCUMENTS = [
        {
            "title": "Python Programming Guide",
            "content": """# Python Programming Guide

Python is a high-level, interpreted programming language with dynamic semantics. Its high-level built-in data structures, combined with dynamic typing and dynamic binding, make it very attractive for Rapid Application Development, as well as for use as a scripting or glue language to connect existing components together.

## Key Features
- Easy to learn and read
- Powerful standard library
- Cross-platform compatibility
- Large community support

## Getting Started
To start programming in Python, you need to install the Python interpreter from the official website.""",
            "url": "https://example.com/python-guide",
            "metadata": {
                "category": "programming",
                "language": "en",
                "word_count": 85,
                "last_updated": "2024-01-15"
            }
        },
        {
            "title": "Machine Learning Basics",
            "content": """# Machine Learning Basics

Machine Learning is a subset of artificial intelligence (AI) that provides systems the ability to automatically learn and improve from experience without being explicitly programmed.

## Types of Machine Learning

### Supervised Learning
Uses labeled training data to learn a mapping function from input variables to output variables.

### Unsupervised Learning  
Uses unlabeled data to find hidden patterns or intrinsic structures in input data.

### Reinforcement Learning
Learns through interaction with an environment using feedback from its own actions and experiences.""",
            "url": "https://example.com/ml-basics",
            "metadata": {
                "category": "machine-learning",
                "language": "en",
                "word_count": 72,
                "last_updated": "2024-01-20"
            }
        },
        {
            "title": "Web Development with React",
            "content": """# Web Development with React

React is a JavaScript library for building user interfaces. It lets you compose complex UIs from small and isolated pieces of code called "components".

## Components
Components let you split the UI into independent, reusable pieces. Think about each piece in isolation.

## JSX
JSX is a syntax extension to JavaScript. It produces React "elements" and makes your code more readable.

## State Management
React components can have state. When the state changes, React re-renders the component.""",
            "url": "https://example.com/react-guide",
            "metadata": {
                "category": "web-development",
                "language": "en",
                "word_count": 58,
                "last_updated": "2024-01-25"
            }
        }
    ]
    
    @classmethod
    def create_crawl_result_dict(cls, doc_index: int = 0, url_override: str = None) -> Dict[str, Any]:
        """Create a crawl result in dictionary format (like domain_deep_crawl output)."""
        doc = cls.SAMPLE_DOCUMENTS[doc_index % len(cls.SAMPLE_DOCUMENTS)]
        url = url_override or doc["url"]
        
        return {
            "success": True,
            "results": [
                {
                    "url": url,
                    "title": doc["title"],
                    "markdown": doc["content"],
                    "success": True,
                    "status_code": 200,
                    "metadata": doc["metadata"],
                    "extracted_content": doc["content"],
                    "links": {"internal": [], "external": []},
                    "media": {"images": [], "videos": [], "audios": []}
                }
            ],
            "metadata": {
                "total_urls": 1,
                "successful_crawls": 1,
                "failed_crawls": 0,
                "crawl_strategy": "bfs"
            }
        }
    
    @classmethod
    def create_crawl_result_string(cls, doc_index: int = 0, url_override: str = None) -> str:
        """Create a crawl result in string format (like web_content_extract output)."""
        doc = cls.SAMPLE_DOCUMENTS[doc_index % len(cls.SAMPLE_DOCUMENTS)]
        return doc["content"]
    
    @classmethod
    def create_multi_result_dict(cls, num_results: int = 3) -> Dict[str, Any]:
        """Create a multi-result crawl in dictionary format."""
        results = []
        for i in range(num_results):
            doc = cls.SAMPLE_DOCUMENTS[i % len(cls.SAMPLE_DOCUMENTS)]
            results.append({
                "url": f"{doc['url']}-{i}",
                "title": f"{doc['title']} - Part {i+1}",
                "markdown": doc["content"],
                "success": True,
                "status_code": 200,
                "metadata": {**doc["metadata"], "part": i+1},
                "extracted_content": doc["content"],
                "links": {"internal": [], "external": []},
                "media": {"images": [], "videos": [], "audios": []}
            })
        
        return {
            "success": True,
            "results": results,
            "metadata": {
                "total_urls": num_results,
                "successful_crawls": num_results,
                "failed_crawls": 0,
                "crawl_strategy": "bfs"
            }
        }
    
    @classmethod
    def create_malformed_result(cls) -> Dict[str, Any]:
        """Create a malformed crawl result for error testing."""
        return {
            "success": False,
            "error": "Network timeout",
            "results": None
        }
    
    @classmethod
    def create_empty_result(cls) -> Dict[str, Any]:
        """Create an empty but valid crawl result."""
        return {
            "success": True,
            "results": [],
            "metadata": {
                "total_urls": 0,
                "successful_crawls": 0,
                "failed_crawls": 0,
                "crawl_strategy": "bfs"
            }
        }
    
    @classmethod
    def create_large_document(cls, word_count: int = 1000) -> str:
        """Create a large document for performance testing."""
        base_content = "This is a sample sentence for testing large document processing. "
        content_parts = [base_content] * (word_count // 10)  # Approximately word_count words
        return "# Large Test Document\n\n" + "".join(content_parts)


class ChromaDBMockFactory:
    """Factory for creating ChromaDB mocks."""
    
    @staticmethod
    def create_persistent_client_mock():
        """Create a mock ChromaDB PersistentClient."""
        mock_client = MagicMock()
        mock_collection = MagicMock()
        
        # Mock collection methods
        mock_collection.add = MagicMock()
        mock_collection.query = MagicMock(return_value={
            "documents": [["Sample document content"]],
            "metadatas": [[{"url": "https://example.com", "title": "Test"}]],
            "distances": [[0.1]],
            "ids": [["doc_1"]]
        })
        mock_collection.count = MagicMock(return_value=0)
        mock_collection.delete = MagicMock()
        mock_collection.peek = MagicMock(return_value={
            "documents": [],
            "metadatas": [],
            "ids": []
        })
        
        # Mock client methods
        mock_client.create_collection = MagicMock(return_value=mock_collection)
        mock_client.get_collection = MagicMock(return_value=mock_collection)
        mock_client.get_or_create_collection = MagicMock(return_value=mock_collection)
        mock_client.list_collections = MagicMock(return_value=[])
        mock_client.delete_collection = MagicMock()
        
        return mock_client, mock_collection
    
    @staticmethod
    def create_collection_mock_with_data(documents: List[str], metadatas: List[Dict] = None):
        """Create a collection mock with pre-populated data."""
        mock_collection = MagicMock()
        
        if metadatas is None:
            metadatas = [{"url": f"https://example.com/doc_{i}"} for i in range(len(documents))]
        
        mock_collection.query = MagicMock(return_value={
            "documents": [documents[:5]],  # Return first 5 for query results
            "metadatas": [metadatas[:5]],
            "distances": [[0.1 * i for i in range(min(5, len(documents)))]],
            "ids": [[f"doc_{i}" for i in range(min(5, len(documents)))]]
        })
        mock_collection.count = MagicMock(return_value=len(documents))
        mock_collection.peek = MagicMock(return_value={
            "documents": documents[:3],  # Peek shows first 3
            "metadatas": metadatas[:3],
            "ids": [f"doc_{i}" for i in range(min(3, len(documents)))]
        })
        
        return mock_collection


class SentenceTransformersMockFactory:
    """Factory for creating SentenceTransformers mocks."""
    
    @staticmethod
    def create_model_mock(embedding_dim: int = 384):
        """Create a mock SentenceTransformers model."""
        mock_model = MagicMock()
        
        def encode_side_effect(sentences, *args, **kwargs):
            """Generate deterministic mock embeddings."""
            if isinstance(sentences, str):
                sentences = [sentences]
            
            # Create deterministic embeddings based on text hash
            embeddings = []
            for text in sentences:
                # Simple hash-based embedding generation
                hash_val = hash(text) % 1000000
                embedding = np.random.RandomState(hash_val).rand(embedding_dim).astype(np.float32)
                # Normalize to unit vector
                embedding = embedding / np.linalg.norm(embedding)
                embeddings.append(embedding)
            
            return np.array(embeddings)
        
        mock_model.encode = MagicMock(side_effect=encode_side_effect)
        return mock_model
    
    @staticmethod
    def create_model_mock_with_error():
        """Create a mock that raises errors for testing."""
        mock_model = MagicMock()
        mock_model.encode = MagicMock(side_effect=RuntimeError("Model loading failed"))
        return mock_model


class TextSplitterMockFactory:
    """Factory for creating text splitter mocks."""
    
    @staticmethod
    def create_recursive_splitter_mock(chunk_size: int = 1000):
        """Create a mock RecursiveCharacterTextSplitter."""
        mock_splitter = MagicMock()
        
        def split_text_side_effect(text):
            """Split text into chunks of approximately chunk_size."""
            if not text:
                return []
            
            # Simple splitting based on chunk_size
            chunks = []
            for i in range(0, len(text), chunk_size):
                chunk = text[i:i + chunk_size]
                if chunk.strip():  # Only add non-empty chunks
                    chunks.append(chunk)
            
            return chunks if chunks else [text]
        
        mock_splitter.split_text = MagicMock(side_effect=split_text_side_effect)
        return mock_splitter


class RAGConfigFactory:
    """Factory for RAG configuration and settings."""
    
    @staticmethod
    def create_default_config():
        """Create default RAG configuration."""
        return {
            "vector_store": {
                "persist_directory": "./test_rag_db",
                "collection_name": "test_collection"
            },
            "embeddings": {
                "model_name": "all-MiniLM-L6-v2",
                "device": "cpu"
            },
            "text_splitter": {
                "chunk_size": 1000,
                "chunk_overlap": 200,
                "separators": ["\n\n", "\n", " ", ""]
            },
            "search": {
                "top_k": 5,
                "similarity_threshold": 0.7
            }
        }
    
    @staticmethod
    def create_test_config():
        """Create configuration optimized for testing."""
        config = RAGConfigFactory.create_default_config()
        config["vector_store"]["persist_directory"] = None  # Use memory-only for tests
        config["embeddings"]["model_name"] = "mock-model"  # Use mock model
        config["text_splitter"]["chunk_size"] = 100  # Smaller chunks for tests
        return config


class TemporaryRAGDatabase:
    """Context manager for temporary RAG database testing."""
    
    def __init__(self, cleanup: bool = True):
        self.cleanup = cleanup
        self.temp_dir = None
        self.db_path = None
    
    def __enter__(self):
        """Create temporary database directory."""
        self.temp_dir = tempfile.mkdtemp(prefix="rag_test_")
        self.db_path = os.path.join(self.temp_dir, "test_db")
        os.makedirs(self.db_path, exist_ok=True)
        return self.db_path
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up temporary database directory."""
        if self.cleanup and self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)


class RAGErrorScenarios:
    """Factory for creating various error scenarios for testing."""
    
    @staticmethod
    def create_database_error_mock():
        """Create mocks that simulate database errors."""
        mock_client = MagicMock()
        mock_client.create_collection = MagicMock(
            side_effect=Exception("Database connection failed")
        )
        return mock_client
    
    @staticmethod
    def create_embedding_error_mock():
        """Create mocks that simulate embedding errors."""
        mock_model = MagicMock()
        mock_model.encode = MagicMock(
            side_effect=RuntimeError("CUDA out of memory")
        )
        return mock_model
    
    @staticmethod
    def create_corrupted_data_scenarios():
        """Create scenarios with corrupted or invalid data."""
        return [
            # Missing required fields
            {"title": "Test", "content": None},
            {"title": None, "content": "Test content"},
            
            # Invalid data types
            {"title": 123, "content": "Valid content"},
            {"title": "Valid title", "content": ["invalid", "list"]},
            
            # Empty data
            {"title": "", "content": ""},
            {"title": "   ", "content": "   "},
            
            # Unicode issues
            {"title": "Test \udcff\udcfe", "content": "Invalid unicode"},
            
            # Extremely large data
            {"title": "A" * 10000, "content": "B" * 100000}
        ]


# Convenience functions for quick test setup
def setup_rag_test_environment():
    """Set up complete RAG test environment with all mocks."""
    chroma_client, chroma_collection = ChromaDBMockFactory.create_persistent_client_mock()
    sentence_model = SentenceTransformersMockFactory.create_model_mock()
    text_splitter = TextSplitterMockFactory.create_recursive_splitter_mock()
    config = RAGConfigFactory.create_test_config()
    
    return {
        "chroma_client": chroma_client,
        "chroma_collection": chroma_collection,
        "sentence_model": sentence_model,
        "text_splitter": text_splitter,
        "config": config,
        "test_data": RAGTestData()
    }


def create_integration_test_data(num_documents: int = 10):
    """Create integration test data with multiple documents."""
    documents = []
    for i in range(num_documents):
        doc_index = i % len(RAGTestData.SAMPLE_DOCUMENTS)
        doc = RAGTestData.SAMPLE_DOCUMENTS[doc_index]
        
        documents.append({
            "title": f"{doc['title']} - Document {i+1}",
            "content": f"Document {i+1} content:\n\n{doc['content']}",
            "url": f"{doc['url']}-{i+1}",
            "metadata": {**doc["metadata"], "document_id": i+1}
        })
    
    return documents