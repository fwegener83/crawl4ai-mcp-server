"""Test MCP protocol regression - subprocess/stdio communication like Claude Desktop."""
import pytest
import subprocess
import sys
import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock


class TestMCPProtocolRegression:
    """Regression tests for complete MCP protocol sequence via subprocess/stdio."""
    
    def test_complete_mcp_initialization_sequence(self):
        """REGRESSION: Ensure MCP protocol initialization is never broken.
        
        This test validates the complete 4-step MCP protocol sequence that
        Claude Desktop uses:
        1. initialize request
        2. notifications/initialized notification (CRITICAL!)
        3. tools/list request 
        4. tools/call request
        """
        # Start server process
        process = subprocess.Popen(
            [sys.executable, 'server.py'], 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        try:
            # Step 1: Send initialize request
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"}
                }
            }
            
            process.stdin.write(json.dumps(init_request) + "\n")
            process.stdin.flush()
            
            # Read initialize response
            init_response = process.stdout.readline()
            assert init_response.strip(), "No response to initialize request"
            
            init_data = json.loads(init_response)
            assert "result" in init_data, f"Initialize failed: {init_data}"
            assert init_data["result"]["protocolVersion"] == "2024-11-05"
            
            # Step 2: Send initialized notification (CRITICAL!)
            initialized_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            
            process.stdin.write(json.dumps(initialized_notification) + "\n")
            process.stdin.flush()
            
            # Step 3: Send tools/list request
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            process.stdin.write(json.dumps(tools_request) + "\n")
            process.stdin.flush()
            
            # Read tools/list response
            tools_response = process.stdout.readline()
            assert tools_response.strip(), "No response to tools/list request"
            
            tools_data = json.loads(tools_response)
            assert "result" in tools_data, f"Tools/list failed: {tools_data}"
            assert "tools" in tools_data["result"]
            assert len(tools_data["result"]["tools"]) >= 1
            tool_names = [t["name"] for t in tools_data["result"]["tools"]]
            assert "web_content_extract" in tool_names
            
            # Step 4: Send tools/call request (with mock-friendly URL to avoid real network call)
            call_request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "web_content_extract",
                    "arguments": {"url": "https://httpbin.org/status/200"}  # Reliable test endpoint
                }
            }
            
            process.stdin.write(json.dumps(call_request) + "\n")
            process.stdin.flush()
            
            # Read tools/call response
            call_response = process.stdout.readline()
            assert call_response.strip(), "No response to tools/call request"
            
            call_data = json.loads(call_response)
            assert "result" in call_data, f"Tools/call failed: {call_data}"
            assert "content" in call_data["result"]
            assert call_data["result"]["isError"] is False
            
        finally:
            # Clean up
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
    
    def test_missing_initialized_notification_fails(self):
        """REGRESSION: Ensure we catch missing initialization step.
        
        This test verifies that skipping the notifications/initialized step
        causes the expected failure, preventing regressions where this 
        critical step is accidentally removed.
        """
        # Start server process
        process = subprocess.Popen(
            [sys.executable, 'server.py'], 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        try:
            # Step 1: Send initialize request
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"}
                }
            }
            
            process.stdin.write(json.dumps(init_request) + "\n")
            process.stdin.flush()
            
            # Read initialize response
            init_response = process.stdout.readline()
            init_data = json.loads(init_response)
            assert "result" in init_data
            
            # Step 2: SKIP notifications/initialized (this should cause failure)
            
            # Step 3: Send tools/list request (should fail)
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            process.stdin.write(json.dumps(tools_request) + "\n")
            process.stdin.flush()
            
            # Read tools/list response - should be an error
            tools_response = process.stdout.readline()
            assert tools_response.strip(), "No response to tools/list request"
            
            tools_data = json.loads(tools_response)
            # Should get error response due to missing initialization
            assert "error" in tools_data, "Expected error due to missing notifications/initialized"
            assert tools_data["error"]["code"] == -32602  # Invalid request parameters
            
        finally:
            # Clean up
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
    
    def test_subprocess_error_handling_and_cleanup(self):
        """REGRESSION: Ensure robust subprocess error handling and cleanup."""
        # Start server process
        process = subprocess.Popen(
            [sys.executable, 'server.py'], 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        try:
            # Send malformed JSON to test error handling
            malformed_request = "{ invalid json }"
            process.stdin.write(malformed_request + "\n")
            process.stdin.flush()
            
            # Server should handle this gracefully and not crash
            # Give it a moment to process
            time.sleep(0.1)
            
            # Check if process is still running
            poll_result = process.poll()
            assert poll_result is None, "Server crashed on malformed JSON"
            
            # Now send a valid request to verify server recovered
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"}
                }
            }
            
            process.stdin.write(json.dumps(init_request) + "\n")
            process.stdin.flush()
            
            # Should get valid response
            init_response = process.stdout.readline()
            assert init_response.strip(), "Server didn't recover after error"
            
            init_data = json.loads(init_response)
            assert "result" in init_data, "Server didn't recover properly"
            
        finally:
            # Test proper cleanup
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                # This should not happen with proper cleanup
                pytest.fail("Process didn't terminate gracefully")
    
    def test_mcp_protocol_parameter_validation(self):
        """REGRESSION: Ensure MCP protocol parameter validation works correctly."""
        # Start server process
        process = subprocess.Popen(
            [sys.executable, 'server.py'], 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        try:
            # Complete initialization sequence
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"}
                }
            }
            
            process.stdin.write(json.dumps(init_request) + "\n")
            process.stdin.flush()
            process.stdout.readline()  # consume response
            
            # Send initialized notification
            initialized_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            process.stdin.write(json.dumps(initialized_notification) + "\n")
            process.stdin.flush()
            
            # Test tools/list with missing params (our server is lenient and accepts this)
            tools_request_no_params = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
                # Missing "params": {} - but our server accepts this
            }
            
            process.stdin.write(json.dumps(tools_request_no_params) + "\n")
            process.stdin.flush()
            
            tools_response = process.stdout.readline()
            tools_data = json.loads(tools_response)
            # Our server is lenient and should succeed
            assert "result" in tools_data, "Server should accept tools/list without params"
            
            # Test tools/list with correct params (should succeed)
            tools_request_correct = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/list",
                "params": {}
            }
            
            process.stdin.write(json.dumps(tools_request_correct) + "\n")
            process.stdin.flush()
            
            tools_response = process.stdout.readline()
            tools_data = json.loads(tools_response)
            assert "result" in tools_data, "Should succeed with correct params"
            
        finally:
            # Clean up
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()


class TestMCPProtocolProductionPatterns:
    """Test production-like patterns extracted from temporary test files."""
    
    def test_production_environment_setup(self):
        """Test subprocess setup with production-like environment."""
        # Use production-like paths
        server_path = Path(__file__).parent.parent / "server.py"
        python_path = Path(__file__).parent.parent / ".venv" / "bin" / "python"
        
        # Fallback to system python if venv doesn't exist
        if not python_path.exists():
            python_path = sys.executable
        
        process = subprocess.Popen(
            [str(python_path), str(server_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )
        
        try:
            # Test that server starts successfully with production setup
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "claude-desktop", "version": "1.0.0"}
                }
            }
            
            process.stdin.write(json.dumps(init_request) + "\n")
            process.stdin.flush()
            
            init_response = process.stdout.readline()
            assert init_response.strip(), "No response with production setup"
            
            init_data = json.loads(init_response)
            assert "result" in init_data, f"Initialize failed with production setup: {init_data}"
            
        finally:
            # Test stderr capture for debugging
            process.terminate()
            try:
                process.wait(timeout=5)
                stderr_output = process.stderr.read()
                if stderr_output:
                    # This is useful for debugging but shouldn't fail the test
                    print(f"Server stderr: {stderr_output}")
            except subprocess.TimeoutExpired:
                process.kill()
    
