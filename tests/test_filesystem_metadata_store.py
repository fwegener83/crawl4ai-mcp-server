"""
Unit tests for FilesystemMetadataStore.

Tests the SQLite metadata store for filesystem-based collections.
"""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime, timezone

from tools.filesystem_metadata_store import FilesystemMetadataStore


class TestFilesystemMetadataStore:
    """Test FilesystemMetadataStore functionality."""

    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir) / "test_metadata.db"

    @pytest.fixture
    def store(self):
        """Create FilesystemMetadataStore instance with unique path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            store = FilesystemMetadataStore(db_path)
            yield store

    def test_initialization_creates_path(self, temp_db_path):
        """Test initialization creates parent directory."""
        # Ensure parent doesn't exist
        temp_db_path.parent.rmdir()
        assert not temp_db_path.parent.exists()
        
        store = FilesystemMetadataStore(temp_db_path)
        assert temp_db_path.parent.exists()
        assert store.db_path == temp_db_path

    @pytest.mark.asyncio
    async def test_create_collection_success(self, store):
        """Test successful collection creation."""
        result = await store.create_collection("test_collection", "Test description")
        
        assert result["success"] is True
        assert result["name"] == "test_collection"
        assert "created successfully" in result["message"]

    @pytest.mark.asyncio
    async def test_create_collection_duplicate(self, store):
        """Test creating duplicate collection fails."""
        # Create first collection
        await store.create_collection("test_collection", "First")
        
        # Try to create duplicate
        result = await store.create_collection("test_collection", "Second")
        
        assert result["success"] is False
        assert "already exists" in result["error"]

    @pytest.mark.asyncio  
    @pytest.mark.asyncio
    async def test_collection_exists(self, store):
        """Test collection existence checking."""
        # Collection doesn't exist initially
        assert await store.collection_exists("test_collection") is False
        
        # Create collection
        await store.create_collection("test_collection")
        
        # Now it exists
        assert await store.collection_exists("test_collection") is True

    @pytest.mark.asyncio
    async def test_list_collections_empty(self, store):
        """Test listing collections when none exist."""
        result = await store.list_collections()
        
        assert result["success"] is True
        assert result["collections"] == []

    @pytest.mark.asyncio
    async def test_list_collections_with_files(self, store):
        """Test listing collections with file counts."""
        # Create collections
        await store.create_collection("collection1", "First collection")
        await store.create_collection("collection2", "Second collection")
        
        # Add some files
        await store.update_file_metadata(
            collection_name="collection1",
            file_path="test1.md",
            content_hash="hash1",
            file_size=100
        )
        await store.update_file_metadata(
            collection_name="collection1", 
            file_path="test2.md",
            content_hash="hash2",
            file_size=200
        )
        await store.update_file_metadata(
            collection_name="collection2",
            file_path="test3.md",
            content_hash="hash3",
            file_size=150
        )
        
        result = await store.list_collections()
        
        assert result["success"] is True
        assert len(result["collections"]) == 2
        
        # Check file counts
        collections = {c["name"]: c for c in result["collections"]}
        assert collections["collection1"]["file_count"] == 2
        assert collections["collection2"]["file_count"] == 1

    @pytest.mark.asyncio
    async def test_get_collection_success(self, store):
        """Test getting collection information."""
        await store.create_collection("test_collection", "Test description")
        
        # Add a file
        await store.update_file_metadata(
            collection_name="test_collection",
            file_path="test.md",
            content_hash="hash1",
            file_size=500
        )
        
        result = await store.get_collection("test_collection")
        
        assert result["success"] is True
        collection = result["collection"]
        assert collection["name"] == "test_collection"
        assert collection["description"] == "Test description"
        assert collection["file_count"] == 1
        assert collection["total_size"] == 500

    @pytest.mark.asyncio
    async def test_get_collection_not_found(self, store):
        """Test getting non-existent collection."""
        result = await store.get_collection("nonexistent")
        
        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_delete_collection_success(self, store):
        """Test successful collection deletion."""
        await store.create_collection("test_collection")
        
        # Add some files
        await store.update_file_metadata(
            collection_name="test_collection",
            file_path="test1.md", 
            content_hash="hash1",
            file_size=100
        )
        await store.update_file_metadata(
            collection_name="test_collection",
            file_path="test2.md",
            content_hash="hash2", 
            file_size=200
        )
        
        result = await store.delete_collection("test_collection")
        
        assert result["success"] is True
        assert result["deleted_files"] == 2
        assert "deleted successfully" in result["message"]
        
        # Verify collection is gone
        assert await store.collection_exists("test_collection") is False

    @pytest.mark.asyncio
    async def test_delete_collection_not_found(self, store):
        """Test deleting non-existent collection."""
        result = await store.delete_collection("nonexistent")
        
        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_update_file_metadata_new_file(self, store):
        """Test adding metadata for new file."""
        await store.create_collection("test_collection")
        
        result = await store.update_file_metadata(
            collection_name="test_collection",
            file_path="test.md",
            content_hash="abcd1234",
            file_size=256,
            vector_sync_status="not_synced",
            source_url="https://example.com"
        )
        
        assert result["success"] is True
        assert result["file_path"] == "test.md"
        assert result["content_hash"] == "abcd1234"

    @pytest.mark.asyncio
    async def test_update_file_metadata_existing_file(self, store):
        """Test updating metadata for existing file."""
        await store.create_collection("test_collection")
        
        # Add initial file
        await store.update_file_metadata(
            collection_name="test_collection",
            file_path="test.md",
            content_hash="hash1",
            file_size=100
        )
        
        # Update same file
        result = await store.update_file_metadata(
            collection_name="test_collection",
            file_path="test.md",
            content_hash="hash2",
            file_size=200,
            vector_sync_status="synced"
        )
        
        assert result["success"] is True
        assert result["content_hash"] == "hash2"
        
        # Verify updated metadata
        file_result = await store.get_file_metadata("test_collection", "test.md")
        assert file_result["success"] is True
        metadata = file_result["metadata"]
        assert metadata["content_hash"] == "hash2"
        assert metadata["file_size"] == 200
        assert metadata["vector_sync_status"] == "synced"

    @pytest.mark.asyncio
    async def test_get_file_metadata_success(self, store):
        """Test getting file metadata."""
        await store.create_collection("test_collection")
        
        # Add file
        await store.update_file_metadata(
            collection_name="test_collection",
            file_path="test.md",
            content_hash="abcd1234",
            file_size=512,
            vector_sync_status="synced",
            source_url="https://example.com/page"
        )
        
        result = await store.get_file_metadata("test_collection", "test.md")
        
        assert result["success"] is True
        metadata = result["metadata"]
        assert metadata["file_path"] == "test.md"
        assert metadata["content_hash"] == "abcd1234"
        assert metadata["file_size"] == 512
        assert metadata["vector_sync_status"] == "synced"
        assert metadata["source_url"] == "https://example.com/page"

    @pytest.mark.asyncio
    async def test_get_file_metadata_not_found(self, store):
        """Test getting metadata for non-existent file."""
        await store.create_collection("test_collection")
        
        result = await store.get_file_metadata("test_collection", "nonexistent.md")
        
        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_get_collection_files(self, store):
        """Test getting all files in a collection."""
        await store.create_collection("test_collection")
        
        # Add multiple files
        files_data = [
            ("file1.md", "hash1", 100, "synced"),
            ("file2.md", "hash2", 200, "not_synced"), 
            ("folder/file3.md", "hash3", 150, "sync_error")
        ]
        
        for file_path, content_hash, size, sync_status in files_data:
            await store.update_file_metadata(
                collection_name="test_collection",
                file_path=file_path,
                content_hash=content_hash,
                file_size=size,
                vector_sync_status=sync_status
            )
        
        result = await store.get_collection_files("test_collection")
        
        assert result["success"] is True
        files = result["files"]
        assert len(files) == 3
        
        # Check files are sorted by path
        assert files[0]["file_path"] == "file1.md"
        assert files[1]["file_path"] == "file2.md"
        assert files[2]["file_path"] == "folder/file3.md"
        
        # Check sync statuses
        sync_statuses = [f["vector_sync_status"] for f in files]
        assert "synced" in sync_statuses
        assert "not_synced" in sync_statuses
        assert "sync_error" in sync_statuses

    @pytest.mark.asyncio
    async def test_delete_file_metadata_success(self, store):
        """Test successful file metadata deletion."""
        await store.create_collection("test_collection")
        
        # Add file
        await store.update_file_metadata(
            collection_name="test_collection",
            file_path="test.md",
            content_hash="hash1",
            file_size=100
        )
        
        # Delete file metadata
        result = await store.delete_file_metadata("test_collection", "test.md")
        
        assert result["success"] is True
        assert "deleted" in result["message"]
        
        # Verify file is gone
        file_result = await store.get_file_metadata("test_collection", "test.md")
        assert file_result["success"] is False

    @pytest.mark.asyncio
    async def test_delete_file_metadata_not_found(self, store):
        """Test deleting non-existent file metadata."""
        await store.create_collection("test_collection")
        
        result = await store.delete_file_metadata("test_collection", "nonexistent.md")
        
        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_log_reconciliation(self, store):
        """Test logging reconciliation actions."""
        await store.create_collection("test_collection")
        
        actions = [
            {
                "action": "added_to_metadata",
                "file": "new_file.md",
                "reason": "New file detected"
            },
            {
                "action": "detected_modification",
                "file": "changed_file.md", 
                "reason": "Content hash changed"
            }
        ]
        
        result = await store.log_reconciliation(
            collection_name="test_collection",
            actions=actions,
            files_added=1,
            files_modified=1,
            files_deleted=0
        )
        
        assert result["success"] is True
        assert "logged successfully" in result["message"]

    @pytest.mark.asyncio
    async def test_get_last_reconciliation(self, store):
        """Test getting last reconciliation information."""
        await store.create_collection("test_collection")
        
        # No reconciliation yet
        result = await store.get_last_reconciliation("test_collection")
        assert result is None
        
        # Log a reconciliation
        actions = [{"action": "test", "file": "test.md"}]
        await store.log_reconciliation(
            collection_name="test_collection",
            actions=actions,
            files_added=1,
            files_modified=0,
            files_deleted=0
        )
        
        # Get last reconciliation
        result = await store.get_last_reconciliation("test_collection")
        assert result is not None
        assert result["files_added"] == 1
        assert result["files_modified"] == 0
        assert result["files_deleted"] == 0
        assert len(result["actions"]) == 1
        assert result["actions"][0]["action"] == "test"

    @pytest.mark.asyncio
    async def test_multiple_reconciliations_ordering(self, store):
        """Test that get_last_reconciliation returns the most recent."""
        await store.create_collection("test_collection")
        
        # Log first reconciliation
        await store.log_reconciliation(
            collection_name="test_collection",
            actions=[{"action": "first"}],
            files_added=1
        )
        
        # Log second reconciliation
        await store.log_reconciliation(
            collection_name="test_collection",
            actions=[{"action": "second"}],
            files_added=2
        )
        
        # Should get the second (most recent) one
        result = await store.get_last_reconciliation("test_collection")
        assert result is not None
        assert result["files_added"] == 2
        assert result["actions"][0]["action"] == "second"

    @pytest.mark.asyncio
    async def test_cascade_deletion(self, store):
        """Test that deleting collection removes all related data."""
        await store.create_collection("test_collection")
        
        # Add files and reconciliation logs
        await store.update_file_metadata(
            collection_name="test_collection",
            file_path="test.md",
            content_hash="hash1",
            file_size=100
        )
        
        await store.log_reconciliation(
            collection_name="test_collection",
            actions=[{"action": "test"}],
            files_added=1
        )
        
        # Delete collection
        await store.delete_collection("test_collection")
        
        # Verify all related data is gone
        files_result = await store.get_collection_files("test_collection")
        assert files_result["success"] is False
        
        reconciliation_result = await store.get_last_reconciliation("test_collection")
        assert reconciliation_result is None

    @pytest.mark.asyncio
    async def test_upsert_behavior(self, store):
        """Test INSERT OR REPLACE behavior preserves created_at."""
        await store.create_collection("test_collection")
        
        # Add initial file
        await store.update_file_metadata(
            collection_name="test_collection",
            file_path="test.md",
            content_hash="hash1",
            file_size=100
        )
        
        # Get initial created_at
        initial_result = await store.get_file_metadata("test_collection", "test.md")
        initial_created_at = initial_result["metadata"]["created_at"]
        
        # Update same file
        await store.update_file_metadata(
            collection_name="test_collection",
            file_path="test.md",
            content_hash="hash2",
            file_size=200
        )
        
        # Check created_at is preserved but modified_at is updated
        updated_result = await store.get_file_metadata("test_collection", "test.md")
        updated_metadata = updated_result["metadata"]
        
        assert updated_metadata["created_at"] == initial_created_at
        assert updated_metadata["modified_at"] != initial_created_at
        assert updated_metadata["content_hash"] == "hash2"