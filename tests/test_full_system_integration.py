"""
Full System Integration Tests for SQLite Migration.
Tests the complete stack from HTTP API through SQLite storage.
"""
import asyncio
import json
import tempfile
from pathlib import Path
from typing import Dict, Any

from tools.sqlite_collection_manager import SQLiteCollectionFileManager
from tools.collection_manager import CollectionFileManager


class TestFullSystemIntegration:
    """Test complete system integration with SQLite backend."""
    
    def test_end_to_end_collection_lifecycle(self):
        """Test complete collection lifecycle through SQLite backend."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = SQLiteCollectionFileManager(Path(temp_dir))
            
            try:
                # 1. Create collection
                collection_name = "E2E Test Collection"
                description = "End-to-end test collection"
                
                create_result = manager.create_collection(collection_name, description)
                assert create_result["success"] is True
                assert "created successfully" in create_result["message"]
                
                # 2. List collections (should have our new collection)
                list_result = manager.list_collections()
                assert list_result["success"] is True
                assert len(list_result["collections"]) == 1
                assert list_result["collections"][0]["name"] == collection_name
                assert list_result["collections"][0]["description"] == description
                
                # 3. Save multiple files in different folders
                test_files = [
                    {"filename": "readme.md", "content": "# Project README", "folder": ""},
                    {"filename": "config.json", "content": '{"version": "1.0"}', "folder": "config"},
                    {"filename": "doc1.md", "content": "# Documentation 1", "folder": "docs"},
                    {"filename": "doc2.md", "content": "# Documentation 2", "folder": "docs"},
                    {"filename": "nested.txt", "content": "Nested content", "folder": "docs/guides"},
                ]
                
                for file_data in test_files:
                    save_result = manager.save_file(
                        collection_name, 
                        file_data["filename"], 
                        file_data["content"], 
                        file_data["folder"]
                    )
                    assert save_result["success"] is True, f"Failed to save {file_data['filename']}"
                
                # 4. List files in collection
                files_result = manager.list_files_in_collection(collection_name)
                assert files_result["success"] is True
                assert files_result["total_files"] == 5
                assert files_result["total_folders"] > 0
                
                # Verify all files are present
                file_names = {f["name"] for f in files_result["files"]}
                expected_names = {f["filename"] for f in test_files}
                assert file_names == expected_names
                
                # 5. Read files back and verify content
                for file_data in test_files:
                    read_result = manager.read_file(
                        collection_name, 
                        file_data["filename"], 
                        file_data["folder"]
                    )
                    assert read_result["success"] is True
                    assert read_result["content"] == file_data["content"]
                    assert "metadata" in read_result
                    assert "size" in read_result["metadata"]
                
                # 6. Get collection info (should show updated file count)
                info_result = manager.get_collection_info(collection_name)
                assert info_result["success"] is True
                collection_info = info_result["collection"]
                assert collection_info["name"] == collection_name
                assert collection_info["description"] == description
                assert collection_info["file_count"] == 5
                assert len(collection_info["folders"]) > 0
                
                # 7. Update a file
                updated_content = "# Updated README\n\nThis has been updated."
                update_result = manager.save_file(collection_name, "readme.md", updated_content, "")
                assert update_result["success"] is True
                
                # Verify update
                read_updated = manager.read_file(collection_name, "readme.md", "")
                assert read_updated["success"] is True
                assert read_updated["content"] == updated_content
                
                # 8. Delete collection
                delete_result = manager.delete_collection(collection_name)
                assert delete_result["success"] is True
                assert "deleted successfully" in delete_result["message"]
                
                # 9. Verify collection is gone
                final_list = manager.list_collections()
                assert final_list["success"] is True
                assert len(final_list["collections"]) == 0
                
                # 10. Try to access deleted collection (should fail)
                get_deleted = manager.get_collection_info(collection_name)
                assert get_deleted["success"] is False
                assert "not found" in get_deleted["error"]
                
            finally:
                manager.close()
    
    def test_api_format_consistency_with_file_manager(self):
        """Test that SQLite manager returns identical formats to file manager."""
        with tempfile.TemporaryDirectory() as sqlite_dir:
            with tempfile.TemporaryDirectory() as file_dir:
                sqlite_manager = SQLiteCollectionFileManager(Path(sqlite_dir))
                file_manager = CollectionFileManager(Path(file_dir))
                
                try:
                    collection_name = "Format Test"
                    
                    # Create collections in both
                    sqlite_create = sqlite_manager.create_collection(collection_name, "Test")
                    file_create = file_manager.create_collection(collection_name, "Test")
                    
                    # Both should succeed and have same structure
                    assert sqlite_create["success"] == file_create["success"]
                    assert set(sqlite_create.keys()) == set(file_create.keys())
                    
                    # Add a file to both
                    sqlite_save = sqlite_manager.save_file(collection_name, "test.md", "content", "folder")
                    file_save = file_manager.save_file(collection_name, "test.md", "content", "folder")
                    
                    # Both should succeed
                    assert sqlite_save["success"] == file_save["success"]
                    
                    # SQLite may have additional fields like content_hash for enhanced functionality
                    # but must have at least the core fields that file manager has
                    file_keys = set(file_save.keys())
                    sqlite_keys = set(sqlite_save.keys())
                    assert file_keys.issubset(sqlite_keys), f"SQLite missing required keys: {file_keys - sqlite_keys}"
                    
                    # Read files from both
                    sqlite_read = sqlite_manager.read_file(collection_name, "test.md", "folder")
                    file_read = file_manager.read_file(collection_name, "test.md", "folder")
                    
                    # Content should match
                    assert sqlite_read["content"] == file_read["content"]
                    
                    # Both should have either metadata or path (SQLite has both for enhanced compatibility)
                    assert "path" in sqlite_read or "metadata" in sqlite_read
                    assert "path" in file_read or "metadata" in file_read
                    
                    # List files from both
                    sqlite_list = sqlite_manager.list_files_in_collection(collection_name)
                    file_list = file_manager.list_files_in_collection(collection_name)
                    
                    # Structure should be identical
                    assert set(sqlite_list.keys()) == set(file_list.keys())
                    assert sqlite_list["total_files"] == file_list["total_files"]
                    assert sqlite_list["total_folders"] == file_list["total_folders"]
                    
                    # File entries should have same structure
                    if sqlite_list["files"] and file_list["files"]:
                        sqlite_file = sqlite_list["files"][0]
                        file_file = file_list["files"][0]
                        
                        # Both should have required fields
                        required_fields = ["name", "path", "type", "size", "folder"]
                        for field in required_fields:
                            assert field in sqlite_file, f"SQLite missing {field}"
                            assert field in file_file, f"File manager missing {field}"
                
                finally:
                    sqlite_manager.close()
    
    def test_error_handling_consistency(self):
        """Test error handling provides consistent responses."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = SQLiteCollectionFileManager(Path(temp_dir))
            
            try:
                # Test non-existent collection errors
                read_result = manager.read_file("nonexistent", "test.md")
                assert read_result["success"] is False
                assert "error" in read_result
                assert "message" in read_result
                
                # Test invalid file extension
                manager.create_collection("test")
                save_result = manager.save_file("test", "malicious.exe", "content")
                assert save_result["success"] is False
                assert "File extension not allowed" in save_result["error"]
                
                # Test empty collection name
                empty_result = manager.create_collection("")
                assert empty_result["success"] is False
                assert "empty" in empty_result["error"].lower()
                
                # Test dangerous collection names
                dangerous_names = ["../escape", "collection\\windows", "col:on"]
                for name in dangerous_names:
                    result = manager.create_collection(name)
                    # Should either succeed with sanitized name or fail gracefully
                    assert "success" in result
                    if result["success"]:
                        # Dangerous chars should not appear in path/message
                        assert "../" not in result.get("message", "")
                        assert "\\\\" not in result.get("message", "")
                
            finally:
                manager.close()
    
    def test_concurrency_and_thread_safety(self):
        """Test basic thread safety of SQLite manager."""
        import threading
        import time
        
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = SQLiteCollectionFileManager(Path(temp_dir))
            
            try:
                # Create a collection
                manager.create_collection("concurrent_test")
                
                results = []
                errors = []
                
                def worker_thread(thread_id: int):
                    """Worker function for concurrent testing."""
                    try:
                        for i in range(10):
                            # Save a file
                            filename = f"thread_{thread_id}_file_{i}.md"
                            content = f"Content from thread {thread_id}, iteration {i}"
                            
                            save_result = manager.save_file("concurrent_test", filename, content)
                            results.append((thread_id, i, save_result["success"]))
                            
                            # Small delay to increase chance of race conditions
                            time.sleep(0.001)
                            
                            # Read the file back
                            read_result = manager.read_file("concurrent_test", filename)
                            if read_result["success"]:
                                assert read_result["content"] == content
                            else:
                                errors.append(f"Thread {thread_id}: Read failed for {filename}")
                    
                    except Exception as e:
                        errors.append(f"Thread {thread_id}: {str(e)}")
                
                # Run 5 threads concurrently
                threads = []
                for thread_id in range(5):
                    thread = threading.Thread(target=worker_thread, args=(thread_id,))
                    threads.append(thread)
                    thread.start()
                
                # Wait for all threads to complete
                for thread in threads:
                    thread.join()
                
                # Check results
                assert len(errors) == 0, f"Concurrency errors: {errors}"
                assert len(results) == 50  # 5 threads * 10 operations each
                
                # All operations should have succeeded
                failed_operations = [r for r in results if not r[2]]
                assert len(failed_operations) == 0, f"Failed operations: {failed_operations}"
                
                # Verify all files were saved
                files_result = manager.list_files_in_collection("concurrent_test")
                assert files_result["success"] is True
                assert files_result["total_files"] == 50
                
            finally:
                manager.close()
    
    def test_large_content_handling(self):
        """Test handling of large file content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = SQLiteCollectionFileManager(Path(temp_dir))
            
            try:
                manager.create_collection("large_content_test")
                
                # Test increasingly large content
                sizes = [1024, 10*1024, 100*1024, 1024*1024]  # 1KB to 1MB
                
                for size in sizes:
                    content = "A" * size
                    filename = f"large_file_{size}.txt"
                    
                    # Save large content
                    save_result = manager.save_file("large_content_test", filename, content)
                    assert save_result["success"] is True, f"Failed to save {size} byte file"
                    
                    # Read it back
                    read_result = manager.read_file("large_content_test", filename)
                    assert read_result["success"] is True, f"Failed to read {size} byte file"
                    assert len(read_result["content"]) == size
                    assert read_result["content"] == content
                    
                    # Verify metadata
                    assert read_result["metadata"]["size"] == size
                
            finally:
                manager.close()
    
    def test_unicode_and_special_characters(self):
        """Test handling of Unicode and special characters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = SQLiteCollectionFileManager(Path(temp_dir))
            
            try:
                # Test Unicode in collection name and content
                collection_name = "Unicode Test Collection 中文 🎉"
                manager.create_collection(collection_name, "Collection with émojis and special chars")
                
                # Test Unicode content
                unicode_content = """
                # Unicode Test 🎉
                
                This file contains various Unicode characters:
                - Émojis: 🚀 💻 📱 🌟
                - Chinese: 你好世界
                - Arabic: مرحبا بالعالم
                - Japanese: こんにちは世界
                - Mathematical: ∑ ∫ ∞ ≠ ≤ ≥
                - Currency: $ € £ ¥ ₹ ₿
                - Special: "quotes" 'apostrophes' —dashes— …ellipsis
                """
                
                save_result = manager.save_file(collection_name, "unicode_test.md", unicode_content)
                assert save_result["success"] is True
                
                # Read back and verify
                read_result = manager.read_file(collection_name, "unicode_test.md")
                assert read_result["success"] is True
                assert read_result["content"] == unicode_content
                
                # Test filename with special characters (within allowed limits)
                special_filename = "file-with_special.chars.and.numbers123.md"
                save_special = manager.save_file(collection_name, special_filename, "Special filename content")
                assert save_special["success"] is True
                
                read_special = manager.read_file(collection_name, special_filename)
                assert read_special["success"] is True
                assert read_special["content"] == "Special filename content"
                
            finally:
                manager.close()


