"""Global pytest configuration for CI environment."""

import os
import sys
import asyncio
import warnings
import gc
import sqlite3
import threading
import pytest
from pathlib import Path

# Suppress warnings in CI environment
if os.getenv('CI'):
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=ResourceWarning)
    warnings.filterwarnings("ignore", category=UserWarning)

# Set asyncio event loop policy for CI
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
else:
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

# Ensure test environment isolation
if os.getenv('CI'):
    # Create test collections directory for CI
    test_collections_dir = Path("./test_collections")
    test_collections_dir.mkdir(exist_ok=True)
    
    # Set environment variables for test isolation
    os.environ.setdefault('COLLECTIONS_BASE_PATH', str(test_collections_dir))
    os.environ.setdefault('CRAWL4AI_AVAILABLE', 'false')
    os.environ.setdefault('SECURITY_TEST_MODE', 'mock')


def pytest_runtest_teardown(item, nextitem):
    """Clean up after each test to prevent resource leaks."""
    # Force garbage collection to trigger __del__ methods
    gc.collect()
    
    # Close any remaining sqlite3 connections
    for obj in gc.get_objects():
        if isinstance(obj, sqlite3.Connection):
            try:
                obj.close()
            except Exception:
                pass  # Ignore errors on close
    
    # Clear thread-local storage that might hold connections
    for thread in threading.enumerate():
        if hasattr(thread, '__dict__'):
            thread_locals = getattr(thread, '__dict__', {})
            for key, value in list(thread_locals.items()):
                if hasattr(value, 'connection') and isinstance(getattr(value, 'connection', None), sqlite3.Connection):
                    try:
                        value.connection.close()
                        value.connection = None
                    except Exception:
                        pass


@pytest.fixture(autouse=True)
def cleanup_database_connections():
    """Automatically clean up database connections after each test."""
    yield
    # Post-test cleanup
    gc.collect()
    
    # Find and close any open sqlite3 connections
    for obj in gc.get_objects():
        if isinstance(obj, sqlite3.Connection):
            try:
                obj.close()
            except Exception:
                pass