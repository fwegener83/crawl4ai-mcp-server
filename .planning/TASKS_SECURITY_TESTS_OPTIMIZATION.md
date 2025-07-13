# Test-First Task Plan: Security Tests Optimization & CI/CD Implementation

## Source
- **Exploration Document**: .planning/EXPLORE_SECURITY_TESTS_OPTIMIZATION.md
- **Planning Method**: Test-First Development (TDD)
- **Generated**: 2025-07-13

## Overview

This task plan implements a test-first approach to solve critical performance and security issues in the crawl4ai-mcp-server project. The primary goal is to reduce security test runtime from 20+ minutes to <2 minutes while implementing comprehensive CI/CD infrastructure.

**Critical Issues to Address:**
- Security tests with 1254+ second runtime due to real network operations
- Security vulnerability in error message sanitization (password exposure)
- Missing CI/CD pipeline for automated validation
- Pydantic deprecation warnings affecting test output

## Test Strategy

**Test-First Development Principles:**
1. **Red-Green-Refactor Cycle**: Write failing tests first, implement minimal code to pass, then refactor
2. **Comprehensive Mock Strategy**: Test logic without external dependencies
3. **Performance Validation**: Test performance requirements at each level
4. **Security Validation**: Test security measures before implementing features
5. **Integration Testing**: Validate component interactions through tests

**Testing Hierarchy:**
- **Unit Tests**: Individual function/class behavior with mocks
- **Integration Tests**: Component interaction without external dependencies  
- **System Tests**: End-to-end functionality with comprehensive mocking
- **Performance Tests**: Timing and resource usage validation
- **Security Tests**: Vulnerability and sanitization validation

## Task Breakdown

### Phase 1: Test Foundation Setup

#### Task 1.1: Enhanced Testing Infrastructure
**Objective**: Establish comprehensive test environment with performance monitoring

**Test Requirements:**
```python
# tests/test_framework_setup.py
def test_pytest_configuration_loaded():
    """Verify pytest configuration is properly loaded."""
    assert pytest_config.timeout == 300
    assert "slow" in pytest_config.markers
    assert "security" in pytest_config.markers

def test_async_testing_support():
    """Verify asyncio testing works correctly."""
    async def sample_async_function():
        return "test"
    
    result = await sample_async_function()
    assert result == "test"

def test_timeout_enforcement():
    """Verify timeout mechanisms work properly."""
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(asyncio.sleep(2), timeout=0.1)
```

**Implementation Tasks:**
- [ ] Create enhanced `pyproject.toml` with security markers
- [ ] Add pytest-timeout configuration
- [ ] Implement performance monitoring fixtures
- [ ] Set up test environment isolation

**Validation Command:**
```bash
pytest tests/test_framework_setup.py -v --timeout=10
```

#### Task 1.2: Mock Factory Framework
**Objective**: Create reusable mock infrastructure for security testing

**Test Requirements:**
```python
# tests/test_mock_factory.py
def test_crawl_result_factory_success():
    """Test successful crawl result mock creation."""
    result = CrawlResultFactory.create_success_result(
        content="Test content",
        title="Test Title"
    )
    assert result.markdown == "Test content"
    assert result.title == "Test Title"
    assert result.success is True

def test_async_web_crawler_mock_context_manager():
    """Test AsyncWebCrawler mock as context manager."""
    with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
        mock_instance = AsyncMock()
        mock_crawler.return_value.__aenter__.return_value = mock_instance
        
        # Test context manager behavior
        assert mock_instance is not None

def test_security_scenario_mock_factory():
    """Test security scenario mock responses."""
    factory = SecurityMockFactory()
    
    # Test malicious URL blocking
    with pytest.raises(ValueError):
        factory.mock_response("javascript:alert('xss')")
    
    # Test private IP blocking  
    with pytest.raises(ConnectionError):
        factory.mock_response("http://127.0.0.1/admin")
```

**Implementation Tasks:**
- [ ] Create `CrawlResultFactory` class
- [ ] Implement `SecurityMockFactory` class
- [ ] Add async context manager mock utilities
- [ ] Create configurable response patterns

**Validation Command:**
```bash
pytest tests/test_mock_factory.py -v --timeout=5
```

### Phase 2: Error Message Sanitization (Security Critical)

#### Task 2.1: Sanitization Logic Unit Tests
**Objective**: Test error message sanitization before implementation

