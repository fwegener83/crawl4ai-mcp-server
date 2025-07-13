# Crawl4AI MCP Server

A Model Context Protocol (MCP) server that provides web content extraction capabilities using [Crawl4AI](https://github.com/unclecode/crawl4ai).

## Features

- **Web Content Extraction**: Extract and process web page content using Crawl4AI
- **MCP Protocol Compliance**: Full compatibility with MCP clients like Claude Desktop
- **Clean Output**: Stdout contamination prevention for proper JSON-RPC communication
- **Async/Await Support**: High-performance async implementation with proper event loop handling

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js (for MCP Inspector testing)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/fwegener83/crawl4ai-mcp-server.git
   cd crawl4ai-mcp-server
   ```

2. **Set up Python environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Make start script executable**:
   ```bash
   chmod +x start_server.sh
   ```

### Usage

#### Standalone Server
```bash
./start_server.sh
```

#### With Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "crawl4ai": {
      "command": "/absolute/path/to/crawl4ai-mcp-server/start_server.sh",
      "args": []
    }
  }
}
```

**Important**: Use absolute paths in the configuration.

## Testing Strategy & Development

### Test Architecture Overview

This project uses a comprehensive testing strategy designed for reliability, speed, and thorough validation. Our test suite is organized into categories that balance development velocity with production confidence.

#### Test Categories & Performance Targets

- **Fast Tests** (`pytest -m "not slow"`): <1 minute total
  - Unit tests with mocked dependencies
  - Integration tests using FastMCP Client (no subprocess)
  - Mocked security validation tests
  - Target: <1 second per test, immediate feedback for development

- **Slow Tests** (`pytest -m "slow"`): <5 minutes total (optimization target)
  - Real network operations for security validation
  - Subprocess-based MCP protocol testing
  - Performance and load testing scenarios
  - Target: <30 seconds per test, thorough validation

- **Regression Tests**: <30 seconds total
  - Critical MCP protocol sequence validation
  - Core functionality that must never break
  - Component integration preventing regressions
  - Target: <10 seconds per test, CI/CD gate

### Development Workflows

#### Quick Development Feedback (<1 minute)
For immediate feedback during active development:
```bash
# Core functionality only - fastest feedback loop
pytest tests/test_stdout_contamination.py tests/test_models.py tests/test_server.py::TestFastMCPServerIntegration -v

# Alternative: exclude all slow tests
pytest -m "not slow" --tb=short
```

#### Critical Regression Validation (<30 seconds)
Before commits, ensure core functionality works:
```bash
# Critical MCP protocol and component regression
pytest tests/test_mcp_protocol_regression.py tests/test_server.py::TestComponentRegression -v

# Verify no protocol violations that would break Claude Desktop
pytest tests/test_mcp_protocol_regression.py::TestMCPProtocolRegression::test_complete_mcp_initialization_sequence -v
```

#### Pre-Commit Validation (<2 minutes)
Before push, run comprehensive validation excluding heavy operations:
```bash
# All tests except marked slow ones
pytest -m "not slow" --timeout=120

# Verify security without performance overhead
pytest tests/test_security_validation.py::TestURLSecurityValidation::test_malicious_url_blocking -v
```

#### Security Validation (<5 minutes target)
Full security test suite (currently being optimized):
```bash
# Current security tests (some may be slow)
pytest tests/test_security_validation.py -v

# Fast security tests only (recommended during optimization)
pytest tests/test_security_validation.py::TestURLSecurityValidation::test_malicious_url_blocking -v
```

#### Complete Test Suite (<10 minutes target)
Full validation including all test categories:
```bash
# Everything - use for final validation
pytest

# With coverage reporting
pytest --cov=. --cov-report=html
```

### Performance Monitoring & Optimization

#### Expected Execution Times
- **Individual fast tests**: <1 second each
- **Individual slow tests**: <30 seconds each (optimization target)
- **MCP protocol regression**: <10 seconds total
- **Security test suite**: <5 minutes total (optimization in progress)
- **Complete test suite**: <10 minutes total

#### Performance Optimization Guidelines

1. **Mock External Dependencies**: All network operations should be mocked in fast tests
2. **Use @pytest.mark.slow**: Mark any test that takes >5 seconds or uses real networks
3. **Implement Timeouts**: No test should run indefinitely
4. **Monitor Test Performance**: Track execution times in CI/CD

#### Identifying Slow Tests
```bash
# Find tests taking longer than expected
pytest --durations=10

# Run only fast tests to identify slow unmarked tests
pytest -m "not slow" --tb=short
```

### Writing Tests

#### Test Classification Guidelines

**Mark as Fast (default)**:
- Unit tests with mocked dependencies
- Integration tests using FastMCP Client
- Validation logic tests
- Error handling with mock exceptions

**Mark as Slow (`@pytest.mark.slow`)**:
- Real network operations
- Subprocess communication tests
- Performance testing with concurrency
- Security tests requiring actual connections

#### Security Test Best Practices

1. **Mock by Default**: Use mocked AsyncWebCrawler for security validation
2. **Test Logic, Not Network**: Focus on validation logic rather than network behavior
3. **Error Message Sanitization**: Ensure no sensitive data leaks in error responses
4. **Timeout Implementation**: All security tests must have reasonable timeouts

Example secure test pattern:
```python
@pytest.mark.asyncio
async def test_malicious_url_blocking(self):
    """Test URL blocking logic without real network operations."""
    # Mock the crawler to avoid network calls
    mock_result = MagicMock()
    mock_result.markdown = "Blocked content"
    
    with patch('tools.web_extract.AsyncWebCrawler') as mock_crawler:
        mock_instance = AsyncMock()
        mock_crawler.return_value.__aenter__.return_value = mock_instance
        mock_instance.arun.return_value = mock_result
        
        # Test validation logic
        async with Client(mcp) as client:
            result = await client.call_tool_mcp("web_content_extract", {
                "url": "javascript:alert('xss')"
            })
            assert result.isError
```

#### Error Message Security

All error messages must be sanitized to prevent sensitive information leakage:
- Filter out passwords from connection strings
- Remove system paths from error messages  
- Sanitize API keys and tokens
- Validate error message content in tests

### CI/CD Integration Strategy

#### GitHub Actions Workflow (Planned)
```yaml
# Fast feedback for all PRs
fast-tests:
  - pytest -m "not slow" --timeout=120
  
# Comprehensive validation for main branch  
comprehensive-tests:
  - pytest --timeout=600
  
# Security validation with performance monitoring
security-tests:
  - pytest tests/test_security_validation.py --timeout=300
```

#### Branch Protection Strategy
- **Required**: Fast tests must pass for all PRs
- **Required**: Regression tests must pass for main branch
- **Optional**: Slow tests for comprehensive validation
- **Monitoring**: Track test performance over time

### MCP Inspector Setup

The MCP Inspector is excellent for testing and debugging MCP server implementations.

#### Install MCP Inspector
```bash
npm install -g @modelcontextprotocol/inspector
```

#### Start MCP Inspector
```bash
mcp-inspector mcp-inspector-config.json
```

#### Inspector Configuration
The included `mcp-inspector-config.json` contains:
```json
{
  "mcpServers": {
    "crawl4ai": {
      "command": "./start_server.sh",
      "args": []
    }
  }
}
```

#### Testing with Inspector
1. Start the inspector (opens browser at http://localhost:3000)
2. Verify connection to the Crawl4AI server
3. Test the `web_content_extract` tool with sample URLs
4. Check for clean JSON responses without stdout contamination

### Manual Testing

Test the server directly:
```bash
python test_mcp_tool_call.py
```

### Test Performance Troubleshooting

#### Common Issues & Solutions

1. **Tests Running Too Slow**:
   ```bash
   # Identify slow tests
   pytest --durations=10
   
   # Run only fast tests
   pytest -m "not slow"
   ```

2. **Security Tests Hanging**:
   - Ensure proper mocking of AsyncWebCrawler
   - Add timeouts to async operations
   - Check for real network operations in test code

3. **MCP Protocol Failures**:
   ```bash
   # Test complete protocol sequence
   pytest tests/test_mcp_protocol_regression.py::TestMCPProtocolRegression::test_complete_mcp_initialization_sequence -v
   ```

4. **Memory/Resource Issues**:
   - Monitor test resource usage
   - Use proper async context management
   - Clean up subprocess tests properly

#### Performance Monitoring Commands
```bash
# Monitor test performance over time
pytest --durations=0 > test_performance.log

# Check for memory leaks in long-running tests  
pytest tests/test_security_validation.py -v --tb=short

# Validate timeout implementation
timeout 300 pytest tests/test_security_validation.py
```

## Available Tools

### `web_content_extract`

Extracts content from web pages using Crawl4AI.

**Parameters**:
- `url` (string, required): The URL to extract content from

**Returns**:
- Extracted markdown content from the web page

**Example**:
```json
{
  "name": "web_content_extract",
  "arguments": {
    "url": "https://example.com"
  }
}
```

## Troubleshooting

### Common Issues

1. **"Command not found" error**:
   - Ensure `start_server.sh` has execute permissions: `chmod +x start_server.sh`
   - Use absolute paths in client configurations

2. **"Module not found" error**:
   - Verify Python environment is activated
   - Install dependencies: `pip install -r requirements.txt`

3. **Stdout contamination warnings**:
   - This issue has been resolved in current implementation
   - If you see warnings, check Crawl4AI verbosity settings

4. **Connection timeout**:
   - Verify server starts successfully: `./start_server.sh`
   - Check for Python import errors in the logs

### Debug Mode

For detailed debugging, run the server directly:
```bash
python server.py
```

## Architecture

- **Server**: FastMCP-based server with async/await support
- **Tools**: Web content extraction using Crawl4AI
- **Protocol**: JSON-RPC over stdio (MCP standard)
- **Output**: Clean stdout without contamination for proper MCP communication

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

[Add your license information here]

## Links

- [Crawl4AI Documentation](https://github.com/unclecode/crawl4ai)
- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
- [Claude Desktop Integration](https://docs.anthropic.com/en/docs/build-with-claude/mcp)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)