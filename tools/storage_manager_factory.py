"""
Storage Manager Factory for Configurable Collection Storage.

Provides factory pattern for creating appropriate collection managers based on 
configuration. Supports SQLite-only and Filesystem+Metadata storage modes.
"""

from typing import Dict, Any, Protocol
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class CollectionManager(Protocol):
    """Protocol defining the interface that all collection managers must implement."""
    
    async def create_collection(self, name: str, description: str = "") -> Dict[str, Any]:
        """Create a new collection."""
        ...
    
    async def save_file(self, collection_name: str, filename: str, content: str, folder: str = "") -> Dict[str, Any]:
        """Save content to a file within a collection."""
        ...
    
    async def read_file(self, collection_name: str, filename: str, folder: str = "") -> Dict[str, Any]:
        """Read content from a file within a collection."""
        ...
    
    async def list_collections(self) -> Dict[str, Any]:
        """List all available collections."""
        ...
    
    async def list_files_in_collection(self, collection_name: str) -> Dict[str, Any]:
        """List all files in a collection."""
        ...
    
    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get detailed information about a collection."""
        ...
    
    async def delete_collection(self, collection_name: str) -> Dict[str, Any]:
        """Delete a collection and all its files."""
        ...
    
    async def delete_file(self, collection_name: str, filename: str, folder: str = "") -> Dict[str, Any]:
        """Delete a file from a collection."""
        ...


class CollectionStorageFactory:
    """Factory for creating appropriate collection managers based on configuration."""
    
    @staticmethod
    def create_manager(config: Dict[str, Any]) -> CollectionManager:
        """
        Create collection manager based on storage configuration.
        
        Args:
            config: Storage configuration dictionary containing:
                - storage_mode: "sqlite" or "filesystem"
                - Additional mode-specific configuration
        
        Returns:
            CollectionManager: Configured collection manager instance
            
        Raises:
            ValueError: If storage_mode is not supported
            ImportError: If required dependencies are missing
        """
        storage_mode = config.get("storage_mode", "sqlite").lower()
        logger.info(f"Creating collection manager for storage mode: {storage_mode}")
        
        if storage_mode == "sqlite":
            return CollectionStorageFactory._create_sqlite_manager(config)
            
        elif storage_mode == "filesystem":
            return CollectionStorageFactory._create_filesystem_manager(config)
            
        else:
            available_modes = ["sqlite", "filesystem"]
            raise ValueError(f"Unsupported storage mode '{storage_mode}'. Available: {available_modes}")
    
    @staticmethod
    def _create_sqlite_manager(config: Dict[str, Any]) -> CollectionManager:
        """
        Create SQLite-only collection manager (Mode 1 - current behavior).
        
        Args:
            config: Configuration containing database_path
            
        Returns:
            DatabaseCollectionAdapter: SQLite-based collection manager
        """
        try:
            from tools.knowledge_base.database_collection_adapter import DatabaseCollectionAdapter
            
            database_path = config.get("database_path")
            if not database_path:
                raise ValueError("SQLite mode requires 'database_path' in configuration")
            
            logger.info(f"Initializing SQLite collection manager: {database_path}")
            return DatabaseCollectionAdapter(str(database_path))
            
        except ImportError as e:
            raise ImportError(f"SQLite collection manager dependencies missing: {e}")
    
    @staticmethod 
    def _create_filesystem_manager(config: Dict[str, Any]) -> CollectionManager:
        """
        Create Filesystem+Metadata collection manager (Mode 2 - new implementation).
        
        Args:
            config: Configuration containing filesystem_path and metadata_db_path
            
        Returns:
            FilesystemCollectionManager: Filesystem-based collection manager
        """
        try:
            from tools.filesystem_collection_manager import FilesystemCollectionManager
            
            filesystem_path = config.get("filesystem_path")
            metadata_db_path = config.get("metadata_db_path")
            
            if not filesystem_path:
                raise ValueError("Filesystem mode requires 'filesystem_path' in configuration")
            if not metadata_db_path:
                raise ValueError("Filesystem mode requires 'metadata_db_path' in configuration")
            
            # Ensure paths exist
            fs_path = Path(filesystem_path)
            fs_path.mkdir(parents=True, exist_ok=True)
            
            metadata_path = Path(metadata_db_path)
            metadata_path.parent.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Initializing Filesystem collection manager:")
            logger.info(f"  Content storage: {fs_path}")
            logger.info(f"  Metadata database: {metadata_path}")
            
            return FilesystemCollectionManager(
                filesystem_base=fs_path,
                metadata_db_path=metadata_path,
                auto_reconcile=config.get("auto_reconcile", True)
            )
            
        except ImportError as e:
            raise ImportError(f"Filesystem collection manager dependencies missing: {e}")
    
    @staticmethod
    def get_supported_modes() -> list[str]:
        """
        Get list of supported storage modes.
        
        Returns:
            List of supported mode names
        """
        return ["sqlite", "filesystem"]
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate storage configuration.
        
        Args:
            config: Storage configuration to validate
            
        Returns:
            Validation result with success status and any error details
        """
        try:
            storage_mode = config.get("storage_mode", "sqlite").lower()
            
            if storage_mode not in CollectionStorageFactory.get_supported_modes():
                return {
                    "success": False,
                    "error": f"Unsupported storage mode: {storage_mode}",
                    "supported_modes": CollectionStorageFactory.get_supported_modes()
                }
            
            if storage_mode == "sqlite":
                if not config.get("database_path"):
                    return {
                        "success": False,
                        "error": "SQLite mode requires 'database_path'"
                    }
                    
            elif storage_mode == "filesystem":
                required_keys = ["filesystem_path", "metadata_db_path"]
                missing_keys = [key for key in required_keys if not config.get(key)]
                
                if missing_keys:
                    return {
                        "success": False,
                        "error": f"Filesystem mode requires: {', '.join(missing_keys)}"
                    }
                
                # Validate paths
                try:
                    fs_path = Path(config["filesystem_path"]).expanduser().resolve()
                    metadata_path = Path(config["metadata_db_path"]).expanduser().resolve()
                    
                    # Test filesystem access
                    fs_path.mkdir(parents=True, exist_ok=True)
                    metadata_path.parent.mkdir(parents=True, exist_ok=True)
                    
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Path validation failed: {e}"
                    }
            
            return {
                "success": True,
                "storage_mode": storage_mode,
                "message": f"Configuration valid for {storage_mode} mode"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Configuration validation error: {e}"
            }