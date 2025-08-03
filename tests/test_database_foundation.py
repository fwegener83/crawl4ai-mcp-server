"""
Tests for SQLite Database Foundation.
Comprehensive testing of database schema, repositories, and connection management.
"""
import pytest
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import patch

from tools.database import DatabaseManager, CollectionRepository, FileRepository


class TestDatabaseManager:
    """Test database manager initialization and schema."""
    
    def test_database_manager_initialization(self):
        """Test database manager creates schema correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test_collections.db"
            db_manager = DatabaseManager(db_path)
            
            # Check database file exists
            assert db_path.exists()
            
            # Check schema version
            assert db_manager.get_schema_version() == 1
            
            db_manager.close()
    
    def test_database_schema_creation(self):
        """Test that all required tables and indexes are created."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test_collections.db"
            db_manager = DatabaseManager(db_path)
            
            with db_manager.get_connection() as conn:
                # Check tables exist
                tables = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
                table_names = [row[0] for row in tables]
                
                assert "schema_version" in table_names
                assert "collections" in table_names
                assert "files" in table_names
                
                # Check indexes exist
                indexes = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'"
                ).fetchall()
                index_names = [row[0] for row in indexes]
                
                assert "idx_files_collection_id" in index_names
                assert "idx_files_folder_path" in index_names
                assert "idx_collections_name" in index_names
            
            db_manager.close()
    
    def test_database_connection_context_manager(self):
        """Test connection context manager handles transactions correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test_collections.db"
            db_manager = DatabaseManager(db_path)
            
            # Test successful transaction
            with db_manager.get_connection() as conn:
                conn.execute(
                    "INSERT INTO collections (id, name) VALUES (?, ?)",
                    ("test-id", "test-collection")
                )
            
            # Verify data was committed
            with db_manager.get_connection() as conn:
                result = conn.execute(
                    "SELECT name FROM collections WHERE id = ?",
                    ("test-id",)
                ).fetchone()
                assert result["name"] == "test-collection"
            
            db_manager.close()
    
    def test_database_connection_rollback_on_exception(self):
        """Test connection rolls back on exceptions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test_collections.db"
            db_manager = DatabaseManager(db_path)
            
            # Test transaction rollback on exception
            with pytest.raises(sqlite3.IntegrityError):
                with db_manager.get_connection() as conn:
                    conn.execute(
                        "INSERT INTO collections (id, name) VALUES (?, ?)",
                        ("test-id", "test-collection")
                    )
                    # Try to insert duplicate (should fail)
                    conn.execute(
                        "INSERT INTO collections (id, name) VALUES (?, ?)",
                        ("test-id", "duplicate-name")
                    )
            
            # Verify no data was committed
            with db_manager.get_connection() as conn:
                result = conn.execute(
                    "SELECT COUNT(*) as count FROM collections"
                ).fetchone()
                assert result["count"] == 0
            
            db_manager.close()
    
    @patch('tempfile.gettempdir')
    def test_database_fallback_location(self, mock_temp_dir):
        """Test database falls back to temp directory when home is not writable."""
        mock_temp_dir.return_value = "/tmp"
        
        # Mock Path.mkdir to raise OSError for home directory
        with patch('pathlib.Path.mkdir', side_effect=OSError("Permission denied")):
            db_manager = DatabaseManager()
            
            # Should fallback to temp directory
            assert "tmp" in str(db_manager.db_path) or "temp" in str(db_manager.db_path).lower()
            
            db_manager.close()


