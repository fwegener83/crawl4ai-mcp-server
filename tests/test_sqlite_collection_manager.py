"""
Tests for SQLite Collection Manager API Compatibility.
Ensures SQLite-based manager provides identical API to file-based version.
"""
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch

from tools.sqlite_collection_manager import SQLiteCollectionFileManager, create_collection_manager
from tools.collection_manager import CollectionFileManager


class TestSQLiteCollectionManagerCompatibility:
    """Test SQLite manager provides identical API to file-based manager."""
    
    @pytest.fixture
    def sqlite_manager(self):
        """Create SQLite collection manager for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = SQLiteCollectionFileManager(Path(temp_dir))
            yield manager
            manager.close()
    
    @pytest.fixture
    def file_manager(self):
        """Create file-based collection manager for comparison."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield CollectionFileManager(Path(temp_dir))
    
    def test_create_collection_api_compatibility(self, sqlite_manager, file_manager):
        """Test create_collection returns identical API format."""
        collection_name = "Test Collection"
        description = "Test Description"
        
        # Test both managers
        sqlite_result = sqlite_manager.create_collection(collection_name, description)
        file_result = file_manager.create_collection(collection_name, description)
        
        # Both should succeed
        assert sqlite_result["success"] is True
        assert file_result["success"] is True
        
        # Check response structure
        assert "message" in sqlite_result
        assert "path" in sqlite_result
        assert "message" in file_result
        assert "path" in file_result
        
        # Messages should be similar format
        assert "created successfully" in sqlite_result["message"]
        assert "created successfully" in file_result["message"]
    
    def test_create_collection_duplicate_name_handling(self, sqlite_manager):
        """Test duplicate collection name handling."""
        collection_name = "Duplicate Collection"
        
        # Create first collection
        result1 = sqlite_manager.create_collection(collection_name)
        assert result1["success"] is True
        
        # Try to create duplicate
        result2 = sqlite_manager.create_collection(collection_name)
        assert result2["success"] is False
        assert "already exists" in result2["error"] or "UNIQUE constraint" in result2["error"]
    
    def test_list_collections_api_compatibility(self, sqlite_manager, file_manager):
        """Test list_collections returns identical API format."""
        # Create test collections in both
        sqlite_manager.create_collection("Collection 1", "Description 1")
        sqlite_manager.create_collection("Collection 2", "Description 2")
        
        file_manager.create_collection("Collection 1", "Description 1") 
        file_manager.create_collection("Collection 2", "Description 2")
        
        # List collections
        sqlite_result = sqlite_manager.list_collections()
        file_result = file_manager.list_collections()
        
        # Both should succeed
        assert sqlite_result["success"] is True
        assert file_result["success"] is True
        
        # Check structure
        assert "collections" in sqlite_result
        assert "collections" in file_result
        assert len(sqlite_result["collections"]) == 2
        assert len(file_result["collections"]) == 2
        
        # Check collection metadata structure
        sqlite_collection = sqlite_result["collections"][0]
        file_collection = file_result["collections"][0]
        
        required_fields = ["name", "description", "created_at", "file_count"]
        for field in required_fields:
            assert field in sqlite_collection
            assert field in file_collection
    
    def test_save_file_api_compatibility(self, sqlite_manager, file_manager):
        """Test save_file returns identical API format."""
        # Create collections first
        collection_name = "Test Collection"
        sqlite_manager.create_collection(collection_name)
        file_manager.create_collection(collection_name)
        
        # Save files
        filename = "test.md"
        content = "# Test Content"
        folder = "docs"
        
        sqlite_result = sqlite_manager.save_file(collection_name, filename, content, folder)
        file_result = file_manager.save_file(collection_name, filename, content, folder)
        
        # Both should succeed
        assert sqlite_result["success"] is True
        assert file_result["success"] is True
        
        # Check response structure
        assert "message" in sqlite_result
        assert "path" in sqlite_result
        assert "content_hash" in sqlite_result
        assert "message" in file_result
        assert "path" in file_result
        # Note: file manager might not return content_hash, but sqlite does for compatibility
    
    def test_save_file_invalid_extension(self, sqlite_manager):
        """Test file extension validation."""
        collection_name = "Test Collection"
        sqlite_manager.create_collection(collection_name)
        
        # Try to save file with invalid extension
        result = sqlite_manager.save_file(collection_name, "test.exe", "content")
        
        assert result["success"] is False
        assert "File extension not allowed" in result["error"]
        assert ".md" in result["error"]  # Should mention allowed extensions
    
    def test_read_file_api_compatibility(self, sqlite_manager, file_manager):
        """Test read_file returns identical API format."""
        # Create collections and save files
        collection_name = "Test Collection"
        filename = "test.md"
        content = "# Test Content"
        
        sqlite_manager.create_collection(collection_name)
        file_manager.create_collection(collection_name)
        
        sqlite_manager.save_file(collection_name, filename, content)
        file_manager.save_file(collection_name, filename, content)
        
        # Read files
        sqlite_result = sqlite_manager.read_file(collection_name, filename)
        file_result = file_manager.read_file(collection_name, filename)
        
        # Both should succeed
        assert sqlite_result["success"] is True
        assert file_result["success"] is True
        
        # Content should match
        assert sqlite_result["content"] == content
        assert file_result["content"] == content
        
        # Check response structure - SQLite has enhanced metadata, file manager has basic path
        assert "metadata" in sqlite_result  # SQLite provides enhanced metadata
        assert "path" in file_result  # File manager provides path
        
        # SQLite should have enhanced metadata
        assert "size" in sqlite_result["metadata"] or "file_size" in sqlite_result["metadata"]
        assert "created_at" in sqlite_result["metadata"]
    
    def test_read_file_with_folder_path(self, sqlite_manager):
        """Test reading file with folder path."""
        collection_name = "Test Collection"
        filename = "test.md"
        content = "# Test Content"
        folder = "docs/subfolder"
        
        sqlite_manager.create_collection(collection_name)
        sqlite_manager.save_file(collection_name, filename, content, folder)
        
        # Read with correct folder
        result = sqlite_manager.read_file(collection_name, filename, folder)
        assert result["success"] is True
        assert result["content"] == content
        
        # Read with wrong folder should fail
        result = sqlite_manager.read_file(collection_name, filename, "wrong-folder")
        assert result["success"] is False
    
    def test_get_collection_info_api_compatibility(self, sqlite_manager, file_manager):
        """Test get_collection_info returns identical API format."""
        collection_name = "Test Collection"
        description = "Test Description"
        
        # Create collections
        sqlite_manager.create_collection(collection_name, description)
        file_manager.create_collection(collection_name, description)
        
        # Add a file to update statistics
        sqlite_manager.save_file(collection_name, "test.md", "content")
        file_manager.save_file(collection_name, "test.md", "content")
        
        # Get collection info
        sqlite_result = sqlite_manager.get_collection_info(collection_name)
        file_result = file_manager.get_collection_info(collection_name)
        
        # Both should succeed
        assert sqlite_result["success"] is True
        assert file_result["success"] is True
        
        # Check structure
        assert "collection" in sqlite_result
        assert "collection" in file_result
        
        sqlite_collection = sqlite_result["collection"]
        file_collection = file_result["collection"]
        
        # Check required fields
        required_fields = ["name", "description", "created_at", "file_count"]
        for field in required_fields:
            assert field in sqlite_collection
            assert field in file_collection
        
        # File count should be updated
        assert sqlite_collection["file_count"] > 0
        assert file_collection["file_count"] > 0
    
    def test_delete_collection_api_compatibility(self, sqlite_manager, file_manager):
        """Test delete_collection returns identical API format."""
        collection_name = "Test Collection"
        
        # Create collections
        sqlite_manager.create_collection(collection_name)
        file_manager.create_collection(collection_name)
        
        # Delete collections
        sqlite_result = sqlite_manager.delete_collection(collection_name)
        file_result = file_manager.delete_collection(collection_name)
        
        # Both should succeed
        assert sqlite_result["success"] is True
        assert file_result["success"] is True
        
        # Check message format
        assert "message" in sqlite_result
        assert "message" in file_result
        assert "deleted successfully" in sqlite_result["message"]
        assert "deleted successfully" in file_result["message"]
        
        # Collections should be gone
        get_sqlite = sqlite_manager.get_collection_info(collection_name)
        get_file = file_manager.get_collection_info(collection_name)
        
        assert get_sqlite["success"] is False
        assert get_file["success"] is False
    
    def test_list_files_in_collection_api_compatibility(self, sqlite_manager):
        """Test list_files_in_collection returns proper structure."""
        collection_name = "Test Collection"
        sqlite_manager.create_collection(collection_name)
        
        # Add files in different folders
        sqlite_manager.save_file(collection_name, "root.md", "Root content")
        sqlite_manager.save_file(collection_name, "doc1.md", "Doc content", "docs")
        sqlite_manager.save_file(collection_name, "doc2.txt", "Doc2 content", "docs")
        sqlite_manager.save_file(collection_name, "sub.json", "Sub content", "docs/sub")
        
        # List files
        result = sqlite_manager.list_files_in_collection(collection_name)
        
        assert result["success"] is True
        assert "files" in result
        assert "folders" in result
        assert "total_files" in result
        assert "total_folders" in result
        
        # Check we have the right number of files and folders
        assert result["total_files"] == 4
        assert result["total_folders"] > 0  # Should have at least "docs" folder
        
        # Check file structure
        files = result["files"]
        assert len(files) == 4
        
        # Find root file
        root_files = [f for f in files if f["folder"] == ""]
        assert len(root_files) == 1
        assert root_files[0]["name"] == "root.md"
        
        # Check required file fields
        for file_item in files:
            assert "name" in file_item
            assert "path" in file_item
            assert "type" in file_item
            assert file_item["type"] == "file"
            assert "size" in file_item
            assert "folder" in file_item
    
    def test_file_extension_validation_consistency(self, sqlite_manager):
        """Test file extension validation matches original."""
        collection_name = "Test Collection"
        sqlite_manager.create_collection(collection_name)
        
        # Valid extensions should work
        valid_files = ["test.md", "test.txt", "test.json"]
        for filename in valid_files:
            result = sqlite_manager.save_file(collection_name, filename, "content")
            assert result["success"] is True, f"Failed for {filename}"
        
        # Invalid extensions should fail
        invalid_files = ["test.exe", "test.py", "test.html", "test.pdf"]
        for filename in invalid_files:
            result = sqlite_manager.save_file(collection_name, filename, "content")
            assert result["success"] is False, f"Should have failed for {filename}"
            assert "File extension not allowed" in result["error"]
    
    def test_collection_name_sanitization(self, sqlite_manager):
        """Test collection name sanitization matches original."""
        dangerous_names = [
            "collection/../escape",
            "collection\\\\windows",
            "collection:with:colons",
            "collection*with*wildcards",
            'collection"with"quotes'
        ]
        
        for name in dangerous_names:
            result = sqlite_manager.create_collection(name)
            # Should succeed with sanitized name
            assert result["success"] is True
            # Dangerous characters should be replaced
            assert "../" not in result["message"]
            assert "\\\\" not in result["message"]
    
    def test_error_handling_consistency(self, sqlite_manager):
        """Test error handling provides consistent messages."""
        # Non-existent collection
        result = sqlite_manager.read_file("non-existent", "test.md")
        assert result["success"] is False
        assert "error" in result
        assert "message" in result
        
        # Non-existent file
        sqlite_manager.create_collection("test")
        result = sqlite_manager.read_file("test", "non-existent.md")
        assert result["success"] is False
        assert "not found" in result["error"]


