# MCP Inspector Setup Guide

This guide explains how to test and debug the Crawl4AI MCP Server using the MCP Inspector tool.

## Prerequisites

- Node.js and npm installed
- Crawl4AI MCP Server running
- Python environment with required dependencies

## Install MCP Inspector

```bash
npm install -g @modelcontextprotocol/inspector
```

## Start MCP Inspector

Use the provided configuration file to connect to the Crawl4AI MCP Server:

```bash
mcp-inspector mcp-inspector-config.json
```

The inspector will start and connect to the server via the `start_server.sh` script.

## MCP Inspector Configuration

The `mcp-inspector-config.json` file contains:

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

## Client Configuration Examples

### Claude Desktop Integration

Add to your Claude Desktop configuration file:

**Location**: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)

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

### Alternative: Direct Python Execution

If you prefer running the server directly with Python:

```json
{
  "mcpServers": {
    "crawl4ai": {
      "command": "python",
      "args": ["/absolute/path/to/crawl4ai-mcp-server/server.py"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/crawl4ai-mcp-server"
      }
    }
  }
}
```

## Testing with MCP Inspector

1. **Start the Inspector**:
   ```bash
   mcp-inspector mcp-inspector-config.json
   ```

2. **Verify Connection**:
   - Inspector should show "Connected" status
   - No error messages in the console
   - Tool `web_content_extract` should be listed

3. **Test Tool Execution**:
   - Use the inspector's tool testing interface
   - Try extracting content from a test URL
   - Verify clean JSON responses without stdout contamination

## Expected Output

### Successful Connection
```
MCP Inspector started on http://localhost:3000
Connected to crawl4ai server
Available tools: web_content_extract
```

### Successful Tool Call
```json
{
  "content": [
    {
      "type": "text",
      "text": "# Extracted Content\n\nPage content here..."
    }
  ],
  "isError": false
}
```

## Troubleshooting

### Common Issues

1. **"Command not found" error**:
   - Ensure `start_server.sh` has execute permissions: `chmod +x start_server.sh`
   - Use absolute paths in configuration

2. **"Module not found" error**:
   - Verify Python environment is activated
   - Check all dependencies are installed: `pip install -r requirements.txt`

3. **Stdout contamination warnings**:
   - This should be fixed with the current implementation
   - If you see warnings, check Crawl4AI verbosity settings

4. **Connection timeout**:
   - Verify server starts successfully: `./start_server.sh`
   - Check for any Python import errors

### Debug Mode

For detailed debugging information, run the server directly:

```bash
./start_server.sh
```

This will show all log output and help identify any startup issues.

## Alternative Testing

You can also test the server using the provided test utility:

```bash
python test_mcp_tool_call.py
```

This script demonstrates proper MCP protocol usage and validates the server responses.

## Notes

- Always use absolute paths in client configurations
- The `start_server.sh` script sets up the proper Python environment
- MCP Inspector is excellent for debugging JSON-RPC communication
- For production use, consider using process managers like systemd or supervisord