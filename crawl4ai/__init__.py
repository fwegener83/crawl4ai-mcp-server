"""Minimal crawl4ai mock for CI."""

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
    def __init__(self, headless=True, verbose=False):
        self.headless = headless
        self.verbose = verbose

class CrawlerRunConfig:
    """Mock CrawlerRunConfig for CI testing."""
    def __init__(self, verbose=False, stream=False, log_console=False):
        self.verbose = verbose
        self.stream = stream
        self.log_console = log_console

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
