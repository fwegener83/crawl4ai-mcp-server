"""Test model loading fix for multilingual embedding consistency."""

import pytest
import os
import sys
from pathlib import Path

# Add project root to path for tests
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Check if RAG dependencies are available
from tools.knowledge_base.dependencies import is_rag_available

pytestmark = pytest.mark.skipif(
    not is_rag_available(),
    reason="RAG dependencies not available"
)


def test_embedding_service_loads_correct_model():
    """Test that EmbeddingService loads the correct multilingual model from .env."""
    # Import after setting path
    from tools.knowledge_base.embeddings import EmbeddingService
    
    # Initialize service (should load from .env through module import)
    service = EmbeddingService()
    
    # Check that correct model is loaded
    assert service.model_name == "distiluse-base-multilingual-cased-v1", f"Expected distiluse-base-multilingual-cased-v1, got {service.model_name}"
    
    # Check model dimensions (512 for multilingual vs 384 for MiniLM)
    dimension = service.get_embedding_dimension()
    assert dimension == 512, f"Expected 512 dimensions for multilingual model, got {dimension}"


def test_cross_language_semantic_similarity():
    """Test that multilingual model provides good cross-language similarity."""
    from tools.knowledge_base.embeddings import EmbeddingService
    
    service = EmbeddingService()
    
    # Test with the same queries from the notebook
    german_query = "Welche verschiedenen Arten von Speicher gibt es in Claude Code?"
    english_query = "What are the different types of memory in Claude Code?"
    
    # Get embeddings
    german_emb = service.encode_text(german_query)
    english_emb = service.encode_text(english_query)
    
    # Calculate similarity
    similarity = service.similarity(german_emb, english_emb)
    
    # Should achieve high cross-language similarity (notebook shows 0.881)
    assert similarity > 0.8, f"Cross-language similarity too low: {similarity:.3f}, expected >0.8"
    
    # Should be close to notebook results
    assert abs(similarity - 0.881) < 0.05, f"Similarity {similarity:.3f} differs from expected ~0.881"


def test_model_consistency_across_components():
    """Test that all RAG components use the same model configuration."""
    from tools.knowledge_base.embeddings import EmbeddingService
    from tools.knowledge_base.rag_tools import RAGService
    
    # Create EmbeddingService directly
    embedding_service = EmbeddingService()
    
    # Create RAGService (which creates its own EmbeddingService)
    rag_service = RAGService()
    
    # Both should use the same model
    assert embedding_service.model_name == rag_service.embedding_service.model_name, \
        f"Model mismatch: {embedding_service.model_name} vs {rag_service.embedding_service.model_name}"
    
    # Both should have same dimensions
    assert embedding_service.get_embedding_dimension() == rag_service.embedding_service.get_embedding_dimension(), \
        "Embedding dimensions don't match between services"


def test_environment_variable_loading():
    """Test that environment variables are loaded correctly from .env."""
    # Import should trigger .env loading
    import tools.knowledge_base
    
    # Check that RAG_MODEL_NAME is available
    model_name = os.getenv("RAG_MODEL_NAME")
    assert model_name == "distiluse-base-multilingual-cased-v1", \
        f"RAG_MODEL_NAME should be loaded from .env, got: {model_name}"
    
    # Check other RAG variables
    chunk_size = os.getenv("RAG_CHUNK_SIZE")
    assert chunk_size == "1000", f"RAG_CHUNK_SIZE should be 1000, got: {chunk_size}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])