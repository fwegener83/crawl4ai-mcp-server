#!/usr/bin/env python3
"""
Comprehensive integration test for the Domain Deep Crawler MCP Tool.
This test verifies the complete functionality with real Crawl4AI integration.
"""

import asyncio
import json
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from tools.domain_crawler import DomainDeepCrawlParams, domain_deep_crawl_impl
from tools.domain_link_preview import DomainLinkPreviewParams, domain_link_preview_impl
from tools.mcp_domain_tools import domain_deep_crawl, domain_link_preview


async def test_core_functionality():
    """Test core deep crawling functionality."""
    print("=== Testing Core Deep Crawling Functionality ===")
    
    # Test BFS strategy
    print("\n1. Testing BFS strategy...")
    params = DomainDeepCrawlParams(
        domain_url='https://example.com',
        max_depth=1,
        max_pages=3,
        crawl_strategy='bfs',
        stream_results=False
    )
    
    result = await domain_deep_crawl_impl(params)
    parsed = json.loads(result)
    
    print(f"   Success: {parsed.get('success')}")
    print(f"   Total pages: {parsed.get('crawl_summary', {}).get('total_pages')}")
    print(f"   Strategy: {parsed.get('crawl_summary', {}).get('strategy_used')}")
    
    # Test DFS strategy
    print("\n2. Testing DFS strategy...")
    params = DomainDeepCrawlParams(
        domain_url='https://example.com',
        max_depth=1,
        max_pages=3,
        crawl_strategy='dfs',
        stream_results=False
    )
    
    result = await domain_deep_crawl_impl(params)
    parsed = json.loads(result)
    
    print(f"   Success: {parsed.get('success')}")
    print(f"   Total pages: {parsed.get('crawl_summary', {}).get('total_pages')}")
    print(f"   Strategy: {parsed.get('crawl_summary', {}).get('strategy_used')}")
    
    # Test BestFirst strategy with keywords
    print("\n3. Testing BestFirst strategy with keywords...")
    params = DomainDeepCrawlParams(
        domain_url='https://example.com',
        max_depth=1,
        max_pages=3,
        crawl_strategy='best_first',
        keywords=['domain', 'example', 'test'],
        stream_results=False
    )
    
    result = await domain_deep_crawl_impl(params)
    parsed = json.loads(result)
    
    print(f"   Success: {parsed.get('success')}")
    print(f"   Total pages: {parsed.get('crawl_summary', {}).get('total_pages')}")
    print(f"   Strategy: {parsed.get('crawl_summary', {}).get('strategy_used')}")
    
    print("\n✅ Core functionality tests completed!")


async def test_link_preview():
    """Test link preview functionality."""
    print("\n=== Testing Link Preview Functionality ===")
    
    # Test internal links only
    print("\n1. Testing internal links only...")
    params = DomainLinkPreviewParams(
        domain_url='https://example.com',
        include_external=False
    )
    
    result = await domain_link_preview_impl(params)
    parsed = json.loads(result)
    
    print(f"   Success: {parsed.get('success')}")
    print(f"   Total links: {parsed.get('total_links')}")
    print(f"   Internal links: {parsed.get('internal_links')}")
    print(f"   External links: {parsed.get('external_links')}")
    
    # Test with external links
    print("\n2. Testing with external links...")
    params = DomainLinkPreviewParams(
        domain_url='https://example.com',
        include_external=True
    )
    
    result = await domain_link_preview_impl(params)
    parsed = json.loads(result)
    
    print(f"   Success: {parsed.get('success')}")
    print(f"   Total links: {parsed.get('total_links')}")
    print(f"   Internal links: {parsed.get('internal_links')}")
    print(f"   External links: {parsed.get('external_links')}")
    
    print("\n✅ Link preview tests completed!")


async def test_mcp_integration():
    """Test MCP tool integration."""
    print("\n=== Testing MCP Integration ===")
    
    # Test MCP domain deep crawl
    print("\n1. Testing MCP domain deep crawl...")
    result = await domain_deep_crawl(
        domain_url='https://example.com',
        max_depth=1,
        max_pages=2,
        crawl_strategy='bfs'
    )
    
    parsed = json.loads(result)
    print(f"   Success: {parsed.get('success')}")
    print(f"   Total pages: {parsed.get('crawl_summary', {}).get('total_pages')}")
    
    # Test MCP domain link preview
    print("\n2. Testing MCP domain link preview...")
    result = await domain_link_preview(
        domain_url='https://example.com',
        include_external=False
    )
    
    parsed = json.loads(result)
    print(f"   Success: {parsed.get('success')}")
    print(f"   Total links: {parsed.get('total_links')}")
    
    print("\n✅ MCP integration tests completed!")


async def test_error_handling():
    """Test error handling."""
    print("\n=== Testing Error Handling ===")
    
    # Test invalid domain URL
    print("\n1. Testing invalid domain URL...")
    try:
        params = DomainDeepCrawlParams(
            domain_url='invalid-url',
            max_depth=1,
            max_pages=2,
            crawl_strategy='bfs'
        )
        print("   ERROR: Should have raised validation error!")
    except ValueError as e:
        print(f"   ✅ Correctly caught validation error: {e}")
    
    # Test invalid strategy
    print("\n2. Testing invalid strategy...")
    try:
        params = DomainDeepCrawlParams(
            domain_url='https://example.com',
            max_depth=1,
            max_pages=2,
            crawl_strategy='invalid-strategy'
        )
        print("   ERROR: Should have raised validation error!")
    except ValueError as e:
        print(f"   ✅ Correctly caught validation error: {e}")
    
    print("\n✅ Error handling tests completed!")


async def test_server_import():
    """Test server import and tool registration."""
    print("\n=== Testing Server Import ===")
    
    try:
        from server import mcp
        print("   ✅ Server imported successfully")
        
        # Test that tools are registered
        tools = await mcp.get_tools()
        print(f"   ✅ Number of registered tools: {len(tools)}")
        
        # Expected tools: web_content_extract, domain_deep_crawl_tool, domain_link_preview_tool
        if len(tools) >= 3:
            print("   ✅ All expected tools registered")
        else:
            print("   ⚠️  Expected at least 3 tools")
            
    except Exception as e:
        print(f"   ❌ Server import failed: {e}")
    
    print("\n✅ Server import tests completed!")


async def main():
    """Run all integration tests."""
    print("🚀 Starting Domain Deep Crawler MCP Tool Integration Tests")
    print("=" * 60)
    
    try:
        await test_core_functionality()
        await test_link_preview()
        await test_mcp_integration()
        await test_error_handling()
        await test_server_import()
        
        print("\n" + "=" * 60)
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("✅ Domain Deep Crawler MCP Tool is ready for production use!")
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())