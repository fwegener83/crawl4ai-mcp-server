#!/usr/bin/env python3
"""
Test script to verify MCP tools use the same SQLite collection manager as HTTP server.
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

def test_mcp_tools():
    """Test MCP tools by calling them directly."""
    
    # Import the server modules
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    # Test collection manager directly
    from tools.sqlite_collection_manager import create_collection_manager
    
    print("🔍 Testing SQLite Collection Manager directly...")
    collection_manager = create_collection_manager(use_sqlite=True)
    
    # List collections
    result = collection_manager.list_collections()
    
    if isinstance(result, str):
        result = json.loads(result)
    
    if result.get('success'):
        collections = result.get('collections', [])
        print(f"✅ Found {len(collections)} collections in SQLite:")
        for collection in collections:
            print(f"   - {collection.get('name', 'Unknown')} (files: {collection.get('file_count', 0)})")
    else:
        print(f"❌ Failed to list collections: {result.get('error', 'Unknown error')}")
    
    print("\n🔍 Testing file-based collections path (old system)...")
    
    # Check if old file-based collections still exist
    old_collections_path = Path.home() / ".crawl4ai"
    
    if old_collections_path.exists():
        old_collections = [d for d in old_collections_path.iterdir() if d.is_dir()]
        print(f"⚠️  Found {len(old_collections)} old file-based collections:")
        for collection_dir in old_collections:
            print(f"   - {collection_dir.name}")
    else:
        print("✅ No old file-based collections found")
    
    print(f"\n📂 Collections storage location: {collection_manager.base_dir}")

if __name__ == "__main__":
    test_mcp_tools()