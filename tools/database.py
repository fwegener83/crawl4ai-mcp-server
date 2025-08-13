"""
SQLite Database Foundation for Collection Storage.
Provides database schema, connection management, and repository patterns.
"""
import sqlite3
import logging
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Generator
from contextlib import contextmanager
import tempfile
import threading

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database connections and schema."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database manager with connection."""
        if db_path:
            self.db_path = Path(db_path)
        else:
            # Use consistent path strategy with collection_manager
            home_dir = Path.home()
            self.db_path = home_dir / ".crawl4ai" / "collections.db"
        
        # Ensure parent directory exists
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            # Fallback to temp directory like collection_manager
            temp_dir = Path(tempfile.gettempdir()) / "crawl4ai_collections.db"
            logger.warning(f"Using temporary database location {temp_dir}: {e}")
            self.db_path = temp_dir
        
        # Thread-local storage for connections
        self._local = threading.local()
        
        # Initialize database schema
        self._initialize_database()
        
        # Apply performance optimizations
        self._optimize_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection."""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False,
                timeout=30.0
            )
            # Enable foreign key constraints
            self._local.connection.execute("PRAGMA foreign_keys = ON")
            # Enable WAL mode for better concurrent access
            self._local.connection.execute("PRAGMA journal_mode = WAL")
            # Row factory for named access
            self._local.connection.row_factory = sqlite3.Row
        
        return self._local.connection
    
    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for database connections with automatic transaction handling."""
        conn = self._get_connection()
        try:
            yield conn
        except Exception:
            conn.rollback()
            raise
        else:
            conn.commit()
    
    def _initialize_database(self):
        """Create database schema if it doesn't exist."""
        schema_sql = """
        -- Schema version tracking
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Collections table
        CREATE TABLE IF NOT EXISTS collections (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            description TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_count INTEGER DEFAULT 0,
            total_size INTEGER DEFAULT 0,
            metadata TEXT DEFAULT '{}'  -- JSON blob for extensibility
        );
        
        -- Files table
        CREATE TABLE IF NOT EXISTS files (
            id TEXT PRIMARY KEY,
            collection_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            folder_path TEXT DEFAULT '',
            content TEXT,
            content_hash TEXT,
            source_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_size INTEGER DEFAULT 0,
            FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE,
            UNIQUE(collection_id, folder_path, filename)
        );
        
        -- Performance indexes
        CREATE INDEX IF NOT EXISTS idx_files_collection_id ON files(collection_id);
        CREATE INDEX IF NOT EXISTS idx_files_folder_path ON files(collection_id, folder_path);
        CREATE INDEX IF NOT EXISTS idx_files_filename ON files(collection_id, filename);
        CREATE INDEX IF NOT EXISTS idx_collections_name ON collections(name);
        CREATE INDEX IF NOT EXISTS idx_files_created_at ON files(created_at);
        CREATE INDEX IF NOT EXISTS idx_collections_created_at ON collections(created_at);
        """
        
        with self.get_connection() as conn:
            # Execute schema creation
            conn.executescript(schema_sql)
            
            # Check and set schema version
            current_version = conn.execute(
                "SELECT version FROM schema_version ORDER BY version DESC LIMIT 1"
            ).fetchone()
            
            if current_version is None:
                # Initial schema version
                conn.execute(
                    "INSERT INTO schema_version (version) VALUES (1)"
                )
                logger.info("Database schema initialized with version 1")
            else:
                logger.info(f"Database schema version: {current_version['version']}")
    
    def _optimize_database(self):
        """Apply performance optimizations to the database."""
        optimization_sql = """
        -- Enable optimizations for better performance
        PRAGMA synchronous = NORMAL;          -- Faster than FULL, still safe with WAL
        PRAGMA cache_size = 10000;            -- 10MB cache
        PRAGMA temp_store = MEMORY;           -- Store temporary tables in memory
        PRAGMA mmap_size = 268435456;         -- 256MB memory-mapped I/O
        PRAGMA optimize;                      -- Analyze tables for query optimization
        
        -- Additional indexes for common query patterns
        CREATE INDEX IF NOT EXISTS idx_files_content_hash ON files(content_hash);
        CREATE INDEX IF NOT EXISTS idx_files_updated_at ON files(updated_at);
        CREATE INDEX IF NOT EXISTS idx_collections_updated_at ON collections(updated_at);
        CREATE INDEX IF NOT EXISTS idx_files_folder_filename ON files(collection_id, folder_path, filename);
        """
        
        with self.get_connection() as conn:
            conn.executescript(optimization_sql)
            logger.info("Database performance optimizations applied")
    
    def get_schema_version(self) -> int:
        """Get current database schema version."""
        with self.get_connection() as conn:
            result = conn.execute(
                "SELECT version FROM schema_version ORDER BY version DESC LIMIT 1"
            ).fetchone()
            return result['version'] if result else 0
    
    def close(self):
        """Close database connections."""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None