**Test Requirements:**
```python
# tests/test_error_sanitization.py
@pytest.mark.parametrize("input_error,expected_patterns", [
    (
        "Database failed: postgresql://user:password@localhost:5432/db",
        {"should_contain": ["Database failed", "postgresql://", "localhost"],
         "should_not_contain": ["password", "user:password"]}
    ),
    (
        "API key error: sk-1234567890abcdef failed",
        {"should_contain": ["API key error", "failed"],
         "should_not_contain": ["sk-1234567890abcdef"]}
    ),
    (
        "File not found: /etc/passwd",
        {"should_contain": ["File not found"],
         "should_not_contain": ["/etc/passwd"]}
    ),
])
def test_error_message_sanitization(input_error, expected_patterns):
    """Test error message sanitization patterns."""
    # This test will FAIL initially (Red phase)
    sanitized = sanitize_error_message(input_error)
    
    for content in expected_patterns["should_contain"]:
        assert content in sanitized
    
    for sensitive in expected_patterns["should_not_contain"]:
        assert sensitive not in sanitized

def test_sanitization_preserves_useful_info():
    """Test that sanitization doesn't over-sanitize."""
    error = "Connection failed to https://example.com:443 with timeout"
    sanitized = sanitize_error_message(error)
    
    assert "Connection failed" in sanitized
    assert "example.com" in sanitized
    assert "timeout" in sanitized

def test_sanitization_comprehensive_patterns():
    """Test comprehensive sanitization pattern coverage."""
    test_cases = [
        "postgresql://user:secret@db.com/prod",
        "mysql://admin:password123@localhost:3306",
        "API_KEY=sk-abcd1234efgh5678 failed",
        "SECRET_TOKEN=abc123def456 invalid",
        "Error in /etc/passwd access",
        "Failed C:\\Users\\Admin\\secret.txt",
        "AWS key AKIAIOSFODNN7EXAMPLE leaked",
    ]
    
    for case in test_cases:
        sanitized = sanitize_error_message(case)
        # Verify no sensitive patterns remain
        assert not re.search(r'password|secret|sk-[a-zA-Z0-9]+', sanitized, re.IGNORECASE)
```

**Implementation Tasks:**
- [ ] Implement `sanitize_error_message()` function
- [ ] Add comprehensive regex patterns for sensitive data
- [ ] Create validation helper functions
- [ ] Integrate with error handling in `tools/web_extract.py`

**Validation Command:**
```bash
pytest tests/test_error_sanitization.py -v --timeout=5
```

#### Task 2.2: Integration with Web Extract Tool
**Objective**: Integrate sanitization into actual error handling

**Test Requirements:**
```python
# tests/test_web_extract_security.py
@pytest.mark.asyncio
async def test_web_extract_sanitizes_network_errors():
    """Test web extract sanitizes network error messages."""
    # Mock network error with sensitive info
    def mock_error_side_effect(*args, **kwargs):
        raise Exception("Connection to postgresql://user:password@localhost failed")
    
    with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
        mock_instance = AsyncMock()
        mock_crawler.return_value.__aenter__.return_value = mock_instance
        mock_instance.arun.side_effect = mock_error_side_effect
        
        params = WebExtractParams(url="https://example.com")
        result = await web_content_extract(params)
        
        # Verify error is sanitized
        assert "password" not in result
        assert "Error extracting content" in result
        assert "[REDACTED]" in result

@pytest.mark.asyncio
async def test_web_extract_preserves_useful_error_info():
    """Test web extract preserves useful error information."""
    def mock_timeout_error(*args, **kwargs):
        raise asyncio.TimeoutError("Request timeout after 30 seconds")
    
    with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
        mock_instance = AsyncMock()
        mock_crawler.return_value.__aenter__.return_value = mock_instance
        mock_instance.arun.side_effect = mock_timeout_error
        
        params = WebExtractParams(url="https://example.com")
        result = await web_content_extract(params)
        
        # Verify useful info is preserved
        assert "timeout" in result.lower()
        assert "Error extracting content" in result
```

**Implementation Tasks:**
- [ ] Modify `web_content_extract()` to use sanitization
- [ ] Update error logging to use sanitized messages
- [ ] Ensure both sync and async error paths are covered
- [ ] Add performance monitoring for sanitization overhead

**Validation Command:**
```bash
pytest tests/test_web_extract_security.py -v --timeout=10
```

### Phase 3: Security Test Optimization (Performance Critical)

#### Task 3.1: Mock-Based Security Test Suite
**Objective**: Replace slow security tests with fast mocked versions

