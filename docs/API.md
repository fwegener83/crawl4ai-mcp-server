# API Documentation

## Overview

The Crawl4AI MCP Server provides a single MCP tool for web content extraction. This document provides detailed API reference and usage examples.

## MCP Protocol

The server implements the Model Context Protocol (MCP) specification, providing tools that can be called by MCP-compatible clients.

### Server Information

- **Name**: `Crawl4AI-MCP-Server`
- **Version**: `1.0.0`
- **Protocol**: MCP v1.0
- **Transport**: JSON-RPC over stdio/HTTP

### Tool Registration

The server registers one tool with the MCP protocol:

```json
{
  "tools": [
    {
      "name": "web_content_extract",
      "description": "Extract clean text content from a webpage.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "url": {
            "type": "string",
            "description": "URL of the webpage to crawl"
          }
        },
        "required": ["url"]
      }
    }
  ]
}
```

## Tool Reference

### web_content_extract

Extracts clean text content from a webpage and returns it in markdown format.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Yes | The URL of the webpage to extract content from |

#### URL Validation

The URL parameter must satisfy the following criteria:

- **Protocol**: Must use `http://` or `https://`
- **Format**: Must be a valid URL with scheme and netloc
- **Content**: Cannot be empty or whitespace-only
- **Length**: Reasonable length limits apply

**Valid URLs:**
```
https://example.com
https://example.com/article
https://subdomain.example.com/path/to/page
https://example.com/page?param=value
https://example.com/page#section
```

**Invalid URLs:**
```
not-a-url
ftp://example.com
javascript:alert('xss')
file:///etc/passwd
mailto:user@example.com
""
"   "
```

#### Response Format

The tool returns a string containing the extracted content in markdown format.

**Success Response:**
```
# Article Title

This is the main content of the webpage, extracted and formatted as markdown.

## Section Header

- List item 1
- List item 2

**Bold text** and *italic text* are preserved.

> Blockquotes are maintained

Links are preserved: [Example](https://example.com)
```

**Error Response:**
```
Error extracting content: <error description>
```

#### Error Types

1. **Validation Errors**
   - `Invalid URL format`
   - `URL must use HTTP or HTTPS protocol`
   - `URL cannot be empty`

2. **Network Errors**
   - `Connection timeout`
   - `DNS resolution failed`
   - `HTTP error: 404 Not Found`
   - `Connection refused`

3. **Content Errors**
   - `Empty content returned`
   - `Unsupported content type`
   - `Content parsing failed`

4. **Server Errors**
   - `Internal server error`
   - `Service unavailable`
   - `Rate limit exceeded`

## Usage Examples

### Python Client

```python
import asyncio
from fastmcp import Client
from server import mcp

async def extract_webpage():
    async with Client(mcp) as client:
        # Extract content from a webpage
        result = await client.call_tool_mcp("web_content_extract", {
            "url": "https://example.com/article"
        })
        
        if not result.isError:
            content = result.content[0].text
            print("Extracted content:")
            print(content)
        else:
            print(f"Error: {result.content[0].text}")

# Run the example
asyncio.run(extract_webpage())
```

### JSON-RPC Request

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "web_content_extract",
    "arguments": {
      "url": "https://example.com/article"
    }
  }
}
```

### JSON-RPC Response

**Success:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "# Article Title\n\nThis is the extracted content..."
      }
    ],
    "isError": false
  }
}
```

**Error:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Error extracting content: Invalid URL format"
      }
    ],
    "isError": false
  }
}
```

### Batch Processing

```python
async def batch_extract():
    urls = [
        "https://example.com/page1",
        "https://example.com/page2",
        "https://example.com/page3"
    ]
    
    async with Client(mcp) as client:
        tasks = []
        for url in urls:
            task = asyncio.create_task(
                client.call_tool_mcp("web_content_extract", {"url": url})
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        for i, result in enumerate(results):
            if not result.isError:
                print(f"Content from {urls[i]}:")
                print(result.content[0].text[:100] + "...")
            else:
                print(f"Error for {urls[i]}: {result.content[0].text}")
```

## Performance Considerations

### Throughput

- **Maximum RPS**: 50+ requests per second under normal conditions
- **Concurrent Requests**: Handles 50+ concurrent requests efficiently
- **Response Time**: <100ms for typical requests

### Rate Limiting

The server implements intelligent rate limiting:

- **Burst Handling**: Allows temporary spikes in request volume
- **Gradual Degradation**: Performance degrades gracefully under load
- **Resource Protection**: Prevents resource exhaustion

### Optimization Tips

1. **Batch Requests**: Use concurrent requests for multiple URLs
2. **Connection Reuse**: Maintain client connections when possible
3. **Error Handling**: Implement exponential backoff for failed requests
4. **Caching**: Cache results for frequently accessed URLs

## Security Considerations

### Input Validation

All inputs are validated at multiple levels:

1. **Protocol Level**: JSON-RPC parameter validation
2. **Application Level**: URL format and content validation
3. **Library Level**: Crawl4AI internal validation

### Security Features

- **URL Sanitization**: Prevents malicious URL injection
- **Protocol Restriction**: Only HTTP/HTTPS allowed
- **Error Sanitization**: No sensitive information in error messages
- **Resource Limits**: Prevents resource exhaustion attacks

### Blocked Content

The following types of URLs are blocked or restricted:

- **JavaScript URLs**: `javascript:alert('xss')`
- **Data URLs**: `data:text/html,<script>...`
- **File URLs**: `file:///etc/passwd`
- **Local URLs**: `http://localhost:8080`
- **Private IPs**: `http://192.168.1.1`

## Error Handling

### Error Response Format

All errors are returned as successful MCP responses with error information in the content:

```json
{
  "content": [
    {
      "type": "text",
      "text": "Error extracting content: <description>"
    }
  ],
  "isError": false
}
```

### Error Recovery

Implement robust error handling in your client:

```python
async def robust_extract(url: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            async with Client(mcp) as client:
                result = await client.call_tool_mcp("web_content_extract", {
                    "url": url
                })
                
                if not result.isError:
                    return result.content[0].text
                else:
                    error_msg = result.content[0].text
                    if "validation error" in error_msg.lower():
                        # Don't retry validation errors
                        raise ValueError(error_msg)
                    elif attempt < max_retries - 1:
                        # Retry network errors
                        await asyncio.sleep(2 ** attempt)
                    else:
                        raise RuntimeError(error_msg)
                        
        except Exception as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
            else:
                raise
```

## Testing

### Unit Tests

Test individual URL validation and extraction:

```python
import pytest
from tools.web_extract import WebExtractParams, web_content_extract

@pytest.mark.asyncio
async def test_url_validation():
    # Valid URL
    params = WebExtractParams(url="https://example.com")
    assert params.url == "https://example.com"
    
    # Invalid URL
    with pytest.raises(ValueError):
        WebExtractParams(url="not-a-url")
```

### Integration Tests

Test complete MCP workflow:

```python
import pytest
from fastmcp import Client
from server import mcp

@pytest.mark.asyncio
async def test_mcp_integration():
    async with Client(mcp) as client:
        result = await client.call_tool_mcp("web_content_extract", {
            "url": "https://httpbin.org/html"
        })
        
        assert not result.isError
        assert len(result.content) == 1
        assert result.content[0].type == "text"
        assert len(result.content[0].text) > 0
```

## Monitoring and Observability

### Logging

The server provides structured logging:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Log levels used:
# INFO: Normal operations, successful extractions
# WARNING: Validation errors, rate limiting
# ERROR: Network failures, server errors
# DEBUG: Detailed debugging information
```

### Metrics

Key metrics to monitor:

- **Request Rate**: Requests per second
- **Response Time**: Average and percentile latencies
- **Error Rate**: Percentage of failed requests
- **Success Rate**: Percentage of successful extractions
- **Memory Usage**: Server memory consumption
- **Active Connections**: Number of concurrent connections

### Health Checks

Implement health checks for monitoring:

```python
async def health_check():
    try:
        async with Client(mcp) as client:
            result = await client.call_tool_mcp("web_content_extract", {
                "url": "https://httpbin.org/html"
            })
            
            if not result.isError:
                return {"status": "healthy", "timestamp": time.time()}
            else:
                return {"status": "unhealthy", "error": result.content[0].text}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

## Troubleshooting

### Common Issues

1. **Tool Not Found**
   - Ensure server is running
   - Check tool registration
   - Verify client connection

2. **Validation Errors**
   - Check URL format
   - Ensure proper protocol (http/https)
   - Verify URL is not empty

3. **Network Errors**
   - Check internet connectivity
   - Verify DNS resolution
   - Check for proxy settings

4. **Performance Issues**
   - Monitor concurrent requests
   - Check memory usage
   - Verify resource limits

### Debug Mode

Enable debug logging for troubleshooting:

```python
import logging

# Enable debug logging
logging.getLogger('server').setLevel(logging.DEBUG)
logging.getLogger('tools.web_extract').setLevel(logging.DEBUG)
```

### Support

For additional support:

1. Check the [README](../README.md) for setup instructions
2. Review the [test suite](../tests/) for usage examples
3. Submit issues with detailed error messages and reproduction steps