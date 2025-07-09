# Feature Exploration: Crawl4AI MCP Server MVP

## Source Information
- **Input**: .planning/INITIAL_MVP.md
- **Branch**: feature/MVP
- **Generated**: 2025-07-09T14:37:00Z

## Feature Overview
A minimal MCP (Model Context Protocol) server providing web content extraction capabilities using the crawl4ai library. The server implements a single tool `web_content_extract` that accepts URLs and returns clean, structured text content suitable for AI/LLM processing. This MVP serves as a foundation for future extensions including screenshot functionality, structured data extraction, and batch processing.

## Technical Requirements

### Core Dependencies
- **FastMCP 2.0**: Modern Python framework for MCP server development
- **crawl4ai**: AI-optimized web crawling and content extraction library
- **uv**: Fast Python package and project manager for dependency management
- **python-dotenv**: Environment variable management
- **pydantic**: Data validation and settings management
- **asyncio**: Asynchronous programming support

### Python Version
- Python 3.8+ (based on crawl4ai requirements)

### Optional Dependencies
- **pytest**: Testing framework
- **pytest-asyncio**: Async testing support
- **httpx**: HTTP client for advanced requests

## Architecture Context

### MCP Protocol Integration
The server follows the Model Context Protocol specification:
- **Client-Server Model**: Applications (hosts) connect to MCP servers via clients
- **Tool-Based Architecture**: Servers expose tools that LLMs can execute
- **Standardized Communication**: Uses JSON-RPC over stdio/HTTP/SSE transport

### Project Structure
```
crawl4ai-mcp-server/
├── server.py              # Main MCP server with FastMCP
├── tools/                 # Tool implementations
│   └── web_extract.py     # crawl4ai integration
├── tests/                 # Unit tests
│   ├── test_server.py     # Server tests
│   └── test_web_extract.py# Tool tests
├── examples/              # Usage examples
│   └── basic_usage.py     # Basic server usage
├── pyproject.toml         # uv-compatible dependencies
├── .env.example           # Configuration template
├── README.md              # Setup and usage docs
└── .planning/             # Planning documents
```

## Implementation Knowledge Base

### FastMCP 2.0 Framework
- **Installation**: `uv add fastmcp`
- **Basic Server Pattern**:
```python
from fastmcp import FastMCP

mcp = FastMCP("Crawl4AI-MCP-Server")

@mcp.tool
def web_content_extract(url: str) -> str:
    """Extract clean text content from a web page"""
    # Implementation here
    return extracted_content

if __name__ == "__main__":
    mcp.run()
```

### Crawl4AI Integration
- **Installation**: `uv add "crawl4ai[all]"`
- **Model Download**: `crawl4ai-download-models`
- **Playwright Setup**: `playwright install`
- **Basic Usage Pattern**:
```python
import asyncio
from crawl4ai import AsyncWebCrawler

async def extract_content(url: str) -> str:
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        return result.markdown
```

### uv Project Management
- **Project Initialization**: `uv init`
- **Dependency Management**: `uv add <package>`
- **Virtual Environment**: Automatically managed in .venv/
- **Lock File**: uv.lock ensures reproducible builds
- **pyproject.toml Configuration**:
```toml
[project]
name = "crawl4ai-mcp-server"
version = "0.1.0"
description = "MCP server with crawl4ai integration"
dependencies = [
    "fastmcp>=2.0.0",
    "crawl4ai[all]",
    "python-dotenv",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
test = [
    "pytest",
    "pytest-asyncio",
    "httpx",
]
```

## Code Patterns & Examples

### Tool Implementation Pattern
```python
from fastmcp import FastMCP
from pydantic import BaseModel, Field
from crawl4ai import AsyncWebCrawler
import asyncio

class WebExtractParams(BaseModel):
    url: str = Field(..., description="URL of the webpage to crawl")

mcp = FastMCP("Crawl4AI-MCP-Server")

@mcp.tool
async def web_content_extract(params: WebExtractParams) -> str:
    """Extract clean text content from a webpage"""
    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=params.url)
            return result.markdown
    except Exception as e:
        return f"Error extracting content: {str(e)}"
```

### Error Handling Pattern
```python
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

async def safe_extract(url: str) -> Dict[str, Any]:
    """Safely extract content with comprehensive error handling"""
    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url)
            return {
                "success": True,
                "content": result.markdown,
                "url": url,
                "title": result.title or "No title"
            }
    except Exception as e:
        logger.error(f"Content extraction failed for {url}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "url": url,
            "content": None
        }
```

### Testing Pattern
```python
import pytest
from fastmcp import Client
from server import mcp

@pytest.mark.asyncio
async def test_web_content_extract():
    async with Client(mcp) as client:
        tools = await client.list_tools()
        assert "web_content_extract" in [tool.name for tool in tools]
        
        result = await client.call_tool("web_content_extract", {
            "url": "https://example.com"
        })
        assert result.success
        assert "content" in result.data
```

## Configuration Requirements

