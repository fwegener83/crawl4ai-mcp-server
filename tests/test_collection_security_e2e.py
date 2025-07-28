"""
Comprehensive Security & End-to-End Tests for Collection File Management System.
Tests security boundaries, path traversal prevention, and complete workflows.
"""
import pytest
import asyncio
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, AsyncMock

from tools.collection_manager import CollectionFileManager


class TestPathTraversalSecurity:
    """Comprehensive path traversal security tests."""
    
    @pytest.fixture
    def temp_collections_dir(self, tmp_path):
        """Create temporary collections directory."""
        collections_dir = tmp_path / "collections"
        collections_dir.mkdir()
        return collections_dir
    
    def test_path_traversal_attack_scenarios(self, temp_collections_dir):
        """Test comprehensive path traversal attack scenarios."""
        manager = CollectionFileManager(temp_collections_dir)
        manager.create_collection("target-collection")
        
        # Create a sensitive file outside the collections directory
        sensitive_file = temp_collections_dir.parent / "sensitive.txt"
        sensitive_file.write_text("SENSITIVE CONTENT", encoding='utf-8')
        
        # Advanced path traversal attempts
        dangerous_paths = [
            # Basic traversal
            "../sensitive.txt",
            "../../sensitive.txt", 
            "../../../etc/passwd",
            
            # Mixed separators
            "..\\sensitive.txt",
            "..\\..\\sensitive.txt",
            "../..\\sensitive.txt",
            
            # URL encoded
            "%2e%2e%2fsensitive.txt",
            "%2e%2e/%2e%2e/sensitive.txt",
            
            # Double encoded
            "%252e%252e%252fsensitive.txt",
            
            # Unicode normalization attacks
            "..%c0%afsensitive.txt",
            "..%c1%9csensitive.txt",
            
            # Absolute paths
            "/etc/passwd",
            "/tmp/sensitive.txt",
            str(sensitive_file),  # Direct absolute path
            
            # Null byte injection
            "../sensitive.txt\x00.md",
            "..%00/sensitive.txt",
            
            # Long path attacks
            "../" * 100 + "sensitive.txt",
            
            # Current directory bypass
            "./../../sensitive.txt",
            "./../sensitive.txt",
            
            # Mixed case (case-insensitive filesystems)
            "../Sensitive.txt",
            "../SENSITIVE.TXT",
        ]
        
        for dangerous_path in dangerous_paths:
            result = manager.save_file("target-collection", dangerous_path, "malicious content")
            
            if result["success"]:
                # If the operation succeeded, verify the file is safely contained
                saved_path = Path(result["path"])
                collection_path = temp_collections_dir / "target-collection"
                
                # CRITICAL: File must be inside the collection directory
                try:
                    saved_path.resolve().relative_to(collection_path.resolve())
                except ValueError:
                    pytest.fail(f"SECURITY BREACH: File escaped collection directory: {saved_path}")
                
                # Ensure we didn't overwrite the sensitive file
                assert sensitive_file.read_text(encoding='utf-8') == "SENSITIVE CONTENT"
            
            # If the operation failed, that's also acceptable (defensive behavior)
            print(f"Path traversal attempt '{dangerous_path}': {'blocked' if not result['success'] else 'sanitized'}")
    
    def test_collection_name_traversal_attacks(self, temp_collections_dir):
        """Test path traversal through malicious collection names."""
        manager = CollectionFileManager(temp_collections_dir) 
        
        # Create sensitive file outside collections
        sensitive_file = temp_collections_dir.parent / "external_config.json"
        sensitive_file.write_text('{"secret": "leaked"}', encoding='utf-8')
        
        dangerous_collection_names = [
            "../external_target",
            "../../external_target", 
            "../../../tmp/malicious",
            "..\\external_target",
            "collection/../../../tmp/evil",
            "/tmp/absolute_collection",
            str(temp_collections_dir.parent / "external_collection"),
            "con",  # Windows reserved
            "aux",  # Windows reserved
            "prn",  # Windows reserved
            "collection\x00injection",
            "collection/with/embedded/slashes",
            "collection\\with\\embedded\\backslashes",
        ]
        
        for dangerous_name in dangerous_collection_names:
            result = manager.create_collection(dangerous_name)
            
            if result["success"]:
                # If creation succeeded, verify it's safely contained
                created_path = Path(result["path"])
                
                try:
                    created_path.resolve().relative_to(temp_collections_dir.resolve())
                except ValueError:
                    pytest.fail(f"SECURITY BREACH: Collection escaped base directory: {created_path}")
                
                # Ensure we didn't affect external files
                assert sensitive_file.exists()
                assert json.loads(sensitive_file.read_text(encoding='utf-8'))["secret"] == "leaked"
            
            print(f"Collection name '{dangerous_name}': {'blocked' if not result['success'] else 'sanitized'}")
    
    def test_symlink_attack_prevention(self, temp_collections_dir):
        """Test prevention of symlink-based attacks."""
        manager = CollectionFileManager(temp_collections_dir)
        manager.create_collection("symlink-test")
        
        # Create target file outside collections
        external_target = temp_collections_dir.parent / "external_target.txt"
        external_target.write_text("EXTERNAL CONTENT", encoding='utf-8')
        
        # Try to create symlink inside collection (if supported by OS)
        collection_path = temp_collections_dir / "symlink-test"
        potential_symlink = collection_path / "malicious_link.md"
        
        try:
            # Attempt to create symlink pointing outside collection
            potential_symlink.symlink_to(external_target)
            
            # If symlink creation succeeded, verify our read operations are safe
            result = manager.read_file("symlink-test", "malicious_link.md")
            
            if result["success"]:
                # If reading the symlink succeeded, ensure we didn't leak external content
                # The content should either be blocked or clearly marked as symlink
                content = result["content"]
                if "EXTERNAL CONTENT" in content:
                    pytest.fail("SECURITY BREACH: Symlink allowed reading external content")
                    
        except (OSError, NotImplementedError):
            # Symlinks not supported on this system - that's fine
            pass
    
    def test_race_condition_safety(self, temp_collections_dir):
        """Test safety against race condition attacks."""
        manager = CollectionFileManager(temp_collections_dir)
        manager.create_collection("race-test")
        
        # Simulate race condition: try to modify collection while operation in progress
        async def concurrent_operations():
            tasks = []
            
            # Multiple concurrent save operations
            for i in range(10):
                content = f"Content {i}"
                task = asyncio.create_task(
                    asyncio.to_thread(manager.save_file, "race-test", f"file_{i}.md", content)
                )
                tasks.append(task)
            
            # One operation tries path traversal during the race
            malicious_task = asyncio.create_task(
                asyncio.to_thread(manager.save_file, "race-test", "../escape.md", "malicious")
            )
            tasks.append(malicious_task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results
        
        # Run the race condition test
        results = asyncio.run(concurrent_operations())
        
        # Verify no operation escaped the collection directory
        for result in results:
            if isinstance(result, dict) and result.get("success"):
                saved_path = Path(result["path"])
                collection_path = temp_collections_dir / "race-test"
                
                try:
                    saved_path.resolve().relative_to(collection_path.resolve())
                except ValueError:
                    pytest.fail(f"SECURITY BREACH: Race condition allowed path escape: {saved_path}")


class TestEndToEndWorkflows:
    """Comprehensive end-to-end workflow tests."""
    
    @pytest.fixture
    def temp_collections_dir(self, tmp_path):
        """Create temporary collections directory."""
        collections_dir = tmp_path / "collections"
        collections_dir.mkdir()
        return collections_dir
    
    def test_complete_crawl_to_collection_workflow(self, temp_collections_dir):
        """Test complete workflow from web crawling to collection storage."""
        manager = CollectionFileManager(temp_collections_dir)
        
        # Simulate a complete crawl-to-collection workflow
        
        # 1. Create collection for a specific domain
        result = manager.create_collection(
            "tech-articles",
            "Collection of technical articles from various sources"
        )
        assert result["success"] is True
        
        # 2. Simulate crawling multiple pages
        crawled_pages = [
            {
                "url": "https://example.com/article1",
                "title": "Introduction to Python",
                "content": """# Introduction to Python
                
Python is a versatile programming language.

## Key Features
- Easy to learn
- Powerful libraries
- Cross-platform

Source: https://example.com/article1
""",
                "folder": "python",
            },
            {
                "url": "https://example.com/article2", 
                "title": "Advanced JavaScript",
                "content": """# Advanced JavaScript

JavaScript has evolved significantly.

## Modern Features
- Async/await
- Modules
- Classes

Source: https://example.com/article2
""",
                "folder": "javascript",
            },
            {
                "url": "https://example.com/tutorial",
                "title": "Docker Tutorial", 
                "content": """# Docker Tutorial

Containerization with Docker.

## Benefits
- Consistency
- Scalability
- Isolation

Source: https://example.com/tutorial
""",
                "folder": "devops",
            }
        ]
        
        # 3. Save all crawled content
        for page in crawled_pages:
            filename = f"{page['title'].lower().replace(' ', '_')}.md"
            result = manager.save_file(
                "tech-articles",
                filename,
                page["content"],
                page["folder"]
            )
            assert result["success"] is True
            print(f"✓ Saved: {page['folder']}/{filename}")
        
        # 4. Verify collection structure
        collection_info = manager.get_collection_info("tech-articles")
        assert collection_info["success"] is True
        assert collection_info["collection"]["file_count"] == 3
        
        expected_folders = {"python", "javascript", "devops"}
        actual_folders = set(collection_info["collection"]["folders"])
        assert actual_folders == expected_folders
        
        # 5. Test reading back content
        result = manager.read_file("tech-articles", "introduction_to_python.md", "python")
        assert result["success"] is True
        assert "Python is a versatile" in result["content"]
        
        # 6. Test collection listing
        collections = manager.list_collections()
        assert collections["success"] is True
        assert collections["total"] == 1
        assert collections["collections"][0]["name"] == "tech-articles"
        
        print("✓ Complete crawl-to-collection workflow successful")
    
    def test_large_scale_collection_operations(self, temp_collections_dir):
        """Test performance and stability with large numbers of files."""
        manager = CollectionFileManager(temp_collections_dir)
        manager.create_collection("large-test", "Large scale test collection")
        
        # Create 100 files in various folder structures
        import time
        start_time = time.time()
        
        folders = ["docs", "articles", "tutorials", "references", "examples"]
        
        for i in range(100):
            folder = folders[i % len(folders)]
            subfolder = f"category_{i // 20}"  # Group into subcategories
            full_folder = f"{folder}/{subfolder}"
            
            content = f"""# Document {i}

This is test document number {i}.

## Content
Generated content for testing purposes.

## Metadata
- ID: {i}
- Folder: {full_folder}
- Generated: {time.time()}
"""
            
            result = manager.save_file(
                "large-test",
                f"document_{i:03d}.md",
                content,
                full_folder
            )
            assert result["success"] is True
            
            # Progress indicator
            if (i + 1) % 20 == 0:
                print(f"✓ Created {i + 1}/100 files")
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Verify collection integrity
        collection_info = manager.get_collection_info("large-test")
        assert collection_info["success"] is True
        assert collection_info["collection"]["file_count"] == 100
        
        # Performance check: should complete in reasonable time
        assert duration < 10.0, f"Large scale operation took too long: {duration:.2f}s"
        
        print(f"✓ Large scale test completed in {duration:.2f}s")
        print(f"✓ Collection has {len(collection_info['collection']['folders'])} folders")
    
    def test_unicode_and_special_characters(self, temp_collections_dir):
        """Test handling of Unicode and special characters in content and names."""
        manager = CollectionFileManager(temp_collections_dir)
        
        # Collection with Unicode name (should be sanitized)
        result = manager.create_collection(
            "测试-collección-тест", 
            "Test collection with Unicode characters"
        )
        assert result["success"] is True
        
        # Content with various Unicode characters
        unicode_content = """# 国际化测试 (Internationalization Test)

## Various Languages
- **English**: Hello World
- **中文**: 你好世界  
- **Español**: Hola Mundo
- **Русский**: Привет мир
- **العربية**: مرحبا بالعالم
- **日本語**: こんにちは世界
- **Français**: Bonjour le monde
- **Deutsch**: Hallo Welt

## Special Characters
- Emojis: 🌍 🚀 💻 📚 ⭐
- Math: ∑ ∆ π ∞ ≈ ≠ ≤ ≥
- Currency: $ € £ ¥ ₹ ₿
- Symbols: © ® ™ § ¶ †

## Code Examples
```python
def greet(name="世界"):
    return f"Hello, {name}! 🌟"
```

## File Paths Test
- Should handle: /path/to/file
- Should handle: C:\\Windows\\System32
- Special chars: file[1].txt, file(2).md, file@domain.com
"""
        
        result = manager.save_file(
            "测试-collección-тест",
            "unicode_test.md", 
            unicode_content,
            "international"
        )
        assert result["success"] is True
        
        # Read back and verify Unicode preservation
        result = manager.read_file(
            "测试-collección-тест", 
            "unicode_test.md",
            "international"
        )
        assert result["success"] is True
        
        # Verify Unicode content is preserved
        content = result["content"]
        assert "你好世界" in content
        assert "🌍 🚀 💻" in content  
        assert "∑ ∆ π ∞" in content
        assert "def greet" in content
        
        print("✓ Unicode and special characters handled correctly")
    
    def test_error_recovery_and_resilience(self, temp_collections_dir):
        """Test system resilience and error recovery."""
        manager = CollectionFileManager(temp_collections_dir)
        
        # 1. Test recovery from partial failures
        manager.create_collection("resilience-test")
        
        # Save some successful files first
        for i in range(5):
            result = manager.save_file(
                "resilience-test",
                f"good_file_{i}.md",
                f"Good content {i}"
            )
            assert result["success"] is True
        
        # 2. Attempt operations that should fail gracefully
        fail_tests = [
            # Invalid file extensions
            ("bad_file.exe", "malicious content"),
            ("script.sh", "#!/bin/bash\nrm -rf /"),
            ("config.ini", "[dangerous]\ndelete_all=true"),
            
            # Extremely long content
            ("huge_file.md", "x" * 1000000),  # 1MB of data
            
            # Control characters in content
            ("control_chars.md", "Content with \x00 null \x01 control \x1f chars"),
        ]
        
        successful_operations = 0
        failed_operations = 0
        
        for filename, content in fail_tests:
            result = manager.save_file("resilience-test", filename, content)
            
            if result["success"]:
                successful_operations += 1
                # If it succeeded, ensure it's properly contained
                saved_path = Path(result["path"])
                collection_path = temp_collections_dir / "resilience-test"
                assert saved_path.is_relative_to(collection_path)
            else:
                failed_operations += 1
            
            print(f"Operation '{filename}': {'success' if result['success'] else 'failed (safe)'}")
        
        # 3. Verify collection integrity after partial failures
        collection_info = manager.get_collection_info("resilience-test")
        assert collection_info["success"] is True
        
        # Should still have the original 5 good files
        assert collection_info["collection"]["file_count"] >= 5
        
        # 4. Test cleanup and recovery
        collections = manager.list_collections()
        assert collections["success"] is True
        assert len(collections["collections"]) >= 1
        
        print(f"✓ Resilience test: {successful_operations} succeeded, {failed_operations} safely failed")
        print(f"✓ Collection integrity maintained with {collection_info['collection']['file_count']} files")


class TestCrossPlatformCompatibility:
    """Test cross-platform compatibility (Windows, macOS, Linux)."""
    
    @pytest.fixture
    def temp_collections_dir(self, tmp_path):
        """Create temporary collections directory."""
        collections_dir = tmp_path / "collections"
        collections_dir.mkdir()
        return collections_dir
    
    def test_path_separator_handling(self, temp_collections_dir):
        """Test handling of different path separators across platforms."""
        manager = CollectionFileManager(temp_collections_dir)
        manager.create_collection("path-test")
        
        # Test various path separator combinations
        path_variations = [
            ("unix/style/path", "file.md"),
            ("windows\\style\\path", "file.md"),  
            ("mixed/style\\path", "file.md"),
            ("deep/nested/folder/structure/test", "deep_file.md"),
            ("folder-with-dashes/sub-folder", "dashed-file.md"),
            ("folder_with_underscores/sub_folder", "underscore_file.md"),
            ("folder.with.dots/sub.folder", "dotted.file.md"),
        ]
        
        for folder, filename in path_variations:
            result = manager.save_file(
                "path-test",
                filename,
                f"Content for {folder}/{filename}",
                folder  
            )
            
            # Should succeed on all platforms due to pathlib normalization
            assert result["success"] is True
            
            # Verify we can read it back
            read_result = manager.read_file("path-test", filename, folder)
            assert read_result["success"] is True
            assert f"Content for {folder}/{filename}" in read_result["content"]
            
            print(f"✓ Path '{folder}/{filename}' handled correctly")
    
    def test_filesystem_case_sensitivity(self, temp_collections_dir):
        """Test handling of case sensitivity differences across filesystems."""
        manager = CollectionFileManager(temp_collections_dir)
        manager.create_collection("case-test")
        
        # Test case variations (behavior may differ on case-sensitive vs case-insensitive filesystems)
        result1 = manager.save_file("case-test", "TestFile.md", "Content 1")
        result2 = manager.save_file("case-test", "testfile.md", "Content 2") 
        result3 = manager.save_file("case-test", "TESTFILE.md", "Content 3")
        
        # All operations should succeed (pathlib handles case sensitivity)
        assert result1["success"] is True
        assert result2["success"] is True
        assert result3["success"] is True
        
        # Verify collection integrity
        collection_info = manager.get_collection_info("case-test")
        assert collection_info["success"] is True
        
        print(f"✓ Case sensitivity test: {collection_info['collection']['file_count']} files created")
        
        # On case-insensitive filesystems (like macOS default), all three files may be the same
        # On case-sensitive filesystems (like Linux), they should be separate files
        file_count = collection_info['collection']['file_count']
        
        if file_count == 1:
            # Case-insensitive filesystem: all names refer to the same file
            print("✓ Case-insensitive filesystem detected")
            # The last write should have won
            result = manager.read_file("case-test", "TestFile.md")
            assert result["success"] is True
            assert "Content 3" in result["content"]  # Last content written
            
        elif file_count == 3:
            # Case-sensitive filesystem: separate files
            print("✓ Case-sensitive filesystem detected")
            
            # Test reading back with different cases - each should have its own content
            read_tests = [
                ("TestFile.md", "Content 1"),
                ("testfile.md", "Content 2"), 
                ("TESTFILE.md", "Content 3"),
            ]
            
            for filename, expected_partial in read_tests:
                result = manager.read_file("case-test", filename)
                assert result["success"] is True
                assert expected_partial in result["content"]
                print(f"✓ Successfully read {filename}")
        
        else:
            # Unexpected behavior - log for investigation
            print(f"⚠ Unexpected file count: {file_count}")
        
        print("✓ Case sensitivity handling verified for this filesystem")
    
    @pytest.mark.skipif(
        not hasattr(tempfile, 'TemporaryDirectory'),
        reason="TemporaryDirectory not available"
    )
    def test_temporary_directory_cleanup(self, temp_collections_dir):
        """Test proper cleanup of temporary resources."""
        manager = CollectionFileManager(temp_collections_dir)
        
        # Create and use a collection
        manager.create_collection("cleanup-test")
        
        # Add some content
        for i in range(5):
            manager.save_file(
                "cleanup-test",
                f"temp_file_{i}.md",
                f"Temporary content {i}"
            )
        
        # Verify collection exists and has content
        collection_info = manager.get_collection_info("cleanup-test")
        assert collection_info["success"] is True
        assert collection_info["collection"]["file_count"] == 5
        
        # Test deletion cleanup
        delete_result = manager.delete_collection("cleanup-test")
        assert delete_result["success"] is True
        
        # Verify cleanup was thorough
        collection_path = temp_collections_dir / "cleanup-test"
        assert not collection_path.exists()
        
        # Verify other collections are unaffected
        collections = manager.list_collections()
        assert collections["success"] is True
        
        remaining_collections = [c["name"] for c in collections["collections"]]
        assert "cleanup-test" not in remaining_collections
        
        print("✓ Cleanup and resource management working correctly")