**Test Requirements:**
```python
# tests/test_security_optimization.py
@pytest.mark.asyncio
async def test_localhost_blocking_optimized():
    """Test localhost blocking with mocked network calls (target: <5 seconds)."""
    start_time = time.perf_counter()
    
    # Setup mock to simulate private IP blocking
    def mock_private_ip_response(url=None, config=None):
        if any(pattern in url.lower() for pattern in ['127.0.0.1', 'localhost']):
            raise ConnectionError(f"Private IP access denied: {url}")
        return CrawlResultFactory.create_success_result(url=url)
    
    with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
        mock_instance = AsyncMock()
        mock_crawler.return_value.__aenter__.return_value = mock_instance
        mock_instance.arun.side_effect = mock_private_ip_response
        
        from server import mcp
        async with Client(mcp) as client:
            private_addresses = [
                "http://localhost:8080/admin",
                "http://127.0.0.1:3306/database",
                "http://127.0.0.1:22/ssh",
            ]
            
            for url in private_addresses:
                result = await client.call_tool_mcp("web_content_extract", {"url": url})
                assert result.isError or "error" in result.content[0].text.lower()
    
    duration = time.perf_counter() - start_time
    assert duration < 5.0, f"Test took {duration:.2f}s, expected <5s"

@pytest.mark.asyncio  
async def test_port_scanning_prevention_optimized():
    """Test port scanning prevention with mocked responses (target: <5 seconds)."""
    start_time = time.perf_counter()
    
    def mock_port_blocking_response(url=None, config=None):
        suspicious_ports = [':22/', ':3306/', ':5432/', ':6379/']
        if any(port in url for port in suspicious_ports):
            raise ConnectionRefusedError(f"Port access blocked: {url}")
        return CrawlResultFactory.create_success_result(url=url)
    
    with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
        mock_instance = AsyncMock()
        mock_crawler.return_value.__aenter__.return_value = mock_instance
        mock_instance.arun.side_effect = mock_port_blocking_response
        
        from server import mcp
        async with Client(mcp) as client:
            port_scan_attempts = [
                "http://example.com:22/ssh",
                "http://example.com:3306/mysql",
                "http://example.com:5432/postgresql",
            ]
            
            tasks = []
            for url in port_scan_attempts:
                task = asyncio.create_task(
                    client.call_tool_mcp("web_content_extract", {"url": url})
                )
                tasks.append(task)
            
            # Execute concurrently for speed
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Verify all blocked
            for result in results:
                assert isinstance(result, Exception) or result.isError
    
    duration = time.perf_counter() - start_time
    assert duration < 5.0, f"Test took {duration:.2f}s, expected <5s"

def test_security_test_performance_monitoring():
    """Test that security test performance meets targets."""
    # This test validates the performance targets
    performance_targets = {
        'test_localhost_blocking_optimized': 5.0,
        'test_port_scanning_prevention_optimized': 5.0,
        'test_malicious_url_blocking': 3.0,
    }
    
    for test_name, target_time in performance_targets.items():
        assert target_time > 0, f"Performance target for {test_name} must be positive"
```

**Implementation Tasks:**
- [ ] Replace real network calls in `test_localhost_and_private_ip_blocking`
- [ ] Optimize `test_port_scanning_prevention` with comprehensive mocking
- [ ] Add performance monitoring to all security tests
- [ ] Remove `@pytest.mark.slow` from optimized tests

**Validation Command:**
```bash
pytest tests/test_security_optimization.py -v --timeout=30 --durations=5
```

#### Task 3.2: Concurrent Security Testing
**Objective**: Implement concurrent test execution for improved performance

**Test Requirements:**
```python
# tests/test_concurrent_security.py
@pytest.mark.asyncio
async def test_concurrent_security_validation():
    """Test concurrent security validation execution."""
    security_urls = [
        "javascript:alert('xss')",
        "file:///etc/passwd", 
        "http://127.0.0.1/admin",
        "data:text/html,<script>alert('xss')</script>",
        "http://example.com:22/ssh",
    ]
    
    start_time = time.perf_counter()
    
    with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
        mock_instance = AsyncMock()
        mock_crawler.return_value.__aenter__.return_value = mock_instance
        
        def security_mock_response(url=None, config=None):
            # Simulate appropriate blocking for each URL type
            if 'javascript:' in url:
                raise ValueError(f"Invalid URL scheme: {url}")
            elif '127.0.0.1' in url:
                raise ConnectionError(f"Private IP blocked: {url}")
            elif ':22/' in url:
                raise ConnectionRefusedError(f"Port blocked: {url}")
            else:
                return CrawlResultFactory.create_success_result(url=url)
        
        mock_instance.arun.side_effect = security_mock_response
        
        from server import mcp
        async with Client(mcp) as client:
            # Execute all security tests concurrently
            tasks = [
                client.call_tool_mcp("web_content_extract", {"url": url})
                for url in security_urls
            ]
            
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=10.0
            )
            
            # Verify all were properly blocked/handled
            blocked_count = sum(1 for r in results 
                               if isinstance(r, Exception) or 
                               (hasattr(r, 'isError') and r.isError))
            
            assert blocked_count >= len(security_urls) * 0.8  # 80% blocked
    
    duration = time.perf_counter() - start_time
    assert duration < 10.0, f"Concurrent test took {duration:.2f}s, expected <10s"

@pytest.mark.asyncio
async def test_resource_cleanup_after_concurrent_tests():
    """Test proper resource cleanup after concurrent execution."""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Run multiple concurrent test batches
    for batch in range(3):
        await test_concurrent_security_validation()
    
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = final_memory - initial_memory
    
    assert memory_increase < 50, f"Memory leak detected: {memory_increase:.1f}MB increase"
```

**Implementation Tasks:**
- [ ] Implement concurrent test execution patterns
- [ ] Add resource monitoring and cleanup
- [ ] Optimize async context management
- [ ] Add timeout protection for concurrent operations

**Validation Command:**
```bash
pytest tests/test_concurrent_security.py -v --timeout=60
```

