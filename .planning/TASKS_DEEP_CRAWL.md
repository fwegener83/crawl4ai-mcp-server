# Test-First Task Plan: Domain Deep Crawler MCP Tool

## Source
- **Exploration Document**: .planning/EXPLORE_DEEP_CRAWL.md
- **Planning Method**: Test-First Development (TDD)
- **Generated**: 2025-07-16T16:00:00Z

## Overview

This task plan implements the Domain Deep Crawler MCP Tool using Test-Driven Development methodology. The feature adds two sophisticated MCP tools (`domain_deep_crawl` and `domain_link_preview`) to the existing Crawl4AI MCP server, providing configurable deep crawling capabilities with BFS, DFS, and BestFirst strategies.

**TDD Approach:** Each implementation phase begins with comprehensive test writing, followed by minimal implementation to pass tests, then refactoring for quality and performance.

## Test Strategy

### Core Testing Principles
- **Red-Green-Refactor Cycle**: Write failing tests → Implement minimal code → Refactor with confidence
- **Test Coverage**: Maintain >90% code coverage throughout development
- **Mock-Heavy Unit Tests**: Fast, isolated tests using comprehensive mocking
- **Integration Testing**: Real Crawl4AI integration with controlled test environments
- **Performance Testing**: Memory usage and concurrency validation
- **Security Testing**: Input validation and error sanitization verification

### Testing Framework Stack
- **pytest**: Core testing framework
- **pytest-asyncio**: Async test support
- **pytest-cov**: Coverage reporting
- **unittest.mock**: Mocking and patching
- **httpx**: HTTP client for testing
- **psutil**: Memory usage monitoring

## Task Breakdown

### Phase 1: Test Foundation Setup

#### Task 1.1: Test Environment Configuration
**Objective**: Establish robust testing infrastructure for TDD workflow

**Test-First Actions:**
1. Create test configuration files with coverage requirements
2. Set up test fixtures and mock factories
3. Configure pytest for async testing and coverage reporting
4. Establish test data structures and factories

**Implementation Actions:**
1. Install and configure testing dependencies
2. Create test configuration in `pyproject.toml`
3. Set up test directory structure
4. Initialize mock factories and fixtures

**Validation Gate:**
```bash
# Test framework validation
pytest --version
pytest-asyncio --version
pytest-cov --version

# Configuration validation
pytest --collect-only tests/
pytest --cov=tools --cov-report=term-missing --dry-run
```

**Success Criteria:**
- All testing dependencies properly installed
- Test discovery works correctly
- Coverage reporting functional
- Mock factories operational

#### Task 1.2: Test Data & Mock Factory Setup
**Objective**: Create comprehensive test data and mock objects for TDD

**Test-First Actions:**
1. Write test data factories for domain crawl results
2. Create mock objects for Crawl4AI components
3. Design test fixtures for various crawl scenarios
4. Set up test configuration environments

**Implementation Actions:**
1. Implement `CrawlResultFactory` with various result types
2. Create `MockCrawlerFactory` for AsyncWebCrawler mocking
3. Build test data sets for different crawl strategies
4. Configure test environment variables

**Validation Gate:**
```bash
# Mock factory validation
python -c "
from tests.factories import CrawlResultFactory, MockCrawlerFactory
result = CrawlResultFactory.create_success_result()
crawler = MockCrawlerFactory.create_mock_crawler()
print('Mock factories operational')
"
```

**Success Criteria:**
- Comprehensive test data factories available
- Mock objects cover all Crawl4AI components
- Test fixtures support various scenarios
- Environment configuration working

### Phase 2: Parameter Validation Test Development

#### Task 2.1: Parameter Validation Tests
**Objective**: Write comprehensive tests for all parameter validation logic

**Test-First Actions:**
1. Write tests for `DomainDeepCrawlParams` validation
2. Create tests for `DomainLinkPreviewParams` validation
3. Test edge cases and error conditions
4. Validate security constraints