class CollectionRepository:
    """Repository for collection database operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_collection(self, collection_id: str, name: str, description: str = "") -> Dict[str, Any]:
        """Create a new collection in the database."""
        try:
            with self.db.get_connection() as conn:
                conn.execute("""
                    INSERT INTO collections (id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    collection_id,
                    name, 
                    description,
                    datetime.now(timezone.utc).isoformat(),
                    datetime.now(timezone.utc).isoformat()
                ))
                
                return {
                    "success": True,
                    "collection_id": collection_id,
                    "message": f"Collection '{name}' created successfully"
                }
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                return {
                    "success": False,
                    "error": f"Collection with name '{name}' already exists",
                    "message": "Collection name must be unique"
                }
            raise
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create collection '{name}'"
            }
    
    def list_collections(self) -> Dict[str, Any]:
        """List all collections with metadata."""
        try:
            with self.db.get_connection() as conn:
                collections = conn.execute("""
                    SELECT id, name, description, created_at, file_count, total_size
                    FROM collections 
                    ORDER BY created_at DESC
                """).fetchall()
                
                collection_list = []
                for col in collections:
                    collection_list.append({
                        "id": col["id"],
                        "name": col["name"], 
                        "description": col["description"],
                        "created_at": col["created_at"],
                        "file_count": col["file_count"],
                        "total_size": col["total_size"]
                    })
                
                return {
                    "success": True,
                    "collections": collection_list
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to list collections"
            }
    
    def get_collection(self, collection_id: str) -> Dict[str, Any]:
        """Get collection details by ID."""
        try:
            with self.db.get_connection() as conn:
                collection = conn.execute("""
                    SELECT id, name, description, created_at, updated_at, file_count, total_size, metadata
                    FROM collections 
                    WHERE id = ?
                """, (collection_id,)).fetchone()
                
                if not collection:
                    return {
                        "success": False,
                        "error": f"Collection '{collection_id}' not found",
                        "message": "Collection does not exist"
                    }
                
                # Get folder list
                folders = conn.execute("""
                    SELECT DISTINCT folder_path 
                    FROM files 
                    WHERE collection_id = ? AND folder_path != ''
                    ORDER BY folder_path
                """, (collection_id,)).fetchall()
                
                folder_list = [row["folder_path"] for row in folders]
                
                return {
                    "success": True,
                    "collection": {
                        "id": collection["id"],
                        "name": collection["name"],
                        "description": collection["description"],
                        "created_at": collection["created_at"],
                        "updated_at": collection["updated_at"],
                        "file_count": collection["file_count"],
                        "total_size": collection["total_size"],
                        "folders": folder_list,
                        "metadata": collection["metadata"] or "{}"
                    }
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get collection '{collection_id}'"
            }
    
    def delete_collection(self, collection_id: str) -> Dict[str, Any]:
        """Delete a collection and all its files."""
        try:
            with self.db.get_connection() as conn:
                # Check if collection exists
                collection = conn.execute(
                    "SELECT name FROM collections WHERE id = ?", 
                    (collection_id,)
                ).fetchone()
                
                if not collection:
                    return {
                        "success": False,
                        "error": f"Collection '{collection_id}' not found",
                        "message": "Collection does not exist"
                    }
                
                # Delete collection (cascade will delete files)
                conn.execute("DELETE FROM collections WHERE id = ?", (collection_id,))
                
                return {
                    "success": True,
                    "message": f"Collection '{collection['name']}' deleted successfully"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to delete collection '{collection_id}'"
            }
    
    def update_collection_stats(self, collection_id: str):
        """Update collection file count and total size."""
        try:
            with self.db.get_connection() as conn:
                stats = conn.execute("""
                    SELECT COUNT(*) as file_count, COALESCE(SUM(file_size), 0) as total_size
                    FROM files 
                    WHERE collection_id = ?
                """, (collection_id,)).fetchone()
                
                conn.execute("""
                    UPDATE collections 
                    SET file_count = ?, total_size = ?, updated_at = ?
                    WHERE id = ?
                """, (
                    stats["file_count"],
                    stats["total_size"],
                    datetime.now(timezone.utc).isoformat(),
                    collection_id
                ))
        except Exception as e:
            logger.error(f"Failed to update collection stats for {collection_id}: {e}")


