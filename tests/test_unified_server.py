"""
Tests for unified server implementation.

Tests both MCP and HTTP protocol handlers to ensure they provide
consistent functionality through the shared service layer.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json
import os
import asyncio
from fastapi.testclient import TestClient

from unified_server import UnifiedServer
from services.interfaces import CrawlResult, DeepCrawlConfig, LinkPreview, CollectionInfo


class TestUnifiedServer:
    """Test suite for UnifiedServer integration."""
    
    @pytest.fixture
    def server(self):
        """Create a UnifiedServer instance for testing."""
        return UnifiedServer()
    
    def test_server_initialization(self, server):
        """Test basic server initialization."""
        assert server.container is not None
        assert server.mcp_server is None
        assert server.http_app is None
        assert server.running is False
    
    def test_setup_mcp_server(self, server):
        """Test MCP server setup."""
        mcp_server = server.setup_mcp_server()
        
        assert mcp_server is not None
        assert server.mcp_server is mcp_server
        
        # Check that MCP server is FastMCP instance (tools are registered internally)
        from fastmcp import FastMCP
        assert isinstance(mcp_server, FastMCP)
    
    def test_setup_http_app(self, server):
        """Test HTTP app setup."""
        http_app = server.setup_http_app()
        
        assert http_app is not None
        assert server.http_app is http_app
        
        # Check that FastAPI app has routes
        assert len(http_app.routes) > 0
        
        # Check for key endpoints
        route_paths = [route.path for route in http_app.routes if hasattr(route, 'path')]
        assert "/api/health" in route_paths
        assert "/api/status" in route_paths
        assert "/api/extract" in route_paths
        assert "/api/file-collections" in route_paths
    
    def test_http_health_endpoint(self, server):
        """Test HTTP health check endpoint."""
        app = server.setup_http_app()
        client = TestClient(app)
        
        response = client.get("/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["server"] == "unified"
    
    def test_http_status_endpoint(self, server):
        """Test HTTP status endpoint."""
        app = server.setup_http_app()
        client = TestClient(app)
        
        response = client.get("/api/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "running"
        assert data["server_type"] == "unified"
        assert "mcp" in data["protocols"]
        assert "http" in data["protocols"]
        assert "web_crawling" in data["services"]
        assert "collection_management" in data["services"]
        assert "vector_sync" in data["services"]


class TestUnifiedServerHTTPEndpoints:
    """Test HTTP endpoints for protocol consistency."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for HTTP endpoints."""
        server = UnifiedServer()
        app = server.setup_http_app()
        return TestClient(app)
    
    @pytest.mark.asyncio
    async def test_http_extract_content(self, client):
        """Test HTTP content extraction endpoint."""
        # Mock the web crawling service
        mock_result = CrawlResult(
            url="https://example.com",
            content="Test content",
            metadata={"title": "Test Page"}
        )
        
        # Mock the service at the service layer level
        with patch('services.web_crawling_service.web_content_extract', new_callable=AsyncMock) as mock_extract:
            mock_extract.return_value = json.dumps({
                "success": True,
                "content": "Test content",
                "title": "Test Page"
            })
            
            response = client.post("/api/extract", json={"url": "https://example.com"})
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["content"] == "Test content"
            assert data["metadata"]["title"] == "Test Page"
            assert data["error"] is None
    
    @pytest.mark.asyncio
    async def test_http_extract_content_missing_url(self, client):
        """Test HTTP content extraction with missing URL."""
        response = client.post("/api/extract", json={})
        
        assert response.status_code == 400
        assert "URL is required" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_http_deep_crawl(self, client):
        """Test HTTP deep crawl endpoint."""
        # Mock the underlying crawling tool
        mock_crawl_result = {
            "success": True,
            "pages": [
                {
                    "url": "https://example.com",
                    "title": "Page 1",
                    "content": "Page 1 content",
                    "depth": 0
                },
                {
                    "url": "https://example.com/page2", 
                    "title": "Page 2",
                    "content": "Page 2 content",
                    "depth": 1
                }
            ]
        }
        
        with patch('services.web_crawling_service.domain_deep_crawl', new_callable=AsyncMock) as mock_crawl:
            mock_crawl.return_value = json.dumps(mock_crawl_result)
            
            response = client.post("/api/deep-crawl", json={
                "domain_url": "https://example.com",
                "max_depth": 2,
                "max_pages": 5
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["pages"]) == 2
            assert data["pages"][0]["url"] == "https://example.com"
            assert data["pages"][0]["title"] == "Page 1"
    
    @pytest.mark.asyncio
    async def test_http_link_preview(self, client):
        """Test HTTP link preview endpoint."""
        mock_preview_result = {
            "success": True,
            "links": ["https://example.com/page1", "https://example.com/page2"],
            "external_links": ["https://external.com"],
            "timestamp": "2025-01-05T23:00:00Z"
        }
        
        with patch('services.web_crawling_service.domain_link_preview', new_callable=AsyncMock) as mock_preview:
            mock_preview.return_value = json.dumps(mock_preview_result)
            
            response = client.post("/api/link-preview", json={
                "domain_url": "https://example.com",
                "include_external": True
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["domain"] == "https://example.com"
            assert len(data["links"]) == 2
            assert len(data["external_links"]) == 1
    
    @pytest.mark.asyncio
    async def test_http_link_preview_missing_domain(self, client):
        """Test HTTP link preview with missing domain."""
        response = client.post("/api/link-preview", json={})
        
        assert response.status_code == 400
        assert "domain_url is required" in response.json()["detail"]
    
    @pytest.mark.asyncio 
    async def test_http_list_collections(self, client):
        """Test HTTP list collections endpoint basic functionality."""
        # This test just ensures the endpoint exists and returns proper error handling
        response = client.get("/api/file-collections")
        
        # Should return 200 with collections array (empty is ok for test)
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "collections" in data
        assert isinstance(data["collections"], list)
    
    @pytest.mark.asyncio
    async def test_http_create_collection(self, client):
        """Test HTTP create collection endpoint basic functionality."""
        # Test with valid collection name - should not error (may succeed or fail based on implementation)
        response = client.post("/api/file-collections", json={
            "name": "test-collection-unified-server",
            "description": "Test collection"
        })
        
        # Should not be a 400 error (validation passed)
        assert response.status_code != 400
        
        # Should return JSON response
        data = response.json()
        assert isinstance(data, dict)
    
    @pytest.mark.asyncio
    async def test_http_create_collection_missing_name(self, client):
        """Test HTTP create collection with missing name."""
        response = client.post("/api/file-collections", json={
            "description": "Collection without name"
        })
        
        assert response.status_code == 400
        assert "Collection name is required" in response.json()["detail"]


class TestUnifiedServerRunModes:
    """Test different server run modes."""
    
    @pytest.fixture
    def server(self):
        """Create a UnifiedServer instance for testing."""
        return UnifiedServer()
    
    @patch('unified_server.UnifiedServer.run_mcp_server')
    @patch('os.getenv')
    @pytest.mark.asyncio
    async def test_mcp_mode(self, mock_getenv, mock_run_mcp, server):
        """Test running in MCP-only mode."""
        mock_getenv.return_value = "mcp"
        mock_run_mcp.return_value = None
        
        # Mock setup methods
        server.setup_mcp_server = MagicMock()
        server.setup_http_app = MagicMock()
        
        await server.run_unified()
        
        server.setup_mcp_server.assert_called_once()
        server.setup_http_app.assert_called_once()
        mock_run_mcp.assert_called_once()
    
    @patch('unified_server.UnifiedServer.run_http_server')
    @patch('os.getenv')
    @pytest.mark.asyncio
    async def test_http_mode(self, mock_getenv, mock_run_http, server):
        """Test running in HTTP-only mode."""
        mock_getenv.return_value = "http"
        mock_run_http.return_value = None
        
        # Mock setup methods
        server.setup_mcp_server = MagicMock()
        server.setup_http_app = MagicMock()
        
        await server.run_unified()
        
        server.setup_mcp_server.assert_called_once()
        server.setup_http_app.assert_called_once()
        mock_run_http.assert_called_once()
    
    @patch('asyncio.gather', new_callable=AsyncMock)
    @patch('unified_server.UnifiedServer.run_mcp_server', new_callable=AsyncMock)
    @patch('unified_server.UnifiedServer.run_http_server', new_callable=AsyncMock)
    @patch('os.getenv')
    @pytest.mark.asyncio
    async def test_dual_mode(self, mock_getenv, mock_run_http, mock_run_mcp, mock_gather, server):
        """Test running in dual mode (both protocols)."""
        mock_getenv.return_value = "dual"
        
        # Make sure async functions return proper values
        mock_run_mcp.return_value = None
        mock_run_http.return_value = None
        mock_gather.return_value = None
        
        # Mock setup methods
        server.setup_mcp_server = MagicMock()
        server.setup_http_app = MagicMock()
        
        await server.run_unified()
        
        server.setup_mcp_server.assert_called_once()
        server.setup_http_app.assert_called_once()
        mock_gather.assert_called_once()
    
    @patch('unified_server.UnifiedServer.run_mcp_server')
    @patch('os.getenv')
    @patch('sys.argv', ['server.py'])
    @pytest.mark.asyncio
    async def test_auto_mode_mcp_default(self, mock_getenv, mock_run_mcp, server):
        """Test auto mode defaults to MCP when run without arguments."""
        mock_getenv.return_value = "auto"
        mock_run_mcp.return_value = None
        
        # Mock setup methods
        server.setup_mcp_server = MagicMock()
        server.setup_http_app = MagicMock()
        
        await server.run_unified()
        
        mock_run_mcp.assert_called_once()


class TestServiceSharing:
    """Test that services are properly shared between protocols."""
    
    def test_service_container_consistency(self):
        """Test that unified server uses consistent service container."""
        server = UnifiedServer()
        
        # Setup both protocols
        server.setup_mcp_server()
        server.setup_http_app()
        
        # Get services
        collection_service1 = server.container.collection_service()
        collection_service2 = server.container.collection_service()
        
        # Collection service should be singleton
        assert collection_service1 is collection_service2
        
        # Web service should be factory (different instances)
        web_service1 = server.container.web_crawling_service()
        web_service2 = server.container.web_crawling_service()
        assert web_service1 is not web_service2
        assert type(web_service1) == type(web_service2)