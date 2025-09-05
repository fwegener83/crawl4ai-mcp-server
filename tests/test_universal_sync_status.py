"""
Test universal sync status API (Phase 3.1).

Tests the new universal sync summary method that works with both storage modes.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from services.vector_sync_service import VectorSyncService
from services.collection_service import CollectionService


class TestUniversalSyncStatus:
    """Test universal sync status functionality."""

    def setup_method(self):
        """Setup method to clear environment variables."""
        self.original_env = {}
        env_vars = [
            "COLLECTION_STORAGE_MODE", 
            "FILESYSTEM_COLLECTIONS_PATH",
            "FILESYSTEM_METADATA_DB_PATH", 
            "FILESYSTEM_AUTO_RECONCILE",
            "CONTEXT42_HOME",
            "COLLECTIONS_DB_PATH"
        ]
        
        for var in env_vars:
            self.original_env[var] = os.environ.get(var)
            if var in os.environ:
                del os.environ[var]

    def teardown_method(self):
        """Restore original environment variables."""
        for var, value in self.original_env.items():
            if value is not None:
                os.environ[var] = value
            elif var in os.environ:
                del os.environ[var]

    @pytest.mark.asyncio
    async def test_sync_summary_sqlite_mode(self):
        """Test sync summary with SQLite storage mode."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Setup SQLite mode
            os.environ["COLLECTION_STORAGE_MODE"] = "sqlite"
            os.environ["COLLECTIONS_DB_PATH"] = str(Path(temp_dir) / "test.db")
            
            # Create collection service
            collection_service = CollectionService()
            
            # Mock list_files_in_collection to return sample files
            collection_service.list_files_in_collection = AsyncMock(return_value={
                "success": True,
                "files": [
                    {"name": "file1.md", "vector_sync_status": "synced"},
                    {"name": "file2.md", "vector_sync_status": "not_synced"},
                    {"name": "file3.md", "vector_sync_status": "sync_error"},
                ]
            })
            
            # Create vector sync service
            vector_service = VectorSyncService(collection_service=collection_service)
            
            # Test sync summary
            result = await vector_service.get_collection_sync_summary("test_collection")
            
            # Verify results
            assert result["success"] is True
            assert result["collection_name"] == "test_collection"
            assert result["storage_mode"] == "sqlite"
            assert result["total_files"] == 3
            assert result["status_counts"]["synced"] == 1
            assert result["status_counts"]["not_synced"] == 1
            assert result["status_counts"]["sync_error"] == 1
            assert result["overall_status"] == "has_unsynced_files"

    @pytest.mark.asyncio
    async def test_sync_summary_filesystem_mode(self):
        """Test sync summary with filesystem storage mode."""
        with tempfile.TemporaryDirectory() as temp_dir:
            collections_path = Path(temp_dir) / "collections"
            metadata_db_path = Path(temp_dir) / "metadata.db"
            
            # Setup filesystem mode
            os.environ["COLLECTION_STORAGE_MODE"] = "filesystem"
            os.environ["FILESYSTEM_COLLECTIONS_PATH"] = str(collections_path)
            os.environ["FILESYSTEM_METADATA_DB_PATH"] = str(metadata_db_path)
            
            # Create collection service
            collection_service = CollectionService()
            
            # Mock list_files_in_collection to return sample files
            collection_service.list_files_in_collection = AsyncMock(return_value={
                "success": True,
                "files": [
                    {"name": "file1.md", "vector_sync_status": "synced"},
                    {"name": "file2.md", "vector_sync_status": "synced"},
                ]
            })
            
            # Create vector sync service
            vector_service = VectorSyncService(collection_service=collection_service)
            
            # Test sync summary
            result = await vector_service.get_collection_sync_summary("test_collection")
            
            # Verify results
            assert result["success"] is True
            assert result["collection_name"] == "test_collection"
            assert result["storage_mode"] == "filesystem"
            assert result["total_files"] == 2
            assert result["status_counts"]["synced"] == 2
            assert result["status_counts"]["not_synced"] == 0
            assert result["overall_status"] == "fully_synced"

    @pytest.mark.asyncio
    async def test_sync_summary_empty_collection(self):
        """Test sync summary with empty collection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ["COLLECTION_STORAGE_MODE"] = "sqlite"
            os.environ["COLLECTIONS_DB_PATH"] = str(Path(temp_dir) / "test.db")
            
            collection_service = CollectionService()
            collection_service.list_files_in_collection = AsyncMock(return_value={
                "success": True,
                "files": []
            })
            
            vector_service = VectorSyncService(collection_service=collection_service)
            result = await vector_service.get_collection_sync_summary("empty_collection")
            
            assert result["success"] is True
            assert result["total_files"] == 0
            assert result["overall_status"] == "empty"
            assert result["sync_available"] is False

    @pytest.mark.asyncio
    async def test_sync_summary_collection_error(self):
        """Test sync summary when collection service fails."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ["COLLECTION_STORAGE_MODE"] = "sqlite"
            os.environ["COLLECTIONS_DB_PATH"] = str(Path(temp_dir) / "test.db")
            
            collection_service = CollectionService()
            collection_service.list_files_in_collection = AsyncMock(return_value={
                "success": False,
                "error": "Collection not found"
            })
            
            vector_service = VectorSyncService(collection_service=collection_service)
            result = await vector_service.get_collection_sync_summary("nonexistent")
            
            assert result["success"] is False
            assert "Collection not found" in result["error"]

    @pytest.mark.asyncio
    async def test_sync_summary_no_collection_service(self):
        """Test sync summary when no collection service is provided."""
        vector_service = VectorSyncService()  # No collection service
        result = await vector_service.get_collection_sync_summary("test_collection")
        
        assert result["success"] is False
        assert "Collection service not available" in result["error"]

    @pytest.mark.asyncio
    async def test_sync_summary_sync_status_variations(self):
        """Test sync summary with different sync status values."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ["COLLECTION_STORAGE_MODE"] = "sqlite"
            os.environ["COLLECTIONS_DB_PATH"] = str(Path(temp_dir) / "test.db")
            
            collection_service = CollectionService()
            collection_service.list_files_in_collection = AsyncMock(return_value={
                "success": True,
                "files": [
                    {"name": "file1.md", "vector_sync_status": "syncing"},
                    {"name": "file2.md", "vector_sync_status": "syncing"},
                    {"name": "file3.md", "vector_sync_status": "not_synced"},
                    {"name": "file4.md", "vector_sync_status": "unknown_status"},  # Should be treated as not_synced
                ]
            })
            
            vector_service = VectorSyncService(collection_service=collection_service)
            result = await vector_service.get_collection_sync_summary("test_collection")
            
            assert result["success"] is True
            assert result["total_files"] == 4
            assert result["status_counts"]["syncing"] == 2
            assert result["status_counts"]["not_synced"] == 2  # includes unknown_status
            assert result["overall_status"] == "sync_in_progress"
            assert result["sync_available"] is False  # Cannot sync while sync in progress

    @pytest.mark.asyncio
    async def test_sync_summary_vector_availability(self):
        """Test sync summary respects vector availability."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ["COLLECTION_STORAGE_MODE"] = "sqlite"
            os.environ["COLLECTIONS_DB_PATH"] = str(Path(temp_dir) / "test.db")
            
            collection_service = CollectionService()
            collection_service.list_files_in_collection = AsyncMock(return_value={
                "success": True,
                "files": [
                    {"name": "file1.md", "vector_sync_status": "not_synced"},
                ]
            })
            
            vector_service = VectorSyncService(collection_service=collection_service)
            
            # Mock vector availability to False
            vector_service.vector_available = False
            
            result = await vector_service.get_collection_sync_summary("test_collection")
            
            assert result["success"] is True
            assert result["overall_status"] == "has_unsynced_files"
            assert result["sync_available"] is False  # False because vector not available
            assert result["vector_available"] is False