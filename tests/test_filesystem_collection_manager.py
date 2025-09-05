"""
Tests for FilesystemCollectionManager.

Tests the filesystem-based collection management with SQLite metadata.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, AsyncMock
from tools.filesystem_collection_manager import FilesystemCollectionManager
from tools.filesystem_metadata_store import FilesystemMetadataStore


class TestFilesystemCollectionManager:
    """Test filesystem collection manager functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def manager(self, temp_dir):
        """Create test manager with temporary directory."""
        fs_base = temp_dir / "collections"
        fs_base.mkdir(parents=True, exist_ok=True)
        
        metadata_db = temp_dir / "metadata.db"
        
        return FilesystemCollectionManager(
            filesystem_base=fs_base,
            metadata_db_path=metadata_db,
            auto_reconcile=False  # Disable for controlled testing
        )
    
    def test_initialization(self, temp_dir):
        """Test manager initialization."""
        fs_base = temp_dir / "collections"
        metadata_db = temp_dir / "metadata.db"
        
        manager = FilesystemCollectionManager(fs_base, metadata_db)
        
        assert manager.fs_base == fs_base
        assert manager.metadata_db_path == metadata_db
        assert manager.auto_reconcile is True
        assert fs_base.exists()
        
    def test_validate_file_extension_valid(self, manager):
        """Test file extension validation for allowed extensions."""
        assert manager._validate_file_extension("test.md") is True
        assert manager._validate_file_extension("test.txt") is True
        assert manager._validate_file_extension("test.json") is True
        assert manager._validate_file_extension("test.yaml") is True
        assert manager._validate_file_extension("test.yml") is True
        assert manager._validate_file_extension("test.csv") is True
    
    def test_validate_file_extension_invalid(self, manager):
        """Test file extension validation rejects dangerous extensions."""
        assert manager._validate_file_extension("test.exe") is False
        assert manager._validate_file_extension("test.bat") is False
        assert manager._validate_file_extension("test.sh") is False
        assert manager._validate_file_extension("test.py") is False
        assert manager._validate_file_extension("test") is False
    
    def test_sanitize_collection_name_valid(self, manager):
        """Test collection name sanitization for valid names."""
        assert manager._sanitize_collection_name("test") == "test"
        assert manager._sanitize_collection_name("Test Collection") == "Test Collection"
        assert manager._sanitize_collection_name("  spaced  ") == "spaced"
    
    def test_sanitize_collection_name_dangerous_chars(self, manager):
        """Test collection name sanitization removes dangerous characters."""
        assert manager._sanitize_collection_name("with/slash") == "with_slash"
        assert manager._sanitize_collection_name("with\\backslash") == "with_backslash"
        assert manager._sanitize_collection_name("with..dots") == "with__dots"
        assert manager._sanitize_collection_name("with:colon") == "with_colon"

    def test_sanitize_collection_name_empty(self, manager):
        """Test collection name sanitization raises error for empty names."""
        with pytest.raises(ValueError, match="Collection name cannot be empty"):
            manager._sanitize_collection_name("")
        
        with pytest.raises(ValueError, match="Collection name cannot be empty"):
            manager._sanitize_collection_name("   ")

    def test_sanitize_collection_name_long(self, manager):
        """Test collection name truncation for long names."""
        long_name = "a" * 150
        result = manager._sanitize_collection_name(long_name)
        assert len(result) == 100
        assert result == "a" * 100
    
    def test_sanitize_folder_path(self, manager):
        """Test folder path sanitization."""
        assert manager._sanitize_folder_path("") == ""
        assert manager._sanitize_folder_path("folder") == "folder"
        assert manager._sanitize_folder_path("folder/subfolder") == "folder/subfolder"
        assert manager._sanitize_folder_path("/folder/") == "folder"
        assert manager._sanitize_folder_path("../danger") == "danger"
        assert manager._sanitize_folder_path("folder\\with\\backslash") == "folder/with/backslash"

    @patch.object(FilesystemCollectionManager, '_sanitize_collection_name')
    @pytest.mark.asyncio
    async def test_create_collection_success(self, mock_sanitize, manager):
        """Test successful collection creation."""
        mock_sanitize.return_value = "test_collection"
        
        # Mock metadata store
        manager.metadata_store.create_collection = AsyncMock(return_value={
            "success": True,
            "name": "test_collection"
        })
        
        result = await manager.create_collection("test collection", "Test description")
        
        assert result["success"] is True
        assert result["name"] == "test_collection"
        
        # Check filesystem directory was created
        collection_path = manager.fs_base / "test_collection"
        assert collection_path.exists()
        assert collection_path.is_dir()

    @pytest.mark.asyncio
    async def test_list_collections(self, manager):
        """Test collection listing."""
        # Mock metadata store
        manager.metadata_store.list_collections = AsyncMock(return_value={
            "success": True,
            "collections": [
                {
                    "name": "collection1",
                    "description": "First collection", 
                    "file_count": 5
                },
                {
                    "name": "collection2", 
                    "description": "Second collection",
                    "file_count": 3
                }
            ]
        })
        
        result = await manager.list_collections()
        
        assert result["success"] is True
        assert len(result["collections"]) == 2
        assert result["total"] == 2
        
        # Check filesystem paths are added
        for collection in result["collections"]:
            assert "path" in collection