"""
Vector search use-case functions.

Contains protocol-agnostic business logic for vector search operations
that can be shared between API and MCP endpoints.
"""

import hashlib
from typing import Optional, List, Dict, Any
from services.query_expansion_service import QueryExpansionService
from services.llm_service import LLMServiceFactory


class ValidationError(Exception):
    """Exception raised when input validation fails."""
    
    def __init__(self, code: str, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


async def search_vectors_use_case(
    vector_service, collection_service,
    query: str, collection_name: Optional[str], 
    limit: int, similarity_threshold: float,
    # Enhancement parameters (optional, API can override env vars)
    enable_query_expansion: Optional[bool] = None,
    max_query_variants: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Shared vector search logic for API and MCP protocols.
    
    Args:
        vector_service: Vector service instance
        collection_service: Collection service instance
        query: Search query text
        collection_name: Optional collection to search in
        limit: Maximum number of results
        similarity_threshold: Minimum similarity score
        
    Returns:
        List of search results with consistent format
        
    Raises:
        ValidationError: When input parameters are invalid
        RuntimeError: When vector service is unavailable
        Exception: When collection doesn't exist or other service errors
    """
    
    # Input validation (test-driven)
    if not query or not query.strip():
        raise ValidationError("MISSING_QUERY", "Query parameter is required")
    
    if limit < 1:
        raise ValidationError("INVALID_LIMIT", "Limit must be greater than 0")
    
    if not (0 <= similarity_threshold <= 1):
        raise ValidationError("INVALID_THRESHOLD", "Similarity threshold must be between 0 and 1")
    
    # Validate collection exists if specified
    if collection_name:
        await collection_service.get_collection(collection_name)  # Will raise if not found
    
    # Check vector service availability
    if not vector_service.vector_available:
        raise RuntimeError("Vector sync service is not available")
    
    # Smart default for optimal search quality (no environment variables needed)
    expansion_enabled = enable_query_expansion if enable_query_expansion is not None else True
    
    if expansion_enabled:
        try:
            # Execute enhanced multi-query search
            results = await _execute_enhanced_vector_search(
                vector_service, query, collection_name, limit, similarity_threshold, max_query_variants
            )
        except Exception:
            # Graceful fallback to original search on any enhancement error
            results = await vector_service.search_vectors(query, collection_name, limit, similarity_threshold)
    else:
        # Execute original vector search
        results = await vector_service.search_vectors(query, collection_name, limit, similarity_threshold)
    
    # Transform results to consistent format
    # Both API and MCP should return the same structure with similarity_score field
    return [
        {
            **result.model_dump(),
            "similarity_score": result.score  # Ensure consistent field name
        }
        for result in results
    ]


async def _execute_enhanced_vector_search(
    vector_service, query: str, collection_name: Optional[str], 
    limit: int, similarity_threshold: float, max_query_variants: Optional[int] = None
) -> List[Any]:
    """
    Execute enhanced vector search with query expansion and deduplication.
    
    Args:
        vector_service: Vector service instance
        query: Original search query
        collection_name: Optional collection to search in
        limit: Maximum number of results
        similarity_threshold: Minimum similarity score
        
    Returns:
        List of deduplicated and ranked search results
    """
    
    # Initialize query expansion service (with fallback handling)
    try:
        llm_service = LLMServiceFactory.create_service()
        expansion_service = QueryExpansionService(llm_service)
    except Exception:
        # If LLM service creation fails, fall back to original search
        raise Exception("LLM service not available for query expansion")
    
    # Smart default for optimal search quality (no environment variables needed)
    max_variants = max_query_variants if max_query_variants is not None else 3
    
    # Expand query with collection context
    expanded_queries = await expansion_service.expand_query_intelligently(
        query=query,
        collection_context=collection_name,
        max_expansions=max_variants - 1  # -1 because original query is included
    )
    
    # Execute searches for all query variants
    all_results = []
    for query_variant in expanded_queries:
        try:
            variant_results = await vector_service.search_vectors(
                query_variant, collection_name, limit, similarity_threshold
            )
            all_results.extend(variant_results)
        except Exception:
            # Continue with other queries if one fails
            continue
    
    # Deduplicate results by content hash
    deduplicated_results = _deduplicate_results(all_results, query)
    
    # Return top results up to the limit
    return deduplicated_results[:limit]


def _deduplicate_results(results: List[Any], original_query: str) -> List[Any]:
    """
    Deduplicate search results by content and rank by composite score.
    
    Args:
        results: List of search results
        original_query: Original user query for relevance boosting
        
    Returns:
        Deduplicated and ranked results
    """
    
    if not results:
        return []
    
    # Deduplicate by content hash
    seen_hashes = set()
    unique_results = []
    
    for result in results:
        try:
            content = result.model_dump().get('content', '')
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_results.append(result)
        except Exception:
            # Include result if hashing fails
            unique_results.append(result)
    
    # Sort by score (higher is better)
    try:
        unique_results.sort(key=lambda x: x.score, reverse=True)
    except Exception:
        # Continue without sorting if score access fails
        pass
    
    return unique_results