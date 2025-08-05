#!/usr/bin/env python3
"""
Test collections directly by importing the tools.
"""

import asyncio
import json
import sys
from pathlib import Path

async def test_collection_tools():
    """Test collection tools directly."""
    
    # Import the server modules
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    # Import collection tools from server
    from tools.sqlite_collection_manager import create_collection_manager
    
    print("🔍 Testing Collection Manager...")
    
    collection_manager = create_collection_manager(use_sqlite=True)
    
    # Test 1: List existing collections
    print("\n📋 Listing existing collections...")
    result = collection_manager.list_collections()
    if isinstance(result, str):
        result = json.loads(result)
    
    if result.get('success'):
        collections = result.get('collections', [])
        print(f"✅ Found {len(collections)} collections:")
        for collection in collections:
            name = collection.get('name', 'Unknown')
            file_count = collection.get('file_count', 0)
            print(f"   - {name} ({file_count} files)")
    else:
        print(f"❌ Failed: {result.get('error')}")
    
    # Test 2: Create a new collection via MCP tool
    print("\n🆕 Creating new collection 'MCP_TEST'...")
    
    test_collection_name = "MCP_TEST"
    create_result = collection_manager.create_collection(
        test_collection_name, 
        "Test collection created to verify MCP-Frontend consistency"
    )
    
    if isinstance(create_result, str):
        create_result = json.loads(create_result)
    
    if create_result.get('success'):
        print(f"✅ Collection '{test_collection_name}' created successfully")
        
        # Test 3: List collections again to verify it appears
        print(f"\n📋 Verifying '{test_collection_name}' appears in list...")
        result = collection_manager.list_collections()
        if isinstance(result, str):
            result = json.loads(result)
        
        if result.get('success'):
            collections = result.get('collections', [])
            collection_names = [c.get('name') for c in collections]
            
            if test_collection_name in collection_names:
                print(f"✅ Collection '{test_collection_name}' found in list!")
            else:
                print(f"❌ Collection '{test_collection_name}' NOT found in list")
                print(f"Available collections: {collection_names}")
        
    else:
        print(f"❌ Failed to create collection: {create_result.get('error')}")
    
    print("\n🌐 Testing if new collection appears in HTTP API...")
    
    # Test if it shows up in HTTP API
    import requests
    try:
        response = requests.get("http://localhost:8000/api/file-collections")
        if response.status_code == 200:
            http_data = response.json()
            if http_data.get('success'):
                http_collections = http_data.get('data', {}).get('collections', [])
                http_names = [c.get('name') for c in http_collections]
                
                print(f"📋 HTTP API shows {len(http_collections)} collections:")
                for name in http_names:
                    marker = "✅" if name == test_collection_name else "  "
                    print(f"{marker} - {name}")
                
                if test_collection_name in http_names:
                    print(f"🎉 SUCCESS: Collection '{test_collection_name}' is visible in both MCP and HTTP API!")
                else:
                    print(f"⚠️  Collection '{test_collection_name}' created via MCP but NOT visible in HTTP API")
            else:
                print(f"❌ HTTP API error: {http_data.get('error')}")
        else:
            print(f"❌ HTTP API returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing HTTP API: {e}")

if __name__ == "__main__":
    asyncio.run(test_collection_tools())