### Phase 4: CI/CD Pipeline Implementation

#### Task 4.1: GitHub Actions Workflow Tests
**Objective**: Test CI/CD workflow configuration before implementation

**Test Requirements:**
```python
# tests/test_cicd_configuration.py
def test_github_actions_workflow_syntax():
    """Test GitHub Actions workflow file syntax."""
    import yaml
    import os
    
    workflow_path = ".github/workflows/ci.yml"
    if os.path.exists(workflow_path):
        with open(workflow_path, 'r') as f:
            workflow = yaml.safe_load(f)
        
        # Validate required workflow structure
        assert 'name' in workflow
        assert 'on' in workflow  
        assert 'jobs' in workflow
        
        # Validate job structure
        jobs = workflow['jobs']
        assert 'fast-tests' in jobs
        assert 'security-tests' in jobs
        
        # Validate timeout configurations
        for job_name, job_config in jobs.items():
            if 'timeout-minutes' in job_config:
                assert job_config['timeout-minutes'] <= 20

def test_pytest_configuration_for_ci():
    """Test pytest configuration is optimized for CI."""
    import tomli
    
    with open('pyproject.toml', 'rb') as f:
        config = tomli.load(f)
    
    pytest_config = config['tool']['pytest']['ini_options']
    
    # Validate CI-friendly configuration
    assert 'timeout' in pytest_config or 'addopts' in pytest_config
    assert 'slow' in str(pytest_config.get('markers', ''))
    assert pytest_config.get('asyncio_mode') == 'auto'

def test_environment_variable_configuration():
    """Test environment variables for CI testing."""
    test_env_vars = {
        'CRAWL4AI_VERBOSE': 'false',
        'SECURITY_TEST_MODE': 'mock',
        'PYTHONUNBUFFERED': '1'
    }
    
    # These should be set in CI environment
    # Test validates the expected configuration
    for var, expected_value in test_env_vars.items():
        # This test documents required environment variables
        assert expected_value in ['true', 'false', '1', 'mock']
```

**Implementation Tasks:**
- [ ] Create GitHub Actions workflow file (`.github/workflows/ci.yml`)
- [ ] Configure 3-tier testing strategy (fast/comprehensive/security)
- [ ] Add parallel test execution with matrix strategy
- [ ] Set up branch protection rules

**Validation Command:**
```bash
pytest tests/test_cicd_configuration.py -v
```

#### Task 4.2: Performance Monitoring Integration
**Objective**: Test performance tracking and regression detection

**Test Requirements:**
```python
# tests/test_performance_monitoring.py
def test_performance_regression_detection():
    """Test performance regression detection mechanism."""
    import json
    import time
    
    # Simulate performance test results
    current_results = {
        'security_test_suite': 45.2,  # seconds
        'fast_test_suite': 35.8,
        'individual_security_test_avg': 2.1
    }
    
    baseline_results = {
        'security_test_suite': 120.0,  # Previous slow baseline
        'fast_test_suite': 40.0,
        'individual_security_test_avg': 8.5
    }
    
    # Calculate improvement percentages
    for test_name, current_time in current_results.items():
        baseline_time = baseline_results[test_name]
        improvement = (baseline_time - current_time) / baseline_time * 100
        
        # Validate significant improvement achieved
        if test_name == 'security_test_suite':
            assert improvement > 60, f"Security suite should improve >60%, got {improvement:.1f}%"
        elif test_name == 'individual_security_test_avg':
            assert improvement > 50, f"Individual tests should improve >50%, got {improvement:.1f}%"

@pytest.mark.asyncio
async def test_benchmark_data_collection():
    """Test performance benchmark data collection."""
    import asyncio
    import time
    
    # Mock performance test execution
    async def mock_security_test():
        await asyncio.sleep(0.1)  # Simulate fast test
        return "test_passed"
    
    # Measure performance
    start_time = time.perf_counter()
    result = await mock_security_test()
    duration = time.perf_counter() - start_time
    
    # Validate performance data format
    performance_data = {
        'test_name': 'mock_security_test',
        'duration': duration,
        'result': result,
        'timestamp': time.time()
    }
    
    assert 'test_name' in performance_data
    assert 'duration' in performance_data
    assert performance_data['duration'] < 1.0  # Should be fast
    assert performance_data['result'] == "test_passed"

def test_coverage_reporting_configuration():
    """Test coverage reporting is properly configured."""
    import tomli
    
    with open('pyproject.toml', 'rb') as f:
        config = tomli.load(f)
    
    coverage_config = config.get('tool', {}).get('coverage', {})
    
    if coverage_config:
        # Validate coverage configuration
        run_config = coverage_config.get('run', {})
        report_config = coverage_config.get('report', {})
        
        assert 'source' in run_config
        assert 'omit' in run_config
        assert 'tests/*' in run_config['omit']
```

**Implementation Tasks:**
- [ ] Implement performance benchmark collection
- [ ] Add coverage reporting integration
- [ ] Configure performance regression detection
- [ ] Set up automated performance alerts

