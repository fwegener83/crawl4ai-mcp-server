"""RAG Knowledge Base module for Crawl4AI MCP Server.

This module provides vector storage, embedding services, and content processing
for building a local RAG (Retrieval-Augmented Generation) knowledge base from
web crawling results.
"""

import os
from pathlib import Path

# Load environment variables from .env file (same logic as unified_server.py)
# This ensures that environment variables are available when any knowledge_base module is imported
_env_file = Path(__file__).parent.parent.parent / '.env'
if _env_file.exists():
    with open(_env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                # Don't override existing environment variables
                if key not in os.environ:
                    os.environ[key] = value

# Module version
__version__ = "0.1.0"

# Import main components
from .vector_store import VectorStore
from .embeddings import EmbeddingService  
from .content_processor import ContentProcessor
from .rag_tools import (
    store_crawl_results,
    search_knowledge_base,
    list_collections,
    delete_collection,
    RAGService,
    get_rag_service
)

__all__ = [
    "VectorStore",
    "EmbeddingService", 
    "ContentProcessor",
    "store_crawl_results",
    "search_knowledge_base",
    "list_collections",
    "delete_collection",
    "RAGService",
    "get_rag_service"
]