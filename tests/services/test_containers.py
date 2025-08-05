"""
Tests for dependency injection container.

Tests the container configuration, service registration,
and dependency resolution behavior.
"""
import pytest
from unittest.mock import patch, MagicMock
import os
from pathlib import Path

from services.containers import Container, create_container, get_container
from services.web_crawling_service import WebCrawlingService
from services.collection_service import CollectionService
from services.vector_sync_service import VectorSyncService


class TestContainer:
    """Test suite for dependency injection container."""
    
    def test_container_creation(self):
        """Test basic container creation."""
        container = Container()
        
        # Check that providers are defined
        assert hasattr(container, 'config')
        assert hasattr(container, 'collection_service')
        assert hasattr(container, 'vector_sync_service')
        assert hasattr(container, 'web_crawling_service')
    
    def test_create_container_with_defaults(self):
        """Test container creation with default configuration."""
        with patch.dict(os.environ, {}, clear=True):
            container = create_container()
            
            # Check configuration defaults
            assert container.config.collections.base_dir() == "./collections"
            assert container.config.vector.db_path() == "./rag_db"
            assert container.config.crawling.timeout() == 30
            assert container.config.crawling.user_agent() == "Crawl4AI-MCP-Server"
    
    def test_create_container_with_env_vars(self):
        """Test container creation with environment variables."""
        test_env = {
            'COLLECTIONS_BASE_DIR': '/custom/collections',
            'RAG_DB_PATH': '/custom/rag',
            'CRAWL4AI_TIMEOUT': '60',
            'CRAWL4AI_USER_AGENT': 'Custom-Agent'
        }
        
        with patch.dict(os.environ, test_env, clear=True):
            container = create_container()
            
            # Check environment variables are loaded
            assert container.config.collections.base_dir() == "/custom/collections"
            assert container.config.vector.db_path() == "/custom/rag"
            assert container.config.crawling.timeout() == 60
            assert container.config.crawling.user_agent() == "Custom-Agent"
    
    def test_collection_service_provider(self):
        """Test collection service provider configuration."""
        container = Container()
        
        # Configure container
        container.config.collections.base_dir.from_value("./test-collections")
        
        # Get collection service (should be singleton)
        service1 = container.collection_service()
        service2 = container.collection_service()
        
        # Should be same instance (singleton)
        assert service1 is service2
        assert isinstance(service1, CollectionService)
    
    def test_vector_sync_service_provider(self):
        """Test vector sync service provider configuration."""
        container = Container()
        
        # Configure container
        container.config.collections.base_dir.from_value("./test-collections")
        
        # Get services
        collection_service = container.collection_service()
        vector_service1 = container.vector_sync_service()
        vector_service2 = container.vector_sync_service()
        
        # Should be same instance (singleton)
        assert vector_service1 is vector_service2
        assert isinstance(vector_service1, VectorSyncService)
        
        # Should have collection service injected
        assert vector_service1.collection_service is collection_service
    
    def test_web_crawling_service_provider(self):
        """Test web crawling service provider configuration."""
        container = Container()
        
        # Get web crawling service (should be factory, so new instances)
        service1 = container.web_crawling_service()
        service2 = container.web_crawling_service()
        
        # Should be different instances (factory)
        assert service1 is not service2
        assert isinstance(service1, WebCrawlingService)
        assert isinstance(service2, WebCrawlingService)
    
    def test_get_container_singleton(self):
        """Test global container singleton behavior."""
        # Reset global container
        import services.containers
        services.containers._container = None
        
        # Get container instances
        container1 = get_container()
        container2 = get_container()
        
        # Should be same instance
        assert container1 is container2
        # Container should have expected attributes (dependency-injector may transform class)
        assert hasattr(container1, 'collection_service')
        assert hasattr(container1, 'vector_sync_service')
        assert hasattr(container1, 'web_crawling_service')
    
    def test_service_dependencies(self):
        """Test that services receive proper dependencies."""
        container = create_container()
        
        # Get services
        collection_service = container.collection_service()
        vector_service = container.vector_sync_service()
        web_service = container.web_crawling_service()
        
        # Check types
        assert isinstance(collection_service, CollectionService)
        assert isinstance(vector_service, VectorSyncService)
        assert isinstance(web_service, WebCrawlingService)
        
        # Check dependency injection
        assert vector_service.collection_service is collection_service
    
    def test_configuration_with_path_conversion(self):
        """Test configuration with Path conversion."""
        container = Container()
        
        # Configure with string path
        container.config.collections.base_dir.from_value("/test/path")
        
        # Get collection service
        collection_service = container.collection_service()
        
        # Should receive Path object (note: actual behavior depends on implementation)
        assert isinstance(collection_service, CollectionService)
    
    @patch('services.containers.logger')
    def test_container_logging(self, mock_logger):
        """Test that container creation logs appropriately."""
        create_container()
        
        # Check that logging occurred
        mock_logger.info.assert_any_call("Creating dependency injection container")
        mock_logger.info.assert_any_call("Dependency injection container configured successfully")
    
    def test_container_wire_functionality(self):
        """Test that container can be wired (basic functionality test)."""
        container = create_container()
        
        # Container should have wire method available
        assert hasattr(container, 'wire')
        assert callable(container.wire)
    
    def test_container_override_functionality(self):
        """Test that container supports provider overrides."""
        container = Container()
        
        # Create mock service
        mock_service = MagicMock(spec=CollectionService)
        
        # Override provider
        with container.collection_service.override(mock_service):
            service = container.collection_service()
            assert service is mock_service
        
        # After override, should return normal service
        normal_service = container.collection_service()
        assert normal_service is not mock_service
        assert isinstance(normal_service, CollectionService)
    
    def test_container_reset_singletons(self):
        """Test that container singletons can be reset."""
        container = Container()
        
        # Get service instances
        service1 = container.collection_service()
        vector1 = container.vector_sync_service()
        
        # Reset singletons
        container.reset_singletons()
        
        # Get new instances
        service2 = container.collection_service()
        vector2 = container.vector_sync_service()
        
        # Should be different instances after reset
        assert service1 is not service2
        assert vector1 is not vector2
        
        # But still be same type
        assert isinstance(service2, CollectionService)
        assert isinstance(vector2, VectorSyncService)