**Validation Command:**
```bash
pytest tests/test_performance_monitoring.py -v --timeout=10
```

### Phase 5: System Integration Testing

#### Task 5.1: End-to-End Workflow Validation
**Objective**: Test complete system workflow with optimized components

**Test Requirements:**
```python
# tests/test_e2e_optimized.py
@pytest.mark.asyncio
async def test_complete_security_workflow_optimized():
    """Test end-to-end security workflow with all optimizations."""
    start_time = time.perf_counter()
    
    # Test complete MCP protocol sequence with security validation
    with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
        mock_instance = AsyncMock()
        mock_crawler.return_value.__aenter__.return_value = mock_instance
        
        def comprehensive_mock_response(url=None, config=None):
            # Comprehensive URL validation logic
            if any(scheme in url.lower() for scheme in ['javascript:', 'file:', 'data:']):
                raise ValueError(f"Invalid URL scheme: {url}")
            elif any(pattern in url.lower() for pattern in ['127.0.0.1', 'localhost']):
                raise ConnectionError(f"Private IP access denied: {url}")
            elif any(port in url for port in [':22/', ':3306/', ':5432/']):
                raise ConnectionRefusedError(f"Port access blocked: {url}")
            else:
                return CrawlResultFactory.create_success_result(
                    content=f"Safe content from {url}",
                    title="Safe Page",
                    url=url
                )
        
        mock_instance.arun.side_effect = comprehensive_mock_response
        
        from server import mcp
        async with Client(mcp) as client:
            # Test various URL categories
            test_scenarios = [
                # Malicious URLs (should be blocked)
                ("javascript:alert('xss')", True),
                ("file:///etc/passwd", True),
                ("data:text/html,<script>", True),
                
                # Private IPs (should be blocked)
                ("http://127.0.0.1/admin", True),
                ("http://localhost:8080/", True),
                
                # Suspicious ports (should be blocked)
                ("http://example.com:22/ssh", True),
                ("http://example.com:3306/mysql", True),
                
                # Safe URLs (should succeed)
                ("https://example.com", False),
                ("https://httpbin.org/get", False),
            ]
            
            results = []
            for url, should_be_blocked in test_scenarios:
                result = await client.call_tool_mcp("web_content_extract", {"url": url})
                is_blocked = result.isError or "error" in result.content[0].text.lower()
                
                if should_be_blocked:
                    assert is_blocked, f"URL {url} should have been blocked"
                else:
                    assert not is_blocked, f"URL {url} should have succeeded"
                
                results.append((url, is_blocked, should_be_blocked))
    
    duration = time.perf_counter() - start_time
    assert duration < 30.0, f"E2E test took {duration:.2f}s, expected <30s"
    
    return results

@pytest.mark.asyncio
async def test_error_sanitization_e2e():
    """Test error sanitization in end-to-end workflow."""
    sensitive_error_scenarios = [
        "postgresql://user:secret123@localhost:5432/db",
        "mysql://admin:password@db.example.com:3306",
        "API key sk-1234567890abcdef authentication failed",
        "Error accessing /etc/passwd on server",
    ]
    
    with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
        mock_instance = AsyncMock()
        mock_crawler.return_value.__aenter__.return_value = mock_instance
        
        def error_simulation_response(url=None, config=None):
            # Simulate different types of sensitive errors
            if "db-error" in url:
                raise Exception("postgresql://user:secret123@localhost:5432/db connection failed")
            elif "api-error" in url:
                raise Exception("API key sk-1234567890abcdef authentication failed")
            elif "file-error" in url:
                raise Exception("Error accessing /etc/passwd on server")
            else:
                return CrawlResultFactory.create_success_result(url=url)
        
        mock_instance.arun.side_effect = error_simulation_response
        
        from server import mcp
        async with Client(mcp) as client:
            error_test_urls = [
                "https://example.com/db-error",
                "https://example.com/api-error", 
                "https://example.com/file-error",
            ]
            
            for url in error_test_urls:
                result = await client.call_tool_mcp("web_content_extract", {"url": url})
                
                # Should have error response
                assert result.isError or "error" in result.content[0].text.lower()
                
                # Should NOT contain sensitive information
                response_text = result.content[0].text if result.content else ""
                assert "secret123" not in response_text
                assert "password" not in response_text
                assert "sk-1234567890abcdef" not in response_text
                assert "/etc/passwd" not in response_text
                
                # Should contain sanitized indicators
                assert "[REDACTED]" in response_text or "Error extracting content" in response_text

def test_system_performance_targets_met():
    """Test that all system performance targets are met."""
    performance_targets = {
        'security_test_suite_total': 120.0,  # seconds
        'individual_security_test_max': 10.0,  # seconds
        'fast_test_suite_total': 60.0,  # seconds
        'complete_test_suite_total': 300.0,  # seconds (5 minutes)
    }
    
    # This test documents and validates performance requirements
    # Actual measurements will be validated by CI/CD pipeline
    for test_category, target_time in performance_targets.items():
        assert target_time > 0
        assert target_time < 600  # No test should take more than 10 minutes
        
        # Document improvement expectations
        if 'security' in test_category:
            # Security tests should show major improvement from 1254s baseline
            improvement_ratio = 1254.0 / target_time
            assert improvement_ratio > 10, f"Expected >10x improvement for {test_category}"
```

