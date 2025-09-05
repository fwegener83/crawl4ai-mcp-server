"""
Centralized path configuration for Crawl4AI MCP Server.

Implements ~/.context42/ user directory pattern with intelligent fallback strategies
for professional data organization and multi-context deployment support.
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Optional, Union

logger = logging.getLogger(__name__)


class Context42Config:
    """
    Centralized configuration manager for ~/.context42/ user directory.
    
    Features:
    - Professional user directory organization (~/.context42/)
    - Environment variable override support  
    - Automatic directory structure creation
    - Data migration from legacy locations
    - Multi-context deployment support (tests, development, MCP)
    """
    
    # Default directory structure
    DEFAULT_BASE_NAME = ".context42"
    DATABASES_DIR = "databases"
    CONFIG_DIR = "config"
    LOGS_DIR = "logs" 
    CACHE_DIR = "cache"
    
    # Database filenames
    COLLECTIONS_DB_NAME = "vector_sync.db"
    CHROMADB_DIR_NAME = "chromadb"
    
    @classmethod
    def get_base_dir(cls) -> Path:
        """
        Get the base ~/.context42/ directory path.
        
        Priority order:
        1. CONTEXT42_HOME environment variable
        2. ~/.context42/ (standard user directory)
        3. ./context42/ (fallback for restricted environments)
        
        Returns:
            Path: Absolute path to context42 base directory
        """
        # Check environment variable override
        env_path = os.getenv("CONTEXT42_HOME")
        if env_path:
            return Path(env_path).expanduser().resolve()
        
        # Standard user directory
        user_home = Path.home()
        base_dir = user_home / cls.DEFAULT_BASE_NAME
        
        # Check if we can write to user home directory
        if cls._can_create_directory(base_dir):
            return base_dir
        
        # Fallback to current directory for restricted environments
        fallback_dir = Path.cwd() / cls.DEFAULT_BASE_NAME
        logger.warning(
            f"Cannot create {base_dir} (permissions). Using fallback: {fallback_dir}"
        )
        return fallback_dir
    
    @classmethod
    def get_databases_dir(cls) -> Path:
        """Get the databases directory path."""
        return cls.get_base_dir() / cls.DATABASES_DIR
    
    @classmethod
    def get_config_dir(cls) -> Path:
        """Get the config directory path."""
        return cls.get_base_dir() / cls.CONFIG_DIR
        
    @classmethod
    def get_logs_dir(cls) -> Path:
        """Get the logs directory path."""
        return cls.get_base_dir() / cls.LOGS_DIR
        
    @classmethod
    def get_cache_dir(cls) -> Path:
        """Get the cache directory path."""
        return cls.get_base_dir() / cls.CACHE_DIR
    
    @classmethod  
    def get_collections_db_path(cls) -> Path:
        """
        Get the SQLite database path for collections and sync status.
        
        Priority order:
        1. COLLECTIONS_DB_PATH environment variable  
        2. ~/.context42/databases/vector_sync.db
        3. Legacy fallback handling
        
        Returns:
            Path: Absolute path to collections database
        """
        # Check environment variable override
        env_path = os.getenv("COLLECTIONS_DB_PATH")
        if env_path:
            return Path(env_path).expanduser().resolve()
        
        # Standard path in context42 structure
        return cls.get_databases_dir() / cls.COLLECTIONS_DB_NAME
    
    @classmethod
    def get_vector_db_path(cls) -> Path:
        """
        Get the ChromaDB vector database directory path.
        
        Priority order:
        1. VECTOR_DB_PATH environment variable
        2. RAG_DB_PATH environment variable (legacy compatibility)  
        3. ~/.context42/databases/chromadb/
        4. Legacy ./rag_db fallback
        
        Returns:
            Path: Absolute path to vector database directory
        """
        # Check new environment variable
        env_path = os.getenv("VECTOR_DB_PATH")
        if env_path:
            return Path(env_path).expanduser().resolve()
            
        # Check legacy environment variable for backward compatibility
        legacy_env_path = os.getenv("RAG_DB_PATH")
        if legacy_env_path:
            return Path(legacy_env_path).expanduser().resolve()
        
        # Standard path in context42 structure
        return cls.get_databases_dir() / cls.CHROMADB_DIR_NAME
    
    @classmethod
    def get_collection_storage_config(cls) -> dict:
        """
        Get collection storage configuration based on environment variables.
        
        Returns:
            dict: Storage configuration for CollectionStorageFactory
        """
        storage_mode = os.getenv("COLLECTION_STORAGE_MODE", "sqlite").lower()
        
        if storage_mode == "sqlite":
            return {
                "storage_mode": "sqlite",
                "database_path": str(cls.get_collections_db_path())
            }
        elif storage_mode == "filesystem":
            filesystem_path = os.getenv("FILESYSTEM_COLLECTIONS_PATH", "~/.context42/collections")
            metadata_db_path = os.getenv("FILESYSTEM_METADATA_DB_PATH", "~/.context42/databases/filesystem_metadata.db")
            auto_reconcile = os.getenv("FILESYSTEM_AUTO_RECONCILE", "true").lower() == "true"
            
            return {
                "storage_mode": "filesystem",
                "filesystem_path": str(Path(filesystem_path).expanduser().resolve()),
                "metadata_db_path": str(Path(metadata_db_path).expanduser().resolve()),
                "auto_reconcile": auto_reconcile
            }
        else:
            logger.warning(f"Unknown collection storage mode: {storage_mode}, falling back to sqlite")
            return {
                "storage_mode": "sqlite",
                "database_path": str(cls.get_collections_db_path())
            }
    
    @classmethod
    def ensure_directory_structure(cls) -> None:
        """
        Create the complete ~/.context42/ directory structure.
        
        Creates all required directories with proper permissions.
        Safe to call multiple times (idempotent).
        """
        base_dir = cls.get_base_dir()
        
        directories = [
            base_dir,
            cls.get_databases_dir(),
            cls.get_config_dir(), 
            cls.get_logs_dir(),
            cls.get_cache_dir(),
        ]
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Ensured directory exists: {directory}")
            except OSError as e:
                logger.error(f"Failed to create directory {directory}: {e}")
                raise
        
        logger.info(f"Context42 directory structure ensured at: {base_dir}")
    
    @classmethod
    def migrate_legacy_data(cls) -> None:
        """
        Migrate existing data from legacy locations to ~/.context42/.
        
        Handles:
        - vector_sync.db from current directory  
        - rag_db/ directory migration
        - Creates symlinks for backward compatibility (optional)
        
        Safe to call multiple times (idempotent).
        """
        cls.ensure_directory_structure()
        
        # Migrate SQLite database
        legacy_db = Path("vector_sync.db")
        new_db_path = cls.get_collections_db_path()
        
        if legacy_db.exists() and not new_db_path.exists():
            logger.info(f"Migrating database: {legacy_db} -> {new_db_path}")
            try:
                # Ensure target directory exists
                new_db_path.parent.mkdir(parents=True, exist_ok=True)
                # Move database file
                shutil.move(str(legacy_db), str(new_db_path))
                logger.info("Database migration completed successfully")
            except Exception as e:
                logger.error(f"Database migration failed: {e}")
                # Copy as fallback
                try:
                    shutil.copy2(str(legacy_db), str(new_db_path))
                    logger.info("Database copied as fallback (original preserved)")
                except Exception as copy_error:
                    logger.error(f"Database copy fallback failed: {copy_error}")
        
        # Migrate ChromaDB directory
        legacy_vector_db = Path("rag_db")
        new_vector_db_path = cls.get_vector_db_path()
        
        if legacy_vector_db.exists() and legacy_vector_db.is_dir() and not new_vector_db_path.exists():
            logger.info(f"Migrating vector database: {legacy_vector_db} -> {new_vector_db_path}")
            try:
                # Ensure target parent directory exists
                new_vector_db_path.parent.mkdir(parents=True, exist_ok=True)
                # Move directory
                shutil.move(str(legacy_vector_db), str(new_vector_db_path))
                logger.info("Vector database migration completed successfully")
            except Exception as e:
                logger.error(f"Vector database migration failed: {e}")
    
    @classmethod
    def _can_create_directory(cls, path: Path) -> bool:
        """
        Check if we can create a directory at the given path.
        
        Args:
            path: Path to test
            
        Returns:
            bool: True if directory can be created/accessed
        """
        try:
            # Try to create the directory
            path.mkdir(parents=True, exist_ok=True)
            # Test write access by creating a temporary file
            test_file = path / ".write_test"
            test_file.touch()
            test_file.unlink()  # Clean up
            return True
        except (OSError, PermissionError):
            return False
    
    @classmethod
    def get_runtime_info(cls) -> dict:
        """
        Get runtime configuration information for debugging.
        
        Returns:
            dict: Configuration paths and status information
        """
        return {
            "base_dir": str(cls.get_base_dir()),
            "collections_db_path": str(cls.get_collections_db_path()),
            "vector_db_path": str(cls.get_vector_db_path()),
            "collections_db_exists": cls.get_collections_db_path().exists(),
            "vector_db_exists": cls.get_vector_db_path().exists(),
            "base_dir_writable": cls._can_create_directory(cls.get_base_dir() / "test_write"),
            "collection_storage_config": cls.get_collection_storage_config(),
            "env_overrides": {
                "CONTEXT42_HOME": os.getenv("CONTEXT42_HOME"),
                "COLLECTIONS_DB_PATH": os.getenv("COLLECTIONS_DB_PATH"), 
                "VECTOR_DB_PATH": os.getenv("VECTOR_DB_PATH"),
                "RAG_DB_PATH": os.getenv("RAG_DB_PATH"),  # Legacy
                "COLLECTION_STORAGE_MODE": os.getenv("COLLECTION_STORAGE_MODE"),
                "FILESYSTEM_COLLECTIONS_PATH": os.getenv("FILESYSTEM_COLLECTIONS_PATH"),
                "FILESYSTEM_METADATA_DB_PATH": os.getenv("FILESYSTEM_METADATA_DB_PATH"),
                "FILESYSTEM_AUTO_RECONCILE": os.getenv("FILESYSTEM_AUTO_RECONCILE"),
            }
        }