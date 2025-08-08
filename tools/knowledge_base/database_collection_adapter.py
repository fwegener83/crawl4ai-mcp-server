"""
Database Collection Adapter - Provides compatibility layer for IntelligentSyncManager.

This adapter makes DatabaseCollectionManager compatible with the existing 
IntelligentSyncManager interface, enabling database-only file storage.
"""

from typing import Dict, Any, List, Optional
import logging
from .persistent_sync_manager import DatabaseCollectionManager

logger = logging.getLogger(__name__)


class DatabaseCollectionAdapter:
    """Adapter to make DatabaseCollectionManager compatible with existing sync manager interface."""
    
    def __init__(self, db_path: str = "collections.db"):
        """Initialize the database collection adapter."""
        self.db_manager = DatabaseCollectionManager(db_path)
        logger.info(f"DatabaseCollectionAdapter initialized with database: {db_path}")
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get collection info compatible with filesystem API."""
        try:
            if not self.db_manager.collection_exists(collection_name):
                return {"success": False, "error": f"Collection '{collection_name}' not found"}
            
            # Get basic collection info
            collections = self.db_manager.list_collections()
            collection_data = None
            for col in collections:
                if col["name"] == collection_name:
                    collection_data = col
                    break
            
            if not collection_data:
                return {"success": False, "error": f"Collection '{collection_name}' not found"}
            
            # Get file count from database
            files = self.db_manager.list_collection_files(collection_name)
            
            return {
                "success": True,
                "collection": {
                    "name": collection_data["name"],
                    "description": collection_data["description"],
                    "file_count": len(files),
                    "created_at": collection_data["created_at"],
                    "updated_at": collection_data["updated_at"]
                }
            }
        except Exception as e:
            logger.error(f"Error getting collection info for {collection_name}: {e}")
            return {"success": False, "error": str(e)}
    
    def list_files_in_collection(self, collection_name: str) -> Dict[str, Any]:
        """List files in collection - database version."""
        try:
            files = self.db_manager.list_collection_files(collection_name)
            
            # Transform to expected format
            transformed_files = []
            for file_data in files:
                transformed_files.append({
                    "name": file_data["filename"],
                    "path": file_data["path"],
                    "folder": file_data["folder"],
                    "size": file_data["size"],
                    "created_at": file_data["created_at"],
                    "updated_at": file_data["updated_at"],
                    "file_id": file_data["file_id"],  # Database-specific
                    "content_hash": file_data["content_hash"]  # Database-specific
                })
            
            return {
                "success": True,
                "files": transformed_files,
                "total": len(transformed_files)
            }
        except Exception as e:
            logger.error(f"Error listing files in collection {collection_name}: {e}")
            return {"success": False, "error": str(e)}
    
    def read_file(self, collection_name: str, filename: str, folder: str = "") -> Dict[str, Any]:
        """Read file content from database."""
        try:
            # Get file by path
            file_data = self.db_manager.get_file_by_path(collection_name, filename, folder)
            
            if not file_data.get("success"):
                return {"success": False, "error": f"File '{filename}' not found"}
            
            return {
                "success": True,
                "content": file_data["content"],
                "path": file_data["path"],
                "file_id": file_data["file_id"],
                "content_hash": file_data["content_hash"],
                "size": file_data["size"],
                "created_at": file_data["created_at"],
                "updated_at": file_data["updated_at"]
            }
        except Exception as e:
            logger.error(f"Error reading file {filename} from collection {collection_name}: {e}")
            return {"success": False, "error": str(e)}
    
    def create_collection(self, name: str, description: str = "") -> Dict[str, Any]:
        """Create collection in database."""
        return self.db_manager.create_collection(name, description)
    
    def save_file(self, collection_name: str, filename: str, content: str, folder: str = "") -> Dict[str, Any]:
        """Save file to database."""
        return self.db_manager.create_file(collection_name, filename, content, folder)
    
    def list_collections(self) -> List[Dict[str, Any]]:
        """List all collections from database."""
        return self.db_manager.list_collections()
    
    # Compatibility methods for existing interface
    @property
    def collection_manager(self):
        """Return self for compatibility with existing code."""
        return self