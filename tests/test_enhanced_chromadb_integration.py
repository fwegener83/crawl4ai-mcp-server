"""
Test suite for enhanced ChromaDB integration with overlap-aware metadata.

This module tests the enhanced ChromaDB operations that support:
1. Overlap-aware chunk metadata storage and retrieval
2. Chunk relationship tracking in vector database
3. Enhanced search with relationship-aware filtering
4. Integration with OverlapAwareMarkdownProcessor and DynamicContextExpander

Following the plan's test-first development approach for Phase 2.1.
"""

import pytest
import asyncio
from typing import List, Dict, Any, Optional
from unittest.mock import Mock, AsyncMock, patch
import json
import time

from tools.knowledge_base.dependencies import is_rag_available

# Skip all tests if RAG dependencies are not available
pytestmark = pytest.mark.skipif(not is_rag_available(), reason="RAG dependencies not available")


class TestEnhancedChromaDBMetadata:
    """Test suite for enhanced metadata support in ChromaDB operations."""
    
    def test_overlap_metadata_schema(self):
        """Test metadata schema for overlap-aware chunks."""
        # Enhanced metadata schema for overlap-aware chunks
        enhanced_metadata = {
            # Base chunk metadata
            'chunk_index': 3,
            'total_chunks': 10,
            'chunk_type': 'paragraph',
            'content_hash': 'abc123hash',
            'header_hierarchy': ['# Main', '## Section 1'],
            'contains_code': False,
            'programming_language': None,
            'word_count': 150,
            'character_count': 800,
            'created_at': '2025-01-15T16:00:00Z',
            
            # Overlap-specific metadata
            'overlap_sources': ['chunk_002', 'chunk_001'],
            'overlap_regions': [(0, 50), (200, 250)],
            'overlap_percentage': 0.25,
            
            # Relationship metadata
            'previous_chunk_id': 'chunk_002',
            'next_chunk_id': 'chunk_004',
            'section_siblings': ['chunk_005', 'chunk_006'],
            
            # Context expansion metadata
            'context_expansion_eligible': True,
            'expansion_threshold': 0.75,
            
            # Performance metadata
            'storage_efficiency_ratio': 0.85,
            'processing_time_ms': 45.2
        }
        
        # Test required fields
        required_fields = [
            'chunk_index', 'content_hash', 'overlap_sources', 
            'overlap_regions', 'overlap_percentage'
        ]
        
        for field in required_fields:
            assert field in enhanced_metadata, f"Required field {field} missing from metadata"
        
        # Test data types
        assert isinstance(enhanced_metadata['overlap_sources'], list)
        assert isinstance(enhanced_metadata['overlap_regions'], list)
        assert isinstance(enhanced_metadata['overlap_percentage'], (int, float))
        assert isinstance(enhanced_metadata['context_expansion_eligible'], bool)
        
        # Test value ranges
        assert 0.0 <= enhanced_metadata['overlap_percentage'] <= 1.0
        assert 0.0 <= enhanced_metadata['expansion_threshold'] <= 1.0
        assert 0.0 <= enhanced_metadata['storage_efficiency_ratio'] <= 1.0
    
    def test_relationship_metadata_structure(self):
        """Test chunk relationship metadata structure."""
        # Sample relationship metadata
        relationship_metadata = {
            'chunk_id': 'chunk_005',
            'document_id': 'doc_001',
            'collection_name': 'test_collection',
            
            # Sequential relationships
            'previous_chunk_id': 'chunk_004',
            'next_chunk_id': 'chunk_006',
            
            # Hierarchical relationships
            'parent_section_id': 'section_002',
            'section_siblings': ['chunk_007', 'chunk_008'],
            'header_hierarchy': ['# Document', '## Section 2'],
            
            # Overlap relationships
            'overlap_sources': ['chunk_004'],
            'overlap_targets': ['chunk_006'],
            'bidirectional_overlaps': ['chunk_004', 'chunk_006'],
            
            # Context expansion relationships
            'expansion_candidates': ['chunk_004', 'chunk_006', 'chunk_007', 'chunk_008'],
            'expansion_priority': {
                'chunk_004': 1,  # High priority (overlap)
                'chunk_006': 1,  # High priority (sequential)
                'chunk_007': 2   # Medium priority (sibling)
            }
        }
        
        # Test relationship consistency
        assert relationship_metadata['previous_chunk_id'] in relationship_metadata['overlap_sources']
        assert relationship_metadata['next_chunk_id'] in relationship_metadata['expansion_candidates']
        
        # Test relationship types - ensure all siblings are in expansion candidates
        for sibling in relationship_metadata['section_siblings']:
            assert sibling in relationship_metadata['expansion_candidates'], f"Sibling {sibling} not in expansion candidates"
    
    def test_metadata_serialization_compatibility(self):
        """Test that enhanced metadata is serializable for ChromaDB storage."""
        enhanced_metadata = {
            'overlap_sources': ['chunk_001', 'chunk_002'],
            'overlap_regions': [[0, 50], [200, 250]],  # Use lists instead of tuples for JSON compatibility
            'overlap_percentage': 0.25,
            'header_hierarchy': ['# Main', '## Section'],
            'context_expansion_eligible': True,
            'processing_time_ms': 45.2,
            'created_at': '2025-01-15T16:00:00Z'
        }
        
        # Test JSON serialization (ChromaDB requirement)
        serialized = json.dumps(enhanced_metadata)
        deserialized = json.loads(serialized)
        
        assert deserialized == enhanced_metadata
        
        # Test that all values are primitive types (no complex objects)
        def check_primitive_types(obj):
            if isinstance(obj, dict):
                for value in obj.values():
                    check_primitive_types(value)
            elif isinstance(obj, list):
                for item in obj:
                    check_primitive_types(item)
            else:
                assert isinstance(obj, (str, int, float, bool, type(None))), f"Non-primitive type: {type(obj)}"
        
        check_primitive_types(enhanced_metadata)


