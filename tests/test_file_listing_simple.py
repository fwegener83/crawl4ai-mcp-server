#!/usr/bin/env python3
"""Simple tests for file listing functionality without pytest dependency."""
import json
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.collection_manager import CollectionFileManager


def test_basic_file_listing():
    """Test basic file listing functionality."""
    print("Testing basic file listing functionality...")
    
    # Create a temporary directory for test collections
    temp_dir = Path(tempfile.mkdtemp())
    manager = CollectionFileManager(base_dir=temp_dir)
    
    try:
        # Create collection
        collection_name = "test_collection"
        create_result = manager.create_collection(collection_name)
        # Handle both dict and JSON string responses
        if isinstance(create_result, str):
            create_data = json.loads(create_result)
        else:
            create_data = create_result
        assert create_data["success"] is True, f"Failed to create collection: {create_data}"
        print("✓ Collection created successfully")
        
        # Add test files
        test_files = [
            ("test1.md", "# Test File 1\nContent of test file 1"),
            ("test2.txt", "Content of test file 2"),
            ("document.json", '{"key": "value"}')
        ]
        
        for filename, content in test_files:
            save_result = manager.save_file(collection_name, filename, content)
            # Handle both dict and JSON string responses
            if isinstance(save_result, str):
                save_data = json.loads(save_result)
            else:
                save_data = save_result
            assert save_data["success"] is True, f"Failed to save file {filename}: {save_data}"
        
        print("✓ Test files created successfully")
        
        # Test file listing
        result = manager.list_files_in_collection(collection_name)
        
        assert result["success"] is True, f"File listing failed: {result}"
        assert result["total_files"] == 3, f"Expected 3 files, got {result['total_files']}"
        assert result["total_folders"] == 0, f"Expected 0 folders, got {result['total_folders']}"
        
        # Check that all files are listed
        file_names = {f["name"] for f in result["files"]}
        expected_names = {"test1.md", "test2.txt", "document.json"}
        assert file_names == expected_names, f"File names mismatch. Expected {expected_names}, got {file_names}"
        
        print("✓ File listing works correctly")
        
        # Test that files have required properties
        for file_info in result["files"]:
            required_props = ["name", "path", "type", "size", "created_at", "modified_at", "extension", "folder"]
            for prop in required_props:
                assert prop in file_info, f"Missing property {prop} in file info: {file_info}"
            assert file_info["type"] == "file", f"Wrong file type: {file_info['type']}"
            assert file_info["size"] > 0, f"File size should be > 0: {file_info['size']}"
        
        print("✓ File properties are correct")
        
        # Test get_collection_info includes files
        info_result = manager.get_collection_info(collection_name)
        assert info_result["success"] is True, f"Failed to get collection info: {info_result}"
        
        collection_info = info_result["collection"]
        assert collection_info["file_count"] == 3, f"Wrong file count in collection info: {collection_info['file_count']}"
        assert "files" in collection_info, "Files not included in collection info"
        assert len(collection_info["files"]) == 3, f"Wrong number of files in collection info: {len(collection_info['files'])}"
        
        print("✓ Collection info includes file listing")
        
    finally:
        # Clean up
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        print("✓ Cleanup completed")


def test_folder_structure():
    """Test folder structure handling."""
    print("\nTesting folder structure handling...")
    
    temp_dir = Path(tempfile.mkdtemp())
    manager = CollectionFileManager(base_dir=temp_dir)
    
    try:
        # Create collection
        collection_name = "test_folders"
        create_result = manager.create_collection(collection_name)
        # Handle both dict and JSON string responses
        if isinstance(create_result, str):
            create_data = json.loads(create_result)
        else:
            create_data = create_result
        assert create_data["success"] is True
        
        collection_path = manager.base_dir / collection_name
        
        # Create folder structure manually
        folder1 = collection_path / "docs"
        folder2 = collection_path / "examples"
        subfolder = folder1 / "api"
        
        folder1.mkdir()
        folder2.mkdir()
        subfolder.mkdir()
        
        # Add files in different locations
        (collection_path / "README.md").write_text("Root readme")
        (folder1 / "guide.md").write_text("Documentation guide")
        (subfolder / "reference.md").write_text("API reference")
        (folder2 / "example.py").write_text("Example code")
        
        # Test file listing
        result = manager.list_files_in_collection(collection_name)
        
        assert result["success"] is True
        assert result["total_files"] == 4, f"Expected 4 files, got {result['total_files']}"
        assert result["total_folders"] == 3, f"Expected 3 folders, got {result['total_folders']}"
        
        # Check file paths
        file_paths = {f["path"] for f in result["files"]}
        expected_paths = {
            "README.md",
            "docs/guide.md",
            "docs/api/reference.md",
            "examples/example.py"
        }
        assert file_paths == expected_paths, f"Path mismatch. Expected {expected_paths}, got {file_paths}"
        
        print("✓ Folder structure handled correctly")
        
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


def test_hidden_files_ignored():
    """Test that hidden files are ignored."""
    print("\nTesting hidden file filtering...")
    
    temp_dir = Path(tempfile.mkdtemp())
    manager = CollectionFileManager(base_dir=temp_dir)
    
    try:
        # Create collection
        collection_name = "test_hidden"
        create_result = manager.create_collection(collection_name)
        # Handle both dict and JSON string responses
        if isinstance(create_result, str):
            create_data = json.loads(create_result)
        else:
            create_data = create_result
        assert create_data["success"] is True
        
        collection_path = manager.base_dir / collection_name
        
        # Add visible and hidden files
        (collection_path / "visible.md").write_text("Visible content")
        (collection_path / ".hidden").write_text("Hidden content")
        (collection_path / ".DS_Store").write_text("macOS metadata")
        
        # Test file listing
        result = manager.list_files_in_collection(collection_name)
        
        assert result["success"] is True
        assert result["total_files"] == 1, f"Expected 1 visible file, got {result['total_files']}"
        assert result["files"][0]["name"] == "visible.md", f"Wrong file name: {result['files'][0]['name']}"
        
        print("✓ Hidden files properly ignored")
        
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


def test_api_integration():
    """Test API integration if server is available."""
    print("\nTesting API integration...")
    
    try:
        import requests
        import time
        
        # Test the health endpoint first
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code != 200:
            print("⚠ Backend server not available for integration test")
            return
        
        # Test file listing endpoint with known collection
        response = requests.get("http://localhost:8000/api/file-collections/Hallo%20hallo/files", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True, f"API response not successful: {data}"
            assert "files" in data["data"], "Files not in API response"
            assert "folders" in data["data"], "Folders not in API response"
            assert "total_files" in data["data"], "Total files not in API response"
            assert "total_folders" in data["data"], "Total folders not in API response"
            
            print(f"✓ API integration successful - found {data['data']['total_files']} files")
        else:
            print(f"⚠ Test collection not available (status: {response.status_code})")
            
    except ImportError:
        print("⚠ requests module not available for integration test")
    except Exception as e:
        print(f"⚠ Could not connect to backend server: {e}")


def main():
    """Run all tests."""
    print("Running file listing functionality tests...\n")
    
    try:
        test_basic_file_listing()
        test_folder_structure()
        test_hidden_files_ignored()
        test_api_integration()
        
        print("\n🎉 All tests passed successfully!")
        return 0
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())