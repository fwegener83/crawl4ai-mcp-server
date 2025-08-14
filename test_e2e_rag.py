#!/usr/bin/env python3
"""
End-to-End RAG Integration Test Script

This script tests the complete RAG workflow:
1. Start unified server
2. Create test collection 
3. Add test content
4. Sync to vectors
5. Execute RAG query
6. Verify response format
"""

import asyncio
import json
import time
import requests
from typing import Dict, Any
import subprocess
import sys
import os

# Configuration
BASE_URL = "http://localhost:8000"
TEST_COLLECTION = "e2e-test-rag"
TEST_CONTENT = """
# Machine Learning Guide

Machine learning is a subset of artificial intelligence (AI) that provides systems the ability to automatically learn and improve from experience without being explicitly programmed.

## Key Concepts

### Supervised Learning
Supervised learning uses labeled training data to learn a function that maps inputs to outputs.

### Unsupervised Learning  
Unsupervised learning finds hidden patterns in data without labeled examples.

### Deep Learning
Deep learning uses neural networks with multiple layers to model and understand complex patterns.

## Applications
- Image recognition
- Natural language processing
- Recommendation systems
- Autonomous vehicles
"""

class RAGIntegrationTester:
    def __init__(self):
        self.server_process = None
        self.base_url = BASE_URL
        
    def log(self, message: str, level: str = "INFO"):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    async def wait_for_server(self, timeout: int = 30) -> bool:
        """Wait for server to be ready."""
        self.log("Waiting for server to be ready...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.base_url}/api/health", timeout=2)
                if response.status_code == 200:
                    self.log("Server is ready!")
                    return True
            except requests.RequestException:
                pass
            await asyncio.sleep(1)
        
        self.log("Server failed to start within timeout", "ERROR")
        return False
    
    def start_server(self) -> bool:
        """Start the unified server."""
        self.log("Starting unified server...")
        try:
            # Start server in background
            self.server_process = subprocess.Popen(
                ["uv", "run", "python", "unified_server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            self.log(f"Server started with PID: {self.server_process.pid}")
            return True
        except Exception as e:
            self.log(f"Failed to start server: {e}", "ERROR")
            return False
    
    def stop_server(self):
        """Stop the unified server."""
        if self.server_process:
            self.log("Stopping unified server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.log("Force killing server process", "WARN")
                self.server_process.kill()
            self.server_process = None
    
    async def create_test_collection(self) -> bool:
        """Create test collection."""
        self.log(f"Creating test collection: {TEST_COLLECTION}")
        try:
            response = requests.post(
                f"{self.base_url}/api/collections",
                json={
                    "name": TEST_COLLECTION,
                    "description": "E2E RAG test collection"
                },
                timeout=10
            )
            
            if response.status_code == 201:
                self.log("Test collection created successfully")
                return True
            else:
                self.log(f"Failed to create collection: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Error creating collection: {e}", "ERROR")
            return False
    
    async def add_test_content(self) -> bool:
        """Add test content to collection."""
        self.log("Adding test content to collection")
        try:
            response = requests.post(
                f"{self.base_url}/api/collections/{TEST_COLLECTION}/files",
                json={
                    "filename": "ml-guide.md",
                    "content": TEST_CONTENT,
                    "folder": ""
                },
                timeout=10
            )
            
            if response.status_code == 201:
                self.log("Test content added successfully")
                return True
            else:
                self.log(f"Failed to add content: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Error adding content: {e}", "ERROR")
            return False
    
    async def sync_to_vectors(self) -> bool:
        """Sync collection to vector database."""
        self.log("Syncing collection to vectors...")
        try:
            response = requests.post(
                f"{self.base_url}/api/vector-sync/collections/{TEST_COLLECTION}/sync",
                json={
                    "force_reprocess": True,
                    "chunking_strategy": "baseline"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success", False):
                    self.log("Vector sync completed successfully")
                    return True
                else:
                    self.log(f"Vector sync failed: {result.get('error', 'Unknown error')}", "ERROR")
                    return False
            else:
                self.log(f"Vector sync failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Error syncing vectors: {e}", "ERROR")
            return False
    
    async def execute_rag_query(self, query: str) -> Dict[str, Any]:
        """Execute RAG query and return response."""
        self.log(f"Executing RAG query: '{query}'")
        try:
            response = requests.post(
                f"{self.base_url}/api/query",
                json={
                    "query": query,
                    "collection_name": TEST_COLLECTION,
                    "max_chunks": 3,
                    "similarity_threshold": 0.1
                },
                timeout=60  # Allow more time for LLM processing
            )
            
            if response.status_code == 200:
                result = response.json()
                self.log("RAG query executed successfully")
                return result
            else:
                self.log(f"RAG query failed: {response.status_code} - {response.text}", "ERROR")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            self.log(f"Error executing RAG query: {e}", "ERROR")
            return {"success": False, "error": str(e)}
    
    def validate_rag_response(self, response: Dict[str, Any]) -> bool:
        """Validate RAG response format and content."""
        self.log("Validating RAG response...")
        
        # Check basic structure
        if not isinstance(response, dict):
            self.log("Response is not a dictionary", "ERROR")
            return False
        
        if not response.get("success", False):
            self.log(f"Response indicates failure: {response.get('error', 'Unknown')}", "ERROR")
            return False
        
        # Check required fields
        required_fields = ["answer", "sources", "metadata"]
        for field in required_fields:
            if field not in response:
                self.log(f"Missing required field: {field}", "ERROR")
                return False
        
        # Validate sources
        sources = response.get("sources", [])
        if not isinstance(sources, list):
            self.log("Sources is not a list", "ERROR")
            return False
        
        if len(sources) == 0:
            self.log("No sources found in response", "WARN")
        else:
            self.log(f"Found {len(sources)} sources")
            
            # Validate first source structure
            first_source = sources[0]
            source_fields = ["content", "similarity_score", "metadata"]
            for field in source_fields:
                if field not in first_source:
                    self.log(f"Missing source field: {field}", "ERROR")
                    return False
        
        # Validate metadata
        metadata = response.get("metadata", {})
        if not isinstance(metadata, dict):
            self.log("Metadata is not a dictionary", "ERROR")
            return False
        
        metadata_fields = ["chunks_used", "collection_searched", "response_time_ms"]
        for field in metadata_fields:
            if field not in metadata:
                self.log(f"Missing metadata field: {field}", "ERROR")
                return False
        
        # Log response summary
        answer = response.get("answer")
        if answer:
            self.log(f"Answer received: {answer[:100]}{'...' if len(answer) > 100 else ''}")
        else:
            self.log("No answer generated (degraded mode)", "WARN")
        
        self.log(f"Sources: {len(sources)}, Chunks used: {metadata.get('chunks_used')}")
        self.log(f"Response time: {metadata.get('response_time_ms')}ms")
        
        self.log("RAG response validation passed!")
        return True
    
    async def cleanup(self):
        """Clean up test resources."""
        self.log("Cleaning up test resources...")
        try:
            # Delete test collection
            response = requests.delete(
                f"{self.base_url}/api/collections/{TEST_COLLECTION}",
                timeout=10
            )
            if response.status_code == 200:
                self.log("Test collection deleted")
            else:
                self.log(f"Failed to delete test collection: {response.status_code}", "WARN")
        except Exception as e:
            self.log(f"Error during cleanup: {e}", "WARN")
    
    async def run_test(self) -> bool:
        """Run complete end-to-end test."""
        self.log("Starting RAG End-to-End Integration Test")
        success = True
        
        try:
            # Start server
            if not self.start_server():
                return False
            
            # Wait for server to be ready
            if not await self.wait_for_server():
                return False
            
            # Create test collection
            if not await self.create_test_collection():
                success = False
                return success
            
            # Add test content
            if not await self.add_test_content():
                success = False
                return success
            
            # Sync to vectors
            if not await self.sync_to_vectors():
                success = False
                return success
            
            # Wait a bit for sync to complete
            await asyncio.sleep(2)
            
            # Execute RAG queries
            test_queries = [
                "What is machine learning?",
                "Tell me about supervised learning",
                "What are the applications of ML?"
            ]
            
            for query in test_queries:
                response = await self.execute_rag_query(query)
                if not self.validate_rag_response(response):
                    success = False
                    break
                
                self.log("=" * 50)
            
            if success:
                self.log("All RAG queries passed validation!", "SUCCESS")
            
        except Exception as e:
            self.log(f"Test execution failed: {e}", "ERROR")
            success = False
        
        finally:
            # Cleanup
            await self.cleanup()
            self.stop_server()
        
        return success

async def main():
    """Main test execution."""
    tester = RAGIntegrationTester()
    
    try:
        success = await tester.run_test()
        
        if success:
            print("\n🎉 RAG End-to-End Integration Test PASSED!")
            sys.exit(0)
        else:
            print("\n❌ RAG End-to-End Integration Test FAILED!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        tester.stop_server()
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test crashed: {e}")
        tester.stop_server()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())