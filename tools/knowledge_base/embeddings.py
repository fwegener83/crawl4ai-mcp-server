"""Embedding service implementation using SentenceTransformers."""
import os
import logging
from typing import List, Union, Optional
from .dependencies import rag_deps, ensure_rag_available

logger = logging.getLogger(__name__)


class EmbeddingService:
    """SentenceTransformers-based embedding service."""
    
    def __init__(
        self,
        model_name: Optional[str] = None,
        device: Optional[str] = None,
        cache_folder: Optional[str] = None
    ):
        """Initialize the embedding service.
        
        Args:
            model_name: Name of the sentence transformer model.
            device: Device to run the model on ('cpu', 'cuda', etc.).
            cache_folder: Folder to cache the model.
        """
        ensure_rag_available()
        
        self.model_name = model_name or os.getenv("RAG_MODEL_NAME", "all-MiniLM-L6-v2")
        self.device = device or os.getenv("RAG_DEVICE", "cpu")
        self.cache_folder = cache_folder
        self.model = None
        
        self._load_model()
        logger.info(f"EmbeddingService initialized with model: {self.model_name}")
    
    def _load_model(self):
        """Load the SentenceTransformer model."""
        try:
            logger.info(f"Loading model: {self.model_name}")
            sentence_transformer = rag_deps.get_component('SentenceTransformer')
            self.model = sentence_transformer(
                self.model_name,
                device=self.device,
                cache_folder=self.cache_folder
            )
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {str(e)}")
            raise
    
    def encode_text(self, text: str) -> List[float]:
        """Encode a single text into embeddings.
        
        Args:
            text: Input text to encode.
            
        Returns:
            List of embedding values.
            
        Raises:
            Exception: If encoding fails.
        """
        try:
            embedding = self.model.encode(text, convert_to_tensor=False)
            # Ensure it's a list of floats
            np = rag_deps.get_component('numpy')
            if isinstance(embedding, np.ndarray):
                embedding = embedding.tolist()
            
            logger.debug(f"Encoded text of length {len(text)} to embedding of dimension {len(embedding)}")
            return embedding
        except Exception as e:
            logger.error(f"Failed to encode text: {str(e)}")
            raise
    
    def encode_batch(
        self,
        texts: List[str],
        batch_size: Optional[int] = None,
        show_progress_bar: bool = False
    ) -> List[List[float]]:
        """Encode a batch of texts into embeddings.
        
        Args:
            texts: List of input texts to encode.
            batch_size: Batch size for processing. Uses model default if None.
            show_progress_bar: Whether to show progress bar.
            
        Returns:
            List of embeddings, each embedding is a list of floats.
            
        Raises:
            Exception: If batch encoding fails.
        """
        if not texts:
            logger.warning("Empty text list provided for batch encoding")
            return []
        
        try:
            logger.info(f"Encoding batch of {len(texts)} texts")
            
            # Handle batch_size parameter properly
            encode_kwargs = {
                "show_progress_bar": show_progress_bar,
                "convert_to_tensor": False
            }
            if batch_size is not None:
                encode_kwargs["batch_size"] = batch_size
            
            embeddings = self.model.encode(texts, **encode_kwargs)
            
            # Ensure embeddings are lists of floats
            np = rag_deps.get_component('numpy')
            if isinstance(embeddings, np.ndarray):
                embeddings = embeddings.tolist()
            elif isinstance(embeddings[0], np.ndarray):
                embeddings = [emb.tolist() for emb in embeddings]
            
            logger.info(f"Successfully encoded {len(embeddings)} texts")
            return embeddings
        except Exception as e:
            logger.error(f"Failed to encode batch: {str(e)}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this model.
        
        Returns:
            Embedding dimension.
        """
        try:
            # Test with a simple text to get dimension
            test_embedding = self.encode_text("test")
            dimension = len(test_embedding)
            logger.info(f"Model embedding dimension: {dimension}")
            return dimension
        except Exception as e:
            logger.error(f"Failed to get embedding dimension: {str(e)}")
            raise
    
    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding.
            embedding2: Second embedding.
            
        Returns:
            Cosine similarity score between -1 and 1.
            
        Raises:
            Exception: If similarity calculation fails.
        """
        try:
            # Convert to numpy arrays
            np = rag_deps.get_component('numpy')
            emb1 = np.array(embedding1)
            emb2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(emb1, emb2)
            norm1 = np.linalg.norm(emb1)
            norm2 = np.linalg.norm(emb2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
        except Exception as e:
            logger.error(f"Failed to calculate similarity: {str(e)}")
            raise
    
    def batch_similarity(
        self,
        query_embedding: List[float],
        embeddings: List[List[float]]
    ) -> List[float]:
        """Calculate similarity between a query embedding and a batch of embeddings.
        
        Args:
            query_embedding: Query embedding to compare against.
            embeddings: List of embeddings to compare with.
            
        Returns:
            List of similarity scores.
            
        Raises:
            Exception: If batch similarity calculation fails.
        """
        try:
            np = rag_deps.get_component('numpy')
            query_emb = np.array(query_embedding)
            batch_embs = np.array(embeddings)
            
            # Calculate dot products
            dot_products = np.dot(batch_embs, query_emb)
            
            # Calculate norms
            query_norm = np.linalg.norm(query_emb)
            batch_norms = np.linalg.norm(batch_embs, axis=1)
            
            # Calculate similarities
            similarities = dot_products / (query_norm * batch_norms)
            
            # Handle any NaN values
            similarities = np.nan_to_num(similarities, nan=0.0)
            
            return similarities.tolist()
        except Exception as e:
            logger.error(f"Failed to calculate batch similarity: {str(e)}")
            raise
    
    def reload_model(self, model_name: Optional[str] = None):
        """Reload the model, optionally with a different model name.
        
        Args:
            model_name: New model name to load. Uses current if None.
        """
        if model_name:
            self.model_name = model_name
        
        logger.info(f"Reloading model: {self.model_name}")
        self._load_model()