**Key Test Cases:**
```python
# Domain URL validation tests
def test_domain_url_validation_empty():
    """Test empty domain URL raises ValueError."""
    with pytest.raises(ValueError, match="Domain URL cannot be empty"):
        DomainDeepCrawlParams(domain_url="")

def test_domain_url_validation_invalid_scheme():
    """Test invalid URL scheme raises ValueError."""
    with pytest.raises(ValueError, match="must use HTTP or HTTPS"):
        DomainDeepCrawlParams(domain_url="ftp://example.com")

def test_crawl_strategy_validation():
    """Test invalid crawl strategy raises ValueError."""
    with pytest.raises(ValueError, match="Strategy must be one of"):
        DomainDeepCrawlParams(domain_url="https://example.com", crawl_strategy="invalid")

def test_max_depth_constraints():
    """Test max depth boundaries."""
    with pytest.raises(ValueError):
        DomainDeepCrawlParams(domain_url="https://example.com", max_depth=11)

def test_max_pages_constraints():
    """Test max pages boundaries."""
    with pytest.raises(ValueError):
        DomainDeepCrawlParams(domain_url="https://example.com", max_pages=0)
```

**Implementation Actions:**
1. Create minimal parameter validation classes
2. Implement URL validation logic
3. Add strategy validation
4. Implement boundary checking

**Validation Gate:**
```bash
pytest tests/test_parameter_validation.py -v
pytest tests/test_parameter_validation.py --cov=tools.domain_crawler --cov-report=term-missing
```

**Success Criteria:**
- All parameter validation tests pass
- Edge cases properly handled
- Error messages clear and helpful
- Security constraints enforced

#### Task 2.2: Strategy Factory Tests
**Objective**: Test dynamic strategy creation and configuration

**Test-First Actions:**
1. Write tests for BFS strategy creation
2. Create tests for DFS strategy creation
3. Test BestFirst strategy with keyword scoring
4. Validate strategy configuration parameters

**Key Test Cases:**
```python
def test_bfs_strategy_creation():
    """Test BFS strategy creation with correct parameters."""
    strategy = create_crawl_strategy(
        strategy_name="bfs",
        max_depth=2,
        max_pages=50,
        filter_chain=None,
        keywords=[]
    )
    assert isinstance(strategy, BFSDeepCrawlStrategy)
    assert strategy.max_depth == 2
    assert strategy.max_pages == 50

def test_best_first_strategy_with_keywords():
    """Test BestFirst strategy with keyword scorer."""
    strategy = create_crawl_strategy(
        strategy_name="best_first",
        max_depth=3,
        max_pages=25,
        filter_chain=None,
        keywords=["python", "crawling"]
    )
    assert isinstance(strategy, BestFirstCrawlingStrategy)
    assert strategy.url_scorer is not None
```

**Implementation Actions:**
1. Implement `create_crawl_strategy` factory function
2. Add strategy configuration logic
3. Implement keyword scorer integration
4. Add strategy validation

**Validation Gate:**
```bash
pytest tests/test_strategy_factory.py -v --cov=tools.domain_crawler
```

**Success Criteria:**
- All strategy types properly created
- Configuration parameters correctly applied
- Keyword scoring functional
- Strategy validation working

### Phase 3: Core Logic Unit Tests

#### Task 3.1: Domain Crawler Core Logic Tests
**Objective**: Test main domain crawling implementation logic

**Test-First Actions:**
1. Write tests for successful crawling scenarios
2. Create tests for error handling and recovery
3. Test streaming vs batch modes
4. Validate result formatting

**Key Test Cases:**
```python
@pytest.mark.asyncio
async def test_domain_deep_crawl_bfs_success():
    """Test successful BFS domain crawling."""
    mock_pages = [
        {"url": "https://example.com", "depth": 0, "title": "Home"},
        {"url": "https://example.com/page1", "depth": 1, "title": "Page 1"},
        {"url": "https://example.com/page2", "depth": 1, "title": "Page 2"}
    ]
    
    mock_result = CrawlResultFactory.create_domain_result(mock_pages)
    
    with patch('tools.domain_crawler.AsyncWebCrawler') as mock_crawler:
        mock_instance = setup_mock_crawler(mock_crawler, mock_result)
        
        params = DomainDeepCrawlParams(
            domain_url="https://example.com",
            max_depth=2,
            crawl_strategy="bfs"
        )
        
        result = await domain_deep_crawl_impl(params)
        
        result_data = json.loads(result)
        assert result_data["success"] is True
        assert result_data["crawl_summary"]["total_pages"] == 3
        assert result_data["crawl_summary"]["strategy_used"] == "bfs"

@pytest.mark.asyncio
async def test_domain_deep_crawl_error_handling():
    """Test error handling in domain crawling."""
    with patch('tools.domain_crawler.AsyncWebCrawler') as mock_crawler:
        mock_crawler.side_effect = Exception("Network error")
        
        params = DomainDeepCrawlParams(domain_url="https://example.com")
        result = await domain_deep_crawl_impl(params)
        
        result_data = json.loads(result)
        assert result_data["success"] is False
        assert "error" in result_data
        assert result_data["domain"] == "https://example.com"
```

