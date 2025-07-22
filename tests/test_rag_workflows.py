"""System-level end-to-end workflow tests for RAG functionality."""
import pytest
import asyncio
import json
from typing import Dict, Any
from unittest.mock import patch, AsyncMock

# Check if RAG dependencies are available
try:
    import numpy as np
    import chromadb
    RAG_DEPENDENCIES_AVAILABLE = True
except ImportError:
    RAG_DEPENDENCIES_AVAILABLE = False

# Skip all tests in this module if dependencies are not available
pytestmark = pytest.mark.skipif(
    not RAG_DEPENDENCIES_AVAILABLE, 
    reason="RAG dependencies (numpy, chromadb) not available"
)

from tests.rag_factories import RAGTestData, setup_rag_test_environment


class TestEndToEndWorkflows:
    """End-to-end workflow tests - initially failing."""
    
    @pytest.mark.asyncio
    async def test_complete_crawl_store_search_workflow(self):
        """Test complete workflow: crawl → store → search → retrieve works correctly."""
        try:
            from tools.knowledge_base.rag_tools import store_crawl_results, search_knowledge_base
            
            with patch('tools.knowledge_base.rag_tools.get_rag_service') as mock_rag_service:
                from unittest.mock import MagicMock
                mock_service = MagicMock()
                # Mock storage
                mock_service.store_content.return_value = {
                    "success": True,
                    "chunks_stored": 2
                }
                # Mock search
                mock_service.search_content.return_value = {
                    "success": True,
                    "results": [{"content": "Found content", "similarity": 0.9}]
                }
                mock_rag_service.return_value = mock_service
                
                # Test workflow
                store_result = await store_crawl_results("Test content", "test_collection")
                search_result = await search_knowledge_base("test query", "test_collection")
                
                assert '"success": true' in store_result.lower()
                assert '"success": true' in search_result.lower()
                
        except ImportError:
            pytest.skip("RAG implementation not available")
    
    @pytest.mark.asyncio
    async def test_web_extract_to_rag_workflow(self):
        """Test web_content_extract → RAG storage workflow works correctly."""
        try:
            from tools.knowledge_base.rag_tools import store_crawl_results
            
            with patch('tools.knowledge_base.rag_tools.get_rag_service') as mock_rag_service:
                from unittest.mock import MagicMock
                mock_service = MagicMock()
                mock_service.store_content.return_value = {
                    "success": True,
                    "message": "Successfully stored content from web extract",
                    "chunks_stored": 1
                }
                mock_rag_service.return_value = mock_service
                
                # Simulate web_content_extract format (markdown string)
                web_content = "# Test Page\n\nThis is content extracted from a webpage."
                result = await store_crawl_results(web_content, "web_extract_collection")
                
                assert '"success": true' in result.lower()
                
        except ImportError:
            pytest.skip("RAG implementation not available")
    
    @pytest.mark.asyncio
    async def test_domain_crawl_to_rag_workflow(self):
        """Test domain_deep_crawl → RAG storage workflow works correctly."""
        try:
            from tools.knowledge_base.rag_tools import store_crawl_results
            
            with patch('tools.knowledge_base.rag_tools.get_rag_service') as mock_rag_service:
                from unittest.mock import MagicMock
                mock_service = MagicMock()
                mock_service.store_content.return_value = {
                    "success": True,
                    "message": "Successfully stored domain crawl results",
                    "chunks_stored": 3
                }
                mock_rag_service.return_value = mock_service
                
                # Simulate domain_deep_crawl format (dict with results array)
                domain_results = {
                    "success": True,
                    "results": [
                        {
                            "url": "https://example.com/page1",
                            "title": "Page 1",
                            "markdown": "# Page 1\n\nContent from page 1"
                        },
                        {
                            "url": "https://example.com/page2", 
                            "title": "Page 2",
                            "markdown": "# Page 2\n\nContent from page 2"
                        }
                    ]
                }
                result = await store_crawl_results(domain_results, "domain_crawl_collection")
                
                assert '"success": true' in result.lower()
                
        except ImportError:
            pytest.skip("RAG implementation not available")


