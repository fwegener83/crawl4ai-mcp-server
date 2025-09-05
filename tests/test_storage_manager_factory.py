"""
Unit tests for CollectionStorageFactory.

Tests the factory pattern for creating appropriate collection managers
based on configuration for both SQLite and Filesystem storage modes.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from tools.storage_manager_factory import CollectionStorageFactory


class TestCollectionStorageFactory:
    """Test CollectionStorageFactory functionality."""
    
    def test_get_supported_modes(self):
        """Test getting list of supported storage modes."""
        modes = CollectionStorageFactory.get_supported_modes()
        assert "sqlite" in modes
        assert "filesystem" in modes
        assert len(modes) == 2
    
    def test_validate_config_sqlite_valid(self):
        """Test validation of valid SQLite configuration."""
        config = {
            "storage_mode": "sqlite",
            "database_path": "/tmp/test.db"
        }
        
        result = CollectionStorageFactory.validate_config(config)
        assert result["success"] is True
        assert result["storage_mode"] == "sqlite"
    
    def test_validate_config_sqlite_missing_path(self):
        """Test validation of SQLite configuration missing database path."""
        config = {
            "storage_mode": "sqlite"
        }
        
        result = CollectionStorageFactory.validate_config(config)
        assert result["success"] is False
        assert "database_path" in result["error"]
    
    def test_validate_config_filesystem_valid(self):
        """Test validation of valid filesystem configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "storage_mode": "filesystem",
                "filesystem_path": temp_dir,
                "metadata_db_path": f"{temp_dir}/metadata.db"
            }
            
            result = CollectionStorageFactory.validate_config(config)
            assert result["success"] is True
            assert result["storage_mode"] == "filesystem"
    
    def test_validate_config_filesystem_missing_paths(self):
        """Test validation of filesystem configuration with missing paths."""
        config = {
            "storage_mode": "filesystem",
            "filesystem_path": "/tmp/collections"
            # Missing metadata_db_path
        }
        
        result = CollectionStorageFactory.validate_config(config)
        assert result["success"] is False
        assert "metadata_db_path" in result["error"]
    
    def test_validate_config_unsupported_mode(self):
        """Test validation of unsupported storage mode."""
        config = {
            "storage_mode": "unsupported_mode"
        }
        
        result = CollectionStorageFactory.validate_config(config)
        assert result["success"] is False
        assert "Unsupported storage mode" in result["error"]
        assert "supported_modes" in result
    
    @patch('tools.knowledge_base.database_collection_adapter.DatabaseCollectionAdapter')
    def test_create_sqlite_manager(self, mock_adapter):
        """Test creating SQLite collection manager."""
        config = {
            "storage_mode": "sqlite",
            "database_path": "/tmp/test.db"
        }
        
        mock_instance = MagicMock()
        mock_adapter.return_value = mock_instance
        
        manager = CollectionStorageFactory.create_manager(config)
        
        assert manager is mock_instance
        mock_adapter.assert_called_once_with("/tmp/test.db")
    
    @patch('tools.filesystem_collection_manager.FilesystemCollectionManager')
    def test_create_filesystem_manager(self, mock_manager):
        """Test creating filesystem collection manager."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "storage_mode": "filesystem",
                "filesystem_path": temp_dir,
                "metadata_db_path": f"{temp_dir}/metadata.db",
                "auto_reconcile": True
            }
            
            mock_instance = MagicMock()
            mock_manager.return_value = mock_instance
            
            manager = CollectionStorageFactory.create_manager(config)
            
            assert manager is mock_instance
            mock_manager.assert_called_once()
            
            # Check arguments passed to FilesystemCollectionManager
            call_args = mock_manager.call_args
            assert call_args.kwargs["filesystem_base"] == Path(temp_dir)
            assert call_args.kwargs["metadata_db_path"] == Path(f"{temp_dir}/metadata.db")
            assert call_args.kwargs["auto_reconcile"] is True
    
    def test_create_manager_unsupported_mode(self):
        """Test creating manager with unsupported mode raises ValueError."""
        config = {
            "storage_mode": "unsupported",
            "database_path": "/tmp/test.db"
        }
        
        with pytest.raises(ValueError, match="Unsupported storage mode"):
            CollectionStorageFactory.create_manager(config)
    
    def test_create_sqlite_manager_missing_path(self):
        """Test creating SQLite manager without database_path raises ValueError.""" 
        config = {
            "storage_mode": "sqlite"
        }
        
        with pytest.raises(ValueError, match="database_path"):
            CollectionStorageFactory.create_manager(config)
    
    def test_create_filesystem_manager_missing_paths(self):
        """Test creating filesystem manager without required paths raises ValueError."""
        config = {
            "storage_mode": "filesystem",
            "filesystem_path": "/tmp/collections"
            # Missing metadata_db_path
        }
        
        with pytest.raises(ValueError, match="metadata_db_path"):
            CollectionStorageFactory.create_manager(config)
    
    @patch('tools.knowledge_base.database_collection_adapter.DatabaseCollectionAdapter')
    def test_create_sqlite_manager_import_error(self, mock_adapter):
        """Test handling of import error for SQLite manager."""
        config = {
            "storage_mode": "sqlite", 
            "database_path": "/tmp/test.db"
        }
        
        mock_adapter.side_effect = ImportError("Missing dependency")
        
        with pytest.raises(ImportError, match="SQLite collection manager dependencies missing"):
            CollectionStorageFactory.create_manager(config)
    
    @patch('tools.filesystem_collection_manager.FilesystemCollectionManager')
    def test_create_filesystem_manager_import_error(self, mock_manager):
        """Test handling of import error for filesystem manager."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "storage_mode": "filesystem",
                "filesystem_path": temp_dir,
                "metadata_db_path": f"{temp_dir}/metadata.db"
            }
            
            mock_manager.side_effect = ImportError("Missing dependency")
            
            with pytest.raises(ImportError, match="Filesystem collection manager dependencies missing"):
                CollectionStorageFactory.create_manager(config)
    
    def test_validate_config_filesystem_invalid_path(self):
        """Test validation fails for inaccessible filesystem paths."""
        config = {
            "storage_mode": "filesystem",
            "filesystem_path": "/nonexistent/path/that/cannot/be/created",
            "metadata_db_path": "/nonexistent/path/metadata.db"
        }
        
        result = CollectionStorageFactory.validate_config(config)
        assert result["success"] is False
        assert "Path validation failed" in result["error"]