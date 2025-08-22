"""RAG tools for MCP server integration."""
import os
import logging
from typing import Dict, Any, List, Optional, Union
import json

from tools.knowledge_base.vector_store import VectorStore
from tools.knowledge_base.embeddings import EmbeddingService  
from tools.knowledge_base.content_processor import ContentProcessor
from tools.error_sanitizer import sanitize_error_message
import functools

logger = logging.getLogger(__name__)


def error_sanitizer(func):
    """Decorator to sanitize error messages in function outputs."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            # If result is a JSON string, try to sanitize any error messages in it
            if isinstance(result, str):
                try:
                    import json
                    parsed = json.loads(result)
                    if isinstance(parsed, dict) and 'message' in parsed:
                        parsed['message'] = sanitize_error_message(parsed['message'])
                    result = json.dumps(parsed, indent=2)
                except (json.JSONDecodeError, TypeError):
                    # If not JSON, sanitize the entire string
                    result = sanitize_error_message(result)
            return result
        except Exception as e:
            # Sanitize any exceptions that bubble up
            sanitized_error = sanitize_error_message(str(e))
            logger.error(f"Sanitized error in {func.__name__}: {sanitized_error}")
            raise Exception(sanitized_error)
    return wrapper


class RAGService:
    """Main RAG service integrating all components."""
    
    def __init__(
        self,
        persist_directory: Optional[str] = None,
        model_name: Optional[str] = None,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None
    ):
        """Initialize RAG service with all components.
        
        Args:
            persist_directory: Directory for vector database persistence.
            model_name: Name of the embedding model.
            chunk_size: Size of text chunks.
            chunk_overlap: Overlap between chunks.
        """
        self.persist_directory = persist_directory or os.getenv("RAG_DB_PATH", "./rag_db")
        self.model_name = model_name or os.getenv("RAG_MODEL_NAME", "distiluse-base-multilingual-cased-v1")
        
        # Initialize components
        try:
            self.vector_store = VectorStore(persist_directory=self.persist_directory)
            self.embedding_service = EmbeddingService(model_name=self.model_name)
            self.content_processor = ContentProcessor(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            logger.info("RAG service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {str(e)}")
            raise
    
    def store_content(
        self,
        crawl_result: Union[str, Dict[str, Any]],
        collection_name: str = "default"
    ) -> Dict[str, Any]:
        """Store crawl results in vector database.
        
        Args:
            crawl_result: Crawl result (string or dict format).
            collection_name: Name of collection to store in.
            
        Returns:
            Dictionary with storage results.
        """
        try:
            # Process crawl result into chunks
            chunks = self.content_processor.process_crawl_result(
                crawl_result, collection_name
            )
            
            if not chunks:
                return {
                    "success": False,
                    "message": "No content to store",
                    "chunks_stored": 0
                }
            
            # Generate embeddings for chunks
            chunk_texts = [chunk["content"] for chunk in chunks]
            embeddings = self.embedding_service.encode_batch(chunk_texts)
            
            # Prepare data for storage
            documents = chunk_texts
            metadatas = [chunk["metadata"] for chunk in chunks]
            ids = [chunk["id"] for chunk in chunks]
            
            # Store in vector database
            self.vector_store.get_or_create_collection(collection_name)
            self.vector_store.add_documents(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )
            
            logger.info(f"Stored {len(chunks)} chunks in collection '{collection_name}'")
            return {
                "success": True,
                "message": f"Successfully stored {len(chunks)} chunks",
                "chunks_stored": len(chunks),
                "collection_name": collection_name
            }
            
        except Exception as e:
            logger.error(f"Failed to store content: {str(e)}")
            return {
                "success": False,
                "message": f"Storage failed: {str(e)}",
                "chunks_stored": 0
            }
    
    def search_content(
        self,
        query: str,
        collection_name: str = "default",
        n_results: int = 5,
        similarity_threshold: Optional[float] = None,
        enable_context_expansion: bool = False,
        relationship_filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Search for similar content in vector database with enhanced relationship support.
        
        Args:
            query: Search query text.
            collection_name: Collection to search in.
            n_results: Maximum number of results to return.
            similarity_threshold: Minimum similarity score (0-1).
            enable_context_expansion: Whether to expand context using relationships.
            relationship_filter: Filter based on chunk relationships.
            
        Returns:
            Dictionary with search results.
        """
        try:
            # Get or create collection
            self.vector_store.get_or_create_collection(collection_name)
            
            # Use enhanced search if relationships are involved
            if enable_context_expansion or relationship_filter:
                search_results = self.vector_store.search_with_relationships(
                    query=query,
                    k=n_results,
                    relationship_filter=relationship_filter,
                    expand_context=enable_context_expansion
                )
                
                # Apply similarity threshold if specified
                if similarity_threshold:
                    search_results = [
                        result for result in search_results 
                        if result.get('score', 0.0) >= similarity_threshold
                    ]
                
                # Convert to standard format
                formatted_results = []
                for i, result in enumerate(search_results):
                    formatted_results.append({
                        "id": result.get("id", ""),
                        "content": result.get("content", ""),
                        "metadata": result.get("metadata", {}),
                        "similarity": result.get("score", 0.0),
                        "rank": i + 1,
                        "relationship_data": result.get("relationship_data", {}),
                        "expansion_source": result.get("expansion_source"),
                        "expansion_type": result.get("expansion_type")
                    })
                
                return {
                    "success": True,
                    "query": query,
                    "collection_name": collection_name,
                    "results": formatted_results,
                    "total_results": len(formatted_results),
                    "enhanced_search": True,
                    "context_expansion_applied": enable_context_expansion
                }
            
            else:
                # Standard search for backward compatibility
                results = self.vector_store.query(
                    query_texts=[query],
                    n_results=n_results
                )
                
                # Process results
                search_results = []
                if results.get("documents") and results["documents"][0]:
                    documents = results["documents"][0]
                    metadatas = results.get("metadatas", [[]])[0]
                    distances = results.get("distances", [[]])[0]
                    ids = results.get("ids", [[]])[0]
                    
                    for i, (doc, metadata, distance, doc_id) in enumerate(zip(
                        documents, metadatas, distances, ids
                    )):
                        # Convert distance to similarity (assuming cosine distance)
                        similarity = 1.0 - distance if distance is not None else 0.0
                        
                        # Apply similarity threshold if specified
                        if similarity_threshold and similarity < similarity_threshold:
                            continue
                        
                        search_results.append({
                            "id": doc_id,
                            "content": doc,
                            "metadata": metadata or {},
                            "similarity": similarity,
                            "rank": i + 1
                        })
                
                logger.info(f"Search returned {len(search_results)} results for query: '{query[:50]}...'")
                return {
                    "success": True,
                    "query": query,
                    "collection_name": collection_name,
                    "results": search_results,
                    "total_results": len(search_results),
                    "enhanced_search": False
                }
            
        except Exception as e:
            logger.error(f"Failed to search content: {str(e)}")
            return {
                "success": False,
                "query": query,
                "message": f"Search failed: {str(e)}",
                "results": []
            }
    
    def list_collections(self) -> Dict[str, Any]:
        """List all available collections.
        
        Returns:
            Dictionary with collection list.
        """
        try:
            collections = self.vector_store.list_collections()
            
            # Get stats for each collection
            collection_stats = []
            for collection_name in collections:
                try:
                    count = self.vector_store.count(collection_name)
                    collection_stats.append({
                        "name": collection_name,
                        "document_count": count
                    })
                except Exception as e:
                    logger.warning(f"Failed to get stats for collection '{collection_name}': {str(e)}")
                    collection_stats.append({
                        "name": collection_name,
                        "document_count": -1,  # Unknown
                        "error": str(e)
                    })
            
            logger.info(f"Listed {len(collections)} collections")
            return {
                "success": True,
                "collections": collection_stats,
                "total_collections": len(collections)
            }
            
        except Exception as e:
            logger.error(f"Failed to list collections: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to list collections: {str(e)}",
                "collections": []
            }
    
    def delete_collection(self, collection_name: str) -> Dict[str, Any]:
        """Delete a collection.
        
        Args:
            collection_name: Name of collection to delete.
            
        Returns:
            Dictionary with deletion result.
        """
        try:
            self.vector_store.delete_collection(collection_name)
            logger.info(f"Deleted collection: '{collection_name}'")
            return {
                "success": True,
                "message": f"Successfully deleted collection '{collection_name}'",
                "collection_name": collection_name
            }
            
        except Exception as e:
            logger.error(f"Failed to delete collection '{collection_name}': {str(e)}")
            return {
                "success": False,
                "message": f"Failed to delete collection: {str(e)}",
                "collection_name": collection_name
            }


