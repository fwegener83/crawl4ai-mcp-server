#!/usr/bin/env python3
"""Setup CI mocks for crawl4ai to avoid heavy dependencies."""
# CI configuration for comprehensive frontend redesign PR

import os
import sys

# Only create mocks in CI environment
if not os.getenv('CI'):
    print("⚠️  Not in CI environment - skipping mock setup")
    sys.exit(0)

# Create crawl4ai mock package
crawl4ai_dir = "crawl4ai"
os.makedirs(crawl4ai_dir, exist_ok=True)

# Create minimal __init__.py with mocked classes
init_content = '''"""Minimal crawl4ai mock for CI."""

class AsyncWebCrawler:
    """Mock AsyncWebCrawler for CI testing."""
    def __init__(self, config=None):
        self.config = config
    
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
        
    async def arun(self, url=None, config=None):
        """Mock arun method."""
        return MockResult()

class BrowserConfig:
    """Mock BrowserConfig for CI testing."""
    def __init__(self, headless=True, verbose=False, **kwargs):
        self.headless = headless
        self.verbose = verbose
        # Accept any additional keyword arguments for compatibility
        for key, value in kwargs.items():
            setattr(self, key, value)

class CrawlerRunConfig:
    """Mock CrawlerRunConfig for CI testing."""
    def __init__(self, verbose=False, stream=False, log_console=False, deep_crawl_strategy=None, **kwargs):
        self.verbose = verbose
        self.stream = stream
        self.log_console = log_console
        self.deep_crawl_strategy = deep_crawl_strategy
        # Accept any additional keyword arguments for compatibility
        for key, value in kwargs.items():
            setattr(self, key, value)

class MockResult:
    """Mock crawl result for CI testing."""
    def __init__(self):
        self.markdown = "Mock content"
        self.title = "Mock Title"
        self.success = True
        self.url = "https://example.com"
        self.html = "<html><body>Mock content</body></html>"
        self.cleaned_html = "<div>Mock content</div>"
        self.links = {"internal": [], "external": []}
        self.media = {"images": [], "videos": [], "audios": []}
        self.metadata = {"description": "Mock description"}

class LinkExtractor:
    """Mock LinkExtractor for CI testing."""
    def __init__(self):
        pass
    
    def extract_links(self, *args, **kwargs):
        return {"internal": [], "external": []}

# Mock database connection for testing
class MockConnection:
    """Mock database connection for CI testing."""
    def __init__(self):
        pass
    
    def execute(self, *args, **kwargs):
        pass
    
    def fetchall(self):
        return []
'''

with open(f"{crawl4ai_dir}/__init__.py", "w") as f:
    f.write(init_content)

# Create deep_crawling module mock
deep_crawling_content = '''"""Mock deep_crawling module for CI."""

class BFSDeepCrawlStrategy:
    """Mock BFS strategy for CI testing."""
    def __init__(self, max_depth=3, max_pages=100, filter_chain=None, *args, **kwargs):
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.filter_chain = filter_chain
        self.args = args
        self.kwargs = kwargs
        # Set any additional attributes from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    async def acrawl(self, *args, **kwargs):
        """Mock acrawl method."""
        return []

class DFSDeepCrawlStrategy:
    """Mock DFS strategy for CI testing."""
    def __init__(self, max_depth=3, max_pages=100, filter_chain=None, *args, **kwargs):
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.filter_chain = filter_chain
        self.args = args
        self.kwargs = kwargs
        # Set any additional attributes from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    async def acrawl(self, *args, **kwargs):
        """Mock acrawl method."""
        return []

class BestFirstCrawlingStrategy:
    """Mock BestFirst strategy for CI testing."""
    def __init__(self, max_depth=3, max_pages=100, filter_chain=None, url_scorer=None, *args, **kwargs):
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.filter_chain = filter_chain
        self.url_scorer = url_scorer
        self.args = args
        self.kwargs = kwargs
        # Set any additional attributes from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    async def acrawl(self, *args, **kwargs):
        """Mock acrawl method."""
        return []

class FilterChain:
    """Mock FilterChain for CI testing."""
    def __init__(self, filters=None, *args, **kwargs):
        self.filters = filters or []
        # Set any additional attributes from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def add_filter(self, filter_obj):
        self.filters.append(filter_obj)

class DomainFilter:
    """Mock DomainFilter for CI testing."""
    def __init__(self, allowed_domains=None, *args, **kwargs):
        self.allowed_domains = allowed_domains or []
        self.args = args
        self.kwargs = kwargs
        # Set any additional attributes from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

class URLPatternFilter:
    """Mock URLPatternFilter for CI testing."""
    def __init__(self, patterns=None, reverse=False, *args, **kwargs):
        self.patterns = patterns or []
        self.reverse = reverse
        self.args = args
        self.kwargs = kwargs
        # Set any additional attributes from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

class KeywordRelevanceScorer:
    """Mock KeywordRelevanceScorer for CI testing."""
    def __init__(self, keywords=None, weight=1.0, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        # Normalize keywords to lowercase (as expected by tests)
        self._keywords = [k.lower() for k in (keywords or [])]
        self.weight = weight
        # Set any additional attributes from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
'''

with open(f"{crawl4ai_dir}/deep_crawling.py", "w") as f:
    f.write(deep_crawling_content)

print("✅ CI mocks created successfully")