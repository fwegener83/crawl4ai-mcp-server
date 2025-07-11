#!/usr/bin/env python3
"""Test MCP tool call specifically to verify string output."""
import asyncio
import json
import subprocess
import sys

async def test_mcp_tool_call():
    """Test actual MCP tool call via subprocess."""
    print("🧪 Testing MCP Tool Call...")
    
    # Start server process
    process = subprocess.Popen(
        [sys.executable, "server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd="/Users/florianwegener/Projects/crawl4ai-mcp-server"
    )
    
    try:
        # 1. Initialize
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        print("📤 Sending initialize request...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Read response
        response = process.stdout.readline()
        print(f"📥 Initialize response: {response.strip()}")
        
        # 1.5. Send initialized notification (CRITICAL!)
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        print("📤 Sending initialized notification...")
        process.stdin.write(json.dumps(initialized_notification) + "\n")
        process.stdin.flush()
        
        # 2. Call web_content_extract tool
        tool_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "web_content_extract",
                "arguments": {
                    "url": "https://example.com"
                }
            }
        }
        
        print("📤 Sending tool call request...")
        process.stdin.write(json.dumps(tool_request) + "\n")
        process.stdin.flush()
        
        # Read response
        response = process.stdout.readline()
        print(f"📥 Tool call response: {response.strip()}")
        
        # Parse the response to check the content
        try:
            response_data = json.loads(response)
            if "result" in response_data:
                content = response_data["result"]["content"]
                print(f"✅ Content type: {type(content)}")
                print(f"✅ Content preview: {content[:100]}...")
                
                # Check if it's a proper string
                if isinstance(content, str):
                    print("✅ Response is a proper string!")
                else:
                    print(f"❌ Response is not a string: {type(content)}")
                    
            else:
                print(f"❌ No result in response: {response_data}")
                
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON response: {e}")
            
    finally:
        # Clean up
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            
    print("🎉 MCP Tool Call test completed!")

if __name__ == "__main__":
    asyncio.run(test_mcp_tool_call())