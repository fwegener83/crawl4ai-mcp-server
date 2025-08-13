"""
File management use-case functions.

Contains protocol-agnostic business logic for file operations within collections
that can be shared between API and MCP endpoints.
"""

from typing import List, Dict, Any
from urllib.parse import unquote
from services.interfaces import FileInfo


class ValidationError(Exception):
    """Exception raised when input validation fails."""
    
    def __init__(self, code: str, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


async def save_file_use_case(
    collection_service,
    collection_name: str,
    file_path: str, 
    content: str,
    folder_path: str = ""
) -> FileInfo:
    """
    Shared file saving logic for API and MCP protocols.
    
    Args:
        collection_service: Collection service instance
        collection_name: Name of the collection
        file_path: Path/name of the file
        content: File content to save
        folder_path: Optional subfolder path
        
    Returns:
        FileInfo object with consistent format
        
    Raises:
        ValidationError: When input parameters are invalid
        Exception: When collection/service errors occur
    """
    
    # Input validation (test-driven)
    if not isinstance(collection_name, str):
        raise ValidationError("INVALID_COLLECTION_NAME_TYPE", "Collection name must be a string")
    
    if not isinstance(file_path, str):
        raise ValidationError("INVALID_FILE_PATH_TYPE", "File path must be a string")
        
    if not isinstance(folder_path, str):
        raise ValidationError("INVALID_FOLDER_PATH_TYPE", "Folder path must be a string")
    
    # Check content type and required - handle None and empty string
    if content is None:
        raise ValidationError("MISSING_CONTENT", "Content is required")
        
    if not isinstance(content, str):
        raise ValidationError("INVALID_CONTENT_TYPE", "Content must be a string")
        
    if not content:  # Empty string validation to maintain backward compatibility
        raise ValidationError("MISSING_CONTENT", "Content is required")
    
    # URL decode collection name and file path (handling spaces and special characters)
    decoded_collection_name = unquote(collection_name) if collection_name else ""
    decoded_file_path = unquote(file_path) if file_path else ""
    decoded_folder_path = unquote(folder_path) if folder_path else ""
    
    # Validate required fields
    if not decoded_collection_name or not decoded_collection_name.strip():
        raise ValidationError("MISSING_COLLECTION_NAME", "Collection name is required")
        
    if not decoded_file_path or not decoded_file_path.strip():
        raise ValidationError("MISSING_FILE_PATH", "File path is required")
    
    # Normalize names  
    decoded_collection_name = decoded_collection_name.strip()
    decoded_file_path = decoded_file_path.strip()
    
    # Execute file saving
    file_info = await collection_service.save_file(
        decoded_collection_name, decoded_file_path, content, decoded_folder_path
    )
    
    # Return consistent format
    return file_info


async def get_file_use_case(
    collection_service,
    collection_name: str,
    file_path: str,
    folder_path: str = ""
) -> FileInfo:
    """
    Shared file retrieval logic for API and MCP protocols.
    
    Args:
        collection_service: Collection service instance
        collection_name: Name of the collection
        file_path: Path/name of the file
        folder_path: Optional subfolder path
        
    Returns:
        FileInfo object with consistent format
        
    Raises:
        ValidationError: When input parameters are invalid
        Exception: When file doesn't exist or service errors occur
    """
    
    # Input validation (test-driven)
    if not isinstance(collection_name, str):
        raise ValidationError("INVALID_COLLECTION_NAME_TYPE", "Collection name must be a string")
    
    if not isinstance(file_path, str):
        raise ValidationError("INVALID_FILE_PATH_TYPE", "File path must be a string")
        
    if not isinstance(folder_path, str):
        raise ValidationError("INVALID_FOLDER_PATH_TYPE", "Folder path must be a string")
    
    # URL decode collection name and file path (handling spaces and special characters)
    decoded_collection_name = unquote(collection_name) if collection_name else ""
    decoded_file_path = unquote(file_path) if file_path else ""
    decoded_folder_path = unquote(folder_path) if folder_path else ""
    
    # Validate required fields
    if not decoded_collection_name or not decoded_collection_name.strip():
        raise ValidationError("MISSING_COLLECTION_NAME", "Collection name is required")
        
    if not decoded_file_path or not decoded_file_path.strip():
        raise ValidationError("MISSING_FILE_PATH", "File path is required")
    
    # Normalize names
    decoded_collection_name = decoded_collection_name.strip()
    decoded_file_path = decoded_file_path.strip()
    
    # Execute file retrieval (will raise if not found)
    file_info = await collection_service.get_file(
        decoded_collection_name, decoded_file_path, decoded_folder_path
    )
    
    # Return consistent format
    return file_info


async def update_file_use_case(
    collection_service,
    collection_name: str,
    file_path: str,
    content: str,
    folder_path: str = ""
) -> FileInfo:
    """
    Shared file updating logic for API and MCP protocols.
    
    Args:
        collection_service: Collection service instance
        collection_name: Name of the collection
        file_path: Path/name of the file
        content: New file content
        folder_path: Optional subfolder path
        
    Returns:
        FileInfo object with consistent format
        
    Raises:
        ValidationError: When input parameters are invalid
        Exception: When file doesn't exist or service errors occur
    """
    
    # Input validation (test-driven)
    if not isinstance(collection_name, str):
        raise ValidationError("INVALID_COLLECTION_NAME_TYPE", "Collection name must be a string")
    
    if not isinstance(file_path, str):
        raise ValidationError("INVALID_FILE_PATH_TYPE", "File path must be a string")
        
    if not isinstance(folder_path, str):
        raise ValidationError("INVALID_FOLDER_PATH_TYPE", "Folder path must be a string")
    
    # Check content type and required - handle None but allow empty string for updates
    if content is None:
        raise ValidationError("MISSING_CONTENT", "Content is required")
        
    if not isinstance(content, str):
        raise ValidationError("INVALID_CONTENT_TYPE", "Content must be a string")
    
    # URL decode collection name and file path (handling spaces and special characters)
    decoded_collection_name = unquote(collection_name) if collection_name else ""
    decoded_file_path = unquote(file_path) if file_path else ""
    decoded_folder_path = unquote(folder_path) if folder_path else ""
    
    # Validate required fields
    if not decoded_collection_name or not decoded_collection_name.strip():
        raise ValidationError("MISSING_COLLECTION_NAME", "Collection name is required")
        
    if not decoded_file_path or not decoded_file_path.strip():
        raise ValidationError("MISSING_FILE_PATH", "File path is required")
    
    # Normalize names
    decoded_collection_name = decoded_collection_name.strip()
    decoded_file_path = decoded_file_path.strip()
    
    # Execute file updating
    file_info = await collection_service.update_file(
        decoded_collection_name, decoded_file_path, content, decoded_folder_path
    )
    
    # Return consistent format
    return file_info


async def delete_file_use_case(
    collection_service,
    collection_name: str,
    file_path: str,
    folder_path: str = ""
) -> Dict[str, Any]:
    """
    Shared file deletion logic for API and MCP protocols.
    
    Args:
        collection_service: Collection service instance
        collection_name: Name of the collection
        file_path: Path/name of the file
        folder_path: Optional subfolder path
        
    Returns:
        Deletion result with consistent format
        
    Raises:
        ValidationError: When input parameters are invalid
        Exception: When file doesn't exist or service errors occur
    """
    
    # Input validation (test-driven)
    if not isinstance(collection_name, str):
        raise ValidationError("INVALID_COLLECTION_NAME_TYPE", "Collection name must be a string")
    
    if not isinstance(file_path, str):
        raise ValidationError("INVALID_FILE_PATH_TYPE", "File path must be a string")
        
    if not isinstance(folder_path, str):
        raise ValidationError("INVALID_FOLDER_PATH_TYPE", "Folder path must be a string")
    
    # URL decode collection name and file path (handling spaces and special characters)
    decoded_collection_name = unquote(collection_name) if collection_name else ""
    decoded_file_path = unquote(file_path) if file_path else ""
    decoded_folder_path = unquote(folder_path) if folder_path else ""
    
    # Validate required fields
    if not decoded_collection_name or not decoded_collection_name.strip():
        raise ValidationError("MISSING_COLLECTION_NAME", "Collection name is required")
        
    if not decoded_file_path or not decoded_file_path.strip():
        raise ValidationError("MISSING_FILE_PATH", "File path is required")
    
    # Normalize names
    decoded_collection_name = decoded_collection_name.strip()
    decoded_file_path = decoded_file_path.strip()
    
    # Execute file deletion (will raise if not found)
    result = await collection_service.delete_file(
        decoded_collection_name, decoded_file_path, decoded_folder_path
    )
    
    # Return consistent format (service already returns proper format)
    return result


async def list_files_use_case(
    collection_service,
    collection_name: str
) -> List[FileInfo]:
    """
    Shared file listing logic for API and MCP protocols.
    
    Args:
        collection_service: Collection service instance
        collection_name: Name of the collection
        
    Returns:
        List of FileInfo objects with consistent format
        
    Raises:
        ValidationError: When input parameters are invalid
        Exception: When collection doesn't exist or service errors occur
    """
    
    # Input validation (test-driven)
    if not isinstance(collection_name, str):
        raise ValidationError("INVALID_COLLECTION_NAME_TYPE", "Collection name must be a string")
    
    # URL decode collection name (handling spaces and special characters)
    decoded_collection_name = unquote(collection_name) if collection_name else ""
    
    # Validate required fields
    if not decoded_collection_name or not decoded_collection_name.strip():
        raise ValidationError("MISSING_COLLECTION_NAME", "Collection name is required")
    
    # Normalize name
    decoded_collection_name = decoded_collection_name.strip()
    
    # Execute file listing (will raise if collection not found)
    files = await collection_service.list_files_in_collection(decoded_collection_name)
    
    # Return consistent format
    return files