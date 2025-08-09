"""
Crawl integration use-case functions.

Contains protocol-agnostic business logic for crawling content and saving to collections,
integrating web crawling and file management functionality.
"""

from typing import Dict, Any
from urllib.parse import urlparse
from services.interfaces import FileInfo


class ValidationError(Exception):
    """Exception raised when input validation fails."""
    
    def __init__(self, code: str, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


async def crawl_single_page_to_collection_use_case(
    web_service,
    collection_service,
    collection_name: str,
    url: str,
    folder: str = ""
) -> FileInfo:
    """
    Shared crawl-and-save logic for API and MCP protocols.
    
    Extracts content from a URL and saves it to a collection with auto-generated filename.
    
    Args:
        web_service: Web service instance
        collection_service: Collection service instance
        collection_name: Name of the collection to save to
        url: URL to crawl and extract content from
        folder: Optional subfolder path
        
    Returns:
        FileInfo object for the saved file
        
    Raises:
        ValidationError: When input parameters are invalid
        Exception: When crawling or saving errors occur
    """
    
    # Input validation (test-driven)
    if not isinstance(collection_name, str):
        raise ValidationError("INVALID_COLLECTION_NAME_TYPE", "Collection name must be a string")
    
    if not collection_name or not collection_name.strip():
        raise ValidationError("MISSING_COLLECTION_NAME", "Collection name is required")
    
    if not isinstance(url, str):
        raise ValidationError("INVALID_URL_TYPE", "URL must be a string")
    
    if not url or not url.strip():
        raise ValidationError("MISSING_URL", "URL is required")
        
    if not isinstance(folder, str):
        raise ValidationError("INVALID_FOLDER_TYPE", "Folder must be a string")
    
    # Normalize inputs
    collection_name = collection_name.strip()
    url = url.strip()
    
    # Extract content from URL using web service
    content_result = await web_service.extract_content(url)
    
    if content_result.error:
        raise ValidationError("CRAWL_FAILED", f"Failed to crawl URL: {content_result.error}")
    
    # Generate filename from URL
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace("www.", "")
        path_parts = [p for p in parsed_url.path.split("/") if p]
        
        if path_parts:
            # Use last path component as base filename
            base_filename = path_parts[-1]
            # Remove file extension if present to add .md
            if '.' in base_filename:
                base_filename = base_filename.rsplit('.', 1)[0]
        else:
            # Use domain as filename if no path
            base_filename = domain.replace(".", "_")
        
        # Clean filename and ensure it has .md extension
        filename = f"{base_filename}.md"
        # Sanitize filename (remove invalid characters)
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, "_")
            
    except Exception as e:
        # Fallback to simple filename if URL parsing fails
        filename = "crawled_content.md"
    
    # Prepare content with metadata
    content_with_metadata = f"""# {content_result.metadata.get('title', 'Crawled Content')}

**Source URL:** {url}
**Crawled at:** {content_result.metadata.get('crawl_time', 'Unknown')}

---

{content_result.content}
"""
    
    # Save to collection using file management service
    file_info = await collection_service.save_file(
        collection_name, filename, content_with_metadata, folder
    )
    
    # Return file info with additional crawl metadata
    return file_info