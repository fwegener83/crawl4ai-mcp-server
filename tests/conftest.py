"""Global pytest configuration for CI environment."""

import os
import sys
import asyncio
import warnings
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