class TestServerIntegration:
    """Server integration tests - initially failing."""
    
    @pytest.mark.asyncio
    async def test_fastmcp_tool_registration(self):
        """Test FastMCP tool registration works correctly."""
        try:
            # This tests that RAG tools are properly registered with FastMCP
            from tools.knowledge_base.rag_tools import store_crawl_results
            from server import mcp
            
            # Check that the tools are properly importable and callable
            assert store_crawl_results is not None
            assert callable(store_crawl_results)  # Should be a callable function
            
        except ImportError:
            pytest.skip("RAG implementation not available")
    
    @pytest.mark.asyncio
    async def test_async_patterns(self):
        """Test async/await patterns with FastMCP work correctly."""
        try:
            from tools.knowledge_base.rag_tools import store_crawl_results
            
            with patch('tools.knowledge_base.rag_tools.get_rag_service') as mock_rag_service:
                from unittest.mock import MagicMock
                mock_service = MagicMock()
                mock_service.store_content.return_value = {
                    "success": True,
                    "chunks_stored": 1
                }
                mock_rag_service.return_value = mock_service
                
                # Test async call pattern
                result = await store_crawl_results("async test content", "async_collection")
                assert isinstance(result, str)  # Should return JSON string
                assert '"success": true' in result.lower()
                
        except ImportError:
            pytest.skip("RAG implementation not available")
    
    @pytest.mark.asyncio
    async def test_mcp_protocol_compliance(self):
        """Test MCP protocol compliance works correctly."""
        try:
            from tools.knowledge_base.rag_tools import search_knowledge_base
            
            with patch('tools.knowledge_base.rag_tools.get_rag_service') as mock_rag_service:
                from unittest.mock import MagicMock
                mock_service = MagicMock()
                mock_service.search_content.return_value = {
                    "success": True,
                    "query": "compliance test",
                    "results": [{"content": "Protocol compliance test result", "similarity": 0.8}]
                }
                mock_rag_service.return_value = mock_service
                
                # Test MCP-style function call
                result = await search_knowledge_base("compliance test", "compliance_collection")
                assert isinstance(result, str)  # MCP tools should return strings
                assert '"success": true' in result.lower()
                assert 'compliance test' in result
                
        except ImportError:
            pytest.skip("RAG implementation not available")


