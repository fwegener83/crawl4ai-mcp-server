"""
Unit tests for FilesystemMetadataReconciler.

Tests the reconciliation between filesystem state and metadata database.
"""

import pytest
import tempfile
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from tools.filesystem_metadata_reconciler import (
    FilesystemMetadataReconciler, 
    FileInfo, 
    ReconciliationResult
)


class TestFileInfo:
    """Test FileInfo named tuple."""
    
    def test_file_info_creation(self):
        """Test FileInfo creation and attributes."""
        modified_time = datetime.now(timezone.utc)
        file_info = FileInfo(
            path="test.md",
            content_hash="abcd1234",
            size=256,
            modified_time=modified_time
        )
        
        assert file_info.path == "test.md"
        assert file_info.content_hash == "abcd1234"
        assert file_info.size == 256
        assert file_info.modified_time == modified_time


class TestReconciliationResult:
    """Test ReconciliationResult named tuple."""
    
    def test_reconciliation_result_creation(self):
        """Test ReconciliationResult creation."""
        actions = [{"action": "test"}]
        result = ReconciliationResult(
            files_added=1,
            files_modified=2,
            files_deleted=3,
            actions=actions
        )
        
        assert result.files_added == 1
        assert result.files_modified == 2
        assert result.files_deleted == 3
        assert result.actions == actions
    
    def test_has_changes_true(self):
        """Test has_changes property when changes exist."""
        result = ReconciliationResult(1, 0, 0, [])
        assert result.has_changes is True
        
        result = ReconciliationResult(0, 1, 0, [])
        assert result.has_changes is True
        
        result = ReconciliationResult(0, 0, 1, [])
        assert result.has_changes is True
        
        result = ReconciliationResult(1, 1, 1, [])
        assert result.has_changes is True
    
    def test_has_changes_false(self):
        """Test has_changes property when no changes exist."""
        result = ReconciliationResult(0, 0, 0, [])
        assert result.has_changes is False


