"""
Collection management use-case functions.

Contains protocol-agnostic business logic for collection operations
that can be shared between API and MCP endpoints.
"""

from typing import List, Dict, Any
from services.interfaces import CollectionInfo


class ValidationError(Exception):
    """Exception raised when input validation fails."""
    
    def __init__(self, code: str, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


async def list_collections_use_case(
    collection_service
) -> List[CollectionInfo]:
    """
    Shared collection listing logic for API and MCP protocols.
    
    Args:
        collection_service: Collection service instance
        
    Returns:
        List of CollectionInfo objects with consistent format
        
    Raises:
        Exception: When collection service errors occur
    """
    
    # No input validation needed for list operation
    
    # Execute collection listing
    collections = await collection_service.list_collections()
    
    # Return consistent format - both API and MCP get same data structure
    return collections


async def create_collection_use_case(
    collection_service, 
    name: str, 
    description: str = ""
) -> CollectionInfo:
    """
    Shared collection creation logic for API and MCP protocols.
    
    Args:
        collection_service: Collection service instance
        name: Collection name
        description: Optional collection description
        
    Returns:
        CollectionInfo object with consistent format
        
    Raises:
        ValidationError: When input parameters are invalid
        Exception: When collection service errors occur (e.g., collection already exists)
    """
    
    # Input validation (test-driven)
    if not isinstance(name, str):
        raise ValidationError("INVALID_NAME_TYPE", "Collection name must be a string")
    
    if not isinstance(description, str):
        raise ValidationError("INVALID_DESCRIPTION_TYPE", "Collection description must be a string")
        
    if not name or not name.strip():
        raise ValidationError("MISSING_NAME", "Collection name is required")
        
    # Additional name validation (following existing service patterns)
    name = name.strip()
    if len(name) == 0:
        raise ValidationError("EMPTY_NAME", "Collection name cannot be empty")
    
    # Execute collection creation
    collection = await collection_service.create_collection(name, description)
    
    # Return consistent format
    return collection


async def get_collection_use_case(
    collection_service,
    name: str
) -> CollectionInfo:
    """
    Shared collection retrieval logic for API and MCP protocols.
    
    Args:
        collection_service: Collection service instance
        name: Collection name
        
    Returns:
        CollectionInfo object with consistent format
        
    Raises:
        ValidationError: When input parameters are invalid
        Exception: When collection doesn't exist or service errors occur
    """
    
    # Input validation (test-driven)
    if not isinstance(name, str):
        raise ValidationError("INVALID_NAME_TYPE", "Collection name must be a string")
        
    if not name or not name.strip():
        raise ValidationError("MISSING_NAME", "Collection name is required")
    
    # Validate and normalize name
    name = name.strip()
    
    # Execute collection retrieval (will raise if not found)
    collection = await collection_service.get_collection(name)
    
    # Return consistent format
    return collection


async def delete_collection_use_case(
    collection_service,
    name: str,
    vector_service=None
) -> Dict[str, Any]:
    """
    Shared collection deletion logic for API and MCP protocols.
    
    Performs cascade deletion: collection → files → vectors
    
    Args:
        collection_service: Collection service instance
        name: Collection name
        vector_service: Optional vector service for cleanup
        
    Returns:
        Deletion result with consistent format
        
    Raises:
        ValidationError: When input parameters are invalid
        Exception: When collection doesn't exist or service errors occur
    """
    
    # Input validation (test-driven)
    if not isinstance(name, str):
        raise ValidationError("INVALID_NAME_TYPE", "Collection name must be a string")
        
    if not name or not name.strip():
        raise ValidationError("MISSING_NAME", "Collection name is required")
    
    # Validate and normalize name
    name = name.strip()
    
    # Step 1: Delete collection files (will raise if not found)
    result = await collection_service.delete_collection(name)
    
    # Step 2: Delete associated vectors if vector service is available
    if vector_service and vector_service.vector_available:
        try:
            vector_result = await vector_service.delete_collection_vectors(name)
            if vector_result.get("success", False):
                result["vectors_deleted"] = vector_result.get("deleted_count", 0)
                result["vector_cleanup"] = "success"
            else:
                result["vectors_deleted"] = 0
                result["vector_cleanup"] = f"failed: {vector_result.get('error', 'unknown error')}"
                # Don't fail the entire operation if vector cleanup fails
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Vector cleanup failed for collection '{name}': {vector_result.get('error')}")
        except Exception as e:
            # Don't fail the entire operation if vector cleanup fails
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Vector cleanup error for collection '{name}': {e}")
            result["vectors_deleted"] = 0
            result["vector_cleanup"] = f"error: {str(e)}"
    else:
        result["vectors_deleted"] = 0
        result["vector_cleanup"] = "skipped: vector service not available"
    
    # Return enhanced result with vector cleanup information
    return result