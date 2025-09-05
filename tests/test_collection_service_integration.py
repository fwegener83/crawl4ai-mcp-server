"""
Integration tests for CollectionService with configurable storage.

Tests the end-to-end integration of the factory pattern, configuration system,
and service layer for both SQLite and filesystem storage modes.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch

from services.collection_service import CollectionService


class TestCollectionServiceIntegration:
    """Test CollectionService integration with configurable storage."""

    def setup_method(self):
        """Setup method to clear any existing collection service instances."""
        # Clear environment variables to ensure clean test state
        self.original_env = {}
        env_vars = [
            "COLLECTION_STORAGE_MODE", 
            "FILESYSTEM_COLLECTIONS_PATH",
            "FILESYSTEM_METADATA_DB_PATH", 
            "FILESYSTEM_AUTO_RECONCILE",
            "CONTEXT42_HOME",
            "COLLECTIONS_DB_PATH"
        ]
        
        for var in env_vars:
            self.original_env[var] = os.environ.get(var)
            if var in os.environ:
                del os.environ[var]

    def teardown_method(self):
        """Restore original environment variables."""
        for var, value in self.original_env.items():
            if value is not None:
                os.environ[var] = value
            elif var in os.environ:
                del os.environ[var]

    def test_service_initialization_sqlite_mode(self):
        """Test service initialization in SQLite mode (default)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set up SQLite mode configuration
            os.environ["COLLECTION_STORAGE_MODE"] = "sqlite"
            os.environ["CONTEXT42_HOME"] = temp_dir
            
            # Initialize service
            service = CollectionService()
            
            # Verify service was created successfully
            assert service.collection_manager is not None
            
            # Check that the expected database path exists in temp directory
            expected_db = Path(temp_dir) / "databases" / "vector_sync.db"
            assert expected_db.parent.exists()  # Parent directory should be created

    def test_service_initialization_filesystem_mode(self):
        """Test service initialization in filesystem mode."""
        with tempfile.TemporaryDirectory() as temp_dir:
            collections_path = Path(temp_dir) / "collections"
            metadata_db_path = Path(temp_dir) / "metadata.db"
            
            # Set up filesystem mode configuration
            os.environ["COLLECTION_STORAGE_MODE"] = "filesystem"
            os.environ["FILESYSTEM_COLLECTIONS_PATH"] = str(collections_path)
            os.environ["FILESYSTEM_METADATA_DB_PATH"] = str(metadata_db_path)
            os.environ["FILESYSTEM_AUTO_RECONCILE"] = "true"
            
            # Initialize service
            service = CollectionService()
            
            # Verify service was created successfully
            assert service.collection_manager is not None
            
            # Check that the expected directories were created
            assert collections_path.exists()
            assert metadata_db_path.parent.exists()

    def test_service_initialization_invalid_mode(self):
        """Test service initialization with invalid storage mode."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set up invalid mode configuration
            os.environ["COLLECTION_STORAGE_MODE"] = "invalid_mode"
            os.environ["CONTEXT42_HOME"] = temp_dir
            
            # Should fall back to SQLite mode with warning
            service = CollectionService()
            
            # Verify service was created successfully (fallback behavior)
            assert service.collection_manager is not None

    def test_service_initialization_missing_filesystem_config(self):
        """Test service initialization with incomplete filesystem configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set up filesystem mode configuration with invalid path that will fail validation
            os.environ["COLLECTION_STORAGE_MODE"] = "filesystem"
            os.environ["FILESYSTEM_COLLECTIONS_PATH"] = "/nonexistent/readonly/path"
            os.environ["FILESYSTEM_METADATA_DB_PATH"] = "/nonexistent/readonly/metadata.db"
            
            # Should raise ValueError due to path validation failure
            with pytest.raises(ValueError, match="Invalid collection storage configuration"):
                CollectionService()

    def test_storage_mode_env_var_precedence(self):
        """Test that environment variables take precedence over defaults."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_collections_path = Path(temp_dir) / "custom_collections"
            custom_metadata_path = Path(temp_dir) / "custom_metadata.db"
            
            # Set custom paths via environment variables
            os.environ["COLLECTION_STORAGE_MODE"] = "filesystem"
            os.environ["FILESYSTEM_COLLECTIONS_PATH"] = str(custom_collections_path)
            os.environ["FILESYSTEM_METADATA_DB_PATH"] = str(custom_metadata_path)
            os.environ["FILESYSTEM_AUTO_RECONCILE"] = "false"
            
            # Initialize service
            service = CollectionService()
            
            # Verify custom paths were used
            assert custom_collections_path.exists()
            assert custom_metadata_path.parent.exists()

    def test_configuration_validation_integration(self):
        """Test that configuration validation is properly integrated."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set up configuration that would fail path validation
            os.environ["COLLECTION_STORAGE_MODE"] = "filesystem"
            os.environ["FILESYSTEM_COLLECTIONS_PATH"] = "/nonexistent/readonly/path"
            os.environ["FILESYSTEM_METADATA_DB_PATH"] = "/nonexistent/readonly/metadata.db"
            
            # Should raise ValueError due to path validation failure
            with pytest.raises(ValueError, match="Invalid collection storage configuration"):
                CollectionService()

    @patch('config.paths.Context42Config.ensure_directory_structure')
    @patch('config.paths.Context42Config.migrate_legacy_data')
    def test_directory_structure_and_migration_called(self, mock_migrate, mock_ensure):
        """Test that directory structure setup and migration are called during initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ["COLLECTION_STORAGE_MODE"] = "sqlite"
            os.environ["COLLECTIONS_DB_PATH"] = str(Path(temp_dir) / "test.db")
            
            # Initialize service
            CollectionService()
            
            # Verify setup methods were called
            mock_ensure.assert_called_once()
            mock_migrate.assert_called_once()

    @pytest.mark.asyncio
    async def test_basic_collection_operations_sqlite(self):
        """Test basic collection operations work with SQLite storage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ["COLLECTION_STORAGE_MODE"] = "sqlite"
            os.environ["COLLECTIONS_DB_PATH"] = str(Path(temp_dir) / "test.db")
            
            service = CollectionService()
            
            # Test list collections (should work without errors)
            collections = await service.list_collections()
            assert isinstance(collections, list)

    @pytest.mark.asyncio
    async def test_basic_collection_operations_filesystem(self):
        """Test basic collection operations work with filesystem storage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            collections_path = Path(temp_dir) / "collections"
            metadata_db_path = Path(temp_dir) / "metadata.db"
            
            os.environ["COLLECTION_STORAGE_MODE"] = "filesystem"
            os.environ["FILESYSTEM_COLLECTIONS_PATH"] = str(collections_path)
            os.environ["FILESYSTEM_METADATA_DB_PATH"] = str(metadata_db_path)
            
            service = CollectionService()
            
            # Test list collections (should work without errors)
            collections = await service.list_collections()
            assert isinstance(collections, list)

    def test_error_handling_storage_creation_failure(self):
        """Test error handling when storage manager creation fails."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ["COLLECTION_STORAGE_MODE"] = "sqlite"
            os.environ["COLLECTIONS_DB_PATH"] = "/invalid/readonly/path/db.sqlite"
            
            # Should raise exception due to storage creation failure
            with pytest.raises(Exception):
                CollectionService()