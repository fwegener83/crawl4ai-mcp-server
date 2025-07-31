"""Tests for file listing functionality in collection manager - Fixed version."""
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import sys
import os

# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.collection_manager import CollectionFileManager


def parse_result(result):
    """Helper function to handle both dict and JSON string responses."""
    if isinstance(result, str):
        return json.loads(result)
    return result


class TestFileListingFunctionality:
    """Test suite for file listing functionality."""

    def setup_method(self):
        """Set up test environment before each test."""
        # Create a temporary directory for test collections
        self.temp_dir = Path(tempfile.mkdtemp())
        self.manager = CollectionFileManager(base_dir=self.temp_dir)
        
    def teardown_method(self):
        """Clean up test environment after each test."""
        # Remove the temporary directory
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_list_files_empty_collection(self):
        """Test listing files in an empty collection."""
        # Create an empty collection
        collection_name = "empty_collection"
        create_result = self.manager.create_collection(collection_name)
        create_data = parse_result(create_result)
        assert create_data["success"] is True
        
        # List files
        result = self.manager.list_files_in_collection(collection_name)
        
        assert result["success"] is True
        assert result["files"] == []
        assert result["folders"] == []
        assert result["total_files"] == 0
        assert result["total_folders"] == 0

    def test_list_files_with_files(self):
        """Test listing files in a collection with files."""
        collection_name = "test_collection"
        
        # Create collection
        create_result = self.manager.create_collection(collection_name)
        create_data = parse_result(create_result)
        assert create_data["success"] is True
        
        # Add some test files
        test_files = [
            ("test1.md", "# Test File 1\nContent of test file 1"),
            ("test2.txt", "Content of test file 2"),
            ("document.json", '{"type": "document", "content": "JSON content placeholder"}')
        ]
        
        for filename, content in test_files:
            save_result = self.manager.save_file(collection_name, filename, content)
            save_data = parse_result(save_result)
            assert save_data["success"] is True
        
        # List files
        result = self.manager.list_files_in_collection(collection_name)
        
        assert result["success"] is True
        assert result["total_files"] == 3
        assert result["total_folders"] == 0
        
        # Check that all files are listed
        file_names = {f["name"] for f in result["files"]}
        expected_names = {"test1.md", "test2.txt", "document.json"}
        assert file_names == expected_names
        
        # Check file properties
        for file_info in result["files"]:
            assert "name" in file_info
            assert "path" in file_info
            assert "type" in file_info
            assert "size" in file_info
            assert "created_at" in file_info
            assert "modified_at" in file_info
            assert "extension" in file_info
            assert "folder" in file_info
            assert file_info["type"] == "file"
            assert file_info["size"] > 0

    def test_list_files_with_folders(self):
        """Test listing files in a collection with folders."""
        collection_name = "test_collection_folders"
        
        # Create collection
        create_result = self.manager.create_collection(collection_name)
        create_data = parse_result(create_result)
        assert create_data["success"] is True
        
        # Create folder structure manually
        collection_path = self.manager.base_dir / collection_name
        folder1 = collection_path / "folder1"
        folder2 = collection_path / "folder2"
        subfolder = folder1 / "subfolder"
        
        folder1.mkdir()
        folder2.mkdir()
        subfolder.mkdir()
        
        # Add files in different folders
        (folder1 / "file1.md").write_text("Content in folder1")
        (folder2 / "file2.txt").write_text("Content in folder2")
        (subfolder / "file3.md").write_text("Content in subfolder")
        (collection_path / "root_file.txt").write_text("Content in root")
        
        # List files
        result = self.manager.list_files_in_collection(collection_name)
        
        assert result["success"] is True
        assert result["total_files"] == 4
        assert result["total_folders"] == 3
        
        # Check folder information
        folder_names = {f["name"] for f in result["folders"]}
        expected_folders = {"folder1", "folder2", "subfolder"}
        assert folder_names == expected_folders
        
        # Check file paths include folder information
        file_paths = {f["path"] for f in result["files"]}
        expected_paths = {
            "root_file.txt",
            "folder1/file1.md", 
            "folder2/file2.txt",
            "folder1/subfolder/file3.md"
        }
        assert file_paths == expected_paths

    def test_list_files_nonexistent_collection(self):
        """Test listing files in a non-existent collection."""
        result = self.manager.list_files_in_collection("nonexistent")
        
        assert result["success"] is False
        assert "not found" in result["error"].lower()

    def test_list_files_ignores_hidden_files(self):
        """Test that hidden files and metadata files are ignored."""
        collection_name = "test_hidden"
        
        # Create collection
        create_result = self.manager.create_collection(collection_name)
        create_data = parse_result(create_result)
        assert create_data["success"] is True
        
        collection_path = self.manager.base_dir / collection_name
        
        # Add visible and hidden files
        (collection_path / "visible.md").write_text("Visible content")
        (collection_path / ".hidden").write_text("Hidden content")
        (collection_path / ".collection.json").write_text("{}")  # Metadata file
        (collection_path / ".DS_Store").write_text("macOS metadata")
        
        # List files
        result = self.manager.list_files_in_collection(collection_name)
        
        assert result["success"] is True
        assert result["total_files"] == 1  # Only the visible file
        assert result["files"][0]["name"] == "visible.md"

    def test_get_collection_info_includes_files(self):
        """Test that get_collection_info now includes actual file listing."""
        collection_name = "test_info"
        
        # Create collection
        create_result = self.manager.create_collection(collection_name)
        create_data = parse_result(create_result)
        assert create_data["success"] is True
        
        # Add a test file
        save_result = self.manager.save_file(collection_name, "test.md", "Test content")
        save_data = parse_result(save_result)
        assert save_data["success"] is True
        
        # Get collection info
        result = self.manager.get_collection_info(collection_name)
        
        assert result["success"] is True
        collection_info = result["collection"]
        
        # Check that file count is accurate
        assert collection_info["file_count"] == 1
        
        # Check that files are included
        assert "files" in collection_info
        assert len(collection_info["files"]) == 1
        assert collection_info["files"][0]["name"] == "test.md"
        
        # Check metadata includes actual counts
        assert collection_info["metadata"]["file_count"] == 1
        assert collection_info["metadata"]["total_size"] > 0

    def test_file_extensions_detected_correctly(self):
        """Test that file extensions are detected correctly."""
        collection_name = "test_extensions"
        
        # Create collection
        create_result = self.manager.create_collection(collection_name)
        create_data = parse_result(create_result)
        assert create_data["success"] is True
        
        # Add files with different extensions (only allowed extensions)
        test_files = [
            ("document.md", "Markdown content"),
            ("data.json", '{"key": "value"}'),
            ("notes.txt", "Text content")
        ]
        
        for filename, content in test_files:
            save_result = self.manager.save_file(collection_name, filename, content)
            save_data = parse_result(save_result)
            assert save_data["success"] is True
        
        # List files
        result = self.manager.list_files_in_collection(collection_name)
        
        # Check extensions
        file_extensions = {f["name"]: f["extension"] for f in result["files"]}
        expected_extensions = {
            "document.md": ".md",
            "data.json": ".json",
            "notes.txt": ".txt"
        }
        
        assert file_extensions == expected_extensions

    def test_folder_hierarchy_preserved(self):
        """Test that folder hierarchy is correctly represented."""
        collection_name = "test_hierarchy"
        
        # Create collection
        create_result = self.manager.create_collection(collection_name)
        create_data = parse_result(create_result)
        assert create_data["success"] is True
        
        collection_path = self.manager.base_dir / collection_name
        
        # Create nested folder structure
        docs_folder = collection_path / "docs"
        api_folder = docs_folder / "api"
        examples_folder = collection_path / "examples"
        
        docs_folder.mkdir()
        api_folder.mkdir()
        examples_folder.mkdir()
        
        # Add files at different levels
        (collection_path / "README.md").write_text("Root readme")
        (docs_folder / "guide.md").write_text("Documentation guide")
        (api_folder / "reference.md").write_text("API reference") 
        (examples_folder / "example1.py").write_text("Example code")
        
        # List files
        result = self.manager.list_files_in_collection(collection_name)
        
        # Check that folder hierarchy is preserved in paths
        file_info_by_path = {f["path"]: f for f in result["files"]}
        
        assert "README.md" in file_info_by_path
        assert "docs/guide.md" in file_info_by_path
        assert "docs/api/reference.md" in file_info_by_path
        assert "examples/example1.py" in file_info_by_path
        
        # Check folder information
        assert file_info_by_path["README.md"]["folder"] == ""
        assert file_info_by_path["docs/guide.md"]["folder"] == "docs"
        assert file_info_by_path["docs/api/reference.md"]["folder"] == "docs/api"
        assert file_info_by_path["examples/example1.py"]["folder"] == "examples"


def test_api_integration():
    """Integration test to verify API endpoint works."""
    import requests
    import time
    
    # Wait a moment for server to be ready
    time.sleep(1)
    
    try:
        # Test the health endpoint first
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code != 200:
            pytest.skip("Backend server not available for integration test")
        
        # Test file listing endpoint with known collection
        response = requests.get("http://localhost:8000/api/file-collections/Hallo%20hallo/files", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            assert "files" in data["data"]
            assert "folders" in data["data"]
            assert "total_files" in data["data"]
            assert "total_folders" in data["data"]
        else:
            # Collection might not exist, which is fine for this test
            pytest.skip("Test collection not available for integration test")
            
    except requests.exceptions.RequestException:
        pytest.skip("Could not connect to backend server for integration test")


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])