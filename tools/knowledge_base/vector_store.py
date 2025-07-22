"""Vector store implementation using ChromaDB for RAG functionality."""
import os
import logging
from typing import Dict, Any, List, Optional, Union
import chromadb
from chromadb.config import Settings

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
                    self.client = chromadb.PersistentClient(path=expanded_path)
                    self.persist_directory = expanded_path  # Update with expanded path
                except OSError as e:
                    if e.errno == 30:  # Read-only file system
                        logger.warning(f"Cannot write to {expanded_path} (read-only filesystem). Falling back to /tmp.")
                        fallback_path = f"/tmp/crawl4ai-rag-db"
                        os.makedirs(fallback_path, exist_ok=True)
                        self.client = chromadb.PersistentClient(path=fallback_path)
                        self.persist_directory = fallback_path
                    else:
                        raise
            else:
                # In-memory client for testing
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
        """Add documents to the collection.
        
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
            if embeddings:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids,
                    embeddings=embeddings
                )
            else:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
            
            logger.info(f"Added {len(documents)} documents to collection")
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