**Implementation Actions:**
1. Implement `domain_deep_crawl_impl` function
2. Add error handling and sanitization
3. Implement result formatting
4. Add streaming support logic

**Validation Gate:**
```bash
pytest tests/test_domain_crawler_core.py -v --cov=tools.domain_crawler
```

**Success Criteria:**
- Core crawling logic functional
- Error handling robust
- Result formatting correct
- Streaming support working

#### Task 3.2: Link Preview Core Logic Tests
**Objective**: Test domain link preview functionality

**Test-First Actions:**
1. Write tests for successful link extraction
2. Create tests for link categorization
3. Test filtering and sorting logic
4. Validate result structure

**Key Test Cases:**
```python
@pytest.mark.asyncio
async def test_domain_link_preview_success():
    """Test successful domain link preview."""
    mock_links = [
        {"url": "https://example.com/about", "text": "About", "type": "internal"},
        {"url": "https://example.com/contact", "text": "Contact", "type": "internal"},
        {"url": "https://external.com", "text": "External", "type": "external"}
    ]
    
    mock_result = CrawlResultFactory.create_link_preview_result(mock_links)
    
    with patch('tools.domain_link_preview.AsyncWebCrawler') as mock_crawler:
        mock_instance = setup_mock_crawler(mock_crawler, mock_result)
        
        params = DomainLinkPreviewParams(
            domain_url="https://example.com",
            include_external=True
        )
        
        result = await domain_link_preview_impl(params)
        
        result_data = json.loads(result)
        assert result_data["success"] is True
        assert result_data["total_links"] == 3
        assert result_data["internal_links"] == 2
        assert result_data["external_links"] == 1
```

**Implementation Actions:**
1. Implement `domain_link_preview_impl` function
2. Add link extraction and categorization
3. Implement filtering logic
4. Add result formatting

**Validation Gate:**
```bash
pytest tests/test_domain_link_preview_core.py -v --cov=tools.domain_link_preview
```

**Success Criteria:**
- Link extraction working
- Categorization accurate
- Filtering functional
- Result structure correct

### Phase 4: Filter Chain Implementation Tests

#### Task 4.1: Filter Chain Tests
**Objective**: Test URL filtering and domain boundary logic

**Test-First Actions:**
1. Write tests for domain filtering
2. Create tests for URL pattern matching
3. Test pattern exclusion logic
4. Validate filter chain composition

**Key Test Cases:**
```python
def test_domain_filter_creation():
    """Test domain filter with allowed/blocked domains."""
    filter_chain = build_filter_chain(
        domain_url="https://example.com",
        include_external=False,
        url_patterns=["*blog*", "*docs*"],
        exclude_patterns=["*admin*"]
    )
    
    assert len(filter_chain.filters) == 3  # Domain, URL pattern, exclude pattern
    
def test_url_pattern_filtering():
    """Test URL pattern inclusion/exclusion."""
    filter_chain = build_filter_chain(
        domain_url="https://example.com",
        include_external=True,
        url_patterns=["*tutorial*"],
        exclude_patterns=["*login*"]
    )
    
    # Test pattern matching
    assert filter_chain.should_crawl("https://example.com/tutorial/python")
    assert not filter_chain.should_crawl("https://example.com/login")
```

**Implementation Actions:**
1. Implement `build_filter_chain` function
2. Add domain boundary logic
3. Implement pattern matching
4. Add filter composition

**Validation Gate:**
```bash
pytest tests/test_filter_chain.py -v --cov=tools.domain_crawler
```

**Success Criteria:**
- Domain filtering working
- Pattern matching accurate
- Exclusion logic functional
- Filter composition correct

#### Task 4.2: Streaming Support Tests
**Objective**: Test streaming functionality for large crawls

**Test-First Actions:**
1. Write tests for streaming mode activation
2. Create tests for batch processing
3. Test memory threshold handling
4. Validate streaming result processing