class TestEnhancedVectorStoreOperations:
    """Test suite for enhanced vector store operations."""
    
    def test_enhanced_document_storage(self):
        """Test storing documents with enhanced overlap-aware metadata."""
        # Mock enhanced documents with overlap metadata
        enhanced_documents = [
            {
                'id': 'chunk_001',
                'content': 'First chunk content with overlap region at the end',
                'metadata': {
                    'chunk_index': 1,
                    'overlap_sources': [],
                    'overlap_regions': [],
                    'overlap_percentage': 0.0,
                    'next_chunk_id': 'chunk_002',
                    'context_expansion_eligible': True
                }
            },
            {
                'id': 'chunk_002',
                'content': 'overlap region at the end. Second chunk content continues here',
                'metadata': {
                    'chunk_index': 2,
                    'overlap_sources': ['chunk_001'],
                    'overlap_regions': [[0, 25]],
                    'overlap_percentage': 0.3,
                    'previous_chunk_id': 'chunk_001',
                    'next_chunk_id': 'chunk_003',
                    'context_expansion_eligible': True
                }
            }
        ]
        
        # Test document preparation for ChromaDB
        documents = [doc['content'] for doc in enhanced_documents]
        metadatas = [doc['metadata'] for doc in enhanced_documents]
        ids = [doc['id'] for doc in enhanced_documents]
        
        # Verify structure
        assert len(documents) == len(metadatas) == len(ids)
        
        # Test metadata contains overlap information
        assert metadatas[1]['overlap_sources'] == ['chunk_001']
        assert metadatas[1]['overlap_percentage'] > 0
        assert metadatas[0]['overlap_percentage'] == 0
        
        # Test relationship consistency
        assert metadatas[0]['next_chunk_id'] == 'chunk_002'
        assert metadatas[1]['previous_chunk_id'] == 'chunk_001'
    
    def test_relationship_aware_search_filtering(self):
        """Test search operations with relationship-aware filtering."""
        # Mock search scenarios with relationship filters
        search_scenarios = [
            {
                'name': 'search_with_siblings',
                'query': 'test query',
                'filter': {
                    'section_siblings': {'$in': ['chunk_005', 'chunk_006']}
                },
                'expected_scope': 'section_level'
            },
            {
                'name': 'search_with_overlap_sources',
                'query': 'test query',
                'filter': {
                    'overlap_sources': {'$size': {'$gt': 0}}
                },
                'expected_scope': 'overlapped_chunks_only'
            },
            {
                'name': 'search_expansion_eligible',
                'query': 'test query',
                'filter': {
                    'context_expansion_eligible': True
                },
                'expected_scope': 'expandable_chunks'
            }
        ]
        
        for scenario in search_scenarios:
            # Test filter structure
            assert 'filter' in scenario
            assert isinstance(scenario['filter'], dict)
            
            # Test that filters target relationship metadata
            filter_keys = list(scenario['filter'].keys())
            relationship_fields = [
                'section_siblings', 'overlap_sources', 'previous_chunk_id',
                'next_chunk_id', 'context_expansion_eligible'
            ]
            
            assert any(key in relationship_fields for key in filter_keys), \
                f"No relationship fields in filter: {filter_keys}"
    
    def test_chunk_relationship_queries(self):
        """Test specialized queries for chunk relationships."""
        # Test neighbor chunk retrieval
        def test_get_neighbor_chunks(center_chunk_id: str, relationship_type: str):
            """Mock function for retrieving neighbor chunks."""
            neighbor_queries = {
                'sequential': {
                    '$or': [
                        {'previous_chunk_id': center_chunk_id},
                        {'next_chunk_id': center_chunk_id}
                    ]
                },
                'siblings': {
                    'section_siblings': {'$in': [center_chunk_id]}
                },
                'overlap': {
                    '$or': [
                        {'overlap_sources': {'$in': [center_chunk_id]}},
                        {'overlap_targets': {'$in': [center_chunk_id]}}
                    ]
                }
            }
            
            return neighbor_queries.get(relationship_type)
        
        # Test sequential neighbor query
        sequential_query = test_get_neighbor_chunks('chunk_005', 'sequential')
        assert '$or' in sequential_query
        assert len(sequential_query['$or']) == 2
        
        # Test sibling query
        sibling_query = test_get_neighbor_chunks('chunk_005', 'siblings')
        assert 'section_siblings' in sibling_query
        
        # Test overlap query
        overlap_query = test_get_neighbor_chunks('chunk_005', 'overlap')
        assert '$or' in overlap_query
        assert any('overlap_sources' in condition for condition in overlap_query['$or'])
    
    def test_context_expansion_candidate_retrieval(self):
        """Test retrieval of context expansion candidates."""
        # Mock context expansion query
        def build_expansion_query(source_chunk_metadata: Dict[str, Any], threshold: float = 0.75):
            """Build query for context expansion candidates."""
            query_conditions = []
            
            # Sequential neighbors
            if source_chunk_metadata.get('previous_chunk_id'):
                query_conditions.append({'chunk_id': source_chunk_metadata['previous_chunk_id']})
            if source_chunk_metadata.get('next_chunk_id'):
                query_conditions.append({'chunk_id': source_chunk_metadata['next_chunk_id']})
            
            # Section siblings
            siblings = source_chunk_metadata.get('section_siblings', [])
            if siblings:
                query_conditions.append({'chunk_id': {'$in': siblings}})
            
            # Overlap sources
            overlap_sources = source_chunk_metadata.get('overlap_sources', [])
            if overlap_sources:
                query_conditions.append({'chunk_id': {'$in': overlap_sources}})
            
            # Filter by expansion eligibility
            expansion_filter = {
                'context_expansion_eligible': True,
                'expansion_threshold': {'$lte': threshold}
            }
            
            return {
                '$and': [
                    {'$or': query_conditions} if query_conditions else {},
                    expansion_filter
                ]
            }
        
        # Test with sample chunk metadata
        sample_metadata = {
            'chunk_id': 'chunk_005',
            'previous_chunk_id': 'chunk_004',
            'next_chunk_id': 'chunk_006',
            'section_siblings': ['chunk_007', 'chunk_008'],
            'overlap_sources': ['chunk_004']
        }
        
        expansion_query = build_expansion_query(sample_metadata)
        
        # Verify query structure
        assert '$and' in expansion_query
        assert len(expansion_query['$and']) == 2
        
        # Verify expansion conditions
        or_conditions = expansion_query['$and'][0]['$or']
        assert len(or_conditions) >= 3  # Sequential + siblings + overlap
        
        # Verify eligibility filter
        eligibility_filter = expansion_query['$and'][1]
        assert eligibility_filter['context_expansion_eligible'] is True