class TestPerformanceWorkflows:
    """Performance workflow tests - initially failing."""
    
    @pytest.mark.asyncio
    async def test_storage_speed_requirements(self):
        """Test storage operations complete within 5 seconds."""
        try:
            from tools.knowledge_base.rag_tools import store_crawl_results
            import time
            
            with patch('tools.knowledge_base.rag_tools.get_rag_service') as mock_rag_service:
                from unittest.mock import MagicMock
                mock_service = MagicMock()
                mock_service.store_content.return_value = {
                    "success": True,
                    "chunks_stored": 5
                }
                mock_rag_service.return_value = mock_service
                
                # Test storage speed
                start_time = time.perf_counter()
                result = await store_crawl_results("Large test content for speed test", "speed_test_collection")
                duration = time.perf_counter() - start_time
                
                assert '"success": true' in result.lower()
                assert duration < 5.0  # Should complete within 5 seconds
                
        except ImportError:
            pytest.skip("RAG implementation not available")
    
    @pytest.mark.asyncio  
    async def test_search_latency_requirements(self):
        """Test search queries return within 1 second."""
        try:
            from tools.knowledge_base.rag_tools import search_knowledge_base
            import time
            
            with patch('tools.knowledge_base.rag_tools.get_rag_service') as mock_rag_service:
                from unittest.mock import MagicMock
                mock_service = MagicMock()
                mock_service.search_content.return_value = {
                    "success": True,
                    "results": [{"content": "Fast search result", "similarity": 0.9}]
                }
                mock_rag_service.return_value = mock_service
                
                # Test search latency
                start_time = time.perf_counter()
                result = await search_knowledge_base("latency test query", "latency_test_collection")
                duration = time.perf_counter() - start_time
                
                assert '"success": true' in result.lower()
                assert duration < 1.0  # Should complete within 1 second
                
        except ImportError:
            pytest.skip("RAG implementation not available")
    
    @pytest.mark.asyncio
    async def test_memory_usage_requirements(self):
        """Test system memory stays under reasonable limits."""
        try:
            from tools.knowledge_base.rag_tools import store_crawl_results
            import psutil
            import os
            
            with patch('tools.knowledge_base.rag_tools.get_rag_service') as mock_rag_service:
                from unittest.mock import MagicMock
                mock_service = MagicMock()
                mock_service.store_content.return_value = {
                    "success": True,
                    "chunks_stored": 10
                }
                mock_rag_service.return_value = mock_service
                
                # Get initial memory usage
                process = psutil.Process(os.getpid())
                initial_memory = process.memory_info().rss / 1024 / 1024  # MB
                
                # Perform operation
                result = await store_crawl_results("Memory usage test content", "memory_test_collection")
                
                # Check memory after operation
                final_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_increase = final_memory - initial_memory
                
                assert '"success": true' in result.lower()
                # With mocking, memory increase should be minimal
                assert memory_increase < 100  # Should not increase by more than 100MB
                
        except ImportError:
            pytest.skip("RAG implementation not available")
        except ImportError as e:
            if 'psutil' in str(e):
                pytest.skip("psutil not available for memory testing")
            else:
                raise


class TestSecurityWorkflows:
    """Security workflow tests - initially failing."""
    
    @pytest.mark.asyncio
    async def test_input_validation_workflow(self):
        """Test input validation in complete workflow."""
        try:
            from tools.knowledge_base.rag_tools import store_crawl_results
            
            with patch('tools.knowledge_base.rag_tools.get_rag_service') as mock_rag_service:
                from unittest.mock import MagicMock
                mock_service = MagicMock()
                mock_service.store_content.return_value = {
                    "success": True,
                    "chunks_stored": 1
                }
                mock_rag_service.return_value = mock_service
                
                # Test with valid input
                valid_result = await store_crawl_results("Valid content for validation test", "validation_collection")
                assert '"success": true' in valid_result.lower()
                
                # Test with empty input (should be handled gracefully)
                empty_result = await store_crawl_results("", "validation_collection")
                # Should still return a result (even if no content stored)
                assert isinstance(empty_result, str)
                
        except ImportError:
            pytest.skip("RAG implementation not available")
    
    @pytest.mark.asyncio
    async def test_query_injection_prevention(self):
        """Test query injection prevention."""
        try:
            from tools.knowledge_base.rag_tools import search_knowledge_base
            
            with patch('tools.knowledge_base.rag_tools.get_rag_service') as mock_rag_service:
                from unittest.mock import MagicMock
                mock_service = MagicMock()
                mock_service.search_content.return_value = {
                    "success": True,
                    "results": [{"content": "Safe search result", "similarity": 0.8}]
                }
                mock_rag_service.return_value = mock_service
                
                # Test with potentially malicious queries
                malicious_queries = [
                    "'; DROP TABLE documents; --",
                    "<script>alert('xss')</script>",
                    "../../../etc/passwd"
                ]
                
                for query in malicious_queries:
                    result = await search_knowledge_base(query, "injection_test_collection")
                    # Should handle malicious input gracefully
                    assert isinstance(result, str)
                    assert '"success": true' in result.lower()
                
        except ImportError:
            pytest.skip("RAG implementation not available")
    
    @pytest.mark.asyncio
    async def test_error_message_sanitization(self):
        """Test error message sanitization."""
        try:
            from tools.knowledge_base.rag_tools import store_crawl_results
            
            with patch('tools.knowledge_base.rag_tools.get_rag_service') as mock_rag_service:
                from unittest.mock import MagicMock
                mock_service = MagicMock()
                # Simulate an error with sensitive information
                mock_service.store_content.side_effect = Exception(
                    "Database connection failed: postgresql://user:secret123@localhost:5432/db"
                )
                mock_rag_service.return_value = mock_service
                
                # Test that errors are sanitized
                result = await store_crawl_results("Test content", "sanitization_test_collection")
                
                # Should contain sanitized error information
                assert isinstance(result, str)
                assert '"success": false' in result.lower()
                # Should not contain sensitive information like passwords
                assert "secret123" not in result
                assert "postgresql://" not in result or "[REDACTED]" in result
                
        except ImportError:
            pytest.skip("RAG implementation not available")