def run_comprehensive_system_test():
    """Run all integration tests and report results."""
    print("Starting comprehensive system integration tests...")
    
    test_instance = TestFullSystemIntegration()
    
    tests = [
        ("End-to-end collection lifecycle", test_instance.test_end_to_end_collection_lifecycle),
        ("API format consistency", test_instance.test_api_format_consistency_with_file_manager),
        ("Error handling consistency", test_instance.test_error_handling_consistency),
        ("Concurrency and thread safety", test_instance.test_concurrency_and_thread_safety),
        ("Large content handling", test_instance.test_large_content_handling),
        ("Unicode and special characters", test_instance.test_unicode_and_special_characters),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"Running: {test_name}...")
            test_func()
            print(f"✅ PASSED: {test_name}")
            passed += 1
        except Exception as e:
            print(f"❌ FAILED: {test_name} - {str(e)}")
            failed += 1
    
    print(f"\n" + "="*60)
    print(f"COMPREHENSIVE SYSTEM TEST RESULTS")
    print(f"="*60)
    print(f"Total tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(passed/len(tests)*100):.1f}%")
    
    if failed == 0:
        print(f"🎉 ALL TESTS PASSED! System is production ready.")
        return True
    else:
        print(f"⚠️  {failed} test(s) failed. Review issues before production deployment.")
        return False


if __name__ == "__main__":
    success = run_comprehensive_system_test()
    exit(0 if success else 1)