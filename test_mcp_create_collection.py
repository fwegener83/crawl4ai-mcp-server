#!/usr/bin/env python3
"""
Test creating a collection via MCP tools to verify SQLite integration.
"""

import asyncio
import json
import sys
from pathlib import Path

async def test_mcp_create_collection():
    """Test creating a collection using MCP tools."""
    
    # Import the server modules
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    # Import the server and its tools
    from server import mcp
    
    print("🔍 Testing MCP collection creation...")
    
    # Create a test collection
    test_collection_name = "MCP_TEST_COLLECTION"
    test_description = "Test collection created via MCP tools"
    
    try:
        # Test the create_collection MCP tool
        result = await mcp.call_tool(
            "create_collection",
            {
                "name": test_collection_name,
                "description": test_description
            }
        )
        
        print(f"✅ Create collection result: {result}")
        
        # Test listing collections
        list_result = await mcp.call_tool("list_file_collections", {})
        print(f"📋 List collections result: {list_result}")
        
    except Exception as e:
        print(f"❌ Error testing MCP tools: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp_create_collection())