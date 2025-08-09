"""
Vector search use-case functions.

Contains protocol-agnostic business logic for vector search operations
that can be shared between API and MCP endpoints.
"""

from typing import Optional, List, Dict, Any


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
    limit: int, similarity_threshold: float
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
    
    # Execute vector search
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