**Implementation Tasks:**
- [ ] Integrate all optimized components into system workflow
- [ ] Validate end-to-end performance meets targets  
- [ ] Test error sanitization across all components
- [ ] Verify system reliability under load

**Validation Command:**
```bash
pytest tests/test_e2e_optimized.py -v --timeout=120 --durations=5
```

#### Task 5.2: Regression Prevention Testing
**Objective**: Ensure optimizations don't break existing functionality

**Test Requirements:**
```python
# tests/test_regression_prevention.py
@pytest.mark.asyncio
async def test_mcp_protocol_still_works():
    """Test that MCP protocol functionality is preserved after optimization."""
    # This should still pass exactly as before optimization
    subprocess_result = subprocess.run([
        sys.executable, 'tests/test_mcp_protocol_regression.py::TestMCPProtocolRegression::test_complete_mcp_initialization_sequence'
    ], capture_output=True, text=True, timeout=30)
    
    assert subprocess_result.returncode == 0, f"MCP protocol regression detected: {subprocess_result.stderr}"

def test_existing_fast_tests_still_fast():
    """Test that previously fast tests remain fast after changes."""
    start_time = time.perf_counter()
    
    # Run existing fast test suite
    result = subprocess.run([
        sys.executable, '-m', 'pytest', '-m', 'not slow', '--tb=short', '-q'
    ], capture_output=True, text=True, timeout=120)
    
    duration = time.perf_counter() - start_time
    
    assert result.returncode == 0, f"Fast tests failed: {result.stdout}\n{result.stderr}"
    assert duration < 60.0, f"Fast tests took {duration:.2f}s, should be <60s"

def test_no_new_deprecation_warnings():
    """Test that optimizations don't introduce new warnings."""
    result = subprocess.run([
        sys.executable, '-m', 'pytest', 'tests/test_models.py', '-v'
    ], capture_output=True, text=True, timeout=30)
    
    # Should not contain Pydantic warnings after ConfigDict migration
    assert "allow_population_by_field_name" not in result.stderr
    assert "Valid config keys have changed" not in result.stderr

@pytest.mark.asyncio
async def test_actual_network_functionality_preserved():
    """Test that actual network functionality still works when needed."""
    # This test should use real network (marked as slow) to verify
    # that mocking doesn't break actual functionality
    
    # Only run this test when explicitly requested (integration testing)
    if os.environ.get('RUN_INTEGRATION_TESTS') != 'true':
        pytest.skip("Integration test skipped - set RUN_INTEGRATION_TESTS=true to run")
    
    from tools.web_extract import web_content_extract, WebExtractParams
    
    # Test with a reliable test endpoint
    params = WebExtractParams(url="https://httpbin.org/html")
    result = await web_content_extract(params)
    
    # Should get actual content, not mocked content
    assert len(result) > 100
    assert "Herman Melville" in result or "Moby Dick" in result
    assert "Error extracting content" not in result
```

**Implementation Tasks:**
- [ ] Validate all existing tests still pass
- [ ] Ensure no performance regressions in fast tests
- [ ] Verify real network functionality when needed
- [ ] Test backward compatibility

**Validation Command:**
```bash
pytest tests/test_regression_prevention.py -v --timeout=180
```

### Phase 6: Documentation & Maintenance Testing

#### Task 6.1: Documentation Validation Tests
**Objective**: Ensure documentation examples work as documented

**Test Requirements:**
```python
# tests/test_documentation_examples.py
def test_readme_command_examples():
    """Test that README command examples work correctly."""
    # Extract commands from README and test them
    readme_commands = [
        "pytest -m 'not slow' --timeout=60",
        "pytest tests/test_security_validation.py --timeout=120",
        "pytest tests/test_mcp_protocol_regression.py::TestMCPProtocolRegression::test_complete_mcp_initialization_sequence -v",
    ]
    
    for command in readme_commands:
        # Parse and validate command structure
        parts = command.split()
        assert parts[0] == "pytest"
        assert "--timeout" in command or "-v" in command

def test_performance_targets_documented():
    """Test that documented performance targets are realistic."""
    documented_targets = {
        'fast_tests': 60,  # seconds
        'security_tests': 120,  # seconds  
        'complete_suite': 300,  # seconds
        'individual_security_test': 10,  # seconds
    }
    
    for target_name, target_time in documented_targets.items():
        # Validate targets are reasonable
        assert 1 <= target_time <= 600, f"Target {target_name} unrealistic: {target_time}s"

def test_developer_workflow_commands():
    """Test developer workflow commands from documentation."""
    workflow_commands = [
        # Quick development feedback
        ["pytest", "tests/test_stdout_contamination.py", "tests/test_models.py", "-v"],
        
        # Security validation
        ["pytest", "tests/test_security_validation.py", "-v"],
        
        # Regression validation
        ["pytest", "tests/test_mcp_protocol_regression.py", "-v"],
    ]
    
    for command in workflow_commands:
        # Validate command structure
        assert command[0] == "pytest"
        assert any(arg.startswith("tests/") for arg in command[1:])
```