# Global RAG service instance
_rag_service = None


def get_rag_service() -> RAGService:
    """Get or create global RAG service instance."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service


# MCP Tool Functions
@error_sanitizer
async def store_crawl_results(
    crawl_result: Union[str, Dict[str, Any]],
    collection_name: str = "default"
) -> str:
    """Store crawl results in RAG knowledge base.
    
    This tool stores web crawling results in a vector database for later
    semantic search and retrieval. Supports both string format (from 
    web_content_extract) and dict format (from domain_deep_crawl).
    
    Args:
        crawl_result: Crawl result data (string or JSON object)
        collection_name: Name of collection to store results in
        
    Returns:
        JSON string with storage results
    """
    try:
        rag_service = get_rag_service()
        
        # Handle string input (parse JSON if needed)
        if isinstance(crawl_result, str):
            try:
                # Try to parse as JSON first
                parsed_result = json.loads(crawl_result)
                result = rag_service.store_content(parsed_result, collection_name)
            except json.JSONDecodeError:
                # Treat as plain text content
                result = rag_service.store_content(crawl_result, collection_name)
        else:
            # Handle dict input directly
            result = rag_service.store_content(crawl_result, collection_name)
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error in store_crawl_results: {str(e)}")
        error_result = {
            "success": False,
            "message": f"Failed to store crawl results: {str(e)}",
            "chunks_stored": 0
        }
        return json.dumps(error_result, indent=2)


@error_sanitizer
async def search_knowledge_base(
    query: str,
    collection_name: str = "default",
    n_results: int = 5,
    similarity_threshold: Optional[float] = None
) -> str:
    """Search the RAG knowledge base for relevant content.
    
    This tool performs semantic search across stored documents using
    vector similarity. Returns ranked results with similarity scores.
    
    Args:
        query: Search query text
        collection_name: Collection to search in
        n_results: Maximum number of results to return (1-20)
        similarity_threshold: Minimum similarity score (0.0-1.0)
        
    Returns:
        JSON string with search results
    """
    try:
        # Validate parameters
        n_results = max(1, min(20, n_results))
        if similarity_threshold is not None:
            similarity_threshold = max(0.0, min(1.0, similarity_threshold))
        
        rag_service = get_rag_service()
        result = rag_service.search_content(
            query=query,
            collection_name=collection_name,
            n_results=n_results,
            similarity_threshold=similarity_threshold
        )
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error in search_knowledge_base: {str(e)}")
        error_result = {
            "success": False,
            "query": query,
            "message": f"Search failed: {str(e)}",
            "results": []
        }
        return json.dumps(error_result, indent=2)


@error_sanitizer
async def list_collections() -> str:
    """List all available collections in the knowledge base.
    
    This tool returns information about all collections in the vector
    database, including document counts and basic statistics.
    
    Returns:
        JSON string with collection information
    """
    try:
        rag_service = get_rag_service()
        result = rag_service.list_collections()
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error in list_collections: {str(e)}")
        error_result = {
            "success": False,
            "message": f"Failed to list collections: {str(e)}",
            "collections": []
        }
        return json.dumps(error_result, indent=2)


@error_sanitizer
async def delete_collection(collection_name: str) -> str:
    """Delete a collection from the knowledge base.
    
    This tool permanently deletes a collection and all its documents
    from the vector database. This action cannot be undone.
    
    Args:
        collection_name: Name of collection to delete
        
    Returns:
        JSON string with deletion result
    """
    try:
        rag_service = get_rag_service()
        result = rag_service.delete_collection(collection_name)
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error in delete_collection: {str(e)}")
        error_result = {
            "success": False,
            "message": f"Failed to delete collection: {str(e)}",
            "collection_name": collection_name
        }
        return json.dumps(error_result, indent=2)


@error_sanitizer
async def search_with_relationships(
    query: str,
    collection_name: str = "default",
    n_results: int = 5,
    similarity_threshold: Optional[float] = None,
    enable_context_expansion: bool = False,
    relationship_filter: Optional[str] = None
) -> str:
    """Enhanced search with relationship-aware filtering and context expansion.
    
    This tool performs semantic search with support for chunk relationship
    filtering and dynamic context expansion based on overlap and sequential
    relationships between chunks.
    
    Args:
        query: Search query text
        collection_name: Collection to search in
        n_results: Maximum number of base results to return (1-20)
        similarity_threshold: Minimum similarity score (0.0-1.0)
        enable_context_expansion: Whether to expand context using relationships
        relationship_filter: JSON string with relationship filter criteria
        
    Returns:
        JSON string with enhanced search results
    """
    try:
        # Validate parameters
        n_results = max(1, min(20, n_results))
        if similarity_threshold is not None:
            similarity_threshold = max(0.0, min(1.0, similarity_threshold))
        
        # Parse relationship filter if provided
        parsed_filter = None
        if relationship_filter:
            try:
                parsed_filter = json.loads(relationship_filter)
            except json.JSONDecodeError as e:
                return json.dumps({
                    "success": False,
                    "message": f"Invalid relationship filter JSON: {str(e)}",
                    "query": query,
                    "results": []
                }, indent=2)
        
        rag_service = get_rag_service()
        result = rag_service.search_content(
            query=query,
            collection_name=collection_name,
            n_results=n_results,
            similarity_threshold=similarity_threshold,
            enable_context_expansion=enable_context_expansion,
            relationship_filter=parsed_filter
        )
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error in search_with_relationships: {str(e)}")
        error_result = {
            "success": False,
            "query": query,
            "message": f"Enhanced search failed: {str(e)}",
            "results": []
        }
        return json.dumps(error_result, indent=2)


@error_sanitizer
async def get_collection_statistics(collection_name: str = "default") -> str:
    """Get enhanced statistics for a collection including relationship analysis.
    
    This tool returns comprehensive statistics about a collection including
    analysis of chunk relationships, overlap patterns, and context expansion
    eligibility.
    
    Args:
        collection_name: Name of collection to analyze
        
    Returns:
        JSON string with collection statistics
    """
    try:
        rag_service = get_rag_service()
        
        # Get basic collection info
        collections_result = rag_service.list_collections()
        if not collections_result.get("success", False):
            return json.dumps({
                "success": False,
                "message": "Failed to access collections",
                "collection_name": collection_name
            }, indent=2)
        
        # Check if collection exists
        collection_names = [c["name"] for c in collections_result.get("collections", [])]
        if collection_name not in collection_names:
            return json.dumps({
                "success": False,
                "message": f"Collection '{collection_name}' not found",
                "collection_name": collection_name,
                "available_collections": collection_names
            }, indent=2)
        
        # Get enhanced statistics
        stats = rag_service.vector_store.get_collection_stats(collection_name)
        
        return json.dumps({
            "success": True,
            "collection_name": collection_name,
            "statistics": stats
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Error in get_collection_statistics: {str(e)}")
        error_result = {
            "success": False,
            "message": f"Failed to get statistics: {str(e)}",
            "collection_name": collection_name
        }
        return json.dumps(error_result, indent=2)


@error_sanitizer
async def get_chunks_by_relationship(
    center_chunk_id: str,
    relationship_type: str,
    collection_name: str = "default",
    max_results: int = 5
) -> str:
    """Get chunks related to a center chunk by specific relationship types.
    
    This tool retrieves chunks that have specific relationships to a given
    center chunk. Supports sequential, sibling, and overlap relationships.
    
    Args:
        center_chunk_id: ID of the center chunk
        relationship_type: Type of relationship ('sequential', 'siblings', 'overlap')
        collection_name: Collection to search in
        max_results: Maximum number of related chunks to return
        
    Returns:
        JSON string with related chunks
    """
    try:
        # Validate relationship type
        valid_types = ['sequential', 'siblings', 'overlap']
        if relationship_type not in valid_types:
            return json.dumps({
                "success": False,
                "message": f"Invalid relationship type. Must be one of: {valid_types}",
                "center_chunk_id": center_chunk_id,
                "relationship_type": relationship_type
            }, indent=2)
        
        # Validate max_results
        max_results = max(1, min(20, max_results))
        
        rag_service = get_rag_service()
        rag_service.vector_store.get_or_create_collection(collection_name)
        
        # Get related chunks
        related_chunks = rag_service.vector_store.get_chunks_by_relationship(
            center_chunk_id=center_chunk_id,
            relationship_type=relationship_type,
            max_results=max_results
        )
        
        return json.dumps({
            "success": True,
            "center_chunk_id": center_chunk_id,
            "relationship_type": relationship_type,
            "collection_name": collection_name,
            "related_chunks": related_chunks,
            "total_found": len(related_chunks)
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Error in get_chunks_by_relationship: {str(e)}")
        error_result = {
            "success": False,
            "message": f"Failed to get related chunks: {str(e)}",
            "center_chunk_id": center_chunk_id,
            "relationship_type": relationship_type
        }
        return json.dumps(error_result, indent=2)