class TestCompatibilityWorkflows:
    """Compatibility workflow tests - initially failing."""
    
    @pytest.mark.asyncio
    async def test_different_document_types(self):
        """Test handling different document types."""
        try:
            from tools.knowledge_base.rag_tools import store_crawl_results
            
            with patch('tools.knowledge_base.rag_tools.get_rag_service') as mock_rag_service:
                from unittest.mock import MagicMock
                mock_service = MagicMock()
                mock_service.store_content.return_value = {
                    "success": True,
                    "chunks_stored": 2
                }
                mock_rag_service.return_value = mock_service
                
                # Test different document formats
                formats = {
                    "markdown": "# Title\n\nMarkdown content",
                    "html": "<h1>Title</h1><p>HTML content</p>",
                    "plain_text": "Plain text content",
                    "json": '{"success": true, "results": [{"markdown": "JSON format content"}]}'
                }
                
                for doc_type, content in formats.items():
                    result = await store_crawl_results(content, f"{doc_type}_collection")
                    assert '"success": true' in result.lower(), f"Failed for {doc_type} format"
                
        except ImportError:
            pytest.skip("RAG implementation not available")
    
    @pytest.mark.asyncio
    async def test_large_collections(self):
        """Test handling large collections."""
        try:
            from tools.knowledge_base.rag_tools import search_knowledge_base, store_crawl_results
            
            with patch('tools.knowledge_base.rag_tools.get_rag_service') as mock_rag_service:
                from unittest.mock import MagicMock
                mock_service = MagicMock()
                
                # Mock large collection behavior
                mock_service.store_content.return_value = {
                    "success": True,
                    "chunks_stored": 1000  # Simulate large collection
                }
                mock_service.search_content.return_value = {
                    "success": True,
                    "results": [{"content": f"Result {i}", "similarity": 0.9 - i*0.01} for i in range(20)],
                    "total_results": 1000
                }
                mock_rag_service.return_value = mock_service
                
                # Test storing to large collection
                store_result = await store_crawl_results("Large collection test", "large_collection")
                assert '"success": true' in store_result.lower()
                
                # Test searching in large collection
                search_result = await search_knowledge_base("test query", "large_collection", n_results=20)
                assert '"success": true' in search_result.lower()
                
        except ImportError:
            pytest.skip("RAG implementation not available")
    
    @pytest.mark.asyncio
    async def test_concurrent_access(self):
        """Test concurrent access patterns."""
        try:
            from tools.knowledge_base.rag_tools import store_crawl_results, search_knowledge_base
            import asyncio
            
            with patch('tools.knowledge_base.rag_tools.get_rag_service') as mock_rag_service:
                from unittest.mock import MagicMock
                mock_service = MagicMock()
                
                mock_service.store_content.return_value = {
                    "success": True,
                    "chunks_stored": 1
                }
                mock_service.search_content.return_value = {
                    "success": True,
                    "results": [{"content": "Concurrent result", "similarity": 0.9}]
                }
                mock_rag_service.return_value = mock_service
                
                # Test concurrent operations
                store_tasks = [
                    store_crawl_results(f"Concurrent content {i}", "concurrent_collection")
                    for i in range(5)
                ]
                search_tasks = [
                    search_knowledge_base(f"concurrent query {i}", "concurrent_collection")
                    for i in range(3)
                ]
                
                # Run all tasks concurrently
                all_tasks = store_tasks + search_tasks
                results = await asyncio.gather(*all_tasks, return_exceptions=True)
                
                # Check that all operations completed successfully
                for i, result in enumerate(results):
                    assert not isinstance(result, Exception), f"Task {i} failed: {result}"
                    assert isinstance(result, str), f"Task {i} returned non-string: {type(result)}"
                    assert '"success": true' in result.lower(), f"Task {i} was not successful"
                
        except ImportError:
            pytest.skip("RAG implementation not available")