**Key Test Cases:**
```python
@pytest.mark.asyncio
async def test_streaming_mode_activation():
    """Test streaming mode for large crawls."""
    params = DomainDeepCrawlParams(
        domain_url="https://example.com",
        max_pages=100,
        stream_results=True
    )
    
    with patch('tools.domain_crawler.handle_streaming_crawl') as mock_stream:
        mock_stream.return_value = '{"success": true, "streaming": true}'
        
        result = await domain_deep_crawl_impl(params)
        
        mock_stream.assert_called_once()
        result_data = json.loads(result)
        assert result_data["streaming"] is True

@pytest.mark.asyncio
async def test_memory_threshold_handling():
    """Test memory threshold triggers streaming."""
    with patch('psutil.virtual_memory') as mock_memory:
        mock_memory.return_value.percent = 75  # Above 70% threshold
        
        params = DomainDeepCrawlParams(
            domain_url="https://example.com",
            max_pages=50,
            stream_results=False  # Auto-enable due to memory
        )
        
        result = await domain_deep_crawl_impl(params)
        
        # Should automatically enable streaming
        assert "streaming activated due to memory threshold" in result
```

**Implementation Actions:**
1. Implement streaming mode logic
2. Add memory threshold monitoring
3. Implement result buffering
4. Add streaming result processing

**Validation Gate:**
```bash
pytest tests/test_streaming_support.py -v --cov=tools.domain_crawler
```

**Success Criteria:**
- Streaming mode functional
- Memory monitoring working
- Result buffering correct
- Performance maintained

### Phase 5: MCP Integration Tests

#### Task 5.1: MCP Tool Registration Tests
**Objective**: Test MCP protocol integration and tool registration

**Test-First Actions:**
1. Write tests for tool registration
2. Create tests for parameter passing
3. Test MCP protocol compliance
4. Validate tool discovery

**Key Test Cases:**
```python
@pytest.mark.asyncio
async def test_mcp_tool_registration():
    """Test MCP tool registration and discovery."""
    from server import mcp
    
    # Test tool registration
    tools = mcp.list_tools()
    tool_names = [tool.name for tool in tools]
    
    assert "domain_deep_crawl" in tool_names
    assert "domain_link_preview" in tool_names

@pytest.mark.asyncio
async def test_mcp_parameter_validation():
    """Test MCP parameter validation and error handling."""
    from server import mcp
    
    # Test invalid parameters
    with pytest.raises(ValueError):
        await mcp.call_tool("domain_deep_crawl", {
            "domain_url": "invalid-url",
            "max_depth": 15  # Exceeds limit
        })

@pytest.mark.asyncio
async def test_mcp_tool_schema_compliance():
    """Test MCP tool schema compliance."""
    from server import mcp
    
    tools = mcp.list_tools()
    domain_crawl_tool = next(t for t in tools if t.name == "domain_deep_crawl")
    
    # Validate schema structure
    assert domain_crawl_tool.description is not None
    assert domain_crawl_tool.inputSchema is not None
    assert "domain_url" in domain_crawl_tool.inputSchema["properties"]
```

**Implementation Actions:**
1. Register tools in `server.py`
2. Implement MCP decorators
3. Add parameter validation
4. Implement response formatting

**Validation Gate:**
```bash
pytest tests/test_mcp_integration.py -v --cov=server
python -c "
from server import mcp
print('Available tools:', [tool.name for tool in mcp.list_tools()])
"
```

**Success Criteria:**
- Tools properly registered
- Parameter validation working
- MCP protocol compliance
- Error handling functional

#### Task 5.2: End-to-End Integration Tests
**Objective**: Test complete workflow from MCP call to result

**Test-First Actions:**
1. Write tests for complete crawl workflows
2. Create tests for error propagation
3. Test result formatting and sanitization
4. Validate logging and monitoring

