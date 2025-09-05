"""
FilesystemMetadataStore - SQLite metadata store for filesystem-based collections.

Provides metadata storage for Mode 2 (Filesystem+Metadata) architecture:
- Collections metadata (name, description, created_at)
- File metadata (path, hash, size, vector sync status)
- Reconciliation logging for tracking filesystem changes
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import logging
import asyncio
import concurrent.futures
import threading

logger = logging.getLogger(__name__)


class FilesystemMetadataStore:
    """SQLite metadata store for filesystem-based collections."""
    
    def __init__(self, db_path: Path):
        """
        Initialize filesystem metadata store.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize schema synchronously to avoid async/threading issues
        self._initialize_schema_sync()
        
        # Create a dedicated thread pool executor for SQLite operations
        self._executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=1, 
            thread_name_prefix="sqlite_thread"
        )
        self._db_lock = threading.Lock()
        
        logger.info(f"Initialized FilesystemMetadataStore with schema: {db_path}")
        
    def _initialize_schema_sync(self):
        """Initialize database schema synchronously."""
        try:
            with sqlite3.connect(str(self.db_path)) as db:
                # Enable foreign key constraints
                db.execute("PRAGMA foreign_keys = ON;")
                db.executescript("""
                    -- Collections table
                    CREATE TABLE IF NOT EXISTS collections (
                        name TEXT PRIMARY KEY,
                        description TEXT DEFAULT '',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    
                    -- File metadata (no content BLOB - content is in filesystem)
                    CREATE TABLE IF NOT EXISTS file_metadata (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        collection_name TEXT NOT NULL,
                        file_path TEXT NOT NULL,
                        content_hash TEXT NOT NULL,
                        file_size INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        source_url TEXT,
                        vector_sync_status TEXT DEFAULT 'not_synced',
                        last_sync_attempt TIMESTAMP,
                        sync_error_message TEXT,
                        UNIQUE(collection_name, file_path),
                        FOREIGN KEY (collection_name) REFERENCES collections(name) ON DELETE CASCADE
                    );
                    
                    -- Reconciliation log for tracking filesystem changes
                    CREATE TABLE IF NOT EXISTS reconciliation_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        collection_name TEXT NOT NULL,
                        reconciliation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        files_added INTEGER DEFAULT 0,
                        files_modified INTEGER DEFAULT 0,
                        files_deleted INTEGER DEFAULT 0,
                        reconciliation_actions TEXT,  -- JSON array of changes detected
                        FOREIGN KEY (collection_name) REFERENCES collections(name) ON DELETE CASCADE
                    );
                    
                    -- Indexes for performance
                    CREATE INDEX IF NOT EXISTS idx_file_metadata_collection ON file_metadata(collection_name);
                    CREATE INDEX IF NOT EXISTS idx_file_metadata_sync_status ON file_metadata(vector_sync_status);
                    CREATE INDEX IF NOT EXISTS idx_reconciliation_log_collection ON reconciliation_log(collection_name);
                    CREATE INDEX IF NOT EXISTS idx_reconciliation_log_timestamp ON reconciliation_log(reconciliation_timestamp);
                """)
                db.commit()
                logger.debug(f"Schema initialized synchronously for {self.db_path}")
        except Exception as e:
            logger.error(f"Synchronous schema initialization failed: {e}")
            raise
    
    def _execute_sync(self, operation_func, *args, **kwargs):
        """Execute a database operation synchronously in dedicated thread."""
        def sync_operation():
            with self._db_lock:
                with sqlite3.connect(str(self.db_path)) as db:
                    # Enable foreign key constraints
                    db.execute("PRAGMA foreign_keys = ON;")
                    return operation_func(db, *args, **kwargs)
        return sync_operation
    
    async def _execute_async(self, operation_func, *args, **kwargs):
        """Execute a database operation asynchronously via thread pool."""
        sync_op = self._execute_sync(operation_func, *args, **kwargs)
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(self._executor, sync_op)
        return result
    
    
    async def create_collection(self, name: str, description: str = "") -> Dict[str, Any]:
        """
        Create a new collection in metadata store.
        
        Args:
            name: Collection name
            description: Collection description
            
        Returns:
            Result dictionary with success status
        """
        def create_collection_sync(db, name, description):
            # Check if collection already exists
            cursor = db.execute("SELECT name FROM collections WHERE name = ?", (name,))
            if cursor.fetchone():
                return {
                    "success": False,
                    "error": f"Collection '{name}' already exists"
                }
            
            # Insert new collection
            now = datetime.now(timezone.utc).isoformat()
            db.execute(
                "INSERT INTO collections (name, description, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (name, description, now, now)
            )
            db.commit()
            
            logger.info(f"Collection '{name}' created in metadata store")
            return {
                "success": True,
                "name": name,
                "message": f"Collection '{name}' created successfully"
            }
        
        try:
            return await self._execute_async(create_collection_sync, name, description)
        except Exception as e:
            logger.error(f"Failed to create collection '{name}': {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def collection_exists(self, name: str) -> bool:
        """
        Check if a collection exists.
        
        Args:
            name: Collection name
            
        Returns:
            True if collection exists, False otherwise
        """
        def collection_exists_sync(db, name):
            cursor = db.execute("SELECT 1 FROM collections WHERE name = ?", (name,))
            return cursor.fetchone() is not None
            
        try:
            return await self._execute_async(collection_exists_sync, name)
        except Exception as e:
            logger.error(f"Error checking collection existence '{name}': {e}")
            return False
    
    async def list_collections(self) -> Dict[str, Any]:
        """
        List all collections with metadata.
        
        Returns:
            Result dictionary with collections list
        """
        def list_collections_sync(db):
            cursor = db.execute("""
                SELECT c.name, c.description, c.created_at, c.updated_at,
                       COUNT(f.id) as file_count
                FROM collections c
                LEFT JOIN file_metadata f ON c.name = f.collection_name
                GROUP BY c.name, c.description, c.created_at, c.updated_at
                ORDER BY c.created_at DESC
            """)
            rows = cursor.fetchall()
            
            collections = []
            for row in rows:
                collections.append({
                    "name": row[0],
                    "description": row[1],
                    "created_at": row[2],
                    "updated_at": row[3], 
                    "file_count": row[4]
                })
            
            return {
                "success": True,
                "collections": collections
            }
        
        try:
            return await self._execute_async(list_collections_sync)
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_collection(self, name: str) -> Dict[str, Any]:
        """
        Get collection information.
        
        Args:
            name: Collection name
            
        Returns:
            Result dictionary with collection info
        """
        def get_collection_sync(db, name):
            cursor = db.execute("""
                SELECT c.name, c.description, c.created_at, c.updated_at,
                       COUNT(f.id) as file_count,
                       SUM(f.file_size) as total_size
                FROM collections c
                LEFT JOIN file_metadata f ON c.name = f.collection_name
                WHERE c.name = ?
                GROUP BY c.name, c.description, c.created_at, c.updated_at
            """, (name,))
            row = cursor.fetchone()
            
            if not row:
                return {
                    "success": False,
                    "error": f"Collection '{name}' not found"
                }
            
            return {
                "success": True,
                "collection": {
                    "name": row[0],
                    "description": row[1],
                    "created_at": row[2],
                    "updated_at": row[3],
                    "file_count": row[4],
                    "total_size": row[5] or 0
                }
            }
        
        try:
            return await self._execute_async(get_collection_sync, name)
        except Exception as e:
            logger.error(f"Failed to get collection '{name}': {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_collection(self, name: str) -> Dict[str, Any]:
        """
        Delete collection and all associated files.
        
        Args:
            name: Collection name
            
        Returns:
            Result dictionary with deletion info
        """
        def delete_collection_sync(db, name):
            # Count files to be deleted
            cursor = db.execute("SELECT COUNT(*) FROM file_metadata WHERE collection_name = ?", (name,))
            file_count_row = cursor.fetchone()
            file_count = file_count_row[0] if file_count_row else 0
            
            # Delete collection (CASCADE will handle files and reconciliation log)
            result = db.execute("DELETE FROM collections WHERE name = ?", (name,))
            db.commit()
            
            if result.rowcount > 0:
                logger.info(f"Deleted collection '{name}' and {file_count} files from metadata store")
                return {
                    "success": True,
                    "deleted_files": file_count,
                    "message": f"Collection '{name}' deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"Collection '{name}' not found"
                }
        
        try:
            return await self._execute_async(delete_collection_sync, name)
        except Exception as e:
            logger.error(f"Failed to delete collection '{name}': {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_file_metadata(self, collection_name: str, file_path: str, 
                                   content_hash: str, file_size: int,
                                   vector_sync_status: str = "not_synced",
                                   source_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Update or insert file metadata.
        
        Args:
            collection_name: Name of the collection
            file_path: Relative path to the file
            content_hash: SHA256 hash of file content
            file_size: Size of file in bytes
            vector_sync_status: Vector sync status
            source_url: Optional source URL for crawled files
            
        Returns:
            Result dictionary with success status
        """
        def update_file_metadata_sync(db, collection_name, file_path, content_hash, file_size, vector_sync_status, source_url):
            now = datetime.now(timezone.utc).isoformat()
            
            # Use INSERT OR REPLACE for upsert behavior
            db.execute("""
                INSERT OR REPLACE INTO file_metadata 
                (collection_name, file_path, content_hash, file_size, 
                 created_at, modified_at, source_url, vector_sync_status)
                VALUES (?, ?, ?, ?, 
                        COALESCE((SELECT created_at FROM file_metadata 
                                 WHERE collection_name = ? AND file_path = ?), ?),
                        ?, ?, ?)
            """, (collection_name, file_path, content_hash, file_size,
                  collection_name, file_path, now,  # For created_at COALESCE
                  now, source_url, vector_sync_status))
            
            db.commit()
            
            logger.debug(f"Updated file metadata: {collection_name}/{file_path}")
            return {
                "success": True,
                "file_path": file_path,
                "content_hash": content_hash
            }
        
        try:
            return await self._execute_async(update_file_metadata_sync, collection_name, file_path, content_hash, file_size, vector_sync_status, source_url)
        except Exception as e:
            logger.error(f"Failed to update file metadata for '{collection_name}/{file_path}': {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_file_metadata(self, collection_name: str, file_path: str) -> Dict[str, Any]:
        """
        Get file metadata.
        
        Args:
            collection_name: Name of the collection
            file_path: Relative path to the file
            
        Returns:
            Result dictionary with file metadata
        """
        def get_file_metadata_sync(db, collection_name, file_path):
            cursor = db.execute("""
                SELECT file_path, content_hash, file_size, created_at, modified_at,
                       source_url, vector_sync_status, last_sync_attempt, sync_error_message
                FROM file_metadata
                WHERE collection_name = ? AND file_path = ?
            """, (collection_name, file_path))
            row = cursor.fetchone()
            
            if not row:
                return {
                    "success": False,
                    "error": f"File '{file_path}' not found in collection '{collection_name}'"
                }
            
            return {
                "success": True,
                "metadata": {
                    "file_path": row[0],
                    "content_hash": row[1], 
                    "file_size": row[2],
                    "created_at": row[3],
                    "modified_at": row[4],
                    "source_url": row[5],
                    "vector_sync_status": row[6],
                    "last_sync_attempt": row[7],
                    "sync_error_message": row[8]
                }
            }
        
        try:
            return await self._execute_async(get_file_metadata_sync, collection_name, file_path)
        except Exception as e:
            logger.error(f"Failed to get file metadata for '{collection_name}/{file_path}': {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_collection_files(self, collection_name: str) -> Dict[str, Any]:
        """
        Get all files in a collection with metadata.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Result dictionary with files list
        """
        def get_collection_files_sync(db, collection_name):
            # First check if collection exists
            cursor = db.execute("SELECT name FROM collections WHERE name = ?", (collection_name,))
            if not cursor.fetchone():
                return {
                    "success": False,
                    "error": f"Collection '{collection_name}' not found"
                }
            
            cursor = db.execute("""
                SELECT file_path, content_hash, file_size, created_at, modified_at,
                       source_url, vector_sync_status, last_sync_attempt, sync_error_message
                FROM file_metadata
                WHERE collection_name = ?
                ORDER BY file_path
            """, (collection_name,))
            rows = cursor.fetchall()
            
            files = []
            for row in rows:
                files.append({
                    "file_path": row[0],
                    "content_hash": row[1],
                    "file_size": row[2],
                    "created_at": row[3],
                    "modified_at": row[4],
                    "source_url": row[5],
                    "vector_sync_status": row[6],
                    "last_sync_attempt": row[7],
                    "sync_error_message": row[8]
                })
            
            return {
                "success": True,
                "files": files
            }
        
        try:
            return await self._execute_async(get_collection_files_sync, collection_name)
        except Exception as e:
            logger.error(f"Failed to get files for collection '{collection_name}': {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_file_metadata(self, collection_name: str, file_path: str) -> Dict[str, Any]:
        """
        Delete file metadata.
        
        Args:
            collection_name: Name of the collection
            file_path: Relative path to the file
            
        Returns:
            Result dictionary with success status
        """
        def delete_file_metadata_sync(db, collection_name, file_path):
            result = db.execute("""
                DELETE FROM file_metadata 
                WHERE collection_name = ? AND file_path = ?
            """, (collection_name, file_path))
            db.commit()
            
            if result.rowcount > 0:
                logger.debug(f"Deleted file metadata: {collection_name}/{file_path}")
                return {
                    "success": True,
                    "message": f"File metadata deleted for '{file_path}'"
                }
            else:
                return {
                    "success": False,
                    "error": f"File '{file_path}' not found in collection '{collection_name}'"
                }
        
        try:
            return await self._execute_async(delete_file_metadata_sync, collection_name, file_path)
        except Exception as e:
            logger.error(f"Failed to delete file metadata for '{collection_name}/{file_path}': {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def log_reconciliation(self, collection_name: str, actions: List[Dict[str, Any]],
                                files_added: int = 0, files_modified: int = 0, files_deleted: int = 0) -> Dict[str, Any]:
        """
        Log reconciliation actions.
        
        Args:
            collection_name: Name of the collection
            actions: List of reconciliation actions
            files_added: Number of files added
            files_modified: Number of files modified
            files_deleted: Number of files deleted
            
        Returns:
            Result dictionary with success status
        """
        def log_reconciliation_sync(db, collection_name, actions, files_added, files_modified, files_deleted):
            actions_json = json.dumps(actions)
            # Use high-precision timestamp to ensure proper ordering
            from datetime import datetime, timezone
            timestamp = datetime.now(timezone.utc).isoformat()
            
            db.execute("""
                INSERT INTO reconciliation_log 
                (collection_name, reconciliation_timestamp, files_added, files_modified, files_deleted, reconciliation_actions)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (collection_name, timestamp, files_added, files_modified, files_deleted, actions_json))
            db.commit()
            
            logger.debug(f"Logged reconciliation for '{collection_name}': +{files_added} ~{files_modified} -{files_deleted}")
            return {
                "success": True,
                "message": "Reconciliation logged successfully"
            }
        
        try:
            return await self._execute_async(log_reconciliation_sync, collection_name, actions, files_added, files_modified, files_deleted)
        except Exception as e:
            logger.error(f"Failed to log reconciliation for '{collection_name}': {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_last_reconciliation(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """
        Get last reconciliation information for a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Dictionary with last reconciliation info or None if not found
        """
        def get_last_reconciliation_sync(db, collection_name):
            cursor = db.execute("""
                SELECT reconciliation_timestamp, files_added, files_modified, files_deleted, reconciliation_actions
                FROM reconciliation_log
                WHERE collection_name = ?
                ORDER BY reconciliation_timestamp DESC
                LIMIT 1
            """, (collection_name,))
            row = cursor.fetchone()
            
            if row:
                actions = json.loads(row[4]) if row[4] else []
                return {
                    "timestamp": row[0],
                    "files_added": row[1],
                    "files_modified": row[2],
                    "files_deleted": row[3],
                    "actions": actions
                }
            
            return None
        
        try:
            return await self._execute_async(get_last_reconciliation_sync, collection_name)
        except Exception as e:
            logger.error(f"Failed to get last reconciliation for '{collection_name}': {e}")
            return None