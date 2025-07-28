"""
Tests for Collection File Management System.
Focus on essential functionality: core operations, security, and error handling.
"""
import pytest
import json
from pathlib import Path
from unittest.mock import patch
from pydantic import ValidationError

# Import the actual implementations
from tools.collection_manager import CollectionFileManager, CollectionMetadata, FileMetadata


class TestCollectionMetadata:
    """Test collection metadata validation."""
    
    def test_collection_metadata_valid(self):
        """Test valid collection metadata creation."""
        metadata = CollectionMetadata(
            name="test-collection",
            description="Test collection"
        )
        assert metadata.name == "test-collection"
        assert metadata.description == "Test collection"
        assert metadata.file_count == 0
        assert isinstance(metadata.folders, list)
    
    def test_invalid_collection_names(self):
        """Test validation of invalid collection names."""
        # Test empty name
        with pytest.raises(ValidationError):
            CollectionMetadata(name="")
        
        # Test whitespace-only name
        with pytest.raises(ValidationError):
            CollectionMetadata(name="   ")
    
    def test_metadata_serialization(self):
        """Test metadata can be serialized to JSON."""
        metadata = CollectionMetadata(name="test", description="desc")
        json_str = metadata.model_dump_json()
        assert json_str is not None
        
        # Should be able to parse back
        parsed = json.loads(json_str)
        assert parsed["name"] == "test"


class TestFileMetadata:
    """Test file metadata validation."""
    
    def test_file_metadata_valid(self):
        """Test valid file metadata creation."""
        metadata = FileMetadata(
            filename="test.md",
            folder_path="folder1",
            source_url="https://example.com"
        )
        assert metadata.filename == "test.md"
        assert metadata.folder_path == "folder1"
        assert metadata.source_url == "https://example.com"


class TestCollectionFileManager:
    """Test core file operations."""
    
    @pytest.fixture
    def temp_collections_dir(self, tmp_path):
        """Create temporary collections directory."""
        collections_dir = tmp_path / "collections"
        collections_dir.mkdir()
        return collections_dir
    
    def test_collection_creation(self, temp_collections_dir):
        """Test basic collection creation."""
        manager = CollectionFileManager(temp_collections_dir)
        result = manager.create_collection("test-collection", "Test description")
        
        assert result["success"] is True
        assert (temp_collections_dir / "test-collection").exists()
        assert (temp_collections_dir / "test-collection" / ".collection.json").exists()
    
    def test_collection_creation_duplicate(self, temp_collections_dir):
        """Test creating duplicate collection."""
        manager = CollectionFileManager(temp_collections_dir)
        
        # Create first collection
        result1 = manager.create_collection("test-collection", "First")
        assert result1["success"] is True
        
        # Create second collection with same name should work (exist_ok=True)
        result2 = manager.create_collection("test-collection", "Second")
        assert result2["success"] is True
        
    
    def test_file_save_and_read(self, temp_collections_dir):
        """Test saving and reading files."""
        manager = CollectionFileManager(temp_collections_dir)
        
        # Create collection first
        manager.create_collection("test-collection")
        
        # Save file
        content = "# Test Content\n\nThis is a test file."
        result = manager.save_file("test-collection", "test.md", content)
        assert result["success"] is True
        
        # Read file back
        file_path = temp_collections_dir / "test-collection" / "test.md"
        assert file_path.exists()
        assert file_path.read_text(encoding='utf-8') == content
    
    def test_hierarchical_folder_creation(self, temp_collections_dir):
        """Test saving files in nested folders."""
        manager = CollectionFileManager(temp_collections_dir)
        manager.create_collection("test-collection")
        
        # Save file in nested folder
        content = "# Nested Content"
        result = manager.save_file(
            "test-collection", 
            "nested.md", 
            content, 
            folder="docs/tutorials"
        )
        assert result["success"] is True
        
        # Check file exists in correct location
        file_path = temp_collections_dir / "test-collection" / "docs" / "tutorials" / "nested.md"
        assert file_path.exists()
        assert file_path.read_text(encoding='utf-8') == content
    
    def test_file_not_found_errors(self, temp_collections_dir):
        """Test error handling for non-existent collections/files."""
        manager = CollectionFileManager(temp_collections_dir)
        
        # Try to save to non-existent collection
        result = manager.save_file("nonexistent", "test.md", "content")
        assert result["success"] is False
        assert "does not exist" in result["error"]


