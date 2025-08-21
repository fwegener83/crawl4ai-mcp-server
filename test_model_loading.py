#!/usr/bin/env python3
"""
Test script to debug model loading consistency.
This script verifies what model is actually being loaded vs configured.
"""
import os
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_environment_variables():
    """Test that environment variables are properly loaded."""
    print("=== Environment Variables Test ===")
    
    # Check if .env exists
    env_file = project_root / '.env'
    print(f".env file exists: {env_file.exists()}")
    
    if env_file.exists():
        print(f".env file path: {env_file}")
        # Read .env file content
        with open(env_file) as f:
            for i, line in enumerate(f, 1):
                if 'RAG_MODEL_NAME' in line:
                    print(f"Line {i}: {line.strip()}")
    
    # Check environment variables
    rag_model = os.getenv("RAG_MODEL_NAME")
    rag_device = os.getenv("RAG_DEVICE", "cpu")
    
    print(f"RAG_MODEL_NAME from env: {rag_model}")
    print(f"RAG_DEVICE from env: {rag_device}")
    print(f"Expected: distiluse-base-multilingual-cased-v1")
    
    return rag_model, rag_device

def test_model_loading():
    """Test actual model loading and dimensions."""
    print("\n=== Model Loading Test ===")
    
    try:
        from tools.knowledge_base.embeddings import EmbeddingService
        
        # Test default initialization (should use .env)
        print("Initializing EmbeddingService with default settings...")
        embedding_service = EmbeddingService()
        
        print(f"Configured model_name: {embedding_service.model_name}")
        print(f"Configured device: {embedding_service.device}")
        
        # Test embedding dimension
        print("Testing embedding dimensions...")
        dimension = embedding_service.get_embedding_dimension()
        print(f"Actual embedding dimension: {dimension}")
        
        # Expected dimensions:
        # - all-MiniLM-L6-v2: 384 dimensions
        # - distiluse-base-multilingual-cased-v1: 512 dimensions
        
        if dimension == 384:
            print("⚠️  WARNING: Model appears to be all-MiniLM-L6-v2 (384D)")
        elif dimension == 512:
            print("✅ SUCCESS: Model appears to be distiluse-base-multilingual-cased-v1 (512D)")
        else:
            print(f"❓ UNKNOWN: Unexpected dimension {dimension}")
            
        return embedding_service
        
    except Exception as e:
        print(f"❌ ERROR: Failed to load model: {e}")
        raise

def test_cross_language_similarity(embedding_service):
    """Test cross-language similarity like in the notebook."""
    print("\n=== Cross-Language Similarity Test ===")
    
    try:
        # Test queries from the original issue
        german_query = "Welche verschiedenen Arten von Speicher gibt es in Claude Code?"
        english_query = "What are the different types of memory in Claude Code?"
        
        print(f"German query: {german_query}")
        print(f"English query: {english_query}")
        
        # Get embeddings
        print("Encoding queries...")
        german_emb = embedding_service.encode_text(german_query)
        english_emb = embedding_service.encode_text(english_query)
        
        # Calculate cross-language similarity
        similarity = embedding_service.similarity(german_emb, english_emb)
        print(f"Cross-language similarity: {similarity:.3f}")
        
        # Expected results:
        # - With distiluse-base-multilingual-cased-v1: ~0.881 (from notebook)
        # - With all-MiniLM-L6-v2: Much lower similarity
        
        if similarity > 0.8:
            print("✅ EXCELLENT: High cross-language similarity - multilingual model working")
        elif similarity > 0.6:
            print("✅ GOOD: Decent cross-language similarity")
        elif similarity > 0.4:
            print("⚠️  MODERATE: Low cross-language similarity")
        else:
            print("❌ POOR: Very low cross-language similarity - model issue likely")
            
        return similarity
        
    except Exception as e:
        print(f"❌ ERROR: Failed cross-language test: {e}")
        raise

def test_model_cache_investigation():
    """Investigate model caching issues."""
    print("\n=== Model Cache Investigation ===")
    
    try:
        # Check sentence-transformers cache
        import sentence_transformers
        cache_dir = sentence_transformers.SentenceTransformer._modules.get('__file__', None)
        if cache_dir:
            cache_dir = Path(cache_dir).parent / '.cache'
            
        # Default cache locations
        home = Path.home()
        possible_cache_dirs = [
            home / '.cache' / 'torch' / 'sentence_transformers',
            home / '.cache' / 'huggingface' / 'hub',
            Path('.cache'),
            Path('~/.sentence_transformers').expanduser()
        ]
        
        print("Checking sentence-transformers cache directories:")
        for cache_dir in possible_cache_dirs:
            if cache_dir.exists():
                print(f"✅ Found cache: {cache_dir}")
                # List cached models
                for item in cache_dir.iterdir():
                    if item.is_dir() and ('all-MiniLM' in item.name or 'distiluse' in item.name):
                        print(f"   - Cached model: {item.name}")
            else:
                print(f"❌ No cache: {cache_dir}")
                
    except Exception as e:
        print(f"⚠️  Cache investigation failed: {e}")

def main():
    """Main test function."""
    print("Model Loading Debug Test")
    print("=" * 50)
    
    try:
        # Test 1: Environment variables
        rag_model, rag_device = test_environment_variables()
        
        # Test 2: Model loading
        embedding_service = test_model_loading()
        
        # Test 3: Cross-language similarity
        similarity = test_cross_language_similarity(embedding_service)
        
        # Test 4: Cache investigation
        test_model_cache_investigation()
        
        # Summary
        print("\n=== SUMMARY ===")
        print(f"Configured model: {rag_model}")
        print(f"Loaded model: {embedding_service.model_name}")
        print(f"Embedding dimension: {embedding_service.get_embedding_dimension()}")
        print(f"Cross-language similarity: {similarity:.3f}")
        
        if embedding_service.model_name == rag_model:
            print("✅ Model configuration matches loaded model")
        else:
            print("❌ Model configuration MISMATCH - this is the problem!")
            
        if similarity > 0.8:
            print("✅ Cross-language performance is excellent")
        else:
            print("❌ Cross-language performance is poor - confirms multilingual model issue")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()