class TestCollectionManagerFactory:
    """Test the factory function for creating managers."""
    
    def test_create_sqlite_manager(self):
        """Test factory creates SQLite manager."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = create_collection_manager(use_sqlite=True, base_dir=Path(temp_dir))
            assert isinstance(manager, SQLiteCollectionFileManager)
            manager.close()
    
    def test_create_file_manager(self):
        """Test factory creates file manager."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = create_collection_manager(use_sqlite=False, base_dir=Path(temp_dir))
            assert isinstance(manager, CollectionFileManager)
    
    def test_sqlite_manager_default(self):
        """Test SQLite manager is default."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = create_collection_manager(base_dir=Path(temp_dir))
            assert isinstance(manager, SQLiteCollectionFileManager)
            manager.close()


class TestSQLiteManagerEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.fixture
    def manager(self):
        """Create SQLite collection manager for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = SQLiteCollectionFileManager(Path(temp_dir))
            yield manager
            manager.close()
    
    def test_empty_collection_name(self, manager):
        """Test empty collection name handling."""
        result = manager.create_collection("")
        assert result["success"] is False
        assert "empty" in result["error"] or "empty" in result["message"]
    
    def test_whitespace_only_collection_name(self, manager):
        """Test whitespace-only collection name."""
        result = manager.create_collection("   ")
        assert result["success"] is False
        assert "empty" in result["error"] or "empty" in result["message"]
    
    def test_very_long_content(self, manager):
        """Test saving very long content."""
        collection_name = "Test Collection"
        manager.create_collection(collection_name)
        
        # Create large content (1MB)
        large_content = "A" * (1024 * 1024)
        
        result = manager.save_file(collection_name, "large.txt", large_content)
        assert result["success"] is True
        
        # Read it back
        read_result = manager.read_file(collection_name, "large.txt")
        assert read_result["success"] is True
        assert read_result["content"] == large_content
    
    def test_special_characters_in_filenames(self, manager):
        """Test handling special characters in filenames."""
        collection_name = "Test Collection"
        manager.create_collection(collection_name)
        
        # Files with special characters (that should be allowed)
        special_files = [
            "file-with-dashes.md",
            "file_with_underscores.txt",
            "file with spaces.json",
            "file.with.dots.md"
        ]
        
        for filename in special_files:
            result = manager.save_file(collection_name, filename, "content")
            assert result["success"] is True, f"Failed for filename: {filename}"
            
            # Should be able to read it back
            read_result = manager.read_file(collection_name, filename)
            assert read_result["success"] is True, f"Failed to read back: {filename}"
    
    def test_unicode_content(self, manager):
        """Test handling Unicode content."""
        collection_name = "Test Collection"
        manager.create_collection(collection_name)
        
        unicode_content = "🎉 Unicode content with émojis and spëcial characters 中文"
        
        result = manager.save_file(collection_name, "unicode.md", unicode_content)
        assert result["success"] is True
        
        read_result = manager.read_file(collection_name, "unicode.md")
        assert read_result["success"] is True
        assert read_result["content"] == unicode_content