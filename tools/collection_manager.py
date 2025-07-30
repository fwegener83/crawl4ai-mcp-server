"""
Collection File Management System.
Provides file-first architecture for organizing crawled content in hierarchical collections.
"""
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator


class CollectionMetadata(BaseModel):
    """Collection metadata structure."""
    name: str = Field(..., description="Collection name")
    description: str = Field(default="", description="Collection description") 
    created_at: datetime = Field(default_factory=datetime.utcnow)
    crawl_sources: List[Dict[str, Any]] = Field(default_factory=list)
    file_count: int = Field(default=0)
    folders: List[str] = Field(default_factory=list)
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Ensure safe collection name."""
        if not v or not v.strip():
            raise ValueError("Collection name cannot be empty")
        
        # Basic sanitization - remove dangerous characters
        sanitized = v.strip()
        
        # Remove path separators and other dangerous characters
        dangerous_chars = ['/', '\\', '..', ':', '*', '?', '"', '<', '>', '|']
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '_')
        
        return sanitized


class FileMetadata(BaseModel):
    """Individual file metadata."""
    filename: str
    folder_path: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    source_url: Optional[str] = None
    content_hash: Optional[str] = None


class CollectionFileManager:
    """Handles file operations for collections with security and validation."""
    
    # Allowed file extensions for security
    ALLOWED_EXTENSIONS = {'.md', '.txt', '.json'}
    
    def __init__(self, base_dir: Path = None):
        """Initialize file manager with base directory."""
        if base_dir:
            self.base_dir = Path(base_dir)
        else:
            # Use user's home directory for collections to avoid read-only issues
            import os
            home_dir = Path.home()
            self.base_dir = home_dir / ".crawl4ai" / "collections"
        
        # Ensure base directory exists and is accessible
        try:
            self.base_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            # If that fails, try temp directory
            import tempfile
            temp_dir = Path(tempfile.gettempdir()) / "crawl4ai_collections"
            try:
                temp_dir.mkdir(parents=True, exist_ok=True)
                self.base_dir = temp_dir
                print(f"Warning: Using temporary directory {self.base_dir} for collections", file=__import__('sys').stderr)
            except OSError:
                raise RuntimeError(f"Cannot create collections directory. Tried {self.base_dir} and {temp_dir}: {e}")
    
    def _validate_path_security(self, collection_name: str, filename: str = None, folder: str = None) -> Path:
        """Validate and sanitize paths to prevent traversal attacks."""
        # Sanitize collection name
        safe_collection = collection_name.replace('..', '').replace('/', '_').replace('\\', '_')
        collection_path = self.base_dir / safe_collection
        
        if filename is None:
            return collection_path
        
        # Sanitize folder if provided
        if folder:
            safe_folder = folder.replace('..', '').replace('\\', '/')
            # Remove leading slashes and create safe path
            safe_folder = safe_folder.strip('/')
            if safe_folder:
                file_path = collection_path / safe_folder / filename
            else:
                file_path = collection_path / filename
        else:
            file_path = collection_path / filename
        
        # Ensure the final path is within the collection directory
        try:
            file_path.resolve().relative_to(collection_path.resolve())
        except ValueError:
            raise ValueError(f"Path traversal attempt detected: path would escape collection directory")
        
        return file_path
    
    def _validate_file_extension(self, filename: str) -> bool:
        """Check if file extension is allowed."""
        file_path = Path(filename)
        return file_path.suffix.lower() in self.ALLOWED_EXTENSIONS
    
    def create_collection(self, name: str, description: str = "") -> Dict[str, Any]:
        """Create a new collection with metadata."""
        try:
            # Validate and get safe collection path
            collection_path = self._validate_path_security(name)
            
            # Create collection directory
            collection_path.mkdir(parents=True, exist_ok=True)
            
            # Create metadata
            metadata = CollectionMetadata(name=name, description=description)
            metadata_path = collection_path / ".collection.json"
            
            # Write metadata file
            metadata_path.write_text(
                metadata.model_dump_json(indent=2), 
                encoding='utf-8'
            )
            
            return {
                "success": True, 
                "path": str(collection_path),
                "message": f"Collection '{name}' created successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create collection '{name}'"
            }
    
    def save_file(self, collection_name: str, filename: str, content: str, folder: str = "") -> Dict[str, Any]:
        """Save content to a file within a collection."""
        try:
            # Validate file extension
            if not self._validate_file_extension(filename):
                return {
                    "success": False,
                    "error": f"File extension not allowed. Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}"
                }
            
            # Get and validate collection path
            collection_path = self._validate_path_security(collection_name)
            if not collection_path.exists():
                return {
                    "success": False,
                    "error": f"Collection '{collection_name}' does not exist"
                }
            
            # Get and validate file path
            file_path = self._validate_path_security(collection_name, filename, folder)
            
            # Create folder structure if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file content with UTF-8 encoding
            file_path.write_text(content, encoding='utf-8')
            
            # Update collection metadata
            self._update_collection_metadata(collection_name)
            
            return {
                "success": True,
                "path": str(file_path),
                "message": f"File '{filename}' saved successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to save file '{filename}'"
            }
    
    def read_file(self, collection_name: str, filename: str, folder: str = "") -> Dict[str, Any]:
        """Read content from a file within a collection."""
        try:
            # Get and validate file path
            file_path = self._validate_path_security(collection_name, filename, folder)
            
            if not file_path.exists():
                return {
                    "success": False,
                    "error": f"File '{filename}' not found in collection '{collection_name}'"
                }
            
            # Read file content
            content = file_path.read_text(encoding='utf-8')
            
            return {
                "success": True,
                "content": content,
                "path": str(file_path)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to read file '{filename}'"
            }
    
    def list_collections(self) -> Dict[str, Any]:
        """List all available collections."""
        try:
            collections = []
            
            if not self.base_dir.exists():
                return {"success": True, "collections": collections}
            
            for item in self.base_dir.iterdir():
                if item.is_dir():
                    metadata_path = item / ".collection.json"
                    if metadata_path.exists():
                        try:
                            metadata_text = metadata_path.read_text(encoding='utf-8')
                            metadata = json.loads(metadata_text)
                            collections.append({
                                "name": metadata.get("name", item.name),
                                "description": metadata.get("description", ""),
                                "created_at": metadata.get("created_at", datetime.utcnow().isoformat()),
                                "file_count": metadata.get("file_count", 0),
                                "folders": metadata.get("folders", []),
                                "metadata": {
                                    "created_at": metadata.get("created_at", datetime.utcnow().isoformat()),
                                    "description": metadata.get("description", ""),
                                    "last_modified": metadata.get("created_at", datetime.utcnow().isoformat()),
                                    "file_count": metadata.get("file_count", 0),
                                    "total_size": 0  # TODO: Calculate actual total size
                                },
                                "path": str(item)
                            })
                        except (json.JSONDecodeError, OSError):
                            # Skip directories with invalid metadata
                            continue
            
            return {
                "success": True,
                "collections": collections,
                "total": len(collections)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to list collections"
            }
    
    def _update_collection_metadata(self, collection_name: str):
        """Update collection metadata (file count, folders, etc.)."""
        try:
            collection_path = self._validate_path_security(collection_name)
            metadata_path = collection_path / ".collection.json"
            
            if not metadata_path.exists():
                return
            
            # Read current metadata
            metadata_text = metadata_path.read_text(encoding='utf-8')
            metadata_dict = json.loads(metadata_text)
            
            # Count files and collect folder names
            file_count = 0
            folders = set()
            
            for file_path in collection_path.rglob('*'):
                if file_path.is_file() and file_path.name != '.collection.json':
                    file_count += 1
                    # Get relative path from collection root
                    rel_path = file_path.relative_to(collection_path)
                    if len(rel_path.parts) > 1:
                        folders.add(rel_path.parts[0])
            
            # Update metadata
            metadata_dict['file_count'] = file_count
            metadata_dict['folders'] = sorted(list(folders))
            
            # Write back updated metadata
            metadata_path.write_text(
                json.dumps(metadata_dict, indent=2),
                encoding='utf-8'
            )
            
        except Exception:
            # Silently fail metadata updates - not critical for core functionality
            pass
    
    def delete_collection(self, collection_name: str) -> Dict[str, Any]:
        """Delete a collection and all its files."""
        try:
            collection_path = self._validate_path_security(collection_name)
            
            if not collection_path.exists():
                return {
                    "success": False,
                    "error": f"Collection '{collection_name}' does not exist"
                }
            
            # Remove the entire collection directory
            import shutil
            shutil.rmtree(collection_path)
            
            return {
                "success": True,
                "message": f"Collection '{collection_name}' deleted successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to delete collection '{collection_name}'"
            }
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get detailed information about a collection."""
        try:
            collection_path = self._validate_path_security(collection_name)
            metadata_path = collection_path / ".collection.json"
            
            if not collection_path.exists() or not metadata_path.exists():
                return {
                    "success": False,
                    "error": f"Collection '{collection_name}' not found"
                }
            
            # Read metadata
            metadata_text = metadata_path.read_text(encoding='utf-8')
            metadata = json.loads(metadata_text)
            
            # Format to match Frontend FileCollection interface
            collection_info = {
                "name": metadata.get("name", collection_name),
                "description": metadata.get("description", ""),
                "created_at": metadata.get("created_at", datetime.utcnow().isoformat()),
                "file_count": metadata.get("file_count", 0),
                "folders": metadata.get("folders", []),
                "metadata": {
                    "created_at": metadata.get("created_at", datetime.utcnow().isoformat()),
                    "description": metadata.get("description", ""),
                    "last_modified": metadata.get("created_at", datetime.utcnow().isoformat()),
                    "file_count": metadata.get("file_count", 0),
                    "total_size": 0  # TODO: Calculate actual total size
                }
            }
            
            return {
                "success": True,
                "collection": collection_info,
                "path": str(collection_path)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get collection info for '{collection_name}'"
            }