class FileRepository:
    """Repository for file database operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def save_file(self, file_id: str, collection_id: str, filename: str, 
                  content: str, folder_path: str = "", source_url: Optional[str] = None) -> Dict[str, Any]:
        """Save a file to the database."""
        try:
            # Calculate content hash and size
            content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            file_size = len(content.encode('utf-8'))
            
            with self.db.get_connection() as conn:
                # Check if collection exists
                collection_exists = conn.execute(
                    "SELECT 1 FROM collections WHERE id = ?", 
                    (collection_id,)
                ).fetchone()
                
                if not collection_exists:
                    return {
                        "success": False,
                        "error": f"Collection '{collection_id}' not found",
                        "message": "Cannot save file to non-existent collection"
                    }
                
                # Insert or replace file
                conn.execute("""
                    INSERT OR REPLACE INTO files 
                    (id, collection_id, filename, folder_path, content, content_hash, 
                     source_url, created_at, updated_at, file_size)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    file_id,
                    collection_id,
                    filename,
                    folder_path,
                    content,
                    content_hash,
                    source_url,
                    datetime.now(timezone.utc).isoformat(),
                    datetime.now(timezone.utc).isoformat(),
                    file_size
                ))
                
                return {
                    "success": True,
                    "file_id": file_id,
                    "content_hash": content_hash,
                    "file_size": file_size,
                    "message": f"File '{filename}' saved successfully"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to save file '{filename}'"
            }
    
    def read_file(self, collection_id: str, filename: str, folder_path: str = "") -> Dict[str, Any]:
        """Read a file from the database."""
        try:
            with self.db.get_connection() as conn:
                file_data = conn.execute("""
                    SELECT content, content_hash, file_size, created_at, updated_at, source_url
                    FROM files 
                    WHERE collection_id = ? AND filename = ? AND folder_path = ?
                """, (collection_id, filename, folder_path)).fetchone()
                
                if not file_data:
                    return {
                        "success": False,
                        "error": f"File '{filename}' not found in collection",
                        "message": "File does not exist"
                    }
                
                return {
                    "success": True,
                    "content": file_data["content"],
                    "metadata": {
                        "content_hash": file_data["content_hash"],
                        "file_size": file_data["file_size"],
                        "created_at": file_data["created_at"],
                        "updated_at": file_data["updated_at"],
                        "source_url": file_data["source_url"]
                    }
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to read file '{filename}'"
            }
    
    def list_files(self, collection_id: str) -> Dict[str, Any]:
        """List all files in a collection."""
        try:
            with self.db.get_connection() as conn:
                files = conn.execute("""
                    SELECT filename, folder_path, file_size, created_at, updated_at, source_url, content_hash
                    FROM files 
                    WHERE collection_id = ?
                    ORDER BY folder_path, filename
                """, (collection_id,)).fetchall()
                
                file_list = []
                for file_row in files:
                    file_list.append({
                        "filename": file_row["filename"],
                        "folder_path": file_row["folder_path"],
                        "file_size": file_row["file_size"],
                        "created_at": file_row["created_at"],
                        "updated_at": file_row["updated_at"],
                        "source_url": file_row["source_url"],
                        "content_hash": file_row["content_hash"]
                    })
                
                return {
                    "success": True,
                    "files": file_list
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to list files in collection '{collection_id}'"
            }
    
    def delete_file(self, collection_id: str, filename: str, folder_path: str = "") -> Dict[str, Any]:
        """Delete a file from a collection."""
        try:
            with self.db.get_connection() as conn:
                # Check if file exists
                file_exists = conn.execute("""
                    SELECT id FROM files 
                    WHERE collection_id = ? AND filename = ? AND folder_path = ?
                """, (collection_id, filename, folder_path)).fetchone()
                
                if not file_exists:
                    return {
                        "success": False,
                        "error": f"File '{filename}' not found in collection '{collection_id}'",
                        "message": "File does not exist"
                    }
                
                # Delete the file
                conn.execute("""
                    DELETE FROM files 
                    WHERE collection_id = ? AND filename = ? AND folder_path = ?
                """, (collection_id, filename, folder_path))
                
                return {
                    "success": True,
                    "message": f"File '{filename}' deleted successfully from collection '{collection_id}'"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to delete file '{filename}' from collection '{collection_id}'"
            }