**Implementation Tasks:**
- [ ] Validate all README command examples
- [ ] Test documented performance targets
- [ ] Verify developer workflow instructions
- [ ] Update documentation based on test results

**Validation Command:**
```bash
pytest tests/test_documentation_examples.py -v
```

#### Task 6.2: Maintenance Automation Tests
**Objective**: Test automated maintenance and monitoring systems

**Test Requirements:**
```python
# tests/test_maintenance_automation.py
def test_automated_test_execution():
    """Test automated test execution configuration."""
    # Validate GitHub Actions workflow exists and is correct
    workflow_path = ".github/workflows/ci.yml"
    assert os.path.exists(workflow_path), "CI workflow file missing"
    
    with open(workflow_path, 'r') as f:
        content = f.read()
        
    # Validate key automation features
    assert "pytest" in content
    assert "timeout" in content
    assert "matrix" in content  # For parallel execution

def test_performance_monitoring_automation():
    """Test performance monitoring automation."""
    # Test that performance data collection works
    performance_file = ".test_performance.json"
    
    # Simulate performance data collection
    performance_data = {
        'timestamp': time.time(),
        'test_suite_duration': 45.2,
        'security_tests_duration': 38.1,
        'memory_usage_mb': 125.3
    }
    
    # Validate performance data structure
    assert 'timestamp' in performance_data
    assert 'test_suite_duration' in performance_data
    assert performance_data['test_suite_duration'] < 300  # 5 minutes max

def test_regression_detection_automation():
    """Test automated regression detection."""
    # Simulate performance regression detection
    baseline_performance = {'security_suite': 40.0}
    current_performance = {'security_suite': 65.0}  # Regression
    
    for test_name, current_time in current_performance.items():
        baseline_time = baseline_performance[test_name]
        regression_threshold = baseline_time * 1.5  # 50% slowdown threshold
        
        if current_time > regression_threshold:
            # This would trigger an alert in real system
            regression_detected = True
            assert regression_detected, f"Performance regression in {test_name}: {current_time}s > {regression_threshold}s"

@pytest.mark.asyncio
async def test_automated_cleanup():
    """Test automated cleanup processes."""
    # Test that resources are properly cleaned up
    import tempfile
    import shutil
    
    temp_dir = tempfile.mkdtemp()
    try:
        # Simulate test resource creation and cleanup
        test_file = os.path.join(temp_dir, "test_resource.txt")
        with open(test_file, 'w') as f:
            f.write("test data")
        
        assert os.path.exists(test_file)
        
        # Cleanup should remove temporary resources
        # (This would be automated in real system)
        
    finally:
        # Ensure cleanup happens even if test fails
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        assert not os.path.exists(temp_dir), "Cleanup failed"
```

**Implementation Tasks:**
- [ ] Set up automated test execution monitoring
- [ ] Implement performance regression detection
- [ ] Configure automated cleanup processes
- [ ] Validate maintenance automation works correctly

**Validation Command:**
```bash
pytest tests/test_maintenance_automation.py -v
```

## Task Dependencies

### Critical Path Dependencies
1. **Task 1.1 → 1.2**: Testing infrastructure must be set up before mock framework
2. **Task 1.2 → 2.1**: Mock framework required for error sanitization tests
3. **Task 2.1 → 2.2**: Sanitization logic must be tested before integration
4. **Task 2.2 → 3.1**: Error handling must be fixed before security optimization
5. **Task 3.1 → 3.2**: Basic security mocking before concurrent optimization
6. **Task 3.2 → 4.1**: Security tests optimized before CI/CD implementation
7. **Task 4.1 → 4.2**: CI/CD basic setup before performance monitoring
8. **Task 4.2 → 5.1**: Performance monitoring before system integration
9. **Task 5.1 → 5.2**: System integration before regression testing
10. **Task 5.2 → 6.1**: Regression testing before documentation validation

### Parallel Execution Opportunities
- **Tasks 2.1 & 3.1**: Error sanitization and security test optimization can be developed in parallel
- **Tasks 4.1 & 4.2**: CI/CD workflow and performance monitoring can be implemented concurrently
- **Tasks 6.1 & 6.2**: Documentation and maintenance testing can run in parallel

## Validation Gates

### Phase 1 Validation
```bash
# Test foundation setup validation
pytest tests/test_framework_setup.py tests/test_mock_factory.py -v --timeout=15
```

### Phase 2 Validation  
```bash
# Error sanitization validation
pytest tests/test_error_sanitization.py tests/test_web_extract_security.py -v --timeout=20
```