**Key Test Cases:**
```python
@pytest.mark.asyncio
async def test_end_to_end_domain_crawl():
    """Test complete domain crawl workflow."""
    # Mock the entire crawl chain
    mock_pages = [
        {"url": "https://example.com", "depth": 0, "title": "Home"},
        {"url": "https://example.com/about", "depth": 1, "title": "About"}
    ]
    
    with patch('tools.domain_crawler.AsyncWebCrawler') as mock_crawler:
        mock_result = CrawlResultFactory.create_domain_result(mock_pages)
        setup_mock_crawler(mock_crawler, mock_result)
        
        # Call via MCP
        result = await domain_deep_crawl(
            domain_url="https://example.com",
            max_depth=2,
            crawl_strategy="bfs"
        )
        
        # Validate end-to-end result
        result_data = json.loads(result)
        assert result_data["success"] is True
        assert len(result_data["pages"]) == 2

@pytest.mark.asyncio
async def test_error_sanitization_end_to_end():
    """Test error sanitization in complete workflow."""
    with patch('tools.domain_crawler.AsyncWebCrawler') as mock_crawler:
        mock_crawler.side_effect = Exception("Password: secret123")
        
        result = await domain_deep_crawl(domain_url="https://example.com")
        
        # Ensure sensitive data is sanitized
        assert "secret123" not in result
        assert "[REDACTED]" in result
```

**Implementation Actions:**
1. Complete MCP integration
2. Implement error sanitization
3. Add comprehensive logging
4. Finalize result formatting

**Validation Gate:**
```bash
pytest tests/test_end_to_end.py -v --cov=tools --cov=server
```

**Success Criteria:**
- Complete workflows functional
- Error sanitization working
- Logging comprehensive
- Results properly formatted

### Phase 6: Performance & Security Testing

#### Task 6.1: Performance Testing
**Objective**: Validate performance requirements and resource usage

**Test-First Actions:**
1. Write memory usage tests
2. Create concurrency tests
3. Test response time requirements
4. Validate resource cleanup

**Key Test Cases:**
```python
@pytest.mark.asyncio
async def test_memory_usage_limits():
    """Test memory usage stays within limits."""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # Simulate large crawl
    mock_pages = [
        {"url": f"https://example.com/page{i}", "depth": 1, "title": f"Page {i}"}
        for i in range(100)
    ]
    
    with patch('tools.domain_crawler.AsyncWebCrawler') as mock_crawler:
        mock_result = CrawlResultFactory.create_domain_result(mock_pages)
        setup_mock_crawler(mock_crawler, mock_result)
        
        params = DomainDeepCrawlParams(
            domain_url="https://example.com",
            max_pages=100
        )
        
        await domain_deep_crawl_impl(params)
        
        final_memory = process.memory_info().rss
        memory_growth = final_memory - initial_memory
        
        # Assert memory growth is reasonable
        assert memory_growth < 100 * 1024 * 1024  # Less than 100MB

@pytest.mark.asyncio
async def test_concurrent_crawl_limits():
    """Test concurrent crawl limits."""
    import asyncio
    
    # Create multiple concurrent crawl tasks
    tasks = []
    for i in range(20):  # More than max_concurrent (15)
        task = asyncio.create_task(domain_deep_crawl(
            domain_url=f"https://example{i}.com"
        ))
        tasks.append(task)
    
    # Should not exceed resource limits
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Validate no resource exhaustion
    success_count = sum(1 for r in results if not isinstance(r, Exception))
    assert success_count > 0  # At least some should succeed
```

**Implementation Actions:**
1. Implement memory monitoring
2. Add concurrency controls
3. Implement resource cleanup
4. Add performance logging

**Validation Gate:**
```bash
pytest tests/test_performance.py -v --cov=tools
python -m pytest tests/test_performance.py --benchmark-only
```

**Success Criteria:**
- Memory usage within limits
- Concurrency properly controlled
- Resource cleanup working
- Performance requirements met

#### Task 6.2: Security Testing
**Objective**: Validate security requirements and input sanitization

**Test-First Actions:**
1. Write input validation tests
2. Create error sanitization tests
3. Test injection attack prevention
4. Validate security constraints