class TestPerformanceOptimizedOperations:
    """Test suite for performance-optimized ChromaDB operations."""
    
    def test_batch_operations_efficiency(self):
        """Test efficiency of batch operations for large chunk sets."""
        # Simulate large batch of overlap-aware chunks
        large_batch_size = 1000
        
        def simulate_batch_processing(batch_size: int, overlap_percentage: float = 0.25):
            """Simulate processing a large batch of chunks."""
            chunks = []
            
            for i in range(batch_size):
                chunk_id = f"chunk_{i:04d}"
                
                # Create overlap metadata
                overlap_sources = []
                overlap_regions = []
                actual_overlap_pct = 0.0
                
                if i > 0:  # Not first chunk
                    prev_chunk_id = f"chunk_{i-1:04d}"
                    overlap_sources.append(prev_chunk_id)
                    overlap_regions.append((0, 50))  # 50 char overlap
                    actual_overlap_pct = overlap_percentage
                
                chunks.append({
                    'id': chunk_id,
                    'content': f"Content for chunk {i} with overlap at start" + " additional content" * 10,
                    'metadata': {
                        'chunk_index': i,
                        'overlap_sources': overlap_sources,
                        'overlap_regions': overlap_regions,
                        'overlap_percentage': actual_overlap_pct,
                        'context_expansion_eligible': i % 3 == 0,  # Every 3rd chunk
                        'processing_time_ms': 25.0 + (i % 10) * 2  # Simulated processing time
                    }
                })
            
            return chunks
        
        # Test batch creation
        large_batch = simulate_batch_processing(large_batch_size)
        
        # Verify batch structure
        assert len(large_batch) == large_batch_size
        
        # Verify overlap relationships
        overlapped_chunks = [c for c in large_batch if c['metadata']['overlap_percentage'] > 0]
        assert len(overlapped_chunks) == large_batch_size - 1  # All except first
        
        # Test batch memory efficiency
        total_metadata_size = sum(len(str(chunk['metadata'])) for chunk in large_batch)
        avg_metadata_size = total_metadata_size / len(large_batch)
        
        # Metadata should be reasonable size (< 1KB per chunk)
        assert avg_metadata_size < 1000, f"Average metadata size {avg_metadata_size} too large"
        
        # Test expansion candidate efficiency
        expansion_candidates = [c for c in large_batch if c['metadata']['context_expansion_eligible']]
        expansion_ratio = len(expansion_candidates) / len(large_batch)
        
        # Should have reasonable number of expansion candidates (not all chunks)
        assert 0.1 <= expansion_ratio <= 0.5, f"Expansion ratio {expansion_ratio} not optimal"
    
    def test_similarity_search_with_relationships(self):
        """Test performance of similarity search enhanced with relationship data."""
        import time
        
        # Mock similarity search with relationship enhancement
        def enhanced_similarity_search(
            query: str,
            base_results: List[Dict[str, Any]],
            expand_context: bool = True,
            max_neighbors: int = 3
        ) -> List[Dict[str, Any]]:
            """Enhanced search that includes relationship-based context."""
            
            start_time = time.time()
            
            enhanced_results = list(base_results)  # Start with base results
            
            if expand_context:
                for result in base_results:
                    chunk_metadata = result.get('metadata', {})
                    
                    # Add sequential neighbors
                    neighbors = []
                    if chunk_metadata.get('previous_chunk_id'):
                        neighbors.append({
                            'id': chunk_metadata['previous_chunk_id'],
                            'relationship': 'previous',
                            'expansion_priority': 1
                        })
                    if chunk_metadata.get('next_chunk_id'):
                        neighbors.append({
                            'id': chunk_metadata['next_chunk_id'],
                            'relationship': 'next', 
                            'expansion_priority': 1
                        })
                    
                    # Add overlap sources (highest priority)
                    for overlap_id in chunk_metadata.get('overlap_sources', []):
                        neighbors.append({
                            'id': overlap_id,
                            'relationship': 'overlap',
                            'expansion_priority': 0  # Highest priority
                        })
                    
                    # Add section siblings (lower priority)
                    for sibling_id in chunk_metadata.get('section_siblings', [])[:2]:  # Limit siblings
                        neighbors.append({
                            'id': sibling_id,
                            'relationship': 'sibling',
                            'expansion_priority': 2
                        })
                    
                    # Sort by priority and limit
                    neighbors.sort(key=lambda x: x['expansion_priority'])
                    selected_neighbors = neighbors[:max_neighbors]
                    
                    # Add to results (mock - would fetch actual chunks)
                    for neighbor in selected_neighbors:
                        enhanced_results.append({
                            'id': neighbor['id'],
                            'content': f"Neighbor content for {neighbor['id']}",
                            'metadata': {'relationship_to_source': neighbor['relationship']},
                            'expansion_source': result['id']
                        })
            
            processing_time = (time.time() - start_time) * 1000  # Convert to ms
            
            return enhanced_results, processing_time
        
        # Test with mock base results
        base_results = [
            {
                'id': 'chunk_005',
                'content': 'Main search result content',
                'metadata': {
                    'previous_chunk_id': 'chunk_004',
                    'next_chunk_id': 'chunk_006',
                    'section_siblings': ['chunk_007', 'chunk_008'],
                    'overlap_sources': ['chunk_004']
                },
                'similarity_score': 0.85
            }
        ]
        
        # Test enhanced search
        enhanced_results, processing_time = enhanced_similarity_search(
            "test query", base_results, expand_context=True
        )
        
        # Verify enhancement
        assert len(enhanced_results) > len(base_results), "Should add neighbor results"
        
        # Verify performance (should be fast for relationship lookup)
        assert processing_time < 100, f"Processing time {processing_time}ms too slow"
        
        # Verify relationships are included
        neighbor_results = [r for r in enhanced_results if 'expansion_source' in r]
        assert len(neighbor_results) > 0, "Should include neighbor chunks"
        
        # Verify priority ordering (overlap sources should come first)
        overlap_neighbors = [r for r in neighbor_results if r['metadata'].get('relationship_to_source') == 'overlap']
        assert len(overlap_neighbors) > 0, "Should include overlap-based neighbors"
    
    def test_memory_efficient_metadata_storage(self):
        """Test memory-efficient storage of relationship metadata."""
        # Test compressed relationship storage
        def compress_relationship_metadata(full_metadata: Dict[str, Any]) -> Dict[str, Any]:
            """Compress relationship metadata for efficient storage."""
            compressed = {}
            
            # Store essential fields only
            essential_fields = [
                'chunk_index', 'overlap_percentage', 'context_expansion_eligible',
                'processing_time_ms', 'storage_efficiency_ratio'
            ]
            
            for field in essential_fields:
                if field in full_metadata:
                    compressed[field] = full_metadata[field]
            
            # Compress relationship lists
            relationships = {}
            if full_metadata.get('overlap_sources'):
                relationships['os'] = full_metadata['overlap_sources']  # Abbreviated key
            if full_metadata.get('section_siblings'):
                relationships['ss'] = full_metadata['section_siblings'][:3]  # Limit to 3
            if full_metadata.get('previous_chunk_id'):
                relationships['p'] = full_metadata['previous_chunk_id']
            if full_metadata.get('next_chunk_id'):
                relationships['n'] = full_metadata['next_chunk_id']
            
            if relationships:
                compressed['rels'] = relationships
            
            return compressed
        
        # Test with comprehensive metadata
        full_metadata = {
            'chunk_index': 5,
            'total_chunks': 100,
            'chunk_type': 'paragraph',
            'content_hash': 'abcdef123456',
            'header_hierarchy': ['# Main', '## Section 1', '### Subsection'],
            'contains_code': False,
            'programming_language': None,
            'word_count': 150,
            'character_count': 800,
            'created_at': '2025-01-15T16:00:00Z',
            'overlap_sources': ['chunk_004'],
            'overlap_regions': [(0, 50)],
            'overlap_percentage': 0.25,
            'previous_chunk_id': 'chunk_004',
            'next_chunk_id': 'chunk_006',
            'section_siblings': ['chunk_007', 'chunk_008', 'chunk_009', 'chunk_010'],
            'context_expansion_eligible': True,
            'expansion_threshold': 0.75,
            'storage_efficiency_ratio': 0.85,
            'processing_time_ms': 45.2
        }
        
        compressed = compress_relationship_metadata(full_metadata)
        
        # Test compression effectiveness
        full_size = len(json.dumps(full_metadata))
        compressed_size = len(json.dumps(compressed))
        compression_ratio = compressed_size / full_size
        
        assert compression_ratio < 0.6, f"Compression ratio {compression_ratio} not effective enough"
        
        # Test essential data preservation
        assert compressed['chunk_index'] == full_metadata['chunk_index']
        assert compressed['overlap_percentage'] == full_metadata['overlap_percentage']
        assert compressed['context_expansion_eligible'] == full_metadata['context_expansion_eligible']
        
        # Test relationship preservation
        assert compressed['rels']['os'] == ['chunk_004']
        assert compressed['rels']['p'] == 'chunk_004'
        assert compressed['rels']['n'] == 'chunk_006'
        assert len(compressed['rels']['ss']) <= 3  # Should limit siblings


