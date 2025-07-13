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

## Testing and Development

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

### Running Tests

```bash
# Quick core functionality tests (~15 seconds)  
pytest tests/test_stdout_contamination.py tests/test_models.py tests/test_server.py::TestFastMCPServerIntegration tests/test_server.py::TestComponentRegression -v

# Critical regression tests (~10 seconds)
pytest tests/test_mcp_protocol_regression.py tests/test_server.py::TestComponentRegression -v

# Full test suite (excluding slow security tests)
pytest -m "not slow"

# Full test suite including slow tests (can take 5+ minutes)
pytest
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