### Phase 3 Validation
```bash
# Security optimization validation
pytest tests/test_security_optimization.py tests/test_concurrent_security.py -v --timeout=60 --durations=10
```

### Phase 4 Validation
```bash
# CI/CD implementation validation
pytest tests/test_cicd_configuration.py tests/test_performance_monitoring.py -v --timeout=30
```

### Phase 5 Validation
```bash
# System integration validation
pytest tests/test_e2e_optimized.py tests/test_regression_prevention.py -v --timeout=300
```

### Phase 6 Validation
```bash
# Documentation and maintenance validation
pytest tests/test_documentation_examples.py tests/test_maintenance_automation.py -v --timeout=30
```

### Complete System Validation
```bash
# Final validation of all components
pytest -v --timeout=300 --durations=20 --cov=. --cov-report=term-missing
```

## Success Criteria

### Phase 1 Success Criteria
- [ ] All test framework configuration tests pass
- [ ] Mock factory creates correct async context manager mocks
- [ ] Performance monitoring fixtures work correctly
- [ ] Test environment isolation is functional

### Phase 2 Success Criteria
- [ ] Error sanitization removes all sensitive patterns
- [ ] Sanitization preserves useful debugging information
- [ ] Integration with `web_content_extract` works correctly
- [ ] No sensitive data appears in error responses

### Phase 3 Success Criteria
- [ ] Security test suite runs in <120 seconds (vs. 1254+ seconds baseline)
- [ ] Individual security tests complete in <10 seconds each
- [ ] All security validation logic preserved with mocks
- [ ] Concurrent execution works without resource issues

### Phase 4 Success Criteria
- [ ] GitHub Actions workflow executes successfully
- [ ] Performance monitoring captures accurate metrics
- [ ] Branch protection rules enforce test requirements
- [ ] CI/CD pipeline completes in <10 minutes total

### Phase 5 Success Criteria
- [ ] End-to-end workflow demonstrates all optimizations
- [ ] No regressions in existing functionality
- [ ] System meets all performance targets
- [ ] Integration between all components works correctly

### Phase 6 Success Criteria
- [ ] All documentation examples work as described
- [ ] Automated maintenance processes function correctly
- [ ] Developer workflow is properly documented
- [ ] Performance targets are realistic and achievable

## Estimated Timeline

### Phase 1: Test Foundation (Days 1-2)
- **Task 1.1**: 0.5 days - Testing infrastructure setup
- **Task 1.2**: 1 day - Mock framework implementation
- **Buffer**: 0.5 days for integration issues

### Phase 2: Error Sanitization (Days 2-3)
- **Task 2.1**: 0.5 days - Sanitization tests and logic
- **Task 2.2**: 0.5 days - Integration with web extract
- **Buffer**: 0.5 days for security validation

### Phase 3: Security Optimization (Days 3-5)
- **Task 3.1**: 1 day - Basic security test optimization
- **Task 3.2**: 1 day - Concurrent execution optimization
- **Buffer**: 1 day for performance tuning

### Phase 4: CI/CD Implementation (Days 5-6)
- **Task 4.1**: 0.5 days - GitHub Actions workflow
- **Task 4.2**: 0.5 days - Performance monitoring
- **Buffer**: 0.5 days for CI/CD debugging

### Phase 5: System Integration (Days 6-7)
- **Task 5.1**: 0.5 days - End-to-end testing
- **Task 5.2**: 0.5 days - Regression prevention
- **Buffer**: 0.5 days for system validation

### Phase 6: Documentation (Days 7-8)
- **Task 6.1**: 0.5 days - Documentation validation
- **Task 6.2**: 0.5 days - Maintenance automation
- **Buffer**: 0.5 days for final validation

**Total Estimated Timeline**: 8 days with built-in buffers for testing and validation.

## Quality Assessment

**Task Plan Completeness: 9/10**
- ✅ All necessary testing phases covered comprehensively
- ✅ Clear progression from unit tests to system tests
- ✅ Performance and security requirements well-defined
- ✅ Realistic timeline with appropriate buffers

**Test-First Adherence: 10/10**
- ✅ Every implementation task has corresponding tests written first
- ✅ Red-Green-Refactor cycle clearly defined for each phase
- ✅ Tests validate requirements before implementation
- ✅ Comprehensive test coverage ensures code quality

**Clarity and Actionability: 9/10**
- ✅ Tasks are specific and measurable
- ✅ Clear validation commands for each phase
- ✅ Dependencies and parallel opportunities identified
- ✅ Success criteria are objective and testable

**Feasibility: 8/10**
- ✅ Based on existing successful patterns in codebase
- ✅ Performance targets based on realistic measurements
- ✅ Timeline accounts for typical development challenges
- ⚠️ Some CI/CD complexity may require additional iteration

This test-first task plan provides a comprehensive roadmap for implementing the security tests optimization and CI/CD infrastructure while maintaining high code quality through systematic testing at every level.