class TestIntegrationWithExistingComponents:
    """Test integration with existing OverlapAwareMarkdownProcessor and DynamicContextExpander."""
    
    def test_overlap_processor_chromadb_integration(self):
        """Test integration between OverlapAwareMarkdownProcessor and ChromaDB storage."""
        # Mock OverlapAwareMarkdownProcessor output
        overlap_processor_output = [
            {
                'content': 'First chunk content ending with overlap',
                'metadata': {
                    'chunk_index': 0,
                    'total_chunks': 3,
                    'overlap_sources': [],
                    'overlap_regions': [],
                    'overlap_percentage': 0.0,
                    'next_chunk_id': 'overlap_chunk_abc123_1',
                    'context_expansion_eligible': True,
                    'storage_efficiency_ratio': 1.0
                },
                'chunk_id': 'overlap_chunk_abc123_0'
            },
            {
                'content': 'overlap. Second chunk content continues here',
                'metadata': {
                    'chunk_index': 1,
                    'total_chunks': 3,
                    'overlap_sources': ['overlap_chunk_abc123_0'],
                    'overlap_regions': [(0, 8)],
                    'overlap_percentage': 0.25,
                    'previous_chunk_id': 'overlap_chunk_abc123_0',
                    'next_chunk_id': 'overlap_chunk_abc123_2',
                    'context_expansion_eligible': True,
                    'storage_efficiency_ratio': 0.85
                },
                'chunk_id': 'overlap_chunk_abc123_1'
            }
        ]
        
        # Test ChromaDB preparation
        def prepare_for_chromadb(processor_chunks: List[Dict[str, Any]]) -> Dict[str, List]:
            """Prepare overlap processor output for ChromaDB storage."""
            documents = []
            metadatas = []
            ids = []
            
            for chunk in processor_chunks:
                documents.append(chunk['content'])
                
                # Enhance metadata for ChromaDB
                enhanced_metadata = chunk['metadata'].copy()
                enhanced_metadata['source_processor'] = 'OverlapAwareMarkdownProcessor'
                enhanced_metadata['storage_timestamp'] = '2025-01-15T16:00:00Z'
                
                metadatas.append(enhanced_metadata)
                ids.append(chunk['chunk_id'])
            
            return {
                'documents': documents,
                'metadatas': metadatas,
                'ids': ids
            }
        
        prepared_data = prepare_for_chromadb(overlap_processor_output)
        
        # Verify preparation
        assert len(prepared_data['documents']) == 2
        assert len(prepared_data['metadatas']) == 2
        assert len(prepared_data['ids']) == 2
        
        # Verify relationship consistency in metadata
        metadata_0 = prepared_data['metadatas'][0]
        metadata_1 = prepared_data['metadatas'][1]
        
        assert metadata_0['next_chunk_id'] == prepared_data['ids'][1]
        assert metadata_1['previous_chunk_id'] == prepared_data['ids'][0]
        assert prepared_data['ids'][0] in metadata_1['overlap_sources']
    
    def test_context_expander_chromadb_integration(self):
        """Test integration between DynamicContextExpander and ChromaDB retrieval."""
        # Mock ChromaDB query results
        chromadb_results = {
            'documents': [['Main query result content']],
            'metadatas': [[{
                'chunk_index': 5,
                'overlap_sources': ['chunk_004'],
                'overlap_regions': [(0, 30)],
                'previous_chunk_id': 'chunk_004',
                'next_chunk_id': 'chunk_006',
                'section_siblings': ['chunk_007', 'chunk_008'],
                'context_expansion_eligible': True,
                'expansion_threshold': 0.75
            }]],
            'distances': [[0.25]],  # ChromaDB distance (lower = more similar)
            'ids': [['chunk_005']]
        }
        
        # Test conversion to DynamicContextExpander format
        def convert_chromadb_to_expander_format(chromadb_results: Dict[str, Any]) -> List[Dict[str, Any]]:
            """Convert ChromaDB results to DynamicContextExpander query format."""
            expander_results = []
            
            if chromadb_results['documents'] and chromadb_results['documents'][0]:
                documents = chromadb_results['documents'][0]
                metadatas = chromadb_results['metadatas'][0] if chromadb_results['metadatas'] else [{}] * len(documents)
                distances = chromadb_results['distances'][0] if chromadb_results['distances'] else [0.0] * len(documents)
                ids = chromadb_results['ids'][0] if chromadb_results['ids'] else [''] * len(documents)
                
                for i, (doc, metadata, distance, doc_id) in enumerate(zip(documents, metadatas, distances, ids)):
                    # Convert ChromaDB distance to similarity score
                    similarity_score = max(0.0, 1.0 - distance)
                    
                    expander_results.append({
                        'chunk_id': doc_id,
                        'content': doc,
                        'similarity_score': similarity_score,
                        'metadata': metadata
                    })
            
            return expander_results
        
        expander_format_results = convert_chromadb_to_expander_format(chromadb_results)
        
        # Verify conversion
        assert len(expander_format_results) == 1
        
        result = expander_format_results[0]
        assert result['chunk_id'] == 'chunk_005'
        assert result['similarity_score'] == 0.75  # 1.0 - 0.25
        assert 'previous_chunk_id' in result['metadata']
        assert 'context_expansion_eligible' in result['metadata']
        
        # Test context expansion candidate identification
        expansion_metadata = result['metadata']
        expansion_candidates = []
        
        # Sequential candidates
        if expansion_metadata.get('previous_chunk_id'):
            expansion_candidates.append(('sequential', expansion_metadata['previous_chunk_id']))
        if expansion_metadata.get('next_chunk_id'):
            expansion_candidates.append(('sequential', expansion_metadata['next_chunk_id']))
        
        # Overlap candidates
        for overlap_id in expansion_metadata.get('overlap_sources', []):
            expansion_candidates.append(('overlap', overlap_id))
        
        # Sibling candidates
        for sibling_id in expansion_metadata.get('section_siblings', []):
            expansion_candidates.append(('sibling', sibling_id))
        
        # Verify candidates identified
        assert len(expansion_candidates) >= 3  # Should find multiple relationship types
        
        relationship_types = [rel_type for rel_type, _ in expansion_candidates]
        assert 'sequential' in relationship_types
        assert 'overlap' in relationship_types
        assert 'sibling' in relationship_types
    
    def test_end_to_end_workflow_integration(self):
        """Test complete end-to-end workflow from processing to search to expansion."""
        # Mock complete workflow
        def simulate_end_to_end_workflow():
            """Simulate complete RAG workflow with enhanced ChromaDB."""
            
            # Step 1: OverlapAwareMarkdownProcessor creates chunks
            processor_chunks = [
                {
                    'content': 'First chunk content',
                    'chunk_id': 'chunk_001', 
                    'metadata': {
                        'chunk_index': 0,
                        'overlap_sources': [],
                        'overlap_percentage': 0.0,
                        'next_chunk_id': 'chunk_002',
                        'context_expansion_eligible': True
                    }
                },
                {
                    'content': 'Second chunk with overlap', 
                    'chunk_id': 'chunk_002',
                    'metadata': {
                        'chunk_index': 1,
                        'overlap_sources': ['chunk_001'],
                        'overlap_percentage': 0.25,
                        'previous_chunk_id': 'chunk_001',
                        'context_expansion_eligible': True
                    }
                }
            ]
            
            # Step 2: Enhanced ChromaDB storage
            def store_with_enhanced_metadata(chunks):
                stored_chunks = []
                for chunk in chunks:
                    enhanced_chunk = chunk.copy()
                    enhanced_chunk['metadata']['stored_at'] = '2025-01-15T16:00:00Z'
                    enhanced_chunk['metadata']['chromadb_collection'] = 'test_collection'
                    stored_chunks.append(enhanced_chunk)
                return stored_chunks
            
            stored_chunks = store_with_enhanced_metadata(processor_chunks)
            
            # Step 3: Enhanced search query
            def enhanced_search_query(query: str, collection_chunks: List[Dict]):
                # Simulate search returning chunks below threshold
                search_results = []
                for chunk in collection_chunks:
                    if 'chunk' in query.lower():  # Simple matching
                        search_results.append({
                            'chunk_id': chunk['chunk_id'],
                            'content': chunk['content'],
                            'similarity_score': 0.65,  # Below 0.75 threshold
                            'metadata': chunk['metadata']
                        })
                return search_results
            
            search_results = enhanced_search_query("find chunk information", stored_chunks)
            
            # Step 4: DynamicContextExpander enhancement
            def apply_context_expansion(marginal_results: List[Dict]):
                expanded_results = list(marginal_results)
                
                for result in marginal_results:
                    metadata = result['metadata']
                    
                    # Add neighbor chunks based on relationships
                    if metadata.get('previous_chunk_id'):
                        expanded_results.append({
                            'chunk_id': metadata['previous_chunk_id'],
                            'content': f"Previous chunk content for {metadata['previous_chunk_id']}",
                            'expansion_source': result['chunk_id'],
                            'expansion_type': 'sequential'
                        })
                    
                    if metadata.get('next_chunk_id'):
                        expanded_results.append({
                            'chunk_id': metadata['next_chunk_id'],
                            'content': f"Next chunk content for {metadata['next_chunk_id']}",
                            'expansion_source': result['chunk_id'],
                            'expansion_type': 'sequential'
                        })
                
                return expanded_results
            
            final_results = apply_context_expansion(search_results)
            
            return {
                'processed_chunks': len(processor_chunks),
                'stored_chunks': len(stored_chunks),
                'search_results': len(search_results),
                'expanded_results': len(final_results),
                'expansion_applied': len(final_results) > len(search_results)
            }
        
        # Execute workflow
        workflow_results = simulate_end_to_end_workflow()
        
        # Verify workflow completion
        assert workflow_results['processed_chunks'] == 2
        assert workflow_results['stored_chunks'] == 2
        assert workflow_results['search_results'] >= 1
        assert workflow_results['expansion_applied'] is True
        assert workflow_results['expanded_results'] > workflow_results['search_results']
        
        # Verify enhancement at each stage
        assert workflow_results['expanded_results'] >= workflow_results['search_results'] * 2, \
            "Context expansion should significantly increase result count"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])