"""
Service interfaces for unified server architecture.

These abstract interfaces define the contracts for all business logic services.
They are protocol-agnostic and focus on business functionality rather than
transport or protocol concerns.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel


class CrawlResult(BaseModel):
    """Result from web crawling operations."""
    url: str
    content: str
    metadata: Dict[str, Any] = {}
    error: Optional[str] = None


class DeepCrawlConfig(BaseModel):
    """Configuration for deep crawling operations."""
    domain_url: str
    max_depth: int = 1
    max_pages: int = 10
    crawl_strategy: str = "bfs"
    include_external: bool = False
    url_patterns: Optional[List[str]] = None
    exclude_patterns: Optional[List[str]] = None


class LinkPreview(BaseModel):
    """Preview of available links on a domain."""
    domain: str
    links: List[str]
    external_links: Optional[List[str]] = None
    metadata: Dict[str, Any] = {}


class CollectionInfo(BaseModel):
    """Information about a file collection."""
    name: str
    description: str
    file_count: int
    created_at: str
    updated_at: str
    metadata: Dict[str, Any] = {}


class FileInfo(BaseModel):
    """Information about a file in a collection."""
    name: str = ""
    path: str
    content: str
    size: int = 0
    metadata: Dict[str, Any] = {}
    created_at: str
    updated_at: str


class VectorSyncStatus(BaseModel):
    """Status of vector synchronization for a collection."""
    collection_name: str
    is_enabled: bool
    last_sync: Optional[str] = None
    file_count: int = 0
    vector_count: int = 0
    sync_status: str = "idle"  # idle, syncing, error
    error_message: Optional[str] = None


class VectorSearchResult(BaseModel):
    """Result from vector search operations."""
    content: str
    metadata: Dict[str, Any]
    score: float
    collection_name: str
    file_path: Optional[str] = None


class IWebCrawlingService(ABC):
    """
    Interface for web crawling operations.
    
    Handles single page extraction, deep crawling, and link preview functionality.
    All methods are protocol-agnostic and return structured data.
    """
    
    @abstractmethod
    async def extract_content(self, url: str, **kwargs) -> CrawlResult:
        """
        Extract content from a single web page.
        
        Args:
            url: URL to extract content from
            **kwargs: Additional extraction parameters
            
        Returns:
            CrawlResult with extracted content and metadata
        """
        pass
    
    @abstractmethod
    async def deep_crawl(self, config: DeepCrawlConfig) -> List[CrawlResult]:
        """
        Perform deep crawling of a domain.
        
        Args:
            config: Deep crawl configuration
            
        Returns:
            List of CrawlResult objects for all crawled pages
        """
        pass
    
    @abstractmethod
    async def preview_links(self, domain_url: str, include_external: bool = False) -> LinkPreview:
        """
        Preview available links on a domain.
        
        Args:
            domain_url: Domain to preview links for
            include_external: Whether to include external links
            
        Returns:
            LinkPreview with available links
        """
        pass


class ICollectionService(ABC):
    """
    Interface for file collection management.
    
    Handles CRUD operations for collections and files within collections.
    All operations are protocol-agnostic and work with structured data.
    """
    
    @abstractmethod
    async def list_collections(self) -> List[CollectionInfo]:
        """
        List all available collections.
        
        Returns:
            List of CollectionInfo objects
        """
        pass
    
    @abstractmethod
    async def create_collection(self, name: str, description: str = "") -> CollectionInfo:
        """
        Create a new collection.
        
        Args:
            name: Collection name
            description: Optional description
            
        Returns:
            CollectionInfo for the created collection
        """
        pass
    
    @abstractmethod
    async def get_collection(self, name: str) -> CollectionInfo:
        """
        Get information about a specific collection.
        
        Args:
            name: Collection name
            
        Returns:
            CollectionInfo for the collection
        """
        pass
    
    @abstractmethod
    async def delete_collection(self, name: str) -> Dict[str, Any]:
        """
        Delete a collection and all its files.
        
        Args:
            name: Collection name
            
        Returns:
            Status information about the deletion
        """
        pass
    
    @abstractmethod
    async def list_files(self, collection_name: str, folder_path: str = "") -> List[str]:
        """
        List files in a collection.
        
        Args:
            collection_name: Name of the collection
            folder_path: Optional subfolder path
            
        Returns:
            List of file paths
        """
        pass
    
    @abstractmethod
    async def save_file(self, collection_name: str, file_path: str, content: str, folder_path: str = "") -> FileInfo:
        """
        Save content to a file in a collection.
        
        Args:
            collection_name: Name of the collection
            file_path: Path to the file
            content: Content to save
            folder_path: Optional subfolder path
            
        Returns:
            FileInfo for the saved file
        """
        pass
    
    @abstractmethod
    async def get_file(self, collection_name: str, file_path: str, folder_path: str = "") -> FileInfo:
        """
        Get content of a file from a collection.
        
        Args:
            collection_name: Name of the collection
            file_path: Path to the file
            folder_path: Optional subfolder path
            
        Returns:
            FileInfo with file content and metadata
        """
        pass
    
    @abstractmethod
    async def update_file(self, collection_name: str, file_path: str, content: str, folder_path: str = "") -> FileInfo:
        """
        Update content of a file in a collection.
        
        Args:
            collection_name: Name of the collection
            file_path: Path to the file
            content: New content
            folder_path: Optional subfolder path
            
        Returns:
            FileInfo for the updated file
        """
        pass
    
    @abstractmethod
    async def delete_file(self, collection_name: str, file_path: str, folder_path: str = "") -> Dict[str, Any]:
        """
        Delete a file from a collection.
        
        Args:
            collection_name: Name of the collection
            file_path: Path to the file
            folder_path: Optional subfolder path
            
        Returns:
            Status information about the deletion
        """
        pass


class IVectorSyncService(ABC):
    """
    Interface for vector synchronization operations.
    
    Handles vector database operations, collection synchronization,
    and semantic search functionality. Optional service that only
    operates when vector dependencies are available.
    """
    
    @abstractmethod
    async def sync_collection(self, collection_name: str, config: Optional[Dict[str, Any]] = None) -> VectorSyncStatus:
        """
        Synchronize a collection with the vector database.
        
        Args:
            collection_name: Name of the collection to sync
            config: Optional sync configuration
            
        Returns:
            VectorSyncStatus with sync results
        """
        pass
    
    @abstractmethod
    async def get_sync_status(self, collection_name: str) -> VectorSyncStatus:
        """
        Get synchronization status for a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            VectorSyncStatus with current status
        """
        pass
    
    @abstractmethod
    async def list_sync_statuses(self) -> List[VectorSyncStatus]:
        """
        List synchronization statuses for all collections.
        
        Returns:
            List of VectorSyncStatus objects
        """
        pass
    
    @abstractmethod
    async def enable_sync(self, collection_name: str) -> VectorSyncStatus:
        """
        Enable vector synchronization for a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            VectorSyncStatus after enabling sync
        """
        pass
    
    @abstractmethod
    async def disable_sync(self, collection_name: str) -> VectorSyncStatus:
        """
        Disable vector synchronization for a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            VectorSyncStatus after disabling sync
        """
        pass
    
    @abstractmethod
    async def delete_vectors(self, collection_name: str) -> Dict[str, Any]:
        """
        Delete all vectors for a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Status information about the deletion
        """
        pass
    
    @abstractmethod
    async def search_vectors(self, query: str, collection_name: Optional[str] = None, limit: int = 10) -> List[VectorSearchResult]:
        """
        Search vectors using semantic similarity.
        
        Args:
            query: Search query text
            collection_name: Optional collection to search in
            limit: Maximum number of results
            
        Returns:
            List of VectorSearchResult objects
        """
        pass