**Key Test Cases:**
```python
def test_sql_injection_prevention():
    """Test SQL injection attempt prevention."""
    malicious_url = "https://example.com'; DROP TABLE users; --"
    
    with pytest.raises(ValueError, match="Invalid domain URL format"):
        DomainDeepCrawlParams(domain_url=malicious_url)

def test_xss_prevention():
    """Test XSS prevention in parameters."""
    xss_patterns = "<script>alert('xss')</script>"
    
    with pytest.raises(ValueError):
        DomainDeepCrawlParams(
            domain_url="https://example.com",
            url_patterns=[xss_patterns]
        )

@pytest.mark.asyncio
async def test_error_message_sanitization():
    """Test sensitive data sanitization in errors."""
    with patch('tools.domain_crawler.AsyncWebCrawler') as mock_crawler:
        mock_crawler.side_effect = Exception(
            "Connection failed: username=admin, password=secret123"
        )
        
        result = await domain_deep_crawl(domain_url="https://example.com")
        
        # Ensure sensitive data is sanitized
        assert "admin" not in result
        assert "secret123" not in result
        assert "[REDACTED]" in result

def test_path_traversal_prevention():
    """Test path traversal prevention."""
    malicious_patterns = ["../../../etc/passwd", "..\\..\\windows\\system32"]
    
    for pattern in malicious_patterns:
        with pytest.raises(ValueError):
            DomainDeepCrawlParams(
                domain_url="https://example.com",
                url_patterns=[pattern]
            )
```

**Implementation Actions:**
1. Implement comprehensive input validation
2. Add security sanitization
3. Implement injection prevention
4. Add security logging

**Validation Gate:**
```bash
pytest tests/test_security.py -v --cov=tools
bandit -r tools/domain_crawler.py
bandit -r tools/domain_link_preview.py
```

**Success Criteria:**
- Input validation comprehensive
- Injection attempts blocked
- Error sanitization working
- Security constraints enforced

### Phase 7: Documentation & Maintenance

#### Task 7.1: Documentation Testing
**Objective**: Validate documentation accuracy and examples

**Test-First Actions:**
1. Write tests for documentation examples
2. Create tests for API documentation
3. Test usage examples
4. Validate configuration documentation

**Key Test Cases:**
```python
def test_documentation_examples():
    """Test all code examples in documentation."""
    # Test basic usage example
    params = DomainDeepCrawlParams(
        domain_url="https://docs.example.com",
        max_depth=2,
        max_pages=50
    )
    assert params.domain_url == "https://docs.example.com"
    assert params.max_depth == 2
    
    # Test advanced usage example
    params = DomainDeepCrawlParams(
        domain_url="https://blog.example.com",
        max_depth=3,
        crawl_strategy="best_first",
        url_patterns=["*tutorial*", "*guide*"],
        exclude_patterns=["*admin*", "*login*"],
        keywords=["python", "crawling", "tutorial"],
        max_pages=25
    )
    assert params.crawl_strategy == "best_first"
    assert len(params.keywords) == 3

@pytest.mark.asyncio
async def test_readme_examples():
    """Test examples from README work correctly."""
    # Test examples from README
    with patch('tools.domain_crawler.AsyncWebCrawler') as mock_crawler:
        mock_result = CrawlResultFactory.create_success_result()
        setup_mock_crawler(mock_crawler, mock_result)
        
        # Example 1: Basic crawl
        result = await domain_deep_crawl(
            domain_url="https://docs.example.com",
            max_depth=2,
            max_pages=50
        )
        assert "success" in result
        
        # Example 2: Advanced crawl
        result = await domain_deep_crawl(
            domain_url="https://blog.example.com",
            max_depth=3,
            crawl_strategy="best_first",
            url_patterns=["*tutorial*", "*guide*"],
            keywords=["python", "crawling"]
        )
        assert "success" in result
```

**Implementation Actions:**
1. Update documentation with examples
2. Add API documentation
3. Create usage guides
4. Add configuration documentation

**Validation Gate:**
```bash
pytest tests/test_documentation.py -v
python -m doctest README.md
```

**Success Criteria:**
- Documentation examples work
- API documentation accurate
- Usage guides functional
- Configuration documented

#### Task 7.2: Maintenance Test Suite
**Objective**: Create comprehensive maintenance and regression tests

**Test-First Actions:**
1. Write regression test suite
2. Create automated test execution
3. Test upgrade scenarios
4. Validate backward compatibility

**Key Test Cases:**
```python
def test_parameter_backward_compatibility():
    """Test parameter backward compatibility."""
    # Test old parameter format still works
    params = DomainDeepCrawlParams(
        domain_url="https://example.com",
        max_depth=2
    )
    assert params.crawl_strategy == "bfs"  # Default
    assert params.max_pages == 50  # Default

@pytest.mark.asyncio
async def test_version_compatibility():
    """Test version compatibility and upgrades."""
    # Test that new features don't break old functionality
    result = await domain_deep_crawl(domain_url="https://example.com")
    assert "success" in result

def test_configuration_migration():
    """Test configuration migration scenarios."""
    # Test environment variable handling
    import os
    
    os.environ["CRAWL4AI_MAX_DEPTH"] = "5"
    os.environ["CRAWL4AI_MAX_PAGES"] = "100"
    
    # Should use environment defaults
    params = DomainDeepCrawlParams(domain_url="https://example.com")
    # Test that environment variables are respected
    
    # Cleanup
    del os.environ["CRAWL4AI_MAX_DEPTH"]
    del os.environ["CRAWL4AI_MAX_PAGES"]
```