class TestCollectionRepository:
    """Test collection repository operations."""
    
    @pytest.fixture
    def db_manager(self):
        """Create temporary database manager for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test_collections.db"
            db_manager = DatabaseManager(db_path)
            yield db_manager
            db_manager.close()
    
    @pytest.fixture
    def collection_repo(self, db_manager):
        """Create collection repository for testing."""
        return CollectionRepository(db_manager)
    
    def test_create_collection_success(self, collection_repo):
        """Test successful collection creation."""
        result = collection_repo.create_collection(
            collection_id="test-collection-1",
            name="Test Collection",
            description="A test collection"
        )
        
        assert result["success"] is True
        assert result["collection_id"] == "test-collection-1"
        assert "created successfully" in result["message"]
    
    def test_create_collection_duplicate_name(self, collection_repo):
        """Test collection creation with duplicate name fails."""
        # Create first collection
        collection_repo.create_collection(
            collection_id="test-collection-1",
            name="Test Collection",
            description="First collection"
        )
        
        # Try to create second collection with same name
        result = collection_repo.create_collection(
            collection_id="test-collection-2",
            name="Test Collection",
            description="Second collection"
        )
        
        assert result["success"] is False
        assert "already exists" in result["error"]
    
    def test_list_collections_empty(self, collection_repo):
        """Test listing collections when none exist."""
        result = collection_repo.list_collections()
        
        assert result["success"] is True
        assert result["collections"] == []
    
    def test_list_collections_with_data(self, collection_repo):
        """Test listing collections with data."""
        # Create test collections
        collection_repo.create_collection("coll-1", "Collection 1", "First")
        collection_repo.create_collection("coll-2", "Collection 2", "Second")
        
        result = collection_repo.list_collections()
        
        assert result["success"] is True
        assert len(result["collections"]) == 2
        
        # Check collection data
        collections = result["collections"]
        names = [c["name"] for c in collections]
        assert "Collection 1" in names
        assert "Collection 2" in names
    
    def test_get_collection_exists(self, collection_repo):
        """Test getting existing collection."""
        collection_repo.create_collection("test-id", "Test Collection", "Description")
        
        result = collection_repo.get_collection("test-id")
        
        assert result["success"] is True
        assert result["collection"]["id"] == "test-id"
        assert result["collection"]["name"] == "Test Collection"
        assert result["collection"]["description"] == "Description"
        assert result["collection"]["file_count"] == 0
        assert result["collection"]["folders"] == []
    
    def test_get_collection_not_exists(self, collection_repo):
        """Test getting non-existent collection."""
        result = collection_repo.get_collection("non-existent")
        
        assert result["success"] is False
        assert "not found" in result["error"]
    
    def test_delete_collection_exists(self, collection_repo):
        """Test deleting existing collection."""
        collection_repo.create_collection("test-id", "Test Collection")
        
        result = collection_repo.delete_collection("test-id")
        
        assert result["success"] is True
        assert "deleted successfully" in result["message"]
        
        # Verify collection is gone
        get_result = collection_repo.get_collection("test-id")
        assert get_result["success"] is False
    
    def test_delete_collection_not_exists(self, collection_repo):
        """Test deleting non-existent collection."""
        result = collection_repo.delete_collection("non-existent")
        
        assert result["success"] is False
        assert "not found" in result["error"]
    
    def test_update_collection_stats(self, collection_repo, db_manager):
        """Test updating collection statistics."""
        # Create collection
        collection_repo.create_collection("test-id", "Test Collection")
        
        # Add files directly to database for testing
        file_repo = FileRepository(db_manager)
        file_repo.save_file("file-1", "test-id", "test1.txt", "Content 1")
        file_repo.save_file("file-2", "test-id", "test2.txt", "Content 2")
        
        # Update stats
        collection_repo.update_collection_stats("test-id")
        
        # Check updated stats
        result = collection_repo.get_collection("test-id")
        assert result["success"] is True
        assert result["collection"]["file_count"] == 2
        assert result["collection"]["total_size"] > 0


class TestFileRepository:
    """Test file repository operations."""
    
    @pytest.fixture
    def db_manager(self):
        """Create temporary database manager for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test_collections.db"
            db_manager = DatabaseManager(db_path)
            yield db_manager
            db_manager.close()
    
    @pytest.fixture
    def file_repo(self, db_manager):
        """Create file repository for testing."""
        return FileRepository(db_manager)
    
    @pytest.fixture
    def collection_with_data(self, db_manager):
        """Create a test collection with data."""
        collection_repo = CollectionRepository(db_manager)
        collection_repo.create_collection("test-collection", "Test Collection")
        return "test-collection"
    
    def test_save_file_success(self, file_repo, collection_with_data):
        """Test successful file saving."""
        result = file_repo.save_file(
            file_id="file-1",
            collection_id=collection_with_data,
            filename="test.md",
            content="# Test Content",
            folder_path="docs",
            source_url="https://example.com"
        )
        
        assert result["success"] is True
        assert result["file_id"] == "file-1"
        assert result["content_hash"] is not None
        assert result["file_size"] > 0
    
    def test_save_file_nonexistent_collection(self, file_repo):
        """Test saving file to non-existent collection fails."""
        result = file_repo.save_file(
            file_id="file-1",
            collection_id="non-existent",
            filename="test.md",
            content="Content"
        )
        
        assert result["success"] is False
        assert "not found" in result["error"]
    
    def test_read_file_success(self, file_repo, collection_with_data):
        """Test successful file reading."""
        # Save file first
        content = "# Test Markdown Content"
        file_repo.save_file("file-1", collection_with_data, "test.md", content)
        
        # Read file
        result = file_repo.read_file(collection_with_data, "test.md")
        
        assert result["success"] is True
        assert result["content"] == content
        assert result["metadata"]["content_hash"] is not None
        assert result["metadata"]["file_size"] == len(content.encode('utf-8'))
    
    def test_read_file_not_exists(self, file_repo, collection_with_data):
        """Test reading non-existent file."""
        result = file_repo.read_file(collection_with_data, "non-existent.md")
        
        assert result["success"] is False
        assert "not found" in result["error"]
    
    def test_read_file_with_folder_path(self, file_repo, collection_with_data):
        """Test reading file with folder path."""
        content = "File in subfolder"
        file_repo.save_file("file-1", collection_with_data, "test.md", content, "subfolder")
        
        # Read with correct folder path
        result = file_repo.read_file(collection_with_data, "test.md", "subfolder")
        assert result["success"] is True
        assert result["content"] == content
        
        # Read with wrong folder path should fail
        result = file_repo.read_file(collection_with_data, "test.md", "")
        assert result["success"] is False
    
    def test_list_files_empty(self, file_repo, collection_with_data):
        """Test listing files in empty collection."""
        result = file_repo.list_files(collection_with_data)
        
        assert result["success"] is True
        assert result["files"] == []
    
    def test_list_files_with_data(self, file_repo, collection_with_data):
        """Test listing files with data."""
        # Add test files
        file_repo.save_file("file-1", collection_with_data, "file1.md", "Content 1")
        file_repo.save_file("file-2", collection_with_data, "file2.txt", "Content 2", "subfolder")
        
        result = file_repo.list_files(collection_with_data)
        
        assert result["success"] is True
        assert len(result["files"]) == 2
        
        # Check file data
        files = result["files"]
        filenames = [f["filename"] for f in files]
        assert "file1.md" in filenames
        assert "file2.txt" in filenames
        
        # Check folder path is preserved
        subfoldered_file = next(f for f in files if f["filename"] == "file2.txt")
        assert subfoldered_file["folder_path"] == "subfolder"
    
    def test_file_content_hash_consistency(self, file_repo, collection_with_data):
        """Test that content hash is calculated consistently."""
        content = "Test content for hashing"
        
        # Save file
        save_result = file_repo.save_file("file-1", collection_with_data, "test.md", content)
        
        # Read file
        read_result = file_repo.read_file(collection_with_data, "test.md")
        
        # Hashes should match
        assert save_result["content_hash"] == read_result["metadata"]["content_hash"]
        
        # Hash should be deterministic
        import hashlib
        expected_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        assert save_result["content_hash"] == expected_hash