### Environment Variables
```bash
# .env.example
# Optional: LLM provider configuration for advanced features
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional: Proxy configuration
HTTP_PROXY=http://proxy.example.com:8080
HTTPS_PROXY=https://proxy.example.com:8080

# Optional: Crawl4AI configuration
CRAWL4AI_USER_AGENT=crawl4ai-mcp-server/1.0
CRAWL4AI_MAX_RETRIES=3
CRAWL4AI_TIMEOUT=30
```

### MCP Client Configuration
```json
{
  "mcpServers": {
    "crawl4ai": {
      "command": "uv",
      "args": ["run", "python", "server.py"],
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

## Testing Considerations

### Test Categories
1. **Unit Tests**: Individual tool functionality
2. **Integration Tests**: MCP server protocol compliance
3. **End-to-End Tests**: Full crawling workflow
4. **Performance Tests**: Response time and resource usage

### Testing Framework Setup
```python
# pytest configuration in pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

### Mock Patterns for Testing
```python
from unittest.mock import AsyncMock, patch
import pytest

@pytest.mark.asyncio
async def test_web_extract_with_mock():
    with patch('crawl4ai.AsyncWebCrawler') as mock_crawler:
        mock_instance = AsyncMock()
        mock_crawler.return_value.__aenter__.return_value = mock_instance
        mock_instance.arun.return_value.markdown = "Test content"
        
        result = await web_content_extract("https://example.com")
        assert result == "Test content"
```

## Integration Points

### MCP Protocol Integration
- **Transport Layer**: stdio (default), HTTP, or SSE
- **Message Format**: JSON-RPC 2.0
- **Tool Registration**: Automatic via FastMCP decorators
- **Error Handling**: Standardized MCP error responses

### Crawl4AI Integration
- **Async Context Management**: Proper crawler lifecycle
- **Content Processing**: Markdown output for AI consumption
- **Error Propagation**: Crawl4AI exceptions to MCP errors
- **Configuration**: Environment-based crawler settings

### Client Integration
- **VS Code**: Via MCP configuration
- **Cursor**: Built-in MCP support
- **Claude Desktop**: Direct MCP server connection
- **Custom Clients**: FastMCP Client library

## Technical Constraints

### Performance Considerations
- **Async Operations**: All I/O operations must be async
- **Resource Management**: Proper crawler cleanup
- **Timeout Handling**: Configurable request timeouts
- **Memory Usage**: Efficient content processing

### Security Considerations
- **URL Validation**: Input sanitization for URLs
- **Content Filtering**: Safe content extraction
- **Rate Limiting**: Prevent abuse of crawling
- **Environment Isolation**: Secure credential management

### Compatibility Requirements
- **Python Version**: 3.8+ minimum
- **Platform Support**: Cross-platform (Windows, macOS, Linux)
- **Browser Dependencies**: Playwright browser installation
- **Network Requirements**: Internet access for crawling

## Success Criteria

### Functional Requirements
- [ ] MCP server starts successfully
- [ ] Tool registration works correctly
- [ ] URL crawling extracts clean content
- [ ] Error handling provides meaningful messages
- [ ] Client integration works seamlessly

### Quality Requirements
- [ ] Response time < 30 seconds for typical pages
- [ ] Memory usage < 500MB during operation
- [ ] 95% success rate for valid URLs
- [ ] Proper error handling for invalid URLs
- [ ] Clean shutdown without resource leaks

### Testing Requirements
- [ ] Unit test coverage > 80%
- [ ] Integration tests pass
- [ ] End-to-end workflow tested
- [ ] Performance benchmarks established
- [ ] Security vulnerability scan clean

## High-Level Approach

### Phase 1: Core Implementation
1. Set up project structure with uv
2. Implement basic FastMCP server
3. Create web_content_extract tool
4. Add crawl4ai integration
5. Implement error handling

### Phase 2: Quality Assurance
1. Add comprehensive testing
2. Implement logging and monitoring
3. Add configuration management
4. Create usage examples
5. Write documentation

### Phase 3: Production Readiness
1. Performance optimization
2. Security hardening
3. Deployment configuration
4. Client integration testing
5. Final documentation

## Validation Gates

### Development Validation
```bash
# Install dependencies
uv sync

# Run tests
uv run pytest tests/

# Type checking
uv run mypy server.py tools/

# Linting
uv run ruff check .

# Security scan
uv run bandit -r .
```

### Integration Validation
```bash
# Start server
uv run python server.py

# Test with MCP client
uv run python examples/basic_usage.py

# Performance test
uv run python tests/performance_test.py
```

### Deployment Validation
```bash
# Build package
uv build

# Test installation
uv pip install dist/crawl4ai_mcp_server-*.whl

# Integration test
python -m crawl4ai_mcp_server.tests.integration
```

## Confidence Assessment

**Rating: 9/10**

This exploration provides comprehensive coverage of:
- ✅ Technical requirements and dependencies
- ✅ Implementation patterns and examples
- ✅ Testing strategies and frameworks
- ✅ Integration points and constraints
- ✅ Project structure and organization
- ✅ Security and performance considerations
- ✅ Validation approaches and success criteria

The knowledge base enables flexible implementation approaches while maintaining focus on the core MVP objectives. The research covers both current best practices and production-ready patterns suitable for future extensions.