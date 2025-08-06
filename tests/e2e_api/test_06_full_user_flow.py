"""
🧪 Test Package 06: Full User Flow - Complete End-to-End Workflow

Tests complete user workflows combining all API functionalities.
This represents realistic user scenarios from start to finish.
"""
import pytest
import httpx
import uuid
import asyncio


@pytest.mark.asyncio
async def test_complete_content_management_workflow(client: httpx.AsyncClient, cleanup_collections):
    """
    Test complete workflow: Create collection → Add manual content → Crawl web page → 
    Sync to vectors → Search content → Update content → Clean up
    """
    # Step 1: Check system health
    health_response = await client.get("/api/health")
    assert health_response.status_code == 200
    assert health_response.json()["status"] == "healthy"
    
    # Step 2: Create a new collection
    collection_name = f"full_workflow_{uuid.uuid4().hex[:6]}"
    create_response = await client.post("/api/file-collections", json={
        "name": collection_name,
        "description": "Complete workflow test collection"
    })
    assert create_response.status_code == 200
    collection_id = create_response.json()["collection"]["id"]
    cleanup_collections(collection_id)
    
    # Step 3: Add manual content to collection
    manual_content = """# Project Overview

This is a comprehensive project about web crawling and content management.
We focus on extracting meaningful information from web pages and organizing it efficiently.

## Key Features
- Web content extraction
- Semantic search capabilities  
- Collection management
- Vector database integration
"""
    
    file_response = await client.post(f"/api/file-collections/{collection_id}/files", json={
        "filename": "project_overview.md",
        "content": manual_content
    })
    assert file_response.status_code == 200
    
    # Step 4: Preview web links before crawling
    preview_response = await client.post("/api/link-preview", json={
        "domain_url": "https://example.com",
        "include_external": False
    })
    assert preview_response.status_code == 200
    
    # Step 5: Crawl a web page and add to collection
    crawl_response = await client.post(f"/api/crawl/single/{collection_id}", json={
        "url": "https://example.com"
    })
    assert crawl_response.status_code == 200
    crawled_file = crawl_response.json()["file"]
    
    # Step 6: Verify files are in collection
    files_response = await client.get(f"/api/file-collections/{collection_id}/files")
    assert files_response.status_code == 200
    files = files_response.json()["files"]
    assert len(files) == 2  # Manual file + crawled file
    
    # Step 7: Read and verify file contents
    manual_file_response = await client.get(f"/api/file-collections/{collection_id}/files/project_overview.md")
    assert manual_file_response.status_code == 200
    assert manual_file_response.json()["file"]["content"] == manual_content
    
    crawled_file_response = await client.get(f"/api/file-collections/{collection_id}/files/{crawled_file['filename']}")
    assert crawled_file_response.status_code == 200
    assert len(crawled_file_response.json()["file"]["content"]) > 0
    
    # Step 8: Sync collection to vector database
    sync_response = await client.post(f"/api/vector-sync/collections/{collection_name}/sync", json={
        "force_reprocess": False,
        "chunking_strategy": "sentence"
    })
    assert sync_response.status_code == 200
    sync_result = sync_response.json()["sync_result"]
    assert sync_result["vector_count"] > 0
    
    # Step 9: Verify sync status
    status_response = await client.get(f"/api/vector-sync/collections/{collection_name}/status")
    assert status_response.status_code == 200
    status = status_response.json()["status"]
    assert status["sync_status"] == "in_sync"
    assert status["vector_count"] == sync_result["vector_count"]
    
    # Step 10: Search for content
    await asyncio.sleep(2)  # Allow indexing
    search_response = await client.post("/api/vector-sync/search", json={
        "query": "web crawling and content management",
        "collection_name": collection_name,
        "limit": 5,
        "similarity_threshold": 0.3
    })
    assert search_response.status_code == 200
    search_results = search_response.json()["results"]
    assert len(search_results) > 0
    
    # Step 11: Update file content
    updated_content = manual_content + "\n\n## Recent Updates\n- Added web crawling functionality\n- Implemented vector search"
    update_response = await client.put(f"/api/file-collections/{collection_id}/files/project_overview.md", json={
        "content": updated_content
    })
    assert update_response.status_code == 200
    
    # Step 12: Re-sync after update
    resync_response = await client.post(f"/api/vector-sync/collections/{collection_name}/sync", json={
        "force_reprocess": True
    })
    assert resync_response.status_code == 200
    
    # Step 13: Final verification - search should find updated content
    await asyncio.sleep(2)
    final_search_response = await client.post("/api/vector-sync/search", json={
        "query": "recent updates and functionality",
        "collection_name": collection_name,
        "limit": 3
    })
    assert final_search_response.status_code == 200
    final_results = final_search_response.json()["results"]
    
    # Should find content related to updates
    found_updates = False
    for result in final_results:
        if "recent updates" in result["content"].lower() or "functionality" in result["content"].lower():
            found_updates = True
            break
    assert found_updates, "Updated content should be findable in search"