# Test infrastructure for when implementation is ready
class TestWorkflowInfrastructure:
    """Workflow test infrastructure readiness."""
    
    @pytest.fixture
    def workflow_test_env(self):
        """Fixture providing complete workflow test environment."""
        return setup_rag_test_environment()
    
    @pytest.fixture
    def mock_crawl_results(self):
        """Fixture providing mock crawl results for workflow testing."""
        # String format (web_content_extract)
        string_result = RAGTestData.create_crawl_result_string()
        
        # Dict format (domain_deep_crawl) 
        dict_result = RAGTestData.create_crawl_result_dict()
        
        # Multi-result format
        multi_result = RAGTestData.create_multi_result_dict(3)
        
        return {
            "string_result": string_result,
            "dict_result": dict_result, 
            "multi_result": multi_result
        }
    
    @pytest.fixture
    def performance_test_data(self):
        """Fixture providing data for performance testing."""
        return {
            "small_doc": RAGTestData.create_crawl_result_string(0),
            "medium_doc": RAGTestData.create_large_document(500),
            "large_doc": RAGTestData.create_large_document(2000),
            "batch_docs": [
                RAGTestData.create_crawl_result_string(i % 3) 
                for i in range(10)
            ]
        }
    
    def test_workflow_test_env_fixture(self, workflow_test_env):
        """Test workflow test environment fixture."""
        assert workflow_test_env is not None
        assert all(key in workflow_test_env for key in [
            "chroma_client", "sentence_model", "text_splitter", "config"
        ])
    
    def test_mock_crawl_results_fixture(self, mock_crawl_results):
        """Test mock crawl results fixture.""" 
        assert "string_result" in mock_crawl_results
        assert "dict_result" in mock_crawl_results
        assert "multi_result" in mock_crawl_results
        
        # Verify string result is string
        assert isinstance(mock_crawl_results["string_result"], str)
        
        # Verify dict result structure
        dict_result = mock_crawl_results["dict_result"]
        assert "success" in dict_result
        assert "results" in dict_result
        assert isinstance(dict_result["results"], list)
    
    def test_performance_test_data_fixture(self, performance_test_data):
        """Test performance test data fixture."""
        assert "small_doc" in performance_test_data
        assert "large_doc" in performance_test_data
        assert "batch_docs" in performance_test_data
        
        # Verify size differences
        small_size = len(performance_test_data["small_doc"])
        large_size = len(performance_test_data["large_doc"])
        assert large_size > small_size * 3  # Large doc should be significantly larger
        
        # Verify batch data
        assert len(performance_test_data["batch_docs"]) == 10


# Async testing utilities
class TestAsyncUtilities:
    """Async testing utility verification."""
    
    @pytest.mark.asyncio
    async def test_async_test_infrastructure_ready(self):
        """Test async testing infrastructure is ready."""
        # Test basic async functionality
        async def sample_async_function():
            await asyncio.sleep(0.001)  # Very short sleep
            return "async_result"
        
        result = await sample_async_function()
        assert result == "async_result"
    
    @pytest.mark.asyncio
    async def test_async_context_manager_ready(self):
        """Test async context manager infrastructure is ready."""
        class AsyncContextManagerTest:
            async def __aenter__(self):
                return self
                
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                return None
                
            def test_method(self):
                return "test_result"
        
        async with AsyncContextManagerTest() as manager:
            result = manager.test_method()
            assert result == "test_result"


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])