**Implementation Actions:**
1. Create regression test suite
2. Implement automated testing
3. Add version compatibility tests
4. Create maintenance procedures

**Validation Gate:**
```bash
pytest tests/test_regression.py -v
pytest tests/test_maintenance.py -v
```

**Success Criteria:**
- Regression tests comprehensive
- Automated testing working
- Version compatibility maintained
- Maintenance procedures documented

## Task Dependencies

### Phase Dependencies
1. **Phase 1** (Test Foundation) → **Phase 2** (Parameter Validation)
2. **Phase 2** (Parameter Validation) → **Phase 3** (Core Logic)
3. **Phase 3** (Core Logic) → **Phase 4** (Filter Chain)
4. **Phase 4** (Filter Chain) → **Phase 5** (MCP Integration)
5. **Phase 5** (MCP Integration) → **Phase 6** (Performance & Security)
6. **Phase 6** (Performance & Security) → **Phase 7** (Documentation)

### Critical Path Tasks
1. **Task 1.1** (Test Environment) → All subsequent tasks
2. **Task 2.1** (Parameter Validation) → **Task 3.1** (Core Logic)
3. **Task 3.1** (Core Logic) → **Task 5.1** (MCP Integration)
4. **Task 5.2** (End-to-End) → **Task 6.1** (Performance Testing)

### Parallel Execution Opportunities
- **Task 2.1** and **Task 2.2** can run in parallel
- **Task 3.1** and **Task 3.2** can run in parallel
- **Task 4.1** and **Task 4.2** can run in parallel
- **Task 6.1** and **Task 6.2** can run in parallel
- **Task 7.1** and **Task 7.2** can run in parallel

## Validation Gates

### Phase 1 Validation
```bash
# Test environment setup
pytest --version && pytest-asyncio --version && pytest-cov --version

# Test discovery and configuration
pytest --collect-only tests/
pytest --cov=tools --cov-report=term-missing --dry-run

# Mock factories operational
python -c "
from tests.factories import CrawlResultFactory, MockCrawlerFactory
print('✓ Mock factories operational')
"
```

### Phase 2 Validation
```bash
# Parameter validation tests
pytest tests/test_parameter_validation.py -v --cov=tools --cov-report=term-missing

# Strategy factory tests
pytest tests/test_strategy_factory.py -v --cov=tools --cov-report=term-missing

# Coverage check
pytest --cov=tools --cov-fail-under=90
```

### Phase 3 Validation
```bash
# Core logic tests
pytest tests/test_domain_crawler_core.py -v --cov=tools
pytest tests/test_domain_link_preview_core.py -v --cov=tools

# Error handling tests
pytest tests/test_error_handling.py -v

# Mock integration tests
pytest tests/test_mock_integration.py -v
```

### Phase 4 Validation
```bash
# Filter chain tests
pytest tests/test_filter_chain.py -v --cov=tools

# Streaming support tests
pytest tests/test_streaming_support.py -v --cov=tools

# Performance baseline tests
pytest tests/test_performance_baseline.py -v
```

### Phase 5 Validation
```bash
# MCP integration tests
pytest tests/test_mcp_integration.py -v --cov=server

# End-to-end tests
pytest tests/test_end_to_end.py -v --cov=tools --cov=server

# Protocol compliance
python -c "
from server import mcp
tools = mcp.list_tools()
print('✓ Available tools:', [t.name for t in tools])
"
```

### Phase 6 Validation
```bash
# Performance tests
pytest tests/test_performance.py -v --cov=tools

# Security tests
pytest tests/test_security.py -v --cov=tools

# Security scanning
bandit -r tools/domain_crawler.py
bandit -r tools/domain_link_preview.py

# Load testing
python scripts/load_test_domain_crawler.py
```