class TestPathSecurity:
    """Critical security tests for path traversal prevention."""
    
    @pytest.fixture
    def temp_collections_dir(self, tmp_path):
        """Create temporary collections directory."""
        collections_dir = tmp_path / "collections"
        collections_dir.mkdir()
        return collections_dir
    
    def test_path_traversal_prevention(self, temp_collections_dir):
        """CRITICAL: Test path traversal attack prevention."""
        manager = CollectionFileManager(temp_collections_dir)
        manager.create_collection("test-collection")
        
        # Test various path traversal attempts
        dangerous_paths = [
            "../../../etc/passwd",
            "..\\\\..\\\\windows\\\\system32\\\\config\\\\sam",
            "../../sensitive_file.txt",
            "../outside_collection.md"
        ]
        
        for dangerous_path in dangerous_paths:
            result = manager.save_file("test-collection", dangerous_path, "malicious content")
            # Should either fail or normalize the path safely
            if result["success"]:
                # If it succeeded, the file should be inside the collection
                saved_path = Path(result["path"])
                collection_path = temp_collections_dir / "test-collection"
                assert saved_path.is_relative_to(collection_path), f"Path traversal vulnerability: {saved_path}"
        
        # manager = CollectionFileManager(temp_collections_dir)
        # manager.create_collection("test-collection")
        # 
        # # Test various path traversal attempts
        # dangerous_paths = [
        #     "../../../etc/passwd",
        #     "..\\..\\windows\\system32\\config\\sam",
        #     "../../sensitive_file.txt",
        #     "../outside_collection.md"
        # ]
        # 
        # for dangerous_path in dangerous_paths:
        #     result = manager.save_file("test-collection", dangerous_path, "malicious content")
        #     # Should either fail or normalize the path safely
        #     if result["success"]:
        #         # If it succeeded, the file should be inside the collection
        #         saved_path = Path(result["path"])
        #         collection_path = temp_collections_dir / "test-collection"
        #         assert saved_path.is_relative_to(collection_path), f"Path traversal vulnerability: {saved_path}"
    
    def test_collection_name_sanitization(self, temp_collections_dir):
        """Test sanitization of dangerous collection names."""
        manager = CollectionFileManager(temp_collections_dir)
        
        # Test dangerous collection names
        dangerous_names = [
            "../outside",
            "../../etc",
            "con",  # Windows reserved name
            "aux",  # Windows reserved name
            "collection/with/slashes",
            "collection\\with\\backslashes"
        ]
        
        for dangerous_name in dangerous_names:
            result = manager.create_collection(dangerous_name)
            if result["success"]:
                # Collection should be created safely within collections directory
                created_path = Path(result["path"])
                assert created_path.is_relative_to(temp_collections_dir), f"Collection name vulnerability: {created_path}"
        
        # manager = CollectionFileManager(temp_collections_dir)
        # 
        # # Test dangerous collection names
        # dangerous_names = [
        #     "../outside",
        #     "../../etc",
        #     "con",  # Windows reserved name
        #     "aux",  # Windows reserved name
        #     "collection/with/slashes",
        #     "collection\\with\\backslashes"
        # ]
        # 
        # for dangerous_name in dangerous_names:
        #     result = manager.create_collection(dangerous_name)
        #     if result["success"]:
        #         # Collection should be created safely within collections directory
        #         created_path = Path(result["path"])
        #         assert created_path.is_relative_to(temp_collections_dir), f"Collection name vulnerability: {created_path}"
    
    def test_file_extension_validation(self, temp_collections_dir):
        """Test that only safe file extensions are allowed."""
        manager = CollectionFileManager(temp_collections_dir)
        manager.create_collection("test-collection")
        
        # Test safe extensions (should work)
        safe_extensions = ["file.md", "file.txt", "file.json"]
        for filename in safe_extensions:
            result = manager.save_file("test-collection", filename, "safe content")
            assert result["success"] is True, f"Safe extension {filename} should be allowed"
        
        # Test potentially dangerous extensions (should be handled safely)
        dangerous_extensions = ["file.exe", "file.sh", "file.bat", "file.js"]
        for filename in dangerous_extensions:
            result = manager.save_file("test-collection", filename, "content")
            # Should reject dangerous extensions
            assert result["success"] is False, f"Dangerous extension {filename} should be rejected"
        
        # manager = CollectionFileManager(temp_collections_dir)
        # manager.create_collection("test-collection")
        # 
        # # Test safe extensions (should work)
        # safe_extensions = ["file.md", "file.txt", "file.json"]
        # for filename in safe_extensions:
        #     result = manager.save_file("test-collection", filename, "safe content")
        #     assert result["success"] is True, f"Safe extension {filename} should be allowed"
        # 
        # # Test potentially dangerous extensions (should be handled safely)
        # dangerous_extensions = ["file.exe", "file.sh", "file.bat", "file.js"]
        # for filename in dangerous_extensions:
        #     result = manager.save_file("test-collection", filename, "content")
        #     # Implementation should either reject or sanitize these
        #     # The exact behavior will depend on our security policy




# Additional test helpers
class TestUtilities:
    """Test utility functions and helpers."""
    
    def test_utf8_encoding_handling(self, tmp_path):
        """Test that files are properly handled with UTF-8 encoding."""
        collections_dir = tmp_path / "collections"
        collections_dir.mkdir()
        manager = CollectionFileManager(collections_dir)
        manager.create_collection("unicode-test")
        
        # Test content with various Unicode characters
        unicode_content = "# Unicode Test\n\n日本語 • Français • Русский • العربية • 🎉"
        result = manager.save_file("unicode-test", "unicode.md", unicode_content)
        assert result["success"] is True
        
        # Read back and verify
        file_path = collections_dir / "unicode-test" / "unicode.md"
        read_content = file_path.read_text(encoding='utf-8')
        assert read_content == unicode_content
        
        # manager = CollectionFileManager(tmp_path / "collections")
        # manager.create_collection("unicode-test")
        # 
        # # Test content with various Unicode characters
        # unicode_content = "# Unicode Test\n\n日本語 • Français • Русский • العربية • 🎉"
        # result = manager.save_file("unicode-test", "unicode.md", unicode_content)
        # assert result["success"] is True
        # 
        # # Read back and verify
        # file_path = tmp_path / "collections" / "unicode-test" / "unicode.md"
        # read_content = file_path.read_text(encoding='utf-8')
        # assert read_content == unicode_content