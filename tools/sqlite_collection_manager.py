"""
SQLite-based Collection File Management System.
Provides identical API to file-based CollectionFileManager but uses SQLite backend.
"""
import json
import hashlib
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator

# Import existing models for compatibility
from tools.collection_manager import CollectionMetadata, FileMetadata
from tools.database import DatabaseManager, CollectionRepository, FileRepository


class SQLiteCollectionFileManager:
    """SQLite-based collection manager with identical API to file-based version."""
    
    # Maintain same allowed file extensions for security
    ALLOWED_EXTENSIONS = {'.md', '.txt', '.json'}
    
    def __init__(self, base_dir: Path = None):
        """Initialize SQLite collection manager."""
        # Initialize database manager with same fallback strategy
        if base_dir:
            db_path = base_dir / "collections.db"
        else:
            # Use same directory strategy as original
            import os
            home_dir = Path.home()
            db_path = home_dir / ".crawl4ai" / "collections.db"
        
        self.db = DatabaseManager(db_path)
        self.collection_repo = CollectionRepository(self.db)
        self.file_repo = FileRepository(self.db)
        
        # For compatibility, track base directory
        self.base_dir = db_path.parent
    
    def _validate_file_extension(self, filename: str) -> bool:
        """Check if file extension is allowed (identical to original)."""
        file_path = Path(filename)
        return file_path.suffix.lower() in self.ALLOWED_EXTENSIONS
    
    def _sanitize_collection_name(self, name: str) -> str:
        """Sanitize collection name (same logic as original)."""
        if not name or not name.strip():
            raise ValueError("Collection name cannot be empty")
        
        # Basic sanitization - remove dangerous characters
        sanitized = name.strip()
        
        # Remove path separators and other dangerous characters
        dangerous_chars = ['/', '\\', '..', ':', '*', '?', '"', '<', '>', '|']
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '_')
        
        return sanitized
    
    def create_collection(self, name: str, description: str = "") -> Dict[str, Any]:
        """Create a new collection with metadata (identical API)."""
        try:
            # Validate collection name using same logic
            sanitized_name = self._sanitize_collection_name(name)
            
            # Generate collection ID 
            collection_id = sanitized_name.lower().replace(' ', '-')
            
            # Create collection in database
            result = self.collection_repo.create_collection(
                collection_id=collection_id,
                name=sanitized_name,
                description=description
            )
            
            if result["success"]:
                # Return format identical to original
                return {
                    "success": True,
                    "path": str(self.base_dir / sanitized_name),  # Virtual path for compatibility
                    "message": f"Collection '{sanitized_name}' created successfully"
                }
            else:
                return result
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create collection '{name}'"
            }
    
    def save_file(self, collection_name: str, filename: str, content: str, folder: str = "") -> Dict[str, Any]:
        """Save content to a file within a collection (identical API)."""
        try:
            # Validate file extension
            if not self._validate_file_extension(filename):
                return {
                    "success": False,
                    "error": f"File extension not allowed. Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}"
                }
            
            # Sanitize collection name and get collection ID
            sanitized_collection_name = self._sanitize_collection_name(collection_name)
            collection_id = sanitized_collection_name.lower().replace(' ', '-')
            
            # Check if collection exists
            collection_info = self.collection_repo.get_collection(collection_id)
            if not collection_info["success"]:
                return {
                    "success": False,
                    "error": f"Collection '{collection_name}' does not exist"
                }
            
            # Sanitize folder path (same logic as original path validation)
            safe_folder = folder.replace('..', '').replace('\\', '/')
            safe_folder = safe_folder.strip('/')
            
            # Generate file ID
            file_id = f"{collection_id}_{safe_folder}_{filename}".replace('/', '_')
            
            # Save file to database
            result = self.file_repo.save_file(
                file_id=file_id,
                collection_id=collection_id,
                filename=filename,
                content=content,
                folder_path=safe_folder,
                source_url=None
            )
            
            if result["success"]:
                # Update collection statistics
                self.collection_repo.update_collection_stats(collection_id)
                
                # Calculate content hash for compatibility
                content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
                
                return {
                    "success": True,
                    "path": str(self.base_dir / sanitized_collection_name / safe_folder / filename),
                    "content_hash": content_hash,
                    "message": f"File '{filename}' saved successfully"
                }
            else:
                return result
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to save file '{filename}'"
            }
    
    def read_file(self, collection_name: str, filename: str, folder: str = "") -> Dict[str, Any]:
        """Read a file from a collection (identical API)."""
        try:
            # Sanitize collection name and get collection ID
            sanitized_collection_name = self._sanitize_collection_name(collection_name)
            collection_id = sanitized_collection_name.lower().replace(' ', '-')
            
            # Sanitize folder path
            safe_folder = folder.replace('..', '').replace('\\', '/')
            safe_folder = safe_folder.strip('/')
            
            # Read file from database
            result = self.file_repo.read_file(
                collection_id=collection_id,
                filename=filename,
                folder_path=safe_folder
            )
            
            if result["success"]:
                # Generate virtual path for compatibility with file manager
                virtual_path = str(self.base_dir / sanitized_collection_name / safe_folder / filename)
                
                return {
                    "success": True,
                    "content": result["content"],
                    "path": virtual_path,  # For compatibility with file manager
                    "metadata": {
                        "size": result["metadata"]["file_size"],
                        "created_at": result["metadata"]["created_at"],
                        "content_hash": result["metadata"]["content_hash"]
                    }
                }
            else:
                return result
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to read file '{filename}'"
            }
    
    def delete_file(self, collection_name: str, filename: str, folder: str = "") -> Dict[str, Any]:
        """Delete a file from a collection (identical API)."""
        try:
            # Sanitize collection name and get collection ID
            sanitized_collection_name = self._sanitize_collection_name(collection_name)
            collection_id = sanitized_collection_name.lower().replace(' ', '-')
            
            # Sanitize folder path
            safe_folder = folder.replace('..', '').replace('\\', '/')
            safe_folder = safe_folder.strip('/')
            
            # Delete file from database
            result = self.file_repo.delete_file(
                collection_id=collection_id,
                filename=filename,
                folder_path=safe_folder
            )
            
            if result["success"]:
                # Update collection stats after deletion
                self.collection_repo.update_collection_stats(collection_id)
                
                return {
                    "success": True,
                    "message": f"File '{filename}' deleted successfully from '{sanitized_collection_name}'"
                }
            else:
                return result
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to delete file '{filename}'"
            }
    
    def list_collections(self) -> Dict[str, Any]:
        """List all collections with metadata (identical API)."""
        try:
            result = self.collection_repo.list_collections()
            
            if result["success"]:
                # Transform to match original format
                collections = []
                for col in result["collections"]:
                    # Create collection data matching original file manager format
                    collection_data = {
                        "name": col["name"],
                        "description": col["description"],
                        "created_at": col["created_at"],
                        "file_count": col["file_count"],
                        "folders": [],  # Will be populated if needed
                        "metadata": {
                            "created_at": col["created_at"],
                            "description": col["description"],
                            "last_modified": col["created_at"],  # Use created_at as fallback
                            "file_count": col["file_count"],
                            "total_size": col["total_size"]
                        },
                        "path": str(self.base_dir / col["name"])  # Virtual path for compatibility
                    }
                    collections.append(collection_data)
                
                return {
                    "success": True,
                    "collections": collections,
                    "total": len(collections)
                }
            else:
                return result
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to list collections"
            }
    
    def delete_collection(self, collection_name: str) -> Dict[str, Any]:
        """Delete a collection and all its files (identical API)."""
        try:
            # Sanitize collection name and get collection ID
            sanitized_collection_name = self._sanitize_collection_name(collection_name)
            collection_id = sanitized_collection_name.lower().replace(' ', '-')
            
            # Delete from database
            result = self.collection_repo.delete_collection(collection_id)
            return result
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to delete collection '{collection_name}'"
            }
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get detailed information about a collection (identical API)."""
        try:
            # Sanitize collection name and get collection ID
            sanitized_collection_name = self._sanitize_collection_name(collection_name)
            collection_id = sanitized_collection_name.lower().replace(' ', '-')
            
            # Get collection from database
            result = self.collection_repo.get_collection(collection_id)
            
            if result["success"]:
                collection = result["collection"]
                
                # Format response to match original API
                return {
                    "success": True,
                    "collection": {
                        "name": collection["name"],
                        "description": collection["description"],
                        "created_at": collection["created_at"],
                        "file_count": collection["file_count"],
                        "total_size": collection["total_size"],
                        "folders": collection["folders"],
                        "path": str(self.base_dir / collection["name"])  # Virtual path
                    }
                }
            else:
                return result
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get collection info for '{collection_name}'"
            }
    
    def list_files_in_collection(self, collection_name: str) -> Dict[str, Any]:
        """List all files in a collection (identical API to original)."""
        try:
            # Sanitize collection name and get collection ID
            sanitized_collection_name = self._sanitize_collection_name(collection_name)
            collection_id = sanitized_collection_name.lower().replace(' ', '-')
            
            # Check if collection exists
            collection_info = self.collection_repo.get_collection(collection_id)
            if not collection_info["success"]:
                return {
                    "success": False,
                    "error": f"Collection '{collection_name}' not found"
                }
            
            # Get files from database
            result = self.file_repo.list_files(collection_id)
            
            if result["success"]:
                files = []
                folders = []
                folder_set = set()
                
                for file_data in result["files"]:
                    # Create file entry matching original format
                    file_path = file_data["folder_path"] + "/" + file_data["filename"] if file_data["folder_path"] else file_data["filename"]
                    
                    files.append({
                        "name": file_data["filename"],
                        "path": file_path,
                        "type": "file",
                        "size": file_data["file_size"],
                        "created_at": file_data["created_at"],
                        "modified_at": file_data["updated_at"],
                        "extension": Path(file_data["filename"]).suffix.lower(),
                        "folder": file_data["folder_path"]
                    })
                    
                    # Track folders
                    if file_data["folder_path"]:
                        # Add all parent folders
                        folder_parts = file_data["folder_path"].split('/')
                        current_path = ""
                        for part in folder_parts:
                            if current_path:
                                current_path += "/" + part
                            else:
                                current_path = part
                            
                            if current_path not in folder_set:
                                folder_set.add(current_path)
                                parent_folder = "/".join(current_path.split('/')[:-1]) if '/' in current_path else ""
                                
                                folders.append({
                                    "name": part,
                                    "path": current_path,
                                    "type": "folder",
                                    "folder": parent_folder
                                })
                
                return {
                    "success": True,
                    "files": files,
                    "folders": folders,
                    "total_files": len(files),
                    "total_folders": len(folders)
                }
            else:
                return result
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to list files in collection '{collection_name}'"
            }
    
    def _update_collection_metadata(self, collection_name: str):
        """Update collection metadata (for compatibility)."""
        try:
            sanitized_collection_name = self._sanitize_collection_name(collection_name)
            collection_id = sanitized_collection_name.lower().replace(' ', '-')
            
            # Update collection statistics
            self.collection_repo.update_collection_stats(collection_id)
            
        except Exception as e:
            # Log error but don't raise for compatibility
            import logging
            logging.error(f"Failed to update collection metadata for {collection_name}: {e}")
    
    def close(self):
        """Close database connections."""
        if hasattr(self, 'db'):
            self.db.close()


# Factory function to create appropriate manager based on configuration
def create_collection_manager(use_sqlite: bool = True, base_dir: Path = None):
    """Create either SQLite or file-based collection manager."""
    if use_sqlite:
        return SQLiteCollectionFileManager(base_dir)
    else:
        from tools.collection_manager import CollectionFileManager
        return CollectionFileManager(base_dir)