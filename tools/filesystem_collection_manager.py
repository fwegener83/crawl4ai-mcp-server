"""
FilesystemCollectionManager - Collection manager with filesystem content storage + SQLite metadata.

Implements Mode 2 of the configurable storage architecture:
- Content stored in filesystem for transparency and tool integration
- Metadata and vector sync status stored in SQLite for performance
- Automatic reconciliation of external filesystem changes
"""

import asyncio
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import logging

from .filesystem_metadata_store import FilesystemMetadataStore
from .filesystem_metadata_reconciler import FilesystemMetadataReconciler

logger = logging.getLogger(__name__)


class FilesystemCollectionManager:
    """Collection manager with filesystem content storage + SQLite metadata."""
    
    # Security: Allowed file extensions
    ALLOWED_EXTENSIONS = {'.md', '.txt', '.json', '.yaml', '.yml', '.csv'}
    
    def __init__(self, filesystem_base: Path, metadata_db_path: Path, auto_reconcile: bool = True):
        """
        Initialize filesystem collection manager.
        
        Args:
            filesystem_base: Base directory for filesystem content storage
            metadata_db_path: Path to SQLite database for metadata
            auto_reconcile: Whether to automatically reconcile on collection access
        """
        self.fs_base = Path(filesystem_base)
        self.metadata_db_path = Path(metadata_db_path) 
        self.auto_reconcile = auto_reconcile
        
        # Ensure base directory exists
        self.fs_base.mkdir(parents=True, exist_ok=True)
        
        # Initialize metadata store and reconciler
        self.metadata_store = FilesystemMetadataStore(metadata_db_path)
        self.reconciler = FilesystemMetadataReconciler(self.fs_base, self.metadata_store)
        
        logger.info(f"FilesystemCollectionManager initialized:")
        logger.info(f"  Filesystem base: {self.fs_base}")
        logger.info(f"  Metadata database: {metadata_db_path}")
        logger.info(f"  Auto-reconcile: {auto_reconcile}")
    
    async def create_collection(self, name: str, description: str = "") -> Dict[str, Any]:
        """
        Create collection: filesystem directory + metadata entry.
        
        Args:
            name: Collection name
            description: Collection description
            
        Returns:
            Result dictionary with success status and collection info
        """
        try:
            # Sanitize collection name for security
            sanitized_name = self._sanitize_collection_name(name)
            
            # Create filesystem directory
            collection_path = self.fs_base / sanitized_name
            collection_path.mkdir(parents=True, exist_ok=True)
            
            # Create metadata entry in SQLite
            result = await self.metadata_store.create_collection(sanitized_name, description)
            
            if result.get("success", False):
                logger.info(f"Collection '{sanitized_name}' created successfully")
                return {
                    "success": True,
                    "name": sanitized_name,
                    "path": str(collection_path),
                    "description": description,
                    "message": f"Collection '{sanitized_name}' created successfully"
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Failed to create collection '{name}': {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create collection '{name}'"
            }
    
    async def save_file(self, collection_name: str, filename: str, content: str, folder: str = "") -> Dict[str, Any]:
        """
        Save file to filesystem + update metadata.
        
        Args:
            collection_name: Name of the collection
            filename: Name of the file
            content: File content
            folder: Optional subfolder path
            
        Returns:
            Result dictionary with success status and file info
        """
        try:
            # Validate file extension
            if not self._validate_file_extension(filename):
                return {
                    "success": False,
                    "error": f"File extension not allowed. Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}"
                }
            
            # Sanitize inputs
            sanitized_collection = self._sanitize_collection_name(collection_name)
            safe_folder = self._sanitize_folder_path(folder)
            
            # Check if collection exists
            collection_exists = await self.metadata_store.collection_exists(sanitized_collection)
            if not collection_exists:
                return {
                    "success": False,
                    "error": f"Collection '{collection_name}' does not exist"
                }
            
            # Write content to filesystem
            if safe_folder:
                file_path = self.fs_base / sanitized_collection / safe_folder / filename
            else:
                file_path = self.fs_base / sanitized_collection / filename
            
            # Create directory structure if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file content
            file_path.write_text(content, encoding='utf-8')
            
            # Update metadata in SQLite
            content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            relative_path = str(Path(safe_folder) / filename) if safe_folder else filename
            
            metadata_result = await self.metadata_store.update_file_metadata(
                collection_name=sanitized_collection,
                file_path=relative_path,
                content_hash=content_hash,
                file_size=len(content.encode('utf-8')),
                vector_sync_status="not_synced"  # User must manually sync
            )
            
            if metadata_result.get("success", False):
                logger.info(f"File saved: {file_path}")
                return {
                    "success": True,
                    "path": str(file_path),
                    "content_hash": content_hash,
                    "message": f"File '{filename}' saved successfully"
                }
            else:
                # Clean up filesystem file if metadata update failed
                try:
                    file_path.unlink(missing_ok=True)
                except Exception:
                    pass
                return metadata_result
                
        except Exception as e:
            logger.error(f"Failed to save file '{filename}' in collection '{collection_name}': {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to save file '{filename}'"
            }
    
    async def read_file(self, collection_name: str, filename: str, folder: str = "") -> Dict[str, Any]:
        """
        Read file content from filesystem.
        
        Args:
            collection_name: Name of the collection
            filename: Name of the file
            folder: Optional subfolder path
            
        Returns:
            Result dictionary with success status and file content
        """
        try:
            # Sanitize inputs
            sanitized_collection = self._sanitize_collection_name(collection_name)
            safe_folder = self._sanitize_folder_path(folder)
            
            # Build file path
            if safe_folder:
                file_path = self.fs_base / sanitized_collection / safe_folder / filename
            else:
                file_path = self.fs_base / sanitized_collection / filename
            
            # Check if file exists
            if not file_path.exists():
                return {
                    "success": False,
                    "error": f"File '{filename}' not found in collection '{collection_name}'"
                }
            
            # Read file content
            content = file_path.read_text(encoding='utf-8')
            
            # Get file metadata from SQLite
            relative_path = str(Path(safe_folder) / filename) if safe_folder else filename
            metadata = await self.metadata_store.get_file_metadata(sanitized_collection, relative_path)
            
            return {
                "success": True,
                "content": content,
                "path": str(file_path),
                "metadata": metadata.get("metadata", {}) if metadata.get("success") else {}
            }
            
        except Exception as e:
            logger.error(f"Failed to read file '{filename}' from collection '{collection_name}': {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to read file '{filename}'"
            }
    
    async def list_collections(self) -> Dict[str, Any]:
        """
        List all collections with metadata from SQLite, with filesystem reconciliation.
        
        Returns:
            Result dictionary with success status and collections list
        """
        try:
            # Auto-reconcile collections if enabled
            if self.auto_reconcile:
                await self._reconcile_collections()
            
            result = await self.metadata_store.list_collections()
            
            if result.get("success", False):
                collections = []
                for col_data in result.get("collections", []):
                    # Add filesystem path for compatibility
                    col_data["path"] = str(self.fs_base / col_data["name"])
                    collections.append(col_data)
                
                return {
                    "success": True,
                    "collections": collections,
                    "total": len(collections)
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to list collections"
            }
    
    async def list_files_in_collection(self, collection_name: str) -> Dict[str, Any]:
        """
        List files with metadata from SQLite, with optional reconciliation.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Result dictionary with success status and files list
        """
        try:
            sanitized_collection = self._sanitize_collection_name(collection_name)
            
            # Auto-reconcile if enabled
            if self.auto_reconcile:
                reconciliation = await self.reconciler.reconcile_collection(sanitized_collection)
                logger.debug(f"Reconciliation for '{sanitized_collection}': {reconciliation}")
            
            # Get file list from metadata store
            result = await self.metadata_store.get_collection_files(sanitized_collection)
            
            if result.get("success", False):
                files = []
                folders = set()
                
                for file_data in result.get("files", []):
                    # Build file info with filesystem compatibility
                    file_info = {
                        "name": Path(file_data["file_path"]).name,
                        "path": file_data["file_path"],
                        "type": "file", 
                        "size": file_data.get("file_size", 0),
                        "created_at": file_data.get("created_at", ""),
                        "modified_at": file_data.get("modified_at", ""),
                        "extension": Path(file_data["file_path"]).suffix.lower(),
                        "folder": str(Path(file_data["file_path"]).parent) if Path(file_data["file_path"]).parent.name != "." else "",
                        "vector_sync_status": file_data.get("vector_sync_status", "not_synced")
                    }
                    files.append(file_info)
                    
                    # Track folders
                    folder_path = Path(file_data["file_path"]).parent
                    if folder_path.name != ".":
                        folders.add(str(folder_path))
                
                # Build folder list
                folder_list = []
                for folder_path in sorted(folders):
                    folder_info = {
                        "name": Path(folder_path).name,
                        "path": folder_path,
                        "type": "folder",
                        "folder": str(Path(folder_path).parent) if Path(folder_path).parent.name != "." else ""
                    }
                    folder_list.append(folder_info)
                
                return {
                    "success": True,
                    "files": files,
                    "folders": folder_list,
                    "total_files": len(files),
                    "total_folders": len(folder_list)
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Failed to list files in collection '{collection_name}': {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to list files in collection '{collection_name}'"
            }
    
    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Result dictionary with success status and collection info
        """
        try:
            sanitized_collection = self._sanitize_collection_name(collection_name)
            
            # Auto-reconcile if enabled
            if self.auto_reconcile:
                await self.reconciler.reconcile_collection(sanitized_collection)
            
            # Get collection info from metadata store
            result = await self.metadata_store.get_collection(sanitized_collection)
            
            if result.get("success", False):
                collection_data = result["collection"]
                
                # Get file listing for additional details
                files_result = await self.list_files_in_collection(sanitized_collection)
                files = files_result.get("files", []) if files_result.get("success") else []
                folders = files_result.get("folders", []) if files_result.get("success") else []
                
                # Calculate total size
                total_size = sum(f.get("size", 0) for f in files)
                
                return {
                    "success": True,
                    "collection": {
                        "name": collection_data["name"],
                        "description": collection_data["description"], 
                        "created_at": collection_data["created_at"],
                        "file_count": len(files),
                        "total_size": total_size,
                        "folders": [f["name"] for f in folders],
                        "files": files,
                        "path": str(self.fs_base / sanitized_collection),
                        "metadata": {
                            "created_at": collection_data["created_at"],
                            "description": collection_data["description"],
                            "last_modified": collection_data.get("updated_at", collection_data["created_at"]),
                            "file_count": len(files),
                            "folder_count": len(folders),
                            "total_size": total_size
                        }
                    }
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Failed to get collection info for '{collection_name}': {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get collection info for '{collection_name}'"
            }
    
    async def delete_collection(self, collection_name: str) -> Dict[str, Any]:
        """
        Delete a collection and all its files from both filesystem and metadata.
        
        Args:
            collection_name: Name of the collection to delete
            
        Returns:
            Result dictionary with success status and deletion info
        """
        try:
            sanitized_collection = self._sanitize_collection_name(collection_name)
            
            # Delete from metadata store first
            metadata_result = await self.metadata_store.delete_collection(sanitized_collection)
            
            # Delete filesystem directory
            collection_path = self.fs_base / sanitized_collection
            if collection_path.exists():
                import shutil
                shutil.rmtree(collection_path)
                logger.info(f"Deleted collection directory: {collection_path}")
            
            if metadata_result.get("success", False):
                return {
                    "success": True,
                    "message": f"Collection '{sanitized_collection}' deleted successfully",
                    "deleted_files": metadata_result.get("deleted_files", 0)
                }
            else:
                return metadata_result
                
        except Exception as e:
            logger.error(f"Failed to delete collection '{collection_name}': {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to delete collection '{collection_name}'"
            }
    
    async def delete_file(self, collection_name: str, filename: str, folder: str = "") -> Dict[str, Any]:
        """
        Delete a file from both filesystem and metadata.
        
        Args:
            collection_name: Name of the collection
            filename: Name of the file
            folder: Optional subfolder path
            
        Returns:
            Result dictionary with success status
        """
        try:
            # Sanitize inputs
            sanitized_collection = self._sanitize_collection_name(collection_name)
            safe_folder = self._sanitize_folder_path(folder)
            
            # Build file path
            if safe_folder:
                file_path = self.fs_base / sanitized_collection / safe_folder / filename
            else:
                file_path = self.fs_base / sanitized_collection / filename
            
            # Delete from metadata store
            relative_path = str(Path(safe_folder) / filename) if safe_folder else filename
            metadata_result = await self.metadata_store.delete_file_metadata(
                sanitized_collection, relative_path
            )
            
            # Delete from filesystem
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted file: {file_path}")
            
            if metadata_result.get("success", False):
                return {
                    "success": True,
                    "message": f"File '{filename}' deleted successfully"
                }
            else:
                return metadata_result
                
        except Exception as e:
            logger.error(f"Failed to delete file '{filename}' from collection '{collection_name}': {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to delete file '{filename}'"
            }
    
    async def _reconcile_collections(self):
        """
        Reconcile collections between filesystem and metadata database.
        
        Discovers new collection directories in filesystem and creates metadata entries.
        """
        try:
            logger.info("Starting collection reconciliation")
            logger.info(f"Filesystem base path: {self.fs_base}")
            
            # Get existing collections from metadata
            metadata_result = await self.metadata_store.list_collections()
            if not metadata_result.get("success", False):
                logger.warning("Could not get existing collections from metadata for reconciliation")
                return
            
            existing_collections = {col["name"] for col in metadata_result.get("collections", [])}
            logger.info(f"Existing collections in metadata: {existing_collections}")
            
            # Scan filesystem for collection directories
            filesystem_collections = set()
            filesystem_raw_names = []
            
            if self.fs_base.exists():
                logger.info(f"Scanning filesystem at: {self.fs_base}")
                for item in self.fs_base.iterdir():
                    filesystem_raw_names.append(item.name)
                    logger.debug(f"Found filesystem item: {item.name} (is_dir: {item.is_dir()})")
                    
                    if item.is_dir() and not item.name.startswith('.'):
                        # Sanitize the name to match our collection naming rules
                        sanitized_name = self._sanitize_collection_name_safe(item.name)
                        logger.debug(f"Raw name: '{item.name}' -> Sanitized: '{sanitized_name}'")
                        if sanitized_name:
                            filesystem_collections.add(sanitized_name)
                            logger.debug(f"Added to filesystem_collections: {sanitized_name}")
            else:
                logger.warning(f"Filesystem base does not exist: {self.fs_base}")
            
            logger.info(f"Raw filesystem names found: {filesystem_raw_names}")
            logger.info(f"Filesystem collections after sanitization: {filesystem_collections}")
            
            # Find collections that exist in filesystem but not in metadata
            missing_collections = filesystem_collections - existing_collections
            logger.info(f"Missing collections (filesystem - metadata): {missing_collections}")
            
            if missing_collections:
                logger.info(f"Found {len(missing_collections)} collections in filesystem not in metadata: {missing_collections}")
                
                for collection_name in missing_collections:
                    try:
                        logger.info(f"Creating metadata entry for: {collection_name}")
                        # Create metadata entry for filesystem collection
                        result = await self.metadata_store.create_collection(
                            collection_name, 
                            f"Auto-discovered from filesystem directory"
                        )
                        if result.get("success", False):
                            logger.info(f"✓ Created metadata for filesystem collection: {collection_name}")
                        else:
                            logger.warning(f"✗ Failed to create metadata for collection {collection_name}: {result.get('error')}")
                    except Exception as e:
                        logger.error(f"Error creating metadata for collection {collection_name}: {e}")
            else:
                logger.info("No missing collections found during reconciliation")
                
        except Exception as e:
            logger.error(f"Collection reconciliation failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    # Utility methods for security and validation
    
    def _sanitize_collection_name(self, name: str) -> str:
        """Sanitize collection name for security."""
        if not name or not name.strip():
            raise ValueError("Collection name cannot be empty")
        
        sanitized = name.strip()
        
        # Remove dangerous characters
        dangerous_chars = {
            '/': '_',
            '\\': '_',
            '..': '__',  # Double dots become double underscore
            ':': '_',
            '*': '_',
            '?': '_',
            '"': '_',
            '<': '_',
            '>': '_',
            '|': '_',
            '\x00': '_'
        }
        for char, replacement in dangerous_chars.items():
            sanitized = sanitized.replace(char, replacement)
        
        # Limit length
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        
        if not sanitized:
            raise ValueError("Collection name becomes empty after sanitization")
        
        return sanitized
    
    def _sanitize_collection_name_safe(self, name: str) -> str:
        """Sanitize collection name safely without raising exceptions."""
        try:
            return self._sanitize_collection_name(name)
        except ValueError:
            # Return None for invalid names during reconciliation
            return None
    
    def _sanitize_folder_path(self, folder: str) -> str:
        """Sanitize folder path for security."""
        if not folder:
            return ""
        
        # Basic sanitization
        safe_folder = folder.replace('..', '').replace('\\', '/')
        safe_folder = safe_folder.strip('/')
        
        return safe_folder
    
    def _validate_file_extension(self, filename: str) -> bool:
        """Check if file extension is allowed."""
        file_path = Path(filename)
        return file_path.suffix.lower() in self.ALLOWED_EXTENSIONS