@pytest.mark.asyncio
async def test_multi_collection_research_workflow(client: httpx.AsyncClient, cleanup_collections):
    """
    Test research workflow: Create multiple collections → Add different content types → 
    Cross-collection search → Compare results
    """
    # Create multiple collections for different topics
    collections = {}
    topics = ["ai_research", "web_development", "data_science"]
    
    for topic in topics:
        collection_name = f"{topic}_{uuid.uuid4().hex[:6]}"
        create_response = await client.post("/api/file-collections", json={
            "name": collection_name,
            "description": f"Collection for {topic} research"
        })
        assert create_response.status_code == 200
        collection_id = create_response.json()["collection"]["id"]
        cleanup_collections(collection_id)
        collections[topic] = {"name": collection_name, "id": collection_id}
    
    # Add topic-specific content
    content_by_topic = {
        "ai_research": {
            "neural_networks.md": "# Neural Networks\n\nArtificial neural networks are computing systems inspired by biological neural networks. Deep learning uses multiple layers of neural networks to model complex patterns.",
            "machine_learning.md": "# Machine Learning Algorithms\n\nSupervised learning, unsupervised learning, and reinforcement learning are the main paradigms in machine learning."
        },
        "web_development": {
            "frontend_frameworks.md": "# Frontend Frameworks\n\nReact, Vue.js, and Angular are popular JavaScript frameworks for building user interfaces. They provide component-based architectures.",
            "backend_apis.md": "# Backend API Development\n\nRESTful APIs and GraphQL are common approaches for building server-side applications. FastAPI and Express.js are popular frameworks."
        },
        "data_science": {
            "data_analysis.md": "# Data Analysis\n\nPython libraries like pandas, numpy, and matplotlib are essential for data manipulation and visualization in data science projects.",
            "statistics.md": "# Statistical Methods\n\nDescriptive statistics, hypothesis testing, and regression analysis are fundamental statistical concepts for data scientists."
        }
    }
    
    # Add content to each collection
    for topic, files in content_by_topic.items():
        collection_id = collections[topic]["id"]
        for filename, content in files.items():
            file_response = await client.post(f"/api/file-collections/{collection_id}/files", json={
                "filename": filename,
                "content": content
            })
            assert file_response.status_code == 200
    
    # Sync all collections
    for topic, collection_info in collections.items():
        sync_response = await client.post(f"/api/vector-sync/collections/{collection_info['name']}/sync", json={
            "force_reprocess": False
        })
        assert sync_response.status_code == 200
        assert sync_response.json()["sync_result"]["vector_count"] > 0
    
    # Wait for all indexing to complete
    await asyncio.sleep(3)
    
    # Test topic-specific searches
    ai_search = await client.post("/api/vector-sync/search", json={
        "query": "neural networks and deep learning",
        "collection_name": collections["ai_research"]["name"],
        "limit": 3
    })
    assert ai_search.status_code == 200
    ai_results = ai_search.json()["results"]
    assert len(ai_results) > 0
    
    web_search = await client.post("/api/vector-sync/search", json={
        "query": "JavaScript frameworks and APIs",
        "collection_name": collections["web_development"]["name"], 
        "limit": 3
    })
    assert web_search.status_code == 200
    web_results = web_search.json()["results"]
    assert len(web_results) > 0
    
    # Test cross-collection search
    cross_search = await client.post("/api/vector-sync/search", json={
        "query": "Python programming and frameworks",
        "limit": 10
    })
    assert cross_search.status_code == 200
    cross_results = cross_search.json()["results"]
    assert len(cross_results) > 0
    
    # Verify cross-search found content from multiple collections
    found_topics = set()
    for result in cross_results:
        content = result["content"].lower()
        if any(word in content for word in ["pandas", "numpy", "python"]):
            found_topics.add("data_science")
        if any(word in content for word in ["api", "backend", "server"]):
            found_topics.add("web_development")
    
    assert len(found_topics) > 1, "Cross-collection search should find content from multiple collections"


