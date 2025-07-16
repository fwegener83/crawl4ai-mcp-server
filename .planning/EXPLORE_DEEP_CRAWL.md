# Feature Exploration: Domain Deep Crawler MCP Tool

## Source Information
- **Input**: .planning/INITIAL_DEEP_CRAWL.md
- **Branch**: feature/DEEP_CRAWL
- **Generated**: 2025-07-16T15:30:00Z

## Feature Overview

The Domain Deep Crawler MCP Tool extends the existing Crawl4AI MCP server with sophisticated domain-based deep crawling capabilities. This feature implements two primary tools:

1. **`domain_deep_crawl`**: Main function for comprehensive domain crawling with configurable depth, strategies, and filtering
2. **`domain_link_preview`**: Helper function providing quick domain link analysis without full crawling

The tool leverages Crawl4AI's advanced deep crawling strategies (BFS, DFS, BestFirst) with intelligent filtering, scoring, and streaming capabilities to provide flexible, production-ready domain exploration.

## Technical Requirements

### Core Dependencies
- **FastMCP**: >=2.0.0 for MCP protocol implementation
- **Crawl4AI[all]**: Advanced web crawling with deep crawling strategies
- **Pydantic**: >=2.0.0 for data validation and modeling
- **Python-dotenv**: Environment configuration management

### Development Dependencies
- **pytest**: Unit testing framework
- **pytest-asyncio**: Async testing support
- **pytest-cov**: Code coverage analysis
- **httpx**: HTTP client for testing
- **mypy**: Type checking
- **ruff**: Code formatting and linting

### Crawl4AI Specific Requirements
- **BFSDeepCrawlStrategy**: Breadth-first domain exploration
- **DFSDeepCrawlStrategy**: Depth-first domain exploration
- **BestFirstCrawlingStrategy**: Priority-based intelligent crawling
- **FilterChain**: URL pattern filtering and domain boundaries
- **KeywordRelevanceScorer**: Content relevance scoring for BestFirst
- **AsyncWebCrawler**: Async crawler with streaming support

## Architecture Context

