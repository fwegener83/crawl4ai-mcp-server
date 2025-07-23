"""RAG Knowledge Base module for Crawl4AI MCP Server.

This module provides vector storage, embedding services, and content processing
for building a local RAG (Retrieval-Augmented Generation) knowledge base from
web crawling results.
"""

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