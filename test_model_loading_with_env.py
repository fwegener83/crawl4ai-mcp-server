#!/usr/bin/env python3
"""
Test script to verify model loading works correctly when .env is loaded.
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def load_env_file():
    """Load .env file manually (same logic as unified_server.py)."""
    print("=== Loading .env file ===")
    env_file = project_root / '.env'
    if env_file.exists():
        print(f"Loading: {env_file}")
        with open(env_file) as f:
            loaded = 0
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Don't override existing environment variables
                    if key not in os.environ:
                        os.environ[key] = value
                        if key.startswith('RAG_'):
                            print(f"  Loaded: {key}={value}")
                            loaded += 1
        print(f"Loaded {loaded} RAG environment variables")
    else:
        print("❌ .env file not found")

def test_with_env():
    """Test model loading with proper environment loading."""
    print("\n=== Test with Environment Loading ===")
    
    # Load .env first
    load_env_file()
    
    # Check environment variables
    rag_model = os.getenv("RAG_MODEL_NAME")
    print(f"RAG_MODEL_NAME: {rag_model}")
    
    if rag_model != "distiluse-base-multilingual-cased-v1":
        print("❌ Environment variable still not loaded correctly")
        return
    
    # Import and test EmbeddingService
    from tools.knowledge_base.embeddings import EmbeddingService
    
    print("Initializing EmbeddingService...")
    embedding_service = EmbeddingService()
    
    print(f"Loaded model: {embedding_service.model_name}")
    print(f"Embedding dimension: {embedding_service.get_embedding_dimension()}")
    
    if embedding_service.model_name == "distiluse-base-multilingual-cased-v1":
        print("✅ SUCCESS: Correct model loaded!")
    else:
        print("❌ FAIL: Wrong model still loaded")
        return
        
    # Test cross-language similarity
    print("\nTesting cross-language similarity...")
    german_query = "Welche verschiedenen Arten von Speicher gibt es in Claude Code?"
    english_query = "What are the different types of memory in Claude Code?"
    
    german_emb = embedding_service.encode_text(german_query)
    english_emb = embedding_service.encode_text(english_query)
    similarity = embedding_service.similarity(german_emb, english_emb)
    
    print(f"Cross-language similarity: {similarity:.3f}")
    
    if similarity > 0.8:
        print("✅ EXCELLENT: High cross-language similarity achieved!")
    else:
        print(f"⚠️  Similarity is {similarity:.3f}, expected >0.8")

if __name__ == "__main__":
    test_with_env()