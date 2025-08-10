"""
Dependency injection container for unified server architecture.

This container manages all service dependencies and provides singleton
instances for shared state management. It follows the DeclarativeContainer
pattern from dependency-injector with proper configuration management.
"""
import os
import logging
# Path import removed - no filesystem dependencies in database-only architecture
from dependency_injector import containers, providers

from .web_crawling_service import WebCrawlingService
from .collection_service import CollectionService
from .vector_sync_service import VectorSyncService
# Import centralized configuration
from config.paths import Context42Config

logger = logging.getLogger(__name__)


class Container(containers.DeclarativeContainer):
    """
    Main dependency injection container for unified server.
    
    Manages all service dependencies with proper singleton behavior
    for shared state management between MCP and HTTP protocols.
    """
    
    # Configuration provider for environment variables
    config = providers.Configuration()
    
    # Shared singletons for state consistency - database-only, no filesystem dependencies
    collection_service = providers.Singleton(
        CollectionService
        # No base_dir needed - uses database-only storage (vector_sync.db)
    )
    
    # Vector sync service (optional, graceful degradation)
    vector_sync_service = providers.Singleton(
        VectorSyncService,
        vector_store=None,  # Will be initialized by the service if available
        collection_service=collection_service
    )
    
    # Web crawling service (stateless, can be Factory)
    web_crawling_service = providers.Factory(
        WebCrawlingService
    )


def create_container() -> Container:
    """
    Create and configure the dependency injection container.
    
    Loads configuration from environment variables and returns
    a fully configured container ready for use.
    
    Returns:
        Configured Container instance
    """
    logger.info("Creating dependency injection container")
    
    container = Container()
    
    # Database-only configuration - no filesystem directories needed
    # COLLECTIONS_BASE_DIR is obsolete - using vector_sync.db database storage
    
    # Configuration with Context42 defaults
    container.config.vector.db_path.from_env(
        "VECTOR_DB_PATH", 
        default=str(Context42Config.get_vector_db_path())
    )
    
    container.config.collections.db_path.from_env(
        "COLLECTIONS_DB_PATH",
        default=str(Context42Config.get_collections_db_path())
    )
    
    container.config.crawling.timeout.from_env(
        "CRAWL4AI_TIMEOUT",
        as_=int,
        default=30
    )
    
    container.config.crawling.user_agent.from_env(
        "CRAWL4AI_USER_AGENT",
        default="Crawl4AI-MCP-Server"
    )
    
    logger.info("Dependency injection container configured successfully")
    return container


# Global container instance (singleton pattern)
_container = None


def get_container() -> Container:
    """
    Get the global container instance.
    
    Creates the container on first access and returns the same
    instance for subsequent calls (singleton pattern).
    
    Returns:
        Global Container instance
    """
    global _container
    if _container is None:
        _container = create_container()
    return _container