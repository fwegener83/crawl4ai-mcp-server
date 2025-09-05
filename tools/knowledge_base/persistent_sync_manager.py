"""
Persistent Sync Manager - Database-only file storage and sync status persistence.

This module implements database-only storage for both file content and sync status,
eliminating dependency on filesystem storage and ensuring sync status survives 
server restarts.
"""

import json
import sqlite3
import hashlib
import logging
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union
from contextlib import contextmanager

from .vector_sync_schemas import VectorSyncStatus, FileVectorMapping, SyncStatus

logger = logging.getLogger(__name__)


class DatabaseCollectionManager:
    """Manages collections and files exclusively in SQLite database."""
    
    # Allowed file extensions for security (same as original collection manager)
    ALLOWED_EXTENSIONS = {'.md', '.txt', '.json'}
    
    # Enhanced database schema for database-only file storage
    DATABASE_SCHEMA = """
    -- Collections table with basic metadata
    CREATE TABLE IF NOT EXISTS collections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Files stored directly in database - NO filesystem dependency
    CREATE TABLE IF NOT EXISTS collection_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        collection_name TEXT NOT NULL,
        filename TEXT NOT NULL,
        folder TEXT DEFAULT '',
        content TEXT NOT NULL,  -- File content directly in database
        content_hash TEXT NOT NULL,  -- SHA256 hash for change detection
        size INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(collection_name, filename, folder),
        FOREIGN KEY (collection_name) REFERENCES collections(name) ON DELETE CASCADE
    );

    -- Vector sync status table - persistent across server restarts
    CREATE TABLE IF NOT EXISTS vector_sync_status (
        collection_name TEXT PRIMARY KEY,
        sync_status TEXT NOT NULL CHECK (sync_status IN ('never_synced', 'in_sync', 'out_of_sync', 'syncing', 'sync_error', 'partial_sync')),
        sync_enabled BOOLEAN DEFAULT 1,
        last_sync TIMESTAMP,
        last_sync_attempt TIMESTAMP,
        total_files INTEGER DEFAULT 0,
        synced_files INTEGER DEFAULT 0,
        changed_files_count INTEGER DEFAULT 0,
        total_chunks INTEGER DEFAULT 0,
        chunk_count INTEGER DEFAULT 0,
        sync_progress REAL,
        last_sync_duration REAL,
        avg_sync_duration REAL,
        errors TEXT DEFAULT '[]',  -- JSON array of error strings
        warnings TEXT DEFAULT '[]',  -- JSON array of warning strings
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (collection_name) REFERENCES collections(name) ON DELETE CASCADE
    );

    -- Vector file mappings - track which files map to which chunks
    CREATE TABLE IF NOT EXISTS vector_file_mappings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        collection_name TEXT NOT NULL,
        file_id INTEGER NOT NULL,  -- Reference to collection_files.id
        file_path TEXT NOT NULL,   -- Logical path (folder/filename)
        file_hash TEXT NOT NULL,
        chunk_ids TEXT NOT NULL,  -- JSON array of chunk IDs
        chunk_count INTEGER DEFAULT 0,
        last_synced TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        sync_status TEXT DEFAULT 'never_synced',
        sync_error TEXT,
        processing_time REAL DEFAULT 0.0,
        chunking_strategy TEXT DEFAULT 'auto',
        UNIQUE(collection_name, file_id),
        FOREIGN KEY (collection_name) REFERENCES collections(name) ON DELETE CASCADE,
        FOREIGN KEY (file_id) REFERENCES collection_files(id) ON DELETE CASCADE
    );

    -- Performance indexes
    CREATE INDEX IF NOT EXISTS idx_collections_name ON collections(name);
    CREATE INDEX IF NOT EXISTS idx_collection_files_collection ON collection_files(collection_name);
    CREATE INDEX IF NOT EXISTS idx_collection_files_hash ON collection_files(content_hash);
    CREATE INDEX IF NOT EXISTS idx_vector_sync_status_collection ON vector_sync_status(collection_name);
    CREATE INDEX IF NOT EXISTS idx_vector_file_mappings_collection ON vector_file_mappings(collection_name);
    CREATE INDEX IF NOT EXISTS idx_vector_file_mappings_file_id ON vector_file_mappings(file_id);
    """
    
    def __init__(self, db_path: str):
        """Initialize database collection manager with given path."""
        self.db_path = os.path.abspath(db_path)  # Make path absolute
        self._init_database()
        logger.debug(f"DatabaseCollectionManager initialized with absolute path: {self.db_path}")
        logger.info(f"DatabaseCollectionManager initialized with database: {self.db_path}")
    
    def _validate_file_extension(self, filename: str) -> bool:
        """Check if file extension is allowed (same as original collection manager)."""
        from pathlib import Path
        file_path = Path(filename)
        return file_path.suffix.lower() in self.ALLOWED_EXTENSIONS
    
    def _init_database(self):
        """Initialize database with enhanced schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(self.DATABASE_SCHEMA)
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON")
            conn.commit()
        logger.info("Database schema initialized successfully")
    
    @contextmanager
    def get_connection(self):
        """Get database connection with proper configuration."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def create_collection(self, name: str, description: str = '') -> Dict[str, Any]:
        """Create a new collection in database."""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT INTO collections (name, description, created_at, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (name, description))
                conn.commit()
                
                return {
                    "success": True,
                    "collection_name": name,
                    "description": description,
                    "message": f"Collection '{name}' created successfully"
                }
        except sqlite3.IntegrityError:
            return {
                "success": False,
                "error": f"Collection '{name}' already exists"
            }
        except Exception as e:
            logger.error(f"Error creating collection '{name}': {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_file(self, collection_name: str, filename: str, content: str, folder: str = '') -> Dict[str, Any]:
        """Create file directly in database - NO filesystem operations."""
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        file_size = len(content.encode('utf-8'))
        
        try:
            # Validate file extension first
            if not self._validate_file_extension(filename):
                return {
                    "success": False,
                    "error": f"File extension not allowed. Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}"
                }
            
            # Check if collection exists - CRITICAL for proper error handling
            if not self.collection_exists(collection_name):
                return {
                    "success": False,
                    "error": f"Collection '{collection_name}' not found"
                }
            
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT OR REPLACE INTO collection_files 
                    (collection_name, filename, folder, content, content_hash, size, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (collection_name, filename, folder, content, content_hash, file_size))
                
                conn.commit()
                file_id = cursor.lastrowid
                
                # Update collection updated_at timestamp
                conn.execute("""
                    UPDATE collections 
                    SET updated_at = CURRENT_TIMESTAMP 
                    WHERE name = ?
                """, (collection_name,))
                conn.commit()
                
                return {
                    "success": True,
                    "file_id": file_id,
                    "filename": filename,
                    "folder": folder,
                    "content_hash": content_hash,
                    "size": file_size,
                    "path": f"{folder}/{filename}" if folder else filename
                }
        except Exception as e:
            logger.error(f"Error creating file {filename} in collection {collection_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_file_content(self, collection_name: str, file_id: int) -> Dict[str, Any]:
        """Get file content directly from database."""
        try:
            # First check if collection exists - CRITICAL for proper error handling
            if not self.collection_exists(collection_name):
                return {
                    "success": False,
                    "error": f"Collection '{collection_name}' not found"
                }
            
            with self.get_connection() as conn:
                row = conn.execute("""
                    SELECT filename, folder, content, content_hash, size, created_at, updated_at
                    FROM collection_files 
                    WHERE collection_name = ? AND id = ?
                """, (collection_name, file_id)).fetchone()
                
                if row:
                    return {
                        "success": True,
                        "filename": row['filename'],
                        "folder": row['folder'], 
                        "content": row['content'],
                        "content_hash": row['content_hash'],
                        "size": row['size'],
                        "created_at": row['created_at'],
                        "updated_at": row['updated_at']
                    }
                return {"success": False, "error": "File not found"}
        except Exception as e:
            logger.error(f"Error getting file content {file_id} from collection {collection_name}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_file_by_path(self, collection_name: str, filename: str, folder: str = '') -> Dict[str, Any]:
        """Get file content by path (filename and folder)."""
        try:
            # First check if collection exists - CRITICAL for proper error handling
            if not self.collection_exists(collection_name):
                return {
                    "success": False,
                    "error": f"Collection '{collection_name}' not found"
                }
            
            with self.get_connection() as conn:
                row = conn.execute("""
                    SELECT id, filename, folder, content, content_hash, size, created_at, updated_at
                    FROM collection_files 
                    WHERE collection_name = ? AND filename = ? AND folder = ?
                """, (collection_name, filename, folder)).fetchone()
                
                if row:
                    return {
                        "success": True,
                        "file_id": row['id'],
                        "filename": row['filename'],
                        "folder": row['folder'], 
                        "content": row['content'],
                        "content_hash": row['content_hash'],
                        "size": row['size'],
                        "created_at": row['created_at'],
                        "updated_at": row['updated_at'],
                        "path": f"{row['folder']}/{row['filename']}" if row['folder'] else row['filename']
                    }
                return {"success": False, "error": f"File '{filename}' not found in folder '{folder}'"}
        except Exception as e:
            logger.error(f"Error getting file {filename} from collection {collection_name}: {e}")
            return {"success": False, "error": str(e)}
    
    def list_collection_files(self, collection_name: str) -> List[Dict[str, Any]]:
        """List all files in collection from database."""
        try:
            # First check if collection exists - CRITICAL for proper error handling
            if not self.collection_exists(collection_name):
                logger.warning(f"Attempted to list files in non-existent collection: {collection_name}")
                return []  # Return empty list for non-existent collections in list operations
            
            with self.get_connection() as conn:
                rows = conn.execute("""
                    SELECT id, filename, folder, content_hash, size, created_at, updated_at
                    FROM collection_files 
                    WHERE collection_name = ?
                    ORDER BY folder, filename
                """, (collection_name,)).fetchall()
                
                return [
                    {
                        "file_id": row['id'],
                        "name": row['filename'],  # Compatible with existing code
                        "filename": row['filename'],
                        "folder": row['folder'],
                        "path": f"{row['folder']}/{row['filename']}" if row['folder'] else row['filename'],
                        "content_hash": row['content_hash'],
                        "size": row['size'],
                        "created_at": row['created_at'],
                        "updated_at": row['updated_at']
                    }
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"Error listing files in collection {collection_name}: {e}")
            return []
    
    def collection_exists(self, collection_name: str) -> bool:
        """Check if collection exists."""
        try:
            with self.get_connection() as conn:
                row = conn.execute("""
                    SELECT 1 FROM collections WHERE name = ?
                """, (collection_name,)).fetchone()
                return row is not None
        except Exception as e:
            logger.error(f"Error checking collection existence {collection_name}: {e}")
            return False
    
    def list_collections(self) -> List[Dict[str, Any]]:
        """List all collections from database."""
        try:
            with self.get_connection() as conn:
                rows = conn.execute("""
                    SELECT c.name, c.description, c.created_at, c.updated_at,
                           COUNT(f.id) as file_count
                    FROM collections c
                    LEFT JOIN collection_files f ON c.name = f.collection_name
                    GROUP BY c.name, c.description, c.created_at, c.updated_at
                    ORDER BY c.created_at DESC
                """).fetchall()
                
                return [
                    {
                        "name": row['name'],
                        "description": row['description'],
                        "file_count": row['file_count'],
                        "created_at": row['created_at'],
                        "updated_at": row['updated_at']
                    }
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            return []
    
    def delete_collection(self, collection_name: str) -> Dict[str, Any]:
        """Delete a collection and all its files from database."""
        try:
            with self.get_connection() as conn:
                # First count files for reporting
                file_count = conn.execute("""
                    SELECT COUNT(*) FROM collection_files WHERE collection_name = ?
                """, (collection_name,)).fetchone()[0]
                
                # Delete files (will cascade due to foreign key, but explicit is better)
                conn.execute("""
                    DELETE FROM collection_files WHERE collection_name = ?
                """, (collection_name,))
                
                # Delete collection
                cursor = conn.execute("""
                    DELETE FROM collections WHERE name = ?
                """, (collection_name,))
                
                conn.commit()
                
                if cursor.rowcount == 0:
                    return {
                        "success": False,
                        "error": f"Collection '{collection_name}' not found"
                    }
                
                return {
                    "success": True,
                    "deleted_files": file_count,
                    "message": f"Collection '{collection_name}' and {file_count} files deleted successfully"
                }
        except Exception as e:
            logger.error(f"Error deleting collection '{collection_name}': {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_file(self, collection_name: str, filename: str, folder: str = "") -> Dict[str, Any]:
        """Delete a specific file from a collection."""
        try:
            with self.get_connection() as conn:
                # Delete the file
                cursor = conn.execute("""
                    DELETE FROM collection_files 
                    WHERE collection_name = ? AND filename = ? AND folder = ?
                """, (collection_name, filename, folder))
                
                conn.commit()
                
                if cursor.rowcount == 0:
                    return {
                        "success": False,
                        "error": f"File '{filename}' not found in collection '{collection_name}'"
                    }
                
                file_path = f"{folder}/{filename}" if folder else filename
                return {
                    "success": True,
                    "message": f"File '{file_path}' deleted successfully from collection '{collection_name}'"
                }
        except Exception as e:
            logger.error(f"Error deleting file {filename} from collection {collection_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class PersistentSyncManager:
    """Handles persistent storage of sync status and file mappings."""
    
    def __init__(self, db_path: str):
        """Initialize persistent sync manager with database path."""
        self.db_path = os.path.abspath(db_path)  # Make path absolute
        self.db_manager = DatabaseCollectionManager(self.db_path)
        logger.debug(f"PersistentSyncManager initialized with absolute path: {self.db_path}")
        logger.info(f"PersistentSyncManager initialized with database: {self.db_path}")
    
    @contextmanager
    def get_connection(self):
        """Get database connection."""
        with self.db_manager.get_connection() as conn:
            yield conn
    
    def save_sync_status(self, status: VectorSyncStatus) -> bool:
        """Save sync status to database."""
        try:
            with self.get_connection() as conn:
                # Ensure collection exists in vector sync database to satisfy foreign key constraint
                # This is needed when using filesystem collections that aren't in the vector sync DB
                conn.execute("""
                    INSERT OR IGNORE INTO collections (name, description, created_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (status.collection_name, f"Vector sync reference for {status.collection_name}"))
                
                conn.execute("""
                    INSERT OR REPLACE INTO vector_sync_status 
                    (collection_name, sync_status, sync_enabled, last_sync, last_sync_attempt,
                     total_files, synced_files, changed_files_count, total_chunks, chunk_count,
                     sync_progress, last_sync_duration, avg_sync_duration, errors, warnings, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    status.collection_name, 
                    status.status.value if hasattr(status.status, 'value') else str(status.status),
                    status.sync_enabled,
                    status.last_sync.isoformat() if status.last_sync else None,
                    status.last_sync_attempt.isoformat() if status.last_sync_attempt else None,
                    status.total_files,
                    status.synced_files,
                    status.changed_files_count,
                    status.total_chunks,
                    status.chunk_count,
                    status.sync_progress,
                    status.last_sync_duration,
                    status.avg_sync_duration,
                    json.dumps(status.errors),
                    json.dumps(status.warnings)
                ))
                conn.commit()
                logger.debug(f"Saved sync status for collection '{status.collection_name}' - status: {status.status}, chunk_count: {status.chunk_count}")
                logger.debug(f"Saved sync status for collection '{status.collection_name}'")
                return True
        except Exception as e:
            logger.error(f"Error saving sync status for collection {status.collection_name}: {e}")
            return False
    
    def load_sync_status(self, collection_name: str) -> Optional[VectorSyncStatus]:
        """Load sync status from database."""
        try:
            with self.get_connection() as conn:
                row = conn.execute("""
                    SELECT * FROM vector_sync_status WHERE collection_name = ?
                """, (collection_name,)).fetchone()
                
                if row:
                    # Parse timestamps
                    last_sync = None
                    if row['last_sync']:
                        last_sync = datetime.fromisoformat(row['last_sync'])
                    
                    last_sync_attempt = None
                    if row['last_sync_attempt']:
                        last_sync_attempt = datetime.fromisoformat(row['last_sync_attempt'])
                    
                    # Parse JSON arrays
                    errors = json.loads(row['errors']) if row['errors'] else []
                    warnings = json.loads(row['warnings']) if row['warnings'] else []
                    
                    # Convert string status back to enum
                    sync_status = SyncStatus(row['sync_status'])
                    
                    return VectorSyncStatus(
                        collection_name=row['collection_name'],
                        sync_enabled=bool(row['sync_enabled']),
                        status=sync_status,
                        last_sync=last_sync,
                        last_sync_attempt=last_sync_attempt,
                        total_files=row['total_files'],
                        synced_files=row['synced_files'],
                        changed_files_count=row['changed_files_count'],
                        total_chunks=row['total_chunks'],
                        chunk_count=row['chunk_count'],
                        sync_progress=row['sync_progress'],
                        errors=errors,
                        warnings=warnings,
                        last_sync_duration=row['last_sync_duration'],
                        avg_sync_duration=row['avg_sync_duration']
                    )
                return None
        except Exception as e:
            logger.error(f"Error loading sync status for collection {collection_name}: {e}")
            return None
    
    def load_all_sync_statuses(self) -> Dict[str, VectorSyncStatus]:
        """Load all sync statuses from database."""
        try:
            with self.get_connection() as conn:
                rows = conn.execute("""
                    SELECT collection_name FROM vector_sync_status
                """).fetchall()
                
                statuses = {}
                for row in rows:
                    status = self.load_sync_status(row['collection_name'])
                    if status:
                        statuses[row['collection_name']] = status
                
                return statuses
        except Exception as e:
            logger.error(f"Error loading all sync statuses: {e}")
            return {}
    
    def save_file_mapping(self, mapping: FileVectorMapping) -> bool:
        """Save file-to-vector mapping in database."""
        try:
            with self.get_connection() as conn:
                # Get the actual file_id from the database
                file_path = Path(mapping.file_path)
                filename = file_path.name
                folder = str(file_path.parent) if file_path.parent != Path('.') else ''
                
                file_info = self.db_manager.get_file_by_path(mapping.collection_name, filename, folder)
                
                if not file_info.get('success'):
                    logger.warning(f"Cannot save mapping: file not found for path {mapping.file_path}")
                    return False
                
                file_id = file_info['file_id']
                
                conn.execute("""
                    INSERT OR REPLACE INTO vector_file_mappings
                    (collection_name, file_id, file_path, file_hash, chunk_ids, 
                     chunk_count, last_synced, sync_status, sync_error, processing_time, chunking_strategy)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    mapping.collection_name,
                    file_id,
                    mapping.file_path,
                    mapping.file_hash,
                    json.dumps(mapping.chunk_ids),
                    mapping.chunk_count,
                    mapping.last_synced.isoformat() if mapping.last_synced else None,
                    mapping.sync_status.value if hasattr(mapping.sync_status, 'value') else str(mapping.sync_status),
                    mapping.sync_error,
                    mapping.processing_time,
                    mapping.chunking_strategy
                ))
                conn.commit()
                logger.debug(f"Saved file mapping for {mapping.file_path} in collection {mapping.collection_name}")
                return True
        except Exception as e:
            logger.error(f"Error saving file mapping for {mapping.file_path}: {e}")
            return False
    
    def load_file_mapping(self, collection_name: str, file_id: int) -> Optional[FileVectorMapping]:
        """Load file mapping from database by file_id."""
        try:
            with self.get_connection() as conn:
                row = conn.execute("""
                    SELECT * FROM vector_file_mappings 
                    WHERE collection_name = ? AND file_id = ?
                """, (collection_name, file_id)).fetchone()
                
                if row:
                    # Parse timestamp
                    last_synced = None
                    if row['last_synced']:
                        last_synced = datetime.fromisoformat(row['last_synced'])
                    
                    # Parse JSON chunk_ids
                    chunk_ids = json.loads(row['chunk_ids']) if row['chunk_ids'] else []
                    
                    # Convert string status back to enum
                    sync_status = SyncStatus(row['sync_status'])
                    
                    return FileVectorMapping(
                        collection_name=row['collection_name'],
                        file_path=row['file_path'],
                        file_hash=row['file_hash'],
                        chunk_ids=chunk_ids,
                        chunk_count=row['chunk_count'],
                        last_synced=last_synced,
                        sync_status=sync_status,
                        sync_error=row['sync_error'],
                        processing_time=row['processing_time'],
                        chunking_strategy=row['chunking_strategy']
                    )
                return None
        except Exception as e:
            logger.error(f"Error loading file mapping for file_id {file_id} in collection {collection_name}: {e}")
            return None
    
    def load_collection_mappings(self, collection_name: str) -> Dict[str, FileVectorMapping]:
        """Load all file mappings for a collection."""
        try:
            with self.get_connection() as conn:
                rows = conn.execute("""
                    SELECT * FROM vector_file_mappings 
                    WHERE collection_name = ?
                """, (collection_name,)).fetchall()
                
                mappings = {}
                for row in rows:
                    # Parse timestamp
                    last_synced = None
                    if row['last_synced']:
                        last_synced = datetime.fromisoformat(row['last_synced'])
                    
                    # Parse JSON chunk_ids
                    chunk_ids = json.loads(row['chunk_ids']) if row['chunk_ids'] else []
                    
                    # Convert string status back to enum
                    sync_status = SyncStatus(row['sync_status'])
                    
                    mapping = FileVectorMapping(
                        collection_name=row['collection_name'],
                        file_path=row['file_path'],
                        file_hash=row['file_hash'],
                        chunk_ids=chunk_ids,
                        chunk_count=row['chunk_count'],
                        last_synced=last_synced,
                        sync_status=sync_status,
                        sync_error=row['sync_error'],
                        processing_time=row['processing_time'],
                        chunking_strategy=row['chunking_strategy']
                    )
                    
                    mappings[row['file_path']] = mapping
                
                return mappings
        except Exception as e:
            logger.error(f"Error loading collection mappings for {collection_name}: {e}")
            return {}


class LimitedCache:
    """Simple LRU-like cache with size limit to prevent memory leaks."""
    
    def __init__(self, max_size: int = 50):
        self.cache = {}
        self.max_size = max_size
        self.access_order = []
    
    def get(self, key):
        """Get item from cache and update access order."""
        if key in self.cache:
            # Move to end (most recently used)
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def __contains__(self, key):
        """Support 'in' operator for cache membership testing."""
        return key in self.cache
    
    def set(self, key, value):
        """Set item in cache with size limit."""
        if key in self.cache:
            # Update existing item
            self.cache[key] = value
            self.access_order.remove(key)
            self.access_order.append(key)
        else:
            # Add new item
            if len(self.cache) >= self.max_size:
                # Remove oldest item
                oldest_key = self.access_order.pop(0)
                del self.cache[oldest_key]
            
            self.cache[key] = value
            self.access_order.append(key)
    
    def clear(self):
        """Clear the cache."""
        self.cache.clear()
        self.access_order.clear()
    
    def size(self):
        """Get current cache size."""
        return len(self.cache)