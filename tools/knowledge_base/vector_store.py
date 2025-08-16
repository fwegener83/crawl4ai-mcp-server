"""Vector store implementation using ChromaDB for RAG functionality."""
import os
import logging
from typing import Dict, Any, List, Optional, Union
from .dependencies import rag_deps, ensure_rag_available

logger = logging.getLogger(__name__)


class VectorStore:
    """ChromaDB-based vector store for document embeddings."""
    
    def __init__(
        self,
        persist_directory: Optional[str] = None,
        collection_name: str = "crawl4ai_documents"
    ):
        """Initialize the vector store.
        
        Args:
            persist_directory: Directory to persist the database. If None, uses memory only.
            collection_name: Name of the collection to use.
        """
        ensure_rag_available()
        
        self.persist_directory = persist_directory or os.getenv("RAG_DB_PATH", "./rag_db")
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        
        self._initialize_client()
        logger.info(f"VectorStore initialized with directory: {self.persist_directory}")
    
    def _initialize_client(self):
        """Initialize ChromaDB client."""
        try:
            if self.persist_directory:
                # Expand user path (~) if present
                expanded_path = os.path.expanduser(self.persist_directory)
                
                try:
                    # Ensure directory exists
                    os.makedirs(expanded_path, exist_ok=True)
                    chromadb = rag_deps.get_component('chromadb')
                    self.client = chromadb.PersistentClient(path=expanded_path)
                    self.persist_directory = expanded_path  # Update with expanded path
                except OSError as e:
                    if e.errno == 30:  # Read-only file system
                        logger.warning(f"Cannot write to {expanded_path} (read-only filesystem). Falling back to /tmp.")
                        fallback_path = f"/tmp/crawl4ai-rag-db"
                        os.makedirs(fallback_path, exist_ok=True)
                        chromadb = rag_deps.get_component('chromadb')
                        self.client = chromadb.PersistentClient(path=fallback_path)
                        self.persist_directory = fallback_path
                    else:
                        raise
            else:
                # In-memory client for testing
                chromadb = rag_deps.get_component('chromadb')
                self.client = chromadb.Client()
            
            logger.info(f"ChromaDB client initialized successfully at {self.persist_directory if self.persist_directory else 'memory'}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {str(e)}")
            raise
    
    def create_collection(self, collection_name: Optional[str] = None) -> Any:
        """Create a new collection.
        
        Args:
            collection_name: Name of the collection. Uses default if None.
            
        Returns:
            The created collection object.
            
        Raises:
            Exception: If collection creation fails.
        """
        name = collection_name or self.collection_name
        
        try:
            self.collection = self.client.create_collection(name=name)
            self.collection_name = name
            logger.info(f"Created collection: {name}")
            return self.collection
        except Exception as e:
            logger.error(f"Failed to create collection {name}: {str(e)}")
            raise
    
    def get_collection(self, collection_name: Optional[str] = None) -> Any:
        """Get an existing collection.
        
        Args:
            collection_name: Name of the collection. Uses default if None.
            
        Returns:
            The collection object.
            
        Raises:
            Exception: If collection doesn't exist or retrieval fails.
        """
        name = collection_name or self.collection_name
        
        try:
            self.collection = self.client.get_collection(name=name)
            self.collection_name = name
            logger.info(f"Retrieved collection: {name}")
            return self.collection
        except Exception as e:
            logger.error(f"Failed to get collection {name}: {str(e)}")
            raise
    
    def get_or_create_collection(self, collection_name: Optional[str] = None) -> Any:
        """Get or create a collection.
        
        Args:
            collection_name: Name of the collection. Uses default if None.
            
        Returns:
            The collection object.
        """
        name = collection_name or self.collection_name
        
        try:
            self.collection = self.client.get_or_create_collection(name=name)
            self.collection_name = name
            logger.info(f"Got or created collection: {name}")
            return self.collection
        except Exception as e:
            logger.error(f"Failed to get or create collection {name}: {str(e)}")
            raise
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
        embeddings: Optional[List[List[float]]] = None
    ) -> None:
        """Add documents to the collection with enhanced metadata support.
        
        Args:
            documents: List of document texts.
            metadatas: List of metadata dictionaries.
            ids: List of unique document IDs.
            embeddings: Pre-computed embeddings (optional).
            
        Raises:
            Exception: If adding documents fails.
        """
        if not self.collection:
            self.get_or_create_collection()
        
        try:
            # Enhance metadata for overlap-aware storage
            enhanced_metadatas = [
                self._enhance_metadata_for_storage(metadata) 
                for metadata in metadatas
            ]
            
            if embeddings:
                result = self.collection.add(
                    documents=documents,
                    metadatas=enhanced_metadatas,
                    ids=ids,
                    embeddings=embeddings
                )
            else:
                result = self.collection.add(
                    documents=documents,
                    metadatas=enhanced_metadatas,
                    ids=ids
                )
            
            # CRITICAL FIX: Force ChromaDB persistence/flush after adding documents
            try:
                # Some ChromaDB versions need explicit persistence
                if hasattr(self.client, 'persist'):
                    self.client.persist()
            except Exception:
                pass  # Persistence may not be supported in all ChromaDB versions
            
            logger.info(f"Added {len(documents)} documents to collection with enhanced metadata")
        except Exception as e:
            logger.error(f"Failed to add documents: {str(e)}")
            raise
    
    def query(
        self,
        query_texts: List[str],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        query_embeddings: Optional[List[List[float]]] = None
    ) -> Dict[str, Any]:
        """Query the collection for similar documents.
        
        Args:
            query_texts: List of query texts.
            n_results: Number of results to return.
            where: Filter conditions.
            query_embeddings: Pre-computed query embeddings (optional).
            
        Returns:
            Dictionary containing query results.
            
        Raises:
            Exception: If query fails.
        """
        if not self.collection:
            self.get_or_create_collection()
        
        try:
            if query_embeddings:
                results = self.collection.query(
                    query_embeddings=query_embeddings,
                    n_results=n_results,
                    where=where
                )
            else:
                results = self.collection.query(
                    query_texts=query_texts,
                    n_results=n_results,
                    where=where
                )
            
            logger.info(f"Query returned {len(results.get('documents', [[]])[0])} results")
            return results
        except Exception as e:
            logger.error(f"Failed to query collection: {str(e)}")
            raise
    
    def delete_collection(self, collection_name: Optional[str] = None) -> None:
        """Delete a collection.
        
        Args:
            collection_name: Name of the collection. Uses default if None.
            
        Raises:
            Exception: If deletion fails.
        """
        name = collection_name or self.collection_name
        
        try:
            self.client.delete_collection(name=name)
            if name == self.collection_name:
                self.collection = None
            logger.info(f"Deleted collection: {name}")
        except Exception as e:
            logger.error(f"Failed to delete collection {name}: {str(e)}")
            raise
    
    def list_collections(self) -> List[str]:
        """List all collections.
        
        Returns:
            List of collection names.
        """
        try:
            collections = self.client.list_collections()
            collection_names = [col.name for col in collections]
            logger.info(f"Found {len(collection_names)} collections")
            return collection_names
        except Exception as e:
            logger.error(f"Failed to list collections: {str(e)}")
            raise
    
    def count(self, collection_name: Optional[str] = None) -> int:
        """Count documents in collection.
        
        Args:
            collection_name: Name of the collection. Uses current if None.
            
        Returns:
            Number of documents in collection.
        """
        if collection_name and collection_name != self.collection_name:
            collection = self.client.get_collection(name=collection_name)
        else:
            if not self.collection:
                self.get_or_create_collection()
            collection = self.collection
        
        try:
            count = collection.count()
            logger.info(f"Collection has {count} documents")
            return count
        except Exception as e:
            logger.error(f"Failed to count documents: {str(e)}")
            raise
    
    def delete_documents(self, ids: List[str]) -> None:
        """Delete documents by their IDs.
        
        Args:
            ids: List of document IDs to delete.
            
        Raises:
            Exception: If deletion fails.
        """
        if not self.collection:
            self.get_or_create_collection()
        
        try:
            self.collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents from collection")
        except Exception as e:
            logger.error(f"Failed to delete documents: {str(e)}")
            raise
    
    def similarity_search(
        self,
        query: str,
        k: int = 5,
        score_threshold: float = 0.0,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents.
        
        Args:
            query: Query text.
            k: Number of results to return.
            score_threshold: Minimum similarity score.
            filter: Metadata filter conditions.
            
        Returns:
            List of similar documents with metadata and scores.
        """
        if not self.collection:
            self.get_or_create_collection()
        
        try:
            # Perform the filtered query
            results = self.collection.query(
                query_texts=[query],
                n_results=k,
                where=filter
            )
            
            # Convert ChromaDB results to standard format
            documents = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    raw_metadata = results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {}
                    metadata = self._deserialize_metadata_from_storage(raw_metadata)
                    distance = results['distances'][0][i] if results['distances'] and results['distances'][0] else 0.0
                    # ChromaDB can return negative cosine distances, handle appropriately
                    score = max(0.0, 1.0 - distance)  # Ensure non-negative scores
                    
                    # Apply score threshold
                    if score >= score_threshold:
                        documents.append({
                            'id': results['ids'][0][i] if results['ids'] and results['ids'][0] else '',
                            'content': doc,
                            'metadata': metadata,
                            'score': score
                        })
            
            logger.info(f"Similarity search returned {len(documents)} results")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to perform similarity search: {str(e)}")
            raise
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by ID.
        
        Args:
            doc_id: Document ID.
            
        Returns:
            Document data or None if not found.
        """
        if not self.collection:
            self.get_or_create_collection()
        
        try:
            results = self.collection.get(ids=[doc_id], include=['documents', 'metadatas'])
            
            if results['documents'] and results['documents'][0]:
                raw_metadata = results['metadatas'][0] if results['metadatas'] else {}
                metadata = self._deserialize_metadata_from_storage(raw_metadata)
                return {
                    'id': doc_id,
                    'content': results['documents'][0],
                    'metadata': metadata
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get document {doc_id}: {str(e)}")
            raise
    
    def update_documents(
        self,
        ids: List[str],
        documents: List[str],
        metadatas: List[Dict[str, Any]]
    ) -> None:
        """Update existing documents.
        
        Args:
            ids: List of document IDs to update.
            documents: List of new document texts.
            metadatas: List of new metadata dictionaries.
            
        Raises:
            Exception: If update fails.
        """
        if not self.collection:
            self.get_or_create_collection()
        
        try:
            # Enhance metadata for overlap-aware storage
            enhanced_metadatas = [
                self._enhance_metadata_for_storage(metadata) 
                for metadata in metadatas
            ]
            
            self.collection.update(
                ids=ids,
                documents=documents,
                metadatas=enhanced_metadatas
            )
            logger.info(f"Updated {len(ids)} documents in collection with enhanced metadata")
        except Exception as e:
            logger.error(f"Failed to update documents: {str(e)}")
            raise
    
    def _enhance_metadata_for_storage(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance metadata for overlap-aware ChromaDB storage.
        
        ChromaDB only supports scalar metadata values (str, int, float, bool, None).
        Lists and other complex types must be JSON-serialized.
        
        Args:
            metadata: Original metadata dictionary.
            
        Returns:
            Enhanced metadata compatible with ChromaDB storage requirements.
        """
        import json
        import time
        
        enhanced = metadata.copy()
        
        # List fields that need JSON serialization for ChromaDB storage
        list_fields = [
            'overlap_sources', 'overlap_regions', 'section_siblings',
            'header_hierarchy', 'expansion_candidates'
        ]
        
        # Convert list fields to JSON strings for ChromaDB compatibility
        for field in list_fields:
            if field in enhanced:
                if enhanced[field] is not None:
                    if isinstance(enhanced[field], list):
                        # Convert tuples to lists first, then serialize to JSON
                        normalized_list = [
                            list(item) if isinstance(item, tuple) else item
                            for item in enhanced[field]
                        ]
                        enhanced[field] = json.dumps(normalized_list)
                    elif not isinstance(enhanced[field], str):
                        # Convert other types to JSON string
                        enhanced[field] = json.dumps(enhanced[field])
                else:
                    # Store null as empty JSON array string
                    enhanced[field] = "[]"
        
        # Add default values for relationship tracking if missing (as JSON strings)
        if 'overlap_sources' not in enhanced:
            enhanced['overlap_sources'] = "[]"
        if 'overlap_regions' not in enhanced:
            enhanced['overlap_regions'] = "[]"
        if 'section_siblings' not in enhanced:
            enhanced['section_siblings'] = "[]"
        if 'header_hierarchy' not in enhanced:
            enhanced['header_hierarchy'] = "[]"
        if 'overlap_percentage' not in enhanced:
            enhanced['overlap_percentage'] = 0.0
        if 'context_expansion_eligible' not in enhanced:
            enhanced['context_expansion_eligible'] = True
        
        # Add storage timestamp
        enhanced['stored_at'] = time.time()
        
        # Remove or convert None values as ChromaDB doesn't support them
        cleaned_metadata = {}
        for key, value in enhanced.items():
            if value is None:
                # Skip None values entirely rather than converting
                continue
            elif isinstance(value, (str, int, float, bool)):
                cleaned_metadata[key] = value
            else:
                # This shouldn't happen after our JSON serialization above, but just in case
                try:
                    cleaned_metadata[key] = str(value)
                except:
                    continue  # Skip problematic values
        
        return cleaned_metadata
    
    def _deserialize_metadata_from_storage(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize metadata retrieved from ChromaDB storage.
        
        Converts JSON-serialized list fields back to Python lists.
        
        Args:
            metadata: Metadata dictionary from ChromaDB.
            
        Returns:
            Metadata with deserialized list fields.
        """
        import json
        
        if not metadata:
            return metadata
            
        deserialized = metadata.copy()
        
        # List fields that were JSON-serialized for storage
        list_fields = [
            'overlap_sources', 'overlap_regions', 'section_siblings',
            'header_hierarchy', 'expansion_candidates'
        ]
        
        # Deserialize JSON string fields back to lists
        for field in list_fields:
            if field in deserialized and isinstance(deserialized[field], str):
                try:
                    deserialized[field] = json.loads(deserialized[field])
                except (json.JSONDecodeError, TypeError):
                    # If deserialization fails, default to empty list
                    deserialized[field] = []
        
        return deserialized
    
    def search_with_relationships(
        self,
        query: str,
        k: int = 5,
        relationship_filter: Optional[Dict[str, Any]] = None,
        expand_context: bool = False
    ) -> List[Dict[str, Any]]:
        """Search with relationship-aware filtering and optional context expansion.
        
        Args:
            query: Query text.
            k: Number of base results to return.
            relationship_filter: Filter based on chunk relationships.
            expand_context: Whether to expand context using relationships.
            
        Returns:
            List of search results with relationship metadata.
        """
        if not self.collection:
            self.get_or_create_collection()
        
        try:
            # Perform base query with relationship filters
            results = self.collection.query(
                query_texts=[query],
                n_results=k,
                where=relationship_filter
            )
            
            # Convert to standard format
            search_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    raw_metadata = results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {}
                    metadata = self._deserialize_metadata_from_storage(raw_metadata)
                    distance = results['distances'][0][i] if results['distances'] and results['distances'][0] else 0.0
                    score = max(0.0, 1.0 - distance)
                    
                    search_results.append({
                        'id': results['ids'][0][i] if results['ids'] and results['ids'][0] else '',
                        'content': doc,
                        'metadata': metadata,
                        'score': score,
                        'relationship_data': self._extract_relationship_data(metadata)
                    })
            
            # Apply context expansion if requested
            if expand_context and search_results:
                search_results = self._expand_search_context(search_results, k)
            
            logger.info(f"Relationship-aware search returned {len(search_results)} results")
            return search_results
            
        except Exception as e:
            logger.error(f"Failed to perform relationship search: {str(e)}")
            raise
    
    def _extract_relationship_data(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relationship data from metadata.
        
        Args:
            metadata: Chunk metadata.
            
        Returns:
            Dictionary containing relationship information.
        """
        return {
            'has_overlaps': bool(metadata.get('overlap_sources', [])),
            'overlap_percentage': metadata.get('overlap_percentage', 0.0),
            'has_neighbors': bool(
                metadata.get('previous_chunk_id') or 
                metadata.get('next_chunk_id')
            ),
            'has_siblings': bool(metadata.get('section_siblings', [])),
            'expansion_eligible': metadata.get('context_expansion_eligible', True)
        }
    
    def _expand_search_context(
        self,
        base_results: List[Dict[str, Any]],
        original_k: int
    ) -> List[Dict[str, Any]]:
        """Expand search context using chunk relationships.
        
        Args:
            base_results: Base search results.
            original_k: Original number of requested results.
            
        Returns:
            Expanded results with context chunks.
        """
        expanded_results = list(base_results)
        
        for result in base_results:
            metadata = result.get('metadata', {})
            
            # Get neighbor chunks based on relationships
            neighbor_ids = []
            
            # Sequential neighbors
            if metadata.get('previous_chunk_id'):
                neighbor_ids.append(metadata['previous_chunk_id'])
            if metadata.get('next_chunk_id'):
                neighbor_ids.append(metadata['next_chunk_id'])
            
            # Overlap sources (highest priority)
            neighbor_ids.extend(metadata.get('overlap_sources', []))
            
            # Section siblings (limited to avoid explosion)
            neighbor_ids.extend(metadata.get('section_siblings', [])[:2])
            
            # Fetch neighbor chunks
            for neighbor_id in neighbor_ids[:3]:  # Limit to prevent explosion
                try:
                    neighbor_results = self.collection.get(
                        ids=[neighbor_id], 
                        include=['documents', 'metadatas']
                    )
                    
                    if neighbor_results['documents'] and neighbor_results['documents'][0]:
                        neighbor_doc = neighbor_results['documents'][0]
                        raw_neighbor_metadata = neighbor_results['metadatas'][0] if neighbor_results['metadatas'] else {}
                        neighbor_metadata = self._deserialize_metadata_from_storage(raw_neighbor_metadata)
                        
                        expanded_results.append({
                            'id': neighbor_id,
                            'content': neighbor_doc,
                            'metadata': neighbor_metadata,
                            'score': 0.0,  # Context chunk, not scored
                            'expansion_source': result['id'],
                            'expansion_type': 'relationship_based',
                            'relationship_data': self._extract_relationship_data(neighbor_metadata)
                        })
                        
                except Exception as e:
                    logger.warning(f"Failed to fetch neighbor chunk {neighbor_id}: {str(e)}")
                    continue
        
        return expanded_results
    
    def get_chunks_by_relationship(
        self,
        center_chunk_id: str,
        relationship_type: str,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Get chunks based on specific relationship types.
        
        Args:
            center_chunk_id: ID of the center chunk.
            relationship_type: Type of relationship ('sequential', 'siblings', 'overlap').
            max_results: Maximum number of results to return.
            
        Returns:
            List of related chunks.
        """
        if not self.collection:
            self.get_or_create_collection()
        
        try:
            # Define query filters based on relationship type
            if relationship_type == 'sequential':
                query_filter = {
                    '$or': [
                        {'previous_chunk_id': center_chunk_id},
                        {'next_chunk_id': center_chunk_id}
                    ]
                }
            elif relationship_type == 'siblings':
                query_filter = {
                    'section_siblings': {'$in': [center_chunk_id]}
                }
            elif relationship_type == 'overlap':
                query_filter = {
                    '$or': [
                        {'overlap_sources': {'$in': [center_chunk_id]}},
                        # Note: ChromaDB might not support all MongoDB-style queries
                        # This is a conceptual implementation
                    ]
                }
            else:
                raise ValueError(f"Unknown relationship type: {relationship_type}")
            
            # Note: ChromaDB's where clause support varies by version
            # This is a simplified implementation - actual implementation may need adjustment
            results = self.collection.query(
                query_texts=[""],  # Empty query to get all matching metadata
                n_results=max_results,
                where=query_filter
            )
            
            # Convert results
            related_chunks = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    raw_metadata = results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {}
                    metadata = self._deserialize_metadata_from_storage(raw_metadata)
                    
                    related_chunks.append({
                        'id': results['ids'][0][i] if results['ids'] and results['ids'][0] else '',
                        'content': doc,
                        'metadata': metadata,
                        'relationship_type': relationship_type,
                        'relationship_data': self._extract_relationship_data(metadata)
                    })
            
            logger.info(f"Found {len(related_chunks)} chunks with {relationship_type} relationship")
            return related_chunks
            
        except Exception as e:
            logger.error(f"Failed to get chunks by relationship: {str(e)}")
            # Fallback: try to get chunks by ID if metadata queries fail
            return self._fallback_relationship_search(center_chunk_id, relationship_type, max_results)
    
    def _fallback_relationship_search(
        self,
        center_chunk_id: str,
        relationship_type: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Fallback method for relationship search when metadata queries fail.
        
        Args:
            center_chunk_id: ID of the center chunk.
            relationship_type: Type of relationship.
            max_results: Maximum number of results.
            
        Returns:
            List of related chunks using fallback approach.
        """
        try:
            # First get the center chunk to access its metadata
            center_results = self.collection.get(
                ids=[center_chunk_id],
                include=['documents', 'metadatas']
            )
            
            if not (center_results['documents'] and center_results['documents'][0]):
                return []
            
            raw_center_metadata = center_results['metadatas'][0] if center_results['metadatas'] else {}
            center_metadata = self._deserialize_metadata_from_storage(raw_center_metadata)
            related_ids = []
            
            # Extract related IDs based on relationship type
            if relationship_type == 'sequential':
                if center_metadata.get('previous_chunk_id'):
                    related_ids.append(center_metadata['previous_chunk_id'])
                if center_metadata.get('next_chunk_id'):
                    related_ids.append(center_metadata['next_chunk_id'])
            elif relationship_type == 'siblings':
                related_ids.extend(center_metadata.get('section_siblings', []))
            elif relationship_type == 'overlap':
                related_ids.extend(center_metadata.get('overlap_sources', []))
            
            # Fetch related chunks by ID
            if not related_ids:
                return []
            
            # Limit to max_results
            related_ids = related_ids[:max_results]
            
            related_results = self.collection.get(
                ids=related_ids,
                include=['documents', 'metadatas']
            )
            
            related_chunks = []
            if related_results['documents']:
                for i, doc in enumerate(related_results['documents']):
                    if doc:  # Skip empty documents
                        raw_metadata = related_results['metadatas'][i] if related_results['metadatas'] else {}
                        metadata = self._deserialize_metadata_from_storage(raw_metadata)
                        
                        related_chunks.append({
                            'id': related_ids[i],
                            'content': doc,
                            'metadata': metadata,
                            'relationship_type': relationship_type,
                            'relationship_data': self._extract_relationship_data(metadata)
                        })
            
            logger.info(f"Fallback search found {len(related_chunks)} related chunks")
            return related_chunks
            
        except Exception as e:
            logger.error(f"Fallback relationship search failed: {str(e)}")
            return []
    
    def get_collection_stats(self, collection_name: Optional[str] = None) -> Dict[str, Any]:
        """Get enhanced statistics for a collection including relationship data.
        
        Args:
            collection_name: Name of the collection. Uses current if None.
            
        Returns:
            Dictionary containing collection statistics.
        """
        if collection_name and collection_name != self.collection_name:
            collection = self.client.get_collection(name=collection_name)
        else:
            if not self.collection:
                self.get_or_create_collection()
            collection = self.collection
        
        try:
            total_count = collection.count()
            
            # Get sample of documents to analyze relationship patterns
            if total_count > 0:
                sample_size = min(100, total_count)  # Sample up to 100 documents
                sample_results = collection.get(
                    limit=sample_size,
                    include=['metadatas']
                )
                
                # Analyze relationship patterns
                overlap_count = 0
                expansion_eligible_count = 0
                has_neighbors_count = 0
                has_siblings_count = 0
                
                if sample_results['metadatas']:
                    for raw_metadata in sample_results['metadatas']:
                        metadata = self._deserialize_metadata_from_storage(raw_metadata)
                        if metadata.get('overlap_sources'):
                            overlap_count += 1
                        if metadata.get('context_expansion_eligible'):
                            expansion_eligible_count += 1
                        if metadata.get('previous_chunk_id') or metadata.get('next_chunk_id'):
                            has_neighbors_count += 1
                        if metadata.get('section_siblings'):
                            has_siblings_count += 1
                
                # Estimate percentages for full collection
                overlap_percentage = (overlap_count / sample_size) * 100 if sample_size > 0 else 0
                expansion_percentage = (expansion_eligible_count / sample_size) * 100 if sample_size > 0 else 0
                neighbors_percentage = (has_neighbors_count / sample_size) * 100 if sample_size > 0 else 0
                siblings_percentage = (has_siblings_count / sample_size) * 100 if sample_size > 0 else 0
            else:
                overlap_percentage = expansion_percentage = neighbors_percentage = siblings_percentage = 0
            
            stats = {
                'collection_name': collection_name or self.collection_name,
                'total_documents': total_count,
                'relationship_analysis': {
                    'chunks_with_overlap': f"{overlap_percentage:.1f}%",
                    'expansion_eligible': f"{expansion_percentage:.1f}%",
                    'has_sequential_neighbors': f"{neighbors_percentage:.1f}%",
                    'has_section_siblings': f"{siblings_percentage:.1f}%"
                },
                'sample_size': sample_size if total_count > 0 else 0
            }
            
            logger.info(f"Generated enhanced stats for collection with {total_count} documents")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {str(e)}")
            return {
                'collection_name': collection_name or self.collection_name,
                'total_documents': -1,
                'error': str(e)
            }