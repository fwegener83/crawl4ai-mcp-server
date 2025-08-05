"""
Collection service implementation.

Implements ICollectionService interface with actual collection management logic
extracted from existing collection manager. This service is protocol-agnostic
and focuses purely on collection business logic.
"""
import logging
from typing import Dict, Any, List
from pathlib import Path
from .interfaces import ICollectionService, CollectionInfo, FileInfo

# Import existing collection manager
from tools.sqlite_collection_manager import create_collection_manager

logger = logging.getLogger(__name__)


class CollectionService(ICollectionService):
    """
    Implementation of collection service.
    
    Delegates to existing collection manager while providing a clean,
    protocol-agnostic interface for business logic.
    """
    
    def __init__(self, base_dir: Path = None):
        """
        Initialize the collection service.
        
        Args:
            base_dir: Base directory for collections (optional)
        """
        logger.info("Initializing CollectionService")
        self.collection_manager = create_collection_manager(base_dir)
    
    async def list_collections(self) -> List[CollectionInfo]:
        """
        List all available collections.
        
        Returns:
            List of CollectionInfo objects
        """
        try:
            logger.info("Listing all collections")
            
            # Use existing collection manager
            result = await self.collection_manager.list_collections()
            
            # Parse JSON result if it's a string
            if isinstance(result, str):
                import json
                result = json.loads(result)
            
            collections = []
            if result.get("success", False):
                collection_data = result.get("collections", [])
                for col_data in collection_data:
                    collection_info = CollectionInfo(
                        name=col_data.get("name", ""),
                        description=col_data.get("description", ""),
                        file_count=col_data.get("file_count", 0),
                        created_at=col_data.get("created_at", ""),
                        updated_at=col_data.get("updated_at", ""),
                        metadata=col_data.get("metadata", {})
                    )
                    collections.append(collection_info)
            
            logger.info(f"Found {len(collections)} collections")
            return collections
            
        except Exception as e:
            logger.error(f"Error listing collections: {str(e)}")
            return []
    
    async def create_collection(self, name: str, description: str = "") -> CollectionInfo:
        """
        Create a new collection.
        
        Args:
            name: Collection name
            description: Optional description
            
        Returns:
            CollectionInfo for the created collection
        """
        try:
            logger.info(f"Creating collection: {name}")
            
            # Use existing collection manager
            result = await self.collection_manager.create_collection(name, description)
            
            # Parse JSON result if it's a string
            if isinstance(result, str):
                import json
                result = json.loads(result)
            
            if result.get("success", False):
                col_data = result.get("collection", {})
                return CollectionInfo(
                    name=col_data.get("name", name),
                    description=col_data.get("description", description),
                    file_count=col_data.get("file_count", 0),
                    created_at=col_data.get("created_at", ""),
                    updated_at=col_data.get("updated_at", ""),
                    metadata=col_data.get("metadata", {})
                )
            else:
                raise Exception(result.get("error", "Failed to create collection"))
                
        except Exception as e:
            logger.error(f"Error creating collection {name}: {str(e)}")
            raise
    
    async def get_collection(self, name: str) -> CollectionInfo:
        """
        Get information about a specific collection.
        
        Args:
            name: Collection name
            
        Returns:
            CollectionInfo for the collection
        """
        try:
            logger.info(f"Getting collection info: {name}")
            
            # Use existing collection manager
            result = await self.collection_manager.get_collection_info(name)
            
            # Parse JSON result if it's a string
            if isinstance(result, str):
                import json
                result = json.loads(result)
            
            if result.get("success", False):
                col_data = result.get("collection", {})
                return CollectionInfo(
                    name=col_data.get("name", name),
                    description=col_data.get("description", ""),
                    file_count=col_data.get("file_count", 0),
                    created_at=col_data.get("created_at", ""),
                    updated_at=col_data.get("updated_at", ""),
                    metadata=col_data.get("metadata", {})
                )
            else:
                raise Exception(result.get("error", f"Collection {name} not found"))
                
        except Exception as e:
            logger.error(f"Error getting collection {name}: {str(e)}")
            raise
    
    async def delete_collection(self, name: str) -> Dict[str, Any]:
        """
        Delete a collection and all its files.
        
        Args:
            name: Collection name
            
        Returns:
            Status information about the deletion
        """
        try:
            logger.info(f"Deleting collection: {name}")
            
            # Use existing collection manager
            result = await self.collection_manager.delete_collection(name)
            
            # Parse JSON result if it's a string
            if isinstance(result, str):
                import json
                result = json.loads(result)
            
            if result.get("success", False):
                return {
                    "success": True,
                    "message": f"Collection {name} deleted successfully",
                    "deleted_files": result.get("deleted_files", 0)
                }
            else:
                raise Exception(result.get("error", "Failed to delete collection"))
                
        except Exception as e:
            logger.error(f"Error deleting collection {name}: {str(e)}")
            raise
    
    async def list_files(self, collection_name: str, folder_path: str = "") -> List[str]:
        """
        List files in a collection.
        
        Args:
            collection_name: Name of the collection
            folder_path: Optional subfolder path
            
        Returns:
            List of file paths
        """
        try:
            logger.info(f"Listing files in collection: {collection_name}, folder: {folder_path}")
            
            # Use existing collection manager
            result = await self.collection_manager.list_files(collection_name, folder_path)
            
            # Parse JSON result if it's a string
            if isinstance(result, str):
                import json
                result = json.loads(result)
            
            if result.get("success", False):
                return result.get("files", [])
            else:
                raise Exception(result.get("error", "Failed to list files"))
                
        except Exception as e:
            logger.error(f"Error listing files in {collection_name}: {str(e)}")
            raise
    
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
        try:
            logger.info(f"Saving file {file_path} in collection {collection_name}")
            
            # Use existing collection manager
            result = await self.collection_manager.save_to_collection(
                collection_name, file_path, content, folder_path
            )
            
            # Parse JSON result if it's a string
            if isinstance(result, str):
                import json
                result = json.loads(result)
            
            if result.get("success", False):
                file_data = result.get("file", {})
                return FileInfo(
                    path=file_data.get("path", file_path),
                    content=content,
                    metadata=file_data.get("metadata", {}),
                    created_at=file_data.get("created_at", ""),
                    updated_at=file_data.get("updated_at", "")
                )
            else:
                raise Exception(result.get("error", "Failed to save file"))
                
        except Exception as e:
            logger.error(f"Error saving file {file_path} in {collection_name}: {str(e)}")
            raise
    
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
        try:
            logger.info(f"Getting file {file_path} from collection {collection_name}")
            
            # Use existing collection manager
            result = await self.collection_manager.read_from_collection(
                collection_name, file_path, folder_path
            )
            
            # Parse JSON result if it's a string
            if isinstance(result, str):
                import json
                result = json.loads(result)
            
            if result.get("success", False):
                file_data = result.get("file", {})
                return FileInfo(
                    path=file_data.get("path", file_path),
                    content=file_data.get("content", ""),
                    metadata=file_data.get("metadata", {}),
                    created_at=file_data.get("created_at", ""),
                    updated_at=file_data.get("updated_at", "")
                )
            else:
                raise Exception(result.get("error", "File not found"))
                
        except Exception as e:
            logger.error(f"Error getting file {file_path} from {collection_name}: {str(e)}")
            raise
    
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
        try:
            logger.info(f"Updating file {file_path} in collection {collection_name}")
            
            # For now, this is the same as save_file in the existing implementation
            return await self.save_file(collection_name, file_path, content, folder_path)
                
        except Exception as e:
            logger.error(f"Error updating file {file_path} in {collection_name}: {str(e)}")
            raise
    
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
        try:
            logger.info(f"Deleting file {file_path} from collection {collection_name}")
            
            # Use existing collection manager
            # Note: The existing manager might not have a direct delete_file method
            # For now, we'll raise NotImplementedError until we can implement it
            raise NotImplementedError("File deletion not yet implemented in collection manager")
                
        except NotImplementedError:
            raise
        except Exception as e:
            logger.error(f"Error deleting file {file_path} from {collection_name}: {str(e)}")
            raise