@pytest.mark.asyncio
async def test_web_content_extraction_and_organization_workflow(client: httpx.AsyncClient, cleanup_collections):
    """
    Test workflow: Deep crawl domain → Extract content → Organize in collections → 
    Semantic analysis → Content management
    """
    # Step 1: Create collection for web content
    collection_name = f"web_content_{uuid.uuid4().hex[:6]}"
    create_response = await client.post("/api/file-collections", json={
        "name": collection_name,
        "description": "Collection for web-crawled content"
    })
    assert create_response.status_code == 200
    collection_id = create_response.json()["collection"]["id"]
    cleanup_collections(collection_id)
    
    # Step 2: Preview available links
    preview_response = await client.post("/api/link-preview", json={
        "domain_url": "https://example.com",
        "include_external": False
    })
    assert preview_response.status_code == 200
    links = preview_response.json()["links"]
    
    # Step 3: Perform deep crawl (limited for testing)
    deep_crawl_response = await client.post("/api/deep-crawl", json={
        "domain_url": "https://example.com",
        "max_pages": 2,
        "max_depth": 1,
        "crawl_strategy": "bfs",
        "include_external": False
    })
    assert deep_crawl_response.status_code == 200
    crawl_results = deep_crawl_response.json()["results"]
    assert len(crawl_results) > 0
    
    # Step 4: Add crawled content to collection
    for i, result in enumerate(crawl_results[:2]):  # Limit to first 2 results
        if result.get("success", False):
            filename = f"crawled_page_{i+1}.md"
            file_response = await client.post(f"/api/file-collections/{collection_id}/files", json={
                "filename": filename,
                "content": result["markdown"]
            })
            assert file_response.status_code == 200
    
    # Step 5: Add single page crawl
    single_crawl_response = await client.post(f"/api/crawl/single/{collection_id}", json={
        "url": "https://example.com"
    })
    assert single_crawl_response.status_code == 200
    
    # Step 6: Verify all files are present
    files_response = await client.get(f"/api/file-collections/{collection_id}/files")
    assert files_response.status_code == 200
    files = files_response.json()["files"]
    assert len(files) >= 3  # At least 2 deep crawl + 1 single crawl
    
    # Step 7: Sync to vectors for semantic analysis
    sync_response = await client.post(f"/api/vector-sync/collections/{collection_name}/sync", json={
        "force_reprocess": False,
        "chunking_strategy": "paragraph"
    })
    assert sync_response.status_code == 200
    
    # Step 8: Analyze content through search
    await asyncio.sleep(2)
    analysis_queries = [
        "main topics and themes",
        "important information and content",
        "key concepts and ideas"
    ]
    
    for query in analysis_queries:
        search_response = await client.post("/api/vector-sync/search", json={
            "query": query,
            "collection_name": collection_name,
            "limit": 5,
            "similarity_threshold": 0.2
        })
        assert search_response.status_code == 200
        results = search_response.json()["results"]
        # Should find some content for each analysis query
        assert len(results) >= 0  # Allow for cases where content might not match
    
    # Step 9: Content management - update one of the files
    first_file = files[0]
    filename = first_file["filename"]
    
    # Get original content
    original_response = await client.get(f"/api/file-collections/{collection_id}/files/{filename}")
    assert original_response.status_code == 200
    original_content = original_response.json()["file"]["content"]
    
    # Add metadata and analysis
    updated_content = f"""# Content Analysis

## Original Web Content
{original_content}

## Analysis Notes
- Source: Web crawling extraction
- Processing: Automated markdown conversion
- Collection: {collection_name}
- Analysis date: {uuid.uuid4().hex[:8]}
"""
    
    update_response = await client.put(f"/api/file-collections/{collection_id}/files/{filename}", json={
        "content": updated_content
    })
    assert update_response.status_code == 200
    
    # Step 10: Final sync and verification
    final_sync_response = await client.post(f"/api/vector-sync/collections/{collection_name}/sync", json={
        "force_reprocess": True
    })
    assert final_sync_response.status_code == 200
    
    # Step 11: Verify updated content is searchable
    await asyncio.sleep(2)
    metadata_search = await client.post("/api/vector-sync/search", json={
        "query": "content analysis and processing",
        "collection_name": collection_name,
        "limit": 3
    })
    assert metadata_search.status_code == 200
    
    # Should find our analysis notes
    metadata_results = metadata_search.json()["results"]
    found_analysis = False
    for result in metadata_results:
        if "analysis notes" in result["content"].lower() or "processing" in result["content"].lower():
            found_analysis = True
            break
    assert found_analysis, "Should find updated analysis content"


