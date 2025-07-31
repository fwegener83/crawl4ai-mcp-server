#!/usr/bin/env python3
"""Integration test for the complete file listing workflow."""
import json
import time
import sys
import os
import pytest

# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_complete_workflow():
    """Test the complete workflow: create collection, crawl URL, list files."""
    print("Testing complete file listing workflow...")
    
    try:
        import requests
    except ImportError:
        pytest.skip("requests module not available for integration test")
    
    base_url = "http://localhost:8000"
    
    try:
        # 1. Check server health
        print("1. Checking server health...")
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Server not healthy: {response.status_code}")
            return False
        print("✓ Server is healthy")
        
        # 2. Create a new collection for testing
        test_collection = "integration-test-collection"
        print(f"2. Creating collection '{test_collection}'...")
        response = requests.post(f"{base_url}/api/file-collections", 
                               json={"name": test_collection, "description": "Integration test collection"},
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✓ Collection created successfully")
            else:
                print(f"❌ Failed to create collection: {data}")
                return False
        else:
            print(f"❌ Failed to create collection: {response.status_code}")
            return False
        
        # 3. Crawl a test URL and save to collection
        print("3. Crawling test URL...")
        crawl_url = "https://httpbin.org/json"
        response = requests.post(f"{base_url}/api/crawl/single/{test_collection}",
                               json={"url": crawl_url, "folder": ""},
                               timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"✓ URL crawled successfully, saved as: {data.get('message', 'unknown file')}")
            else:
                print(f"❌ Failed to crawl URL: {data}")
                return False
        else:
            print(f"❌ Failed to crawl URL: {response.status_code}")
            return False
        
        # 4. List files in the collection using new endpoint
        print("4. Listing files in collection...")
        response = requests.get(f"{base_url}/api/file-collections/{test_collection}/files", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                file_data = data["data"]
                print(f"✓ Found {file_data['total_files']} files and {file_data['total_folders']} folders")
                
                if file_data["total_files"] > 0:
                    print("  Files found:")
                    for file_info in file_data["files"]:
                        print(f"    - {file_info['name']} ({file_info['size']} bytes)")
                else:
                    print("❌ No files found after crawling")
                    return False
            else:
                print(f"❌ Failed to list files: {data}")
                return False
        else:
            print(f"❌ Failed to list files: {response.status_code}")
            return False
        
        # 5. Get collection info to verify files are included
        print("5. Getting collection info...")
        response = requests.get(f"{base_url}/api/file-collections/{test_collection}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                collection_info = data["data"]
                print(f"✓ Collection info includes {collection_info['file_count']} files")
                
                if "files" in collection_info and len(collection_info["files"]) > 0:
                    print("✓ Collection info includes file listing")
                else:
                    print("❌ Collection info does not include file listing")
                    return False
            else:
                print(f"❌ Failed to get collection info: {data}")
                return False
        else:
            print(f"❌ Failed to get collection info: {response.status_code}")
            return False
        
        # 6. Test with folder structure
        print("6. Testing folder structure...")
        response = requests.post(f"{base_url}/api/crawl/single/{test_collection}",
                               json={"url": "https://httpbin.org/get", "folder": "test-folder"},
                               timeout=30)
        
        if response.status_code == 200:
            print("✓ File saved to folder successfully")
            
            # List files again to check folder structure
            response = requests.get(f"{base_url}/api/file-collections/{test_collection}/files", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    file_data = data["data"]
                    
                    # Check if we have files in folders
                    folder_files = [f for f in file_data["files"] if f["folder"]]
                    if folder_files:
                        print(f"✓ Found {len(folder_files)} files in folders")
                        for file_info in folder_files:
                            print(f"    - {file_info['path']} (in folder: {file_info['folder']})")
                    else:
                        print("⚠ No files found in folders")
        else:
            print(f"⚠ Could not test folder structure: {response.status_code}")
        
        # 7. Clean up - delete test collection
        print("7. Cleaning up test collection...")
        response = requests.delete(f"{base_url}/api/file-collections/{test_collection}", timeout=10)
        
        if response.status_code == 200:
            print("✓ Test collection deleted successfully")
        else:
            print(f"⚠ Could not delete test collection: {response.status_code}")
        
        # Test passed successfully
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        pytest.fail(f"Network error during integration test: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        pytest.fail(f"Unexpected error during integration test: {e}")


def main():
    """Run the integration test."""
    print("Running complete file listing workflow integration test...\n")
    
    success = test_complete_workflow()
    
    if success:
        print("\n🎉 Integration test completed successfully!")
        print("✅ File listing functionality is working end-to-end")
        return 0
    else:
        print("\n❌ Integration test failed")
        return 1


if __name__ == "__main__":
    exit(main())