@pytest.mark.asyncio
class TestFilesystemMetadataReconciler:
    """Test FilesystemMetadataReconciler functionality."""

    @pytest.fixture
    def temp_filesystem_base(self):
        """Create temporary filesystem base directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def mock_metadata_store(self):
        """Create mock metadata store."""
        return MagicMock()

    @pytest.fixture
    def reconciler(self, temp_filesystem_base, mock_metadata_store):
        """Create FilesystemMetadataReconciler instance."""
        return FilesystemMetadataReconciler(temp_filesystem_base, mock_metadata_store)

    def test_initialization(self, temp_filesystem_base, mock_metadata_store):
        """Test reconciler initialization."""
        reconciler = FilesystemMetadataReconciler(temp_filesystem_base, mock_metadata_store)
        
        assert reconciler.fs_base == temp_filesystem_base
        assert reconciler.metadata_store == mock_metadata_store

    def test_is_allowed_file_valid_extensions(self, reconciler):
        """Test allowed file extension validation."""
        allowed_files = [
            Path("test.md"),
            Path("test.txt"),
            Path("test.json"),
            Path("test.yaml"),
            Path("test.yml"),
            Path("test.csv")
        ]
        
        for file_path in allowed_files:
            assert reconciler._is_allowed_file(file_path) is True

    def test_is_allowed_file_invalid_extensions(self, reconciler):
        """Test disallowed file extension validation."""
        disallowed_files = [
            Path("test.exe"),
            Path("test.py"),
            Path("test.js"),
            Path("test.html"),
            Path("test"),  # No extension
        ]
        
        for file_path in disallowed_files:
            assert reconciler._is_allowed_file(file_path) is False

    async def test_scan_filesystem_files_empty_collection(self, reconciler):
        """Test scanning empty or non-existent collection."""
        files = await reconciler._scan_filesystem_files("nonexistent_collection")
        assert files == []

    async def test_scan_filesystem_files_with_files(self, reconciler, temp_filesystem_base):
        """Test scanning collection with various files."""
        collection_path = temp_filesystem_base / "test_collection"
        collection_path.mkdir()
        
        # Create test files
        (collection_path / "test1.md").write_text("# Test 1", encoding='utf-8')
        (collection_path / "test2.txt").write_text("Test 2 content", encoding='utf-8')
        (collection_path / "subfolder").mkdir()
        (collection_path / "subfolder" / "test3.yaml").write_text("key: value", encoding='utf-8')
        
        # Create files that should be ignored
        (collection_path / ".hidden.md").write_text("Hidden file", encoding='utf-8')
        (collection_path / "test.exe").write_text("Executable", encoding='utf-8')
        
        files = await reconciler._scan_filesystem_files("test_collection")
        
        # Should find 3 allowed files, ignoring hidden and disallowed files
        assert len(files) == 3
        
        # Check file info
        file_paths = {f.path for f in files}
        assert "test1.md" in file_paths
        assert "test2.txt" in file_paths
        assert "subfolder/test3.yaml" in file_paths
        assert ".hidden.md" not in file_paths
        assert "test.exe" not in file_paths
        
        # Check file info details
        test1_file = next(f for f in files if f.path == "test1.md")
        assert test1_file.content_hash == hashlib.sha256("# Test 1".encode('utf-8')).hexdigest()
        assert test1_file.size == len("# Test 1".encode('utf-8'))
        assert isinstance(test1_file.modified_time, datetime)

    async def test_reconcile_collection_no_changes(self, reconciler, mock_metadata_store):
        """Test reconciliation when no changes are detected."""
        # Mock filesystem scan returns no files
        reconciler._scan_filesystem_files = AsyncMock(return_value=[])
        
        # Mock metadata store returns no files
        mock_metadata_store.get_collection_files = AsyncMock(return_value={
            "success": True,
            "files": []
        })
        
        result = await reconciler.reconcile_collection("test_collection")
        
        assert isinstance(result, ReconciliationResult)
        assert result.files_added == 0
        assert result.files_modified == 0
        assert result.files_deleted == 0
        assert not result.has_changes
        assert len(result.actions) == 0

    async def test_reconcile_collection_new_files(self, reconciler, mock_metadata_store):
        """Test reconciliation when new files are detected."""
        # Mock filesystem scan returns new files
        new_file = FileInfo(
            path="new_file.md",
            content_hash="hash1",
            size=100,
            modified_time=datetime.now(timezone.utc)
        )
        reconciler._scan_filesystem_files = AsyncMock(return_value=[new_file])
        
        # Mock metadata store returns no existing files
        mock_metadata_store.get_collection_files = AsyncMock(return_value={
            "success": True,
            "files": []
        })
        
        # Mock successful file metadata update
        mock_metadata_store.update_file_metadata = AsyncMock(return_value={
            "success": True
        })
        
        # Mock reconciliation logging
        mock_metadata_store.log_reconciliation = AsyncMock(return_value={"success": True})
        
        result = await reconciler.reconcile_collection("test_collection")
        
        assert result.files_added == 1
        assert result.files_modified == 0
        assert result.files_deleted == 0
        assert result.has_changes
        assert len(result.actions) == 1
        assert result.actions[0]["action"] == "added_to_metadata"
        assert result.actions[0]["file"] == "new_file.md"

    async def test_reconcile_collection_deleted_files(self, reconciler, mock_metadata_store):
        """Test reconciliation when files are deleted from filesystem."""
        # Mock filesystem scan returns no files
        reconciler._scan_filesystem_files = AsyncMock(return_value=[])
        
        # Mock metadata store returns existing file
        mock_metadata_store.get_collection_files = AsyncMock(return_value={
            "success": True,
            "files": [
                {
                    "file_path": "deleted_file.md",
                    "content_hash": "hash1",
                    "file_size": 100
                }
            ]
        })
        
        # Mock successful file metadata deletion
        mock_metadata_store.delete_file_metadata = AsyncMock(return_value={
            "success": True
        })
        
        # Mock reconciliation logging
        mock_metadata_store.log_reconciliation = AsyncMock(return_value={"success": True})
        
        result = await reconciler.reconcile_collection("test_collection")
        
        assert result.files_added == 0
        assert result.files_modified == 0
        assert result.files_deleted == 1
        assert result.has_changes
        assert len(result.actions) == 1
        assert result.actions[0]["action"] == "removed_from_metadata"
        assert result.actions[0]["file"] == "deleted_file.md"

    async def test_reconcile_collection_modified_files(self, reconciler, mock_metadata_store):
        """Test reconciliation when files are modified."""
        # Mock filesystem scan returns modified file
        modified_file = FileInfo(
            path="modified_file.md",
            content_hash="new_hash",
            size=200,
            modified_time=datetime.now(timezone.utc)
        )
        reconciler._scan_filesystem_files = AsyncMock(return_value=[modified_file])
        
        # Mock metadata store returns existing file with different hash
        mock_metadata_store.get_collection_files = AsyncMock(return_value={
            "success": True,
            "files": [
                {
                    "file_path": "modified_file.md",
                    "content_hash": "old_hash",
                    "file_size": 100,
                    "vector_sync_status": "synced"
                }
            ]
        })
        
        # Mock successful metadata update
        mock_metadata_store.update_file_metadata = AsyncMock(return_value={
            "success": True
        })
        
        # Mock reconciliation logging
        mock_metadata_store.log_reconciliation = AsyncMock(return_value={"success": True})
        
        result = await reconciler.reconcile_collection("test_collection")
        
        assert result.files_added == 0
        assert result.files_modified == 1
        assert result.files_deleted == 0
        assert result.has_changes
        assert len(result.actions) == 1
        assert result.actions[0]["action"] == "detected_modification"
        assert result.actions[0]["file"] == "modified_file.md"
        assert "old_hash" in result.actions[0]["reason"]
        assert "new_hash" in result.actions[0]["reason"]

    async def test_reconcile_collection_complex_scenario(self, reconciler, mock_metadata_store):
        """Test reconciliation with multiple types of changes."""
        # Mock filesystem scan returns mixed files
        fs_files = [
            FileInfo("existing_unchanged.md", "hash1", 100, datetime.now(timezone.utc)),
            FileInfo("existing_modified.md", "new_hash", 200, datetime.now(timezone.utc)),
            FileInfo("new_file.md", "hash3", 150, datetime.now(timezone.utc))
        ]
        reconciler._scan_filesystem_files = AsyncMock(return_value=fs_files)
        
        # Mock metadata store returns existing files
        mock_metadata_store.get_collection_files = AsyncMock(return_value={
            "success": True,
            "files": [
                {
                    "file_path": "existing_unchanged.md",
                    "content_hash": "hash1",
                    "file_size": 100,
                    "vector_sync_status": "synced"
                },
                {
                    "file_path": "existing_modified.md", 
                    "content_hash": "old_hash",
                    "file_size": 100,
                    "vector_sync_status": "synced"
                },
                {
                    "file_path": "deleted_file.md",
                    "content_hash": "hash4",
                    "file_size": 300,
                    "vector_sync_status": "not_synced"
                }
            ]
        })
        
        # Mock metadata operations
        mock_metadata_store.update_file_metadata = AsyncMock(return_value={"success": True})
        mock_metadata_store.delete_file_metadata = AsyncMock(return_value={"success": True})
        mock_metadata_store.log_reconciliation = AsyncMock(return_value={"success": True})
        
        result = await reconciler.reconcile_collection("test_collection")
        
        assert result.files_added == 1  # new_file.md
        assert result.files_modified == 1  # existing_modified.md
        assert result.files_deleted == 1  # deleted_file.md
        assert result.has_changes
        assert len(result.actions) == 3

    async def test_handle_new_file_success(self, reconciler, mock_metadata_store):
        """Test handling new file addition."""
        new_file = FileInfo("new.md", "hash1", 100, datetime.now(timezone.utc))
        actions = []
        
        mock_metadata_store.update_file_metadata = AsyncMock(return_value={
            "success": True
        })
        
        await reconciler._handle_new_file("test_collection", new_file, actions)
        
        assert len(actions) == 1
        assert actions[0]["action"] == "added_to_metadata"
        assert actions[0]["file"] == "new.md"
        assert actions[0]["content_hash"] == "hash1"

    async def test_handle_new_file_failure(self, reconciler, mock_metadata_store):
        """Test handling new file addition failure."""
        new_file = FileInfo("new.md", "hash1", 100, datetime.now(timezone.utc))
        actions = []
        
        mock_metadata_store.update_file_metadata = AsyncMock(return_value={
            "success": False,
            "error": "Database error"
        })
        
        await reconciler._handle_new_file("test_collection", new_file, actions)
        
        assert len(actions) == 1
        assert actions[0]["action"] == "failed_to_add"
        assert actions[0]["file"] == "new.md"
        assert "Database error" in actions[0]["reason"]

    async def test_handle_deleted_file_success(self, reconciler, mock_metadata_store):
        """Test handling deleted file removal."""
        actions = []
        
        mock_metadata_store.delete_file_metadata = AsyncMock(return_value={
            "success": True
        })
        
        await reconciler._handle_deleted_file("test_collection", "deleted.md", actions)
        
        assert len(actions) == 1
        assert actions[0]["action"] == "removed_from_metadata"
        assert actions[0]["file"] == "deleted.md"

    async def test_handle_deleted_file_failure(self, reconciler, mock_metadata_store):
        """Test handling deleted file removal failure."""
        actions = []
        
        mock_metadata_store.delete_file_metadata = AsyncMock(return_value={
            "success": False,
            "error": "File not found"
        })
        
        await reconciler._handle_deleted_file("test_collection", "deleted.md", actions)
        
        assert len(actions) == 1
        assert actions[0]["action"] == "failed_to_remove"
        assert actions[0]["file"] == "deleted.md"

    async def test_handle_potentially_modified_file_changed(self, reconciler, mock_metadata_store):
        """Test handling modified file detection."""
        fs_file = FileInfo("test.md", "new_hash", 200, datetime.now(timezone.utc))
        db_file = {
            "content_hash": "old_hash",
            "file_size": 100,
            "vector_sync_status": "synced",
            "source_url": "https://example.com"
        }
        actions = []
        
        mock_metadata_store.update_file_metadata = AsyncMock(return_value={
            "success": True
        })
        
        result = await reconciler._handle_potentially_modified_file(
            "test_collection", fs_file, db_file, actions
        )
        
        assert result is True  # File was modified
        assert len(actions) == 1
        assert actions[0]["action"] == "detected_modification"
        assert actions[0]["file"] == "test.md"
        assert actions[0]["new_sync_status"] == "not_synced"
        assert actions[0]["previous_sync_status"] == "synced"
        
        # Check metadata update was called with correct parameters
        mock_metadata_store.update_file_metadata.assert_called_once_with(
            collection_name="test_collection",
            file_path="test.md",
            content_hash="new_hash",
            file_size=200,
            vector_sync_status="not_synced",
            source_url="https://example.com"
        )

    async def test_handle_potentially_modified_file_unchanged(self, reconciler, mock_metadata_store):
        """Test handling file with no changes."""
        fs_file = FileInfo("test.md", "same_hash", 100, datetime.now(timezone.utc))
        db_file = {
            "content_hash": "same_hash",
            "file_size": 100,
            "vector_sync_status": "synced"
        }
        actions = []
        
        result = await reconciler._handle_potentially_modified_file(
            "test_collection", fs_file, db_file, actions
        )
        
        assert result is False  # File was not modified
        assert len(actions) == 0
        
        # Metadata update should not be called
        mock_metadata_store.update_file_metadata.assert_not_called()

    async def test_get_collection_sync_summary_success(self, reconciler, mock_metadata_store):
        """Test getting collection sync status summary."""
        mock_metadata_store.get_collection_files = AsyncMock(return_value={
            "success": True,
            "files": [
                {"vector_sync_status": "synced"},
                {"vector_sync_status": "not_synced"},
                {"vector_sync_status": "not_synced"},
                {"vector_sync_status": "sync_error"}
            ]
        })
        
        mock_metadata_store.get_last_reconciliation = AsyncMock(return_value={
            "timestamp": "2024-01-01T00:00:00Z",
            "files_added": 1
        })
        
        result = await reconciler.get_collection_sync_summary("test_collection")
        
        assert result["success"] is True
        assert result["collection_name"] == "test_collection"
        assert result["overall_status"] == "has_unsynced_files"
        assert result["sync_available"] is True
        assert result["total_files"] == 4
        
        status_counts = result["status_counts"]
        assert status_counts["synced"] == 1
        assert status_counts["not_synced"] == 2
        assert status_counts["sync_error"] == 1
        assert status_counts["syncing"] == 0

    async def test_get_collection_sync_summary_fully_synced(self, reconciler, mock_metadata_store):
        """Test sync summary when collection is fully synced."""
        mock_metadata_store.get_collection_files = AsyncMock(return_value={
            "success": True,
            "files": [
                {"vector_sync_status": "synced"},
                {"vector_sync_status": "synced"}
            ]
        })
        
        mock_metadata_store.get_last_reconciliation = AsyncMock(return_value=None)
        
        result = await reconciler.get_collection_sync_summary("test_collection")
        
        assert result["success"] is True
        assert result["overall_status"] == "fully_synced"
        assert result["sync_available"] is False

    async def test_get_collection_sync_summary_sync_in_progress(self, reconciler, mock_metadata_store):
        """Test sync summary when sync is in progress."""
        mock_metadata_store.get_collection_files = AsyncMock(return_value={
            "success": True,
            "files": [
                {"vector_sync_status": "syncing"},
                {"vector_sync_status": "synced"}
            ]
        })
        
        mock_metadata_store.get_last_reconciliation = AsyncMock(return_value=None)
        
        result = await reconciler.get_collection_sync_summary("test_collection")
        
        assert result["success"] is True
        assert result["overall_status"] == "sync_in_progress"
        assert result["sync_available"] is False

    async def test_reconcile_collection_metadata_failure(self, reconciler, mock_metadata_store):
        """Test reconciliation when metadata store fails."""
        reconciler._scan_filesystem_files = AsyncMock(return_value=[])
        
        mock_metadata_store.get_collection_files = AsyncMock(return_value={
            "success": False,
            "error": "Database connection failed"
        })
        
        result = await reconciler.reconcile_collection("test_collection")
        
        assert result.files_added == 0
        assert result.files_modified == 0
        assert result.files_deleted == 0
        assert not result.has_changes