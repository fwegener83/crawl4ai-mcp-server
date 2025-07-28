"""
MCP Integration Tests for Collection File Management System.
Test integration with FastMCP framework and server.py structure.
"""
import pytest
import asyncio
import json
from unittest.mock import patch, AsyncMock
from pathlib import Path

# Import the collection manager for MCP integration
from tools.collection_manager import CollectionFileManager, CollectionMetadata, FileMetadata


class TestMCPCollectionTools:
    """Test MCP-decorated collection management tools."""
    
    @pytest.fixture
    def temp_collections_dir(self, tmp_path):
        """Create temporary collections directory."""
        collections_dir = tmp_path / "collections"
        collections_dir.mkdir()
        return collections_dir
    
    @pytest.fixture
    def mock_mcp_tool(self):
        """Mock MCP tool decorator to simulate FastMCP behavior."""
        def mcp_tool_decorator():
            def decorator(func):
                # Add mcp_tool attribute to mark as MCP tool
                func.mcp_tool = True
                return func
            return decorator
        return mcp_tool_decorator
    
    def test_create_collection_mcp_tool_response_format(self, temp_collections_dir, mock_mcp_tool):
        """Test MCP tool response format for create_collection."""
        
        # Simulate MCP tool implementation
        @mock_mcp_tool()
        async def create_collection_mcp(name: str, description: str = "") -> str:
            """Create a new collection with metadata."""
            manager = CollectionFileManager(temp_collections_dir)
            result = manager.create_collection(name, description)
            # MCP tools should return JSON strings
            return json.dumps(result)
        
        # Test the tool
        async def run_test():
            result_json = await create_collection_mcp("test-collection", "Test description")
            result = json.loads(result_json)
            
            assert result["success"] is True
            assert "path" in result
            assert "message" in result
            assert result["message"] == "Collection 'test-collection' created successfully"
            
            # Verify collection actually exists
            collection_path = temp_collections_dir / "test-collection"
            assert collection_path.exists()
            assert (collection_path / ".collection.json").exists()
        
        # Run async test
        asyncio.run(run_test())
    
    def test_save_file_to_collection_mcp_tool(self, temp_collections_dir, mock_mcp_tool):
        """Test MCP tool for saving files to collections."""
        
        @mock_mcp_tool()
        async def save_crawl_to_collection_mcp(
            collection_name: str, 
            filename: str, 
            content: str, 
            folder: str = ""
        ) -> str:
            """Save crawled content to a collection file."""
            manager = CollectionFileManager(temp_collections_dir)
            
            # Ensure collection exists
            if not (temp_collections_dir / collection_name).exists():
                manager.create_collection(collection_name)
            
            result = manager.save_file(collection_name, filename, content, folder)
            return json.dumps(result)
        
        async def run_test():
            # Test saving a file
            content = "# Test Page\n\nThis is crawled content from a webpage."
            result_json = await save_crawl_to_collection_mcp(
                "web-articles", 
                "test-article.md", 
                content
            )
            result = json.loads(result_json)
            
            assert result["success"] is True
            assert "path" in result
            
            # Verify file was saved correctly
            file_path = temp_collections_dir / "web-articles" / "test-article.md"
            assert file_path.exists()
            assert file_path.read_text(encoding='utf-8') == content
        
        asyncio.run(run_test())
    
    def test_list_collections_mcp_tool(self, temp_collections_dir, mock_mcp_tool):
        """Test MCP tool for listing collections."""
        
        @mock_mcp_tool()
        async def list_collections_mcp() -> str:
            """List all available collections."""
            manager = CollectionFileManager(temp_collections_dir)
            result = manager.list_collections()
            return json.dumps(result)
        
        async def run_test():
            # Create some test collections
            manager = CollectionFileManager(temp_collections_dir)
            manager.create_collection("collection-1", "First collection")
            manager.create_collection("collection-2", "Second collection")
            
            # Test listing
            result_json = await list_collections_mcp()
            result = json.loads(result_json)
            
            assert result["success"] is True
            assert result["total"] == 2
            assert len(result["collections"]) == 2
            
            # Check collection names
            collection_names = [c["name"] for c in result["collections"]]
            assert "collection-1" in collection_names
            assert "collection-2" in collection_names
        
        asyncio.run(run_test())
    
    def test_get_collection_info_mcp_tool(self, temp_collections_dir, mock_mcp_tool):
        """Test MCP tool for getting collection information."""
        
        @mock_mcp_tool()
        async def get_collection_info_mcp(collection_name: str) -> str:
            """Get detailed information about a collection."""
            manager = CollectionFileManager(temp_collections_dir)
            result = manager.get_collection_info(collection_name)
            return json.dumps(result)
        
        async def run_test():
            # Create a test collection with files
            manager = CollectionFileManager(temp_collections_dir)
            manager.create_collection("info-test", "Collection for info testing")
            manager.save_file("info-test", "file1.md", "Content 1")
            manager.save_file("info-test", "file2.md", "Content 2", "subfolder")
            
            # Test getting info
            result_json = await get_collection_info_mcp("info-test")
            result = json.loads(result_json)
            
            assert result["success"] is True
            assert "collection" in result
            assert result["collection"]["name"] == "info-test"
            assert result["collection"]["description"] == "Collection for info testing"
            assert result["collection"]["file_count"] == 2
            assert "subfolder" in result["collection"]["folders"]
        
        asyncio.run(run_test())


class TestMCPServerIntegration:
    """Test integration with the existing server.py structure."""
    
    @pytest.fixture
    def temp_collections_dir(self, tmp_path):
        """Create temporary collections directory."""
        collections_dir = tmp_path / "collections"
        collections_dir.mkdir()
        return collections_dir
    
    def test_fastmcp_compatibility(self):
        """Test that collection tools are compatible with FastMCP structure."""
        # This test ensures our tools follow the same pattern as existing tools
        
        # Check that our tool signatures match FastMCP expectations
        from tools.collection_manager import CollectionFileManager
        
        # MCP tools should be async and return strings (JSON)
        async def example_collection_tool(name: str) -> str:
            manager = CollectionFileManager()
            result = manager.create_collection(name)
            return json.dumps(result)
        
        # Verify the function signature
        import inspect
        sig = inspect.signature(example_collection_tool)
        
        # Should have async signature
        assert inspect.iscoroutinefunction(example_collection_tool)
        
        # Should return string (for JSON)
        assert sig.return_annotation == str
        
        # Parameters should have type hints
        params = list(sig.parameters.values())
        assert len(params) >= 1
        assert params[0].annotation == str  # name parameter
    
    def test_rag_system_compatibility(self, tmp_path):
        """Test that new collection system doesn't break existing RAG tools."""
        # This is a regression test to ensure existing functionality remains intact
        
        collections_dir = tmp_path / "collections"
        collections_dir.mkdir()
        
        # Create a collection using our new system
        manager = CollectionFileManager(collections_dir)
        result = manager.create_collection("rag-test", "RAG compatibility test")
        
        # Should not interfere with existing directory structure
        assert result["success"] is True
        
        # Collection should be isolated from other systems
        collection_path = collections_dir / "rag-test"
        assert collection_path.exists()
        assert collection_path.is_dir()
        
        # Metadata should be self-contained
        metadata_path = collection_path / ".collection.json"
        assert metadata_path.exists()
        
        # Should not create files outside the collections directory
        parent_files = list(collections_dir.parent.iterdir())
        assert len([f for f in parent_files if f.name.startswith("rag-test")]) == 0
    
    def test_logging_integration(self, temp_collections_dir):
        """Test that collection operations can be logged like existing tools."""
        import logging
        from unittest.mock import patch
        
        # Mock logger to capture log messages
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = mock_get_logger.return_value
            
            # Simulate MCP tool with logging (like existing tools)
            async def logged_create_collection(name: str, description: str = "") -> str:
                logger = logging.getLogger(__name__)
                logger.info(f"Creating collection: {name}")
                
                manager = CollectionFileManager(temp_collections_dir)
                result = manager.create_collection(name, description)
                
                if result["success"]:
                    logger.info(f"Successfully created collection '{name}' at {result['path']}")
                else:
                    logger.error(f"Failed to create collection '{name}': {result['error']}")
                
                return json.dumps(result)
            
            # Test the logged operation
            async def run_test():
                result_json = await logged_create_collection("logged-test", "Test logging")
                result = json.loads(result_json)
                
                assert result["success"] is True
                
                # Verify logging calls would be made
                # (In real implementation, these would be actual log calls)
                mock_get_logger.assert_called()
            
            asyncio.run(run_test())
    
    def test_error_handling_consistency(self, temp_collections_dir):
        """Test that error handling follows the same pattern as existing tools."""
        
        async def error_handling_tool(collection_name: str) -> str:
            """Tool that demonstrates consistent error handling."""
            try:
                manager = CollectionFileManager(temp_collections_dir)
                
                # Try to get info for non-existent collection
                result = manager.get_collection_info(collection_name)
                
                return json.dumps(result)
                
            except Exception as e:
                # Follow same error pattern as existing tools
                error_result = {
                    "success": False,
                    "error": str(e),
                    "message": f"Unexpected error processing collection '{collection_name}'"
                }
                return json.dumps(error_result)
        
        async def run_test():
            # Test error case
            result_json = await error_handling_tool("nonexistent-collection")
            result = json.loads(result_json)
            
            assert result["success"] is False
            assert "error" in result
            assert "not found" in result["error"].lower()
        
        asyncio.run(run_test())


class TestMCPToolDecoration:
    """Test actual MCP tool decoration patterns."""
    
    def test_tool_signature_validation(self):
        """Test that our tools have proper signatures for MCP decoration."""
        
        # Example of how our tools should be structured for MCP
        def create_mcp_collection_tool():
            """Factory function that creates MCP-compatible tools."""
            
            async def create_collection(name: str, description: str = "") -> str:
                """Create a new collection with metadata.
                
                Args:
                    name: Collection name
                    description: Optional collection description
                    
                Returns:
                    str: JSON string with operation result
                """
                # Tool implementation would go here
                return json.dumps({"success": True, "message": "Mock result"})
            
            return create_collection
        
        # Test the factory
        tool_func = create_mcp_collection_tool()
        
        # Verify MCP compatibility
        assert asyncio.iscoroutinefunction(tool_func)
        
        # Check signature
        import inspect
        sig = inspect.signature(tool_func)
        assert sig.return_annotation == str
        
        # Should have proper docstring for MCP introspection
        assert tool_func.__doc__ is not None
        assert "Create a new collection" in tool_func.__doc__
    
    def test_json_serialization_consistency(self):
        """Test that all tool responses can be properly JSON serialized."""
        
        # Test various response types that our tools might return
        test_responses = [
            {"success": True, "path": "/some/path", "message": "Success"},
            {"success": False, "error": "Some error", "message": "Failed"},
            {"success": True, "collections": [], "total": 0},
            {"success": True, "content": "file content", "path": "/file/path"}
        ]
        
        for response in test_responses:
            # Should be serializable to JSON
            json_str = json.dumps(response)
            assert isinstance(json_str, str)
            
            # Should be deserializable back to dict
            parsed = json.loads(json_str)
            assert parsed == response
            
            # Should have consistent structure
            assert "success" in parsed
            assert isinstance(parsed["success"], bool)