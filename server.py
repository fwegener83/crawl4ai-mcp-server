"""
Legacy server.py for backward compatibility with tests.

This module maintains compatibility with existing tests while using 
the unified server architecture internally.
"""
import asyncio
from unified_server import UnifiedServer

# Create unified server instance
unified_server = UnifiedServer()

# Set up MCP server for backward compatibility
mcp = unified_server.setup_mcp_server()

# Export for old-style imports
__all__ = ['mcp', 'unified_server']

# Maintain compatibility with old test imports
VectorStore = None  # Placeholder for tests that import this
IntelligentSyncManager = None  # Placeholder for tests that import this
VectorSyncAPI = None  # Placeholder for tests that import this

if __name__ == "__main__":
    # For MCP stdio mode (like Claude Desktop), run the MCP server directly
    # FastMCP.run() handles the event loop internally with anyio.run()
    mcp.run()