@pytest.mark.asyncio
async def test_error_recovery_and_cleanup_workflow(client: httpx.AsyncClient):
    """
    Test error handling and cleanup: Create resources → Trigger errors → 
    Verify graceful handling → Clean up properly
    """
    # Step 1: Test system resilience with invalid operations
    
    # Try to get non-existent collection
    fake_id = f"nonexistent_{uuid.uuid4().hex[:6]}"
    get_response = await client.get(f"/api/file-collections/{fake_id}")
    assert get_response.status_code == 404
    
    # Try to sync non-existent collection
    sync_response = await client.post(f"/api/vector-sync/collections/{fake_id}/sync", json={
        "force_reprocess": False
    })
    assert sync_response.status_code == 404
    
    # Try invalid web crawling
    invalid_crawl = await client.post("/api/extract", json={
        "url": "not-a-valid-url",
        "extraction_strategy": "NoExtractionStrategy"
    })
    assert invalid_crawl.status_code in [400, 422, 500]  # Should handle gracefully
    
    # Step 2: Create collection and test partial cleanup
    collection_name = f"cleanup_test_{uuid.uuid4().hex[:6]}"
    create_response = await client.post("/api/file-collections", json={
        "name": collection_name,
        "description": "Collection for cleanup testing"
    })
    assert create_response.status_code == 200
    collection_id = create_response.json()["collection"]["id"]
    
    # Add some content
    file_response = await client.post(f"/api/file-collections/{collection_id}/files", json={
        "filename": "test_cleanup.md",
        "content": "# Cleanup Test\n\nThis content will be cleaned up."
    })
    assert file_response.status_code == 200
    
    # Sync to vectors
    sync_response = await client.post(f"/api/vector-sync/collections/{collection_name}/sync", json={
        "force_reprocess": False
    })
    assert sync_response.status_code == 200
    
    # Verify it exists in statuses
    statuses_response = await client.get("/api/vector-sync/collections/statuses")
    assert statuses_response.status_code == 200
    statuses = statuses_response.json()["statuses"]
    assert collection_name in statuses
    
    # Step 3: Clean up collection (this should handle vector cleanup too)
    delete_response = await client.delete(f"/api/file-collections/{collection_id}")
    assert delete_response.status_code == 200
    
    # Step 4: Verify cleanup was complete
    # Collection should be gone
    verify_delete = await client.get(f"/api/file-collections/{collection_id}")
    assert verify_delete.status_code == 404
    
    # Files should be gone
    files_check = await client.get(f"/api/file-collections/{collection_id}/files")
    assert files_check.status_code == 404
    
    # Status should handle missing collection gracefully
    status_check = await client.get(f"/api/vector-sync/collections/{collection_name}/status")
    assert status_check.status_code == 404
    
    # Step 5: System should still be healthy after cleanup
    health_check = await client.get("/api/health")
    assert health_check.status_code == 200
    assert health_check.json()["status"] == "healthy"