### Current MCP Server Architecture
The existing server follows a clean, modular pattern:
- **server.py**: Main MCP server entry point with tool registration
- **tools/**: Individual tool implementations with validation
- **tests/**: Comprehensive test suite with mocking patterns
- **tools/error_sanitizer.py**: Security error sanitization (reusable)

### Integration Points
- **Tool Registration**: Use `@mcp.tool()` decorator following `web_content_extract` pattern
- **Parameter Validation**: Pydantic models with comprehensive validation
- **Error Handling**: Leverage existing `sanitize_error_message` functionality
- **Async Implementation**: Follow established async/await patterns
- **Configuration**: Environment variable support for customization

### File Structure Integration
```
tools/
├── domain_crawler.py          # Main domain deep crawling logic
├── domain_link_preview.py     # Link preview functionality
├── error_sanitizer.py         # Existing security sanitization
└── __init__.py                # Tool registration updates

tests/
├── test_domain_crawler.py     # Unit tests for domain crawler
├── test_domain_link_preview.py # Unit tests for link preview
└── test_domain_integration.py # Integration tests
```

## Implementation Knowledge Base

### Crawl4AI Deep Crawling Strategies

#### BFS (Breadth-First Search) Configuration
```python
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy

strategy = BFSDeepCrawlStrategy(
    max_depth=2,
    include_external=False,
    max_pages=50,
    score_threshold=0.3,
    filter_chain=filter_chain
)
```

#### DFS (Depth-First Search) Configuration
```python
from crawl4ai.deep_crawling import DFSDeepCrawlStrategy

strategy = DFSDeepCrawlStrategy(
    max_depth=2,
    include_external=False,
    max_pages=30,
    score_threshold=0.5,
    filter_chain=filter_chain
)
```

#### BestFirst (Priority-Based) Configuration
```python
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
from crawl4ai.deep_crawling.scorers import KeywordRelevanceScorer

scorer = KeywordRelevanceScorer(
    keywords=["tutorial", "guide", "documentation"],
    weight=0.8
)

strategy = BestFirstCrawlingStrategy(
    max_depth=2,
    include_external=False,
    url_scorer=scorer,
    max_pages=25
)
```

### FilterChain Implementation
```python
from crawl4ai.deep_crawling.filters import (
    FilterChain,
    URLPatternFilter,
    DomainFilter,
    ContentTypeFilter
)

filter_chain = FilterChain([
    DomainFilter(
        allowed_domains=["docs.example.com"],
        blocked_domains=["old.docs.example.com"]
    ),
    URLPatternFilter(patterns=["*blog*", "*tutorial*"]),
    ContentTypeFilter(allowed_types=["text/html"])
])
```

### Streaming Implementation
```python
# Enable streaming for large crawls
config = CrawlerRunConfig(
    deep_crawl_strategy=strategy,
    stream=True,
    memory_threshold_percent=70.0,
    max_session_permit=15
)

async with AsyncWebCrawler(config=browser_config) as crawler:
    async for result in await crawler.arun(url=domain_url, config=config):
        if result.success:
            # Process results in real-time
            await process_result(result)
```

## Code Patterns & Examples

### MCP Tool Registration Pattern
```python
@mcp.tool()
async def domain_deep_crawl(
    domain_url: str,
    max_depth: int = 2,
    crawl_strategy: str = "bfs",
    max_pages: int = 50,
    include_external: bool = False,
    url_patterns: List[str] = None,
    exclude_patterns: List[str] = None,
    keywords: List[str] = None,
    stream_results: bool = False
) -> str:
    """Crawl a complete domain with configurable depth and strategies."""
    logger.info(f"Starting domain deep crawl for: {domain_url}")
    
    try:
        params = DomainDeepCrawlParams(
            domain_url=domain_url,
            max_depth=max_depth,
            crawl_strategy=crawl_strategy,
            max_pages=max_pages,
            include_external=include_external,
            url_patterns=url_patterns or [],
            exclude_patterns=exclude_patterns or [],
            keywords=keywords or [],
            stream_results=stream_results
        )
        
        from tools.domain_crawler import domain_deep_crawl as crawl_func
        result = await crawl_func(params)
        
        logger.info(f"Domain crawl completed for {domain_url}")
        return result
        
    except Exception as e:
        error_msg = f"Domain crawl failed: {str(e)}"
        logger.error(error_msg)
        return sanitize_error_message(error_msg)
```

### Parameter Validation Pattern
```python
class DomainDeepCrawlParams(BaseModel):
    """Parameters for domain deep crawling."""
    model_config = ConfigDict(frozen=True)
    
    domain_url: str = Field(..., description="The base URL/domain to crawl")
    max_depth: int = Field(default=2, ge=0, le=10, description="Maximum crawl depth")
    crawl_strategy: str = Field(default="bfs", description="Crawling strategy")
    max_pages: int = Field(default=50, ge=1, le=1000, description="Maximum pages to crawl")
    include_external: bool = Field(default=False, description="Include external links")
    url_patterns: List[str] = Field(default=[], description="URL patterns to include")
    exclude_patterns: List[str] = Field(default=[], description="URL patterns to exclude")
    keywords: List[str] = Field(default=[], description="Keywords for BestFirst scoring")
    stream_results: bool = Field(default=False, description="Stream results in real-time")
    
    @field_validator('domain_url')
    @classmethod
    def validate_domain_url(cls, v):
        if not v or not v.strip():
            raise ValueError("Domain URL cannot be empty")
        
        parsed = urlparse(v)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid domain URL format")
        
        if parsed.scheme not in ['http', 'https']:
            raise ValueError("Domain URL must use HTTP or HTTPS protocol")
        
        return v.strip()
    
    @field_validator('crawl_strategy')
    @classmethod
    def validate_crawl_strategy(cls, v):
        allowed_strategies = ['bfs', 'dfs', 'best_first']
        if v not in allowed_strategies:
            raise ValueError(f"Strategy must be one of: {allowed_strategies}")
        return v
```

### Error Handling Pattern
```python
async def domain_deep_crawl_impl(params: DomainDeepCrawlParams) -> str:
    """Implementation of domain deep crawling."""
    try:
        # Configure browser for silent operation
        browser_config = BrowserConfig(
            headless=True,
            verbose=False
        )
        
        # Build filter chain
        filter_chain = build_filter_chain(
            domain_url=params.domain_url,
            include_external=params.include_external,
            url_patterns=params.url_patterns,
            exclude_patterns=params.exclude_patterns
        )
        
        # Create strategy
        strategy = create_crawl_strategy(
            strategy_name=params.crawl_strategy,
            max_depth=params.max_depth,
            max_pages=params.max_pages,
            filter_chain=filter_chain,
            keywords=params.keywords
        )
        
        # Configure crawler
        run_config = CrawlerRunConfig(
            deep_crawl_strategy=strategy,
            stream=params.stream_results,
            verbose=False,
            log_console=False,
            memory_threshold_percent=70.0
        )
        
        # Execute crawl
        async with AsyncWebCrawler(config=browser_config) as crawler:
            if params.stream_results:
                return await handle_streaming_crawl(crawler, params.domain_url, run_config)
            else:
                return await handle_batch_crawl(crawler, params.domain_url, run_config)
                
    except Exception as e:
        sanitized_error = sanitize_error_message(str(e))
        logger.error(f"Domain crawl failed for {params.domain_url}: {sanitized_error}")
        return json.dumps({
            "success": False,
            "error": sanitized_error,
            "domain": params.domain_url
        })
```

### Testing Pattern
```python
class TestDomainDeepCrawler:
    @pytest.mark.asyncio
    async def test_bfs_crawl_strategy(self):
        """Test BFS crawling strategy."""
        mock_result = CrawlResultFactory.create_success_result(
            content="# Test Page\n\nTest content",
            title="Test Page",
            url="https://example.com"
        )
        
        with patch('tools.domain_crawler.AsyncWebCrawler') as mock_crawler:
            mock_instance = AsyncMock()
            mock_crawler.return_value.__aenter__.return_value = mock_instance
            mock_instance.arun.return_value = mock_result
            
            params = DomainDeepCrawlParams(
                domain_url="https://example.com",
                max_depth=2,
                crawl_strategy="bfs",
                max_pages=25
            )
            
            result = await domain_deep_crawl_impl(params)
            
            result_data = json.loads(result)
            assert result_data["success"] is True
            assert result_data["crawl_summary"]["strategy_used"] == "bfs"
```

## Configuration Requirements

### Environment Variables
```bash
# Optional: Crawl4AI configuration
CRAWL4AI_USER_AGENT=crawl4ai-mcp-server/1.0
CRAWL4AI_MAX_RETRIES=3
CRAWL4AI_TIMEOUT=30
CRAWL4AI_MAX_DEPTH=5
CRAWL4AI_MAX_PAGES=100

# Performance settings
CRAWL4AI_MEMORY_THRESHOLD=70
CRAWL4AI_MAX_CONCURRENT=15
CRAWL4AI_RATE_LIMIT=True
```

### MCP Inspector Configuration
```json
{
  "mcpServers": {
    "crawl4ai": {
      "command": "/Users/florianwegener/Projects/crawl4ai-mcp-server/.venv/bin/python",
      "args": ["/Users/florianwegener/Projects/crawl4ai-mcp-server/server.py"],
      "env": {
        "PYTHONUNBUFFERED": "1",
        "CRAWL4AI_MAX_DEPTH": "3",
        "CRAWL4AI_MAX_PAGES": "50"
      }
    }
  }
}
```

### Default Configuration
```python
# Default limits for safety
DEFAULT_MAX_DEPTH = 3
DEFAULT_MAX_PAGES = 50
DEFAULT_STRATEGY = "bfs"
DEFAULT_MEMORY_THRESHOLD = 70.0
DEFAULT_MAX_CONCURRENT = 15
DEFAULT_RATE_LIMIT = True
```

## Testing Considerations

### Unit Testing Strategy
- **Parameter Validation**: Test all input validation rules
- **Strategy Selection**: Verify correct strategy instantiation
- **Error Handling**: Test error scenarios with mocked failures
- **Sanitization**: Verify security error message cleaning

### Integration Testing Strategy
- **Real Domain Crawls**: Test with small, controlled test sites
- **Strategy Comparison**: Compare BFS vs DFS vs BestFirst results
- **Performance Testing**: Memory usage and timing validation
- **Edge Cases**: Empty domains, invalid URLs, network failures

### Mock Testing Patterns
```python
class CrawlResultFactory:
    @staticmethod
    def create_domain_result(pages_data: List[Dict]) -> Dict:
        """Create mock domain crawl result."""
        return {
            "success": True,
            "crawl_summary": {
                "total_pages": len(pages_data),
                "max_depth_reached": max(page["depth"] for page in pages_data),
                "strategy_used": "bfs",
                "pages_by_depth": count_pages_by_depth(pages_data)
            },
            "pages": pages_data
        }
```

### Performance Testing
```python
@pytest.mark.asyncio
async def test_memory_management():
    """Test memory usage during large crawls."""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # Simulate large crawl
    params = DomainDeepCrawlParams(
        domain_url="https://example.com",
        max_depth=3,
        max_pages=100
    )
    
    await domain_deep_crawl_impl(params)
    
    final_memory = process.memory_info().rss
    memory_growth = final_memory - initial_memory
    
    # Assert memory growth is reasonable
    assert memory_growth < 100 * 1024 * 1024  # Less than 100MB
```

## Integration Points

### MCP Protocol Integration
- **Tool Registration**: Register both tools in server.py using `@mcp.tool()` decorator
- **Parameter Passing**: JSON-RPC parameter handling with type validation
- **Response Formatting**: Structured JSON responses with success/error status
- **Logging Integration**: Use existing logger patterns for debugging

### Crawl4AI Integration
- **AsyncWebCrawler**: Main crawler instance with proper configuration
- **Strategy Factory**: Dynamic strategy creation based on parameters
- **Filter Chain**: URL filtering and domain boundary management
- **Streaming Support**: Real-time result processing for large crawls

### Error Handling Integration
```python
from tools.error_sanitizer import sanitize_error_message

def handle_crawl_error(error: Exception, domain_url: str) -> str:
    """Handle crawl errors with proper sanitization."""
    sanitized_error = sanitize_error_message(str(error))
    logger.error(f"Domain crawl failed for {domain_url}: {sanitized_error}")
    
    return json.dumps({
        "success": False,
        "error": sanitized_error,
        "domain": domain_url,
        "timestamp": datetime.utcnow().isoformat()
    })
```

## Technical Constraints

### Performance Constraints
- **Memory Management**: 70% memory threshold with streaming for large crawls
- **Concurrency Limits**: Maximum 15 concurrent sessions to prevent resource exhaustion
- **Rate Limiting**: Respect server rate limits and implement backoff strategies
- **Timeout Handling**: 30-second default timeout with configurable override

### Security Constraints
- **Domain Validation**: Only allow HTTP/HTTPS URLs with proper domain validation
- **Error Sanitization**: Use existing security sanitization for all error messages
- **Input Validation**: Comprehensive parameter validation to prevent injection attacks
- **Resource Limits**: Maximum page limits to prevent runaway crawls

### Scalability Constraints
- **Maximum Depth**: Limit to 10 levels to prevent infinite loops
- **Maximum Pages**: Limit to 1000 pages per crawl to prevent resource exhaustion
- **Streaming Mode**: Required for crawls exceeding memory thresholds
- **Queue Management**: Proper task queuing for large domain crawls

### Compatibility Constraints
- **FastMCP**: Requires >=2.0.0 for async tool support
- **Crawl4AI**: Requires [all] extras for full deep crawling functionality
- **Python Version**: Requires Python 3.8+ for async/await support
- **Browser Dependencies**: Requires system browser installation for headless operation

## Success Criteria

### Functional Success Criteria
- **Tool Registration**: Both tools successfully registered in MCP server
- **Parameter Validation**: All input parameters properly validated with clear error messages
- **Strategy Implementation**: All three crawling strategies (BFS, DFS, BestFirst) working correctly
- **Filtering Support**: URL pattern filtering and domain boundaries properly enforced
- **Streaming Support**: Large crawls handled efficiently with streaming mode
- **Error Handling**: Robust error handling with security sanitization

### Performance Success Criteria
- **Memory Efficiency**: Memory usage under 70% threshold with streaming for large crawls
- **Response Times**: Sub-second response for link preview, reasonable times for deep crawls
- **Concurrency**: Support for multiple concurrent crawls without resource conflicts
- **Scalability**: Handle domains with up to 1000 pages efficiently

### Quality Success Criteria
- **Code Coverage**: >90% test coverage for all new code
- **Type Safety**: Full type hints and mypy compliance
- **Documentation**: Comprehensive API documentation and examples
- **Security**: All security requirements met with proper sanitization

## High-Level Approach

### Implementation Strategy
1. **Foundation**: Implement core parameter validation and strategy factory
2. **Core Logic**: Build main domain crawling logic with strategy selection
3. **Filtering**: Implement URL filtering and domain boundary management
4. **Streaming**: Add streaming support for large crawls
5. **Preview Tool**: Implement quick link preview functionality
6. **Integration**: Register tools in MCP server and add comprehensive testing

### Development Methodology
- **Test-Driven Development**: Write tests first for all major functionality
- **Incremental Implementation**: Build and test each component separately
- **Security-First**: Implement security measures from the beginning
- **Performance Monitoring**: Track memory and performance throughout development

### Quality Assurance
- **Comprehensive Testing**: Unit, integration, and performance tests
- **Security Review**: Security validation and error sanitization testing
- **Performance Validation**: Memory usage and timing benchmarks
- **Documentation**: Complete API documentation and usage examples

## Validation Gates

### Pre-Implementation Validation
```bash
# Environment setup validation
python -c "import crawl4ai; print('Crawl4AI available')"
python -c "import fastmcp; print('FastMCP available')"
python -c "import pydantic; print('Pydantic available')"

# Test framework validation
pytest --version
mypy --version
ruff --version
```

### Implementation Validation
```bash
# Unit tests must pass
pytest tests/test_domain_crawler.py -v
pytest tests/test_domain_link_preview.py -v

# Integration tests must pass
pytest tests/test_domain_integration.py -v

# Type checking must pass
mypy tools/domain_crawler.py
mypy tools/domain_link_preview.py

# Code formatting must pass
ruff check tools/domain_crawler.py
ruff check tools/domain_link_preview.py
```

### Security Validation
```bash
# Security scanning must pass
bandit -r tools/domain_crawler.py
bandit -r tools/domain_link_preview.py

# Error sanitization tests must pass
pytest tests/test_security_validation.py -v -k "domain"
```

### Performance Validation
```bash
# Performance tests must pass
pytest tests/test_performance.py -v -k "domain"

# Memory usage tests must pass
python -m pytest tests/test_memory_usage.py -v

# Load testing validation
python scripts/load_test_domain_crawler.py
```

### MCP Protocol Validation
```bash
# MCP protocol compliance
python -m pytest tests/test_mcp_protocol.py -v -k "domain"

# Tool registration validation
python -c "
from server import mcp
print('Available tools:', [tool.name for tool in mcp.list_tools()])
"
```

## Confidence Assessment

**Exploration Completeness: 9/10**

This exploration provides comprehensive coverage of all aspects needed for successful implementation:

- **Technical Foundation**: Complete understanding of Crawl4AI's deep crawling capabilities
- **Architecture Integration**: Clear patterns for MCP tool development and integration
- **Implementation Examples**: Detailed code patterns and examples from existing codebase
- **Security Considerations**: Comprehensive security patterns and sanitization approaches
- **Performance Optimization**: Detailed memory management and scalability strategies
- **Testing Strategy**: Complete testing approach with unit, integration, and performance tests
- **Configuration Management**: Full environment and configuration patterns
- **Error Handling**: Robust error handling and recovery patterns

The only minor gap is the lack of real-world performance benchmarks, but the research provides sufficient guidance for performance optimization based on established patterns and best practices.

**Ready for flexible implementation** regardless of chosen development methodology (test-first, code-first, documentation-first, or iterative).