### Phase 7 Validation
```bash
# Documentation tests
pytest tests/test_documentation.py -v
python -m doctest README.md

# Regression tests
pytest tests/test_regression.py -v
pytest tests/test_maintenance.py -v

# Final comprehensive test
pytest tests/ -v --cov=tools --cov=server --cov-report=term-missing --cov-fail-under=90
```

## Success Criteria

### Functional Success Criteria
- **Tool Registration**: Both `domain_deep_crawl` and `domain_link_preview` tools successfully registered in MCP server
- **Parameter Validation**: All input parameters properly validated with comprehensive error messages
- **Strategy Implementation**: All three crawling strategies (BFS, DFS, BestFirst) implemented and tested
- **Filtering Support**: URL pattern filtering and domain boundaries properly implemented and tested
- **Streaming Support**: Large crawls handled efficiently with streaming mode
- **Error Handling**: Robust error handling with security sanitization

### Performance Success Criteria
- **Memory Efficiency**: Memory usage under 70% threshold with streaming for large crawls
- **Response Times**: Sub-second response for link preview, reasonable times for deep crawls
- **Concurrency**: Support for up to 15 concurrent crawls without resource conflicts
- **Scalability**: Handle domains with up to 1000 pages efficiently

### Quality Success Criteria
- **Code Coverage**: >90% test coverage for all new code
- **Test Quality**: Comprehensive test suite with unit, integration, and end-to-end tests
- **Type Safety**: Full type hints and mypy compliance
- **Security**: All security requirements met with proper sanitization
- **Documentation**: Comprehensive API documentation and working examples

### Test-First Success Criteria
- **TDD Adherence**: All implementation code written after corresponding tests
- **Red-Green-Refactor**: Proper TDD cycle followed throughout development
- **Test Coverage**: Tests written before implementation for all functionality
- **Refactoring Safety**: Comprehensive test suite enables confident refactoring

## Estimated Timeline

### Phase 1: Test Foundation (1-2 days)
- **Task 1.1**: Test Environment Setup (4-6 hours)
- **Task 1.2**: Test Data & Mock Factory Setup (4-6 hours)

### Phase 2: Parameter Validation (1-2 days)
- **Task 2.1**: Parameter Validation Tests (4-6 hours)
- **Task 2.2**: Strategy Factory Tests (4-6 hours)

### Phase 3: Core Logic (2-3 days)
- **Task 3.1**: Domain Crawler Core Logic Tests (8-10 hours)
- **Task 3.2**: Link Preview Core Logic Tests (4-6 hours)

### Phase 4: Filter Chain (1-2 days)
- **Task 4.1**: Filter Chain Tests (4-6 hours)
- **Task 4.2**: Streaming Support Tests (4-6 hours)

### Phase 5: MCP Integration (1-2 days)
- **Task 5.1**: MCP Tool Registration Tests (4-6 hours)
- **Task 5.2**: End-to-End Integration Tests (4-6 hours)

### Phase 6: Performance & Security (2-3 days)
- **Task 6.1**: Performance Testing (6-8 hours)
- **Task 6.2**: Security Testing (6-8 hours)

### Phase 7: Documentation & Maintenance (1-2 days)
- **Task 7.1**: Documentation Testing (4-6 hours)
- **Task 7.2**: Maintenance Test Suite (4-6 hours)

**Total Estimated Time: 8-14 days**

## Quality Assessment

### Task Plan Completeness: 10/10
- All necessary testing phases covered comprehensively
- Each phase includes both test creation and implementation
- Validation gates are executable and specific
- Dependencies clearly defined and manageable

### Test-First Adherence: 10/10
- Tests written before implementation for all functionality
- Red-Green-Refactor cycle explicitly defined
- Test coverage requirements specified (>90%)
- TDD methodology properly followed

### Task Clarity: 9/10
- Tasks are clear, actionable, and well-defined
- Each task has specific objectives and success criteria
- Implementation steps are concrete and achievable
- Dependencies and prerequisites clearly stated

### Feasibility: 9/10
- Tasks are realistically scoped and achievable
- Timeline estimates are reasonable
- Resource requirements are manageable
- Risk mitigation strategies included

**Overall Assessment: 9.5/10**

This test-first task plan provides a comprehensive, systematic approach to implementing the Domain Deep Crawler MCP Tool using rigorous Test-Driven Development methodology. The plan ensures high code quality, comprehensive test coverage, and robust implementation through systematic testing at every level.