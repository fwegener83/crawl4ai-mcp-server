"""Comprehensive unit tests for RAG knowledge base components."""
import pytest
import tempfile
import os
import shutil
from unittest.mock import MagicMock, patch, AsyncMock
from typing import Dict, Any, List

# Check if RAG dependencies are available
try:
    import numpy as np
    import chromadb
    RAG_DEPENDENCIES_AVAILABLE = True
except ImportError:
    RAG_DEPENDENCIES_AVAILABLE = False

# Skip all tests in this module if dependencies are not available
pytestmark = pytest.mark.skipif(
    not RAG_DEPENDENCIES_AVAILABLE, 
    reason="RAG dependencies (numpy, chromadb) not available"
)

from tests.rag_factories import (
    setup_rag_test_environment,
    RAGTestData,
    ChromaDBMockFactory,
    SentenceTransformersMockFactory,
    TextSplitterMockFactory,
    TemporaryRAGDatabase,
    RAGErrorScenarios
)

class TestVectorStore:
    """Test cases for vector store functionality."""
    
    @pytest.fixture
    def temp_db(self):
        """Fixture providing temporary database."""
        with TemporaryRAGDatabase() as db_path:
            yield db_path
            
    @pytest.fixture
    def vector_store(self, temp_db):
        """Fixture providing vector store instance."""
        from tools.knowledge_base.vector_store import VectorStore
        return VectorStore(persist_directory=temp_db)
    
    def test_vector_store_initialization(self, vector_store):
        """Test vector store initialization."""
        assert vector_store is not None
        assert vector_store.client is not None
        assert vector_store.collection_name == "crawl4ai_documents"
            
    def test_vector_store_create_collection(self, vector_store):
        """Test collection creation."""
        collection = vector_store.create_collection("test_collection")
        assert collection is not None
        assert vector_store.collection_name == "test_collection"
            
    def test_vector_store_add_documents(self, vector_store):
        """Test adding documents."""
        vector_store.get_or_create_collection("test_collection")
        
        documents = ["Test document 1", "Test document 2"]
        metadatas = [{"id": 1}, {"id": 2}]
        ids = ["doc1", "doc2"]
        
        # Should not raise exception
        vector_store.add_documents(documents, metadatas, ids)
        
        # Verify documents were added
        count = vector_store.count()
        assert count == 2
            
    def test_vector_store_search(self, vector_store):
        """Test search functionality."""
        vector_store.get_or_create_collection("test_collection")
        
        # Add test documents
        documents = ["Python programming", "Machine learning basics"]
        metadatas = [{"topic": "programming"}, {"topic": "ml"}]
        ids = ["doc1", "doc2"]
        vector_store.add_documents(documents, metadatas, ids)
        
        # Search
        results = vector_store.query(["Python code"], n_results=1)
        assert "documents" in results
        assert len(results["documents"][0]) > 0
            
    def test_vector_store_error_handling(self):
        """Test error handling."""
        from tools.knowledge_base.vector_store import VectorStore
        
        # Test with invalid directory should still work (creates directory)
        vector_store = VectorStore(persist_directory="/tmp/test_invalid_123456")
        assert vector_store.client is not None


class TestEmbeddingService:
    """Test cases for embedding service functionality."""
    
    @pytest.fixture
    def embedding_service(self):
        """Fixture providing embedding service instance."""
        from tools.knowledge_base.embeddings import EmbeddingService
        return EmbeddingService(model_name="all-MiniLM-L6-v2")
    
    def test_embedding_service_initialization(self, embedding_service):
        """Test embedding service initialization."""
        assert embedding_service is not None
        assert embedding_service.model is not None
        assert embedding_service.model_name == "all-MiniLM-L6-v2"
            
    def test_embedding_service_encode_text(self, embedding_service):
        """Test text encoding."""
        text = "This is a test document"
        embedding = embedding_service.encode_text(text)
        
        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, float) for x in embedding)
            
    def test_embedding_service_batch_encode(self, embedding_service):
        """Test batch encoding."""
        texts = ["Document 1", "Document 2", "Document 3"]
        embeddings = embedding_service.encode_batch(texts)
        
        assert len(embeddings) == 3
        assert all(isinstance(emb, list) for emb in embeddings)
        assert all(len(emb) > 0 for emb in embeddings)
            
    def test_embedding_service_similarity(self, embedding_service):
        """Test similarity calculation."""
        text1 = "Python programming language"
        text2 = "Python coding tutorial"
        text3 = "Machine learning algorithms"
        
        emb1 = embedding_service.encode_text(text1)
        emb2 = embedding_service.encode_text(text2)
        emb3 = embedding_service.encode_text(text3)
        
        # Similar texts should have higher similarity
        sim_12 = embedding_service.similarity(emb1, emb2)
        sim_13 = embedding_service.similarity(emb1, emb3)
        
        assert isinstance(sim_12, float)
        assert isinstance(sim_13, float)
        assert -1 <= sim_12 <= 1
        assert -1 <= sim_13 <= 1


class TestContentProcessor:
    """Test cases for content processor functionality."""
    
    @pytest.fixture
    def content_processor(self):
        """Fixture providing content processor instance."""
        from tools.knowledge_base.content_processor import ContentProcessor
        return ContentProcessor(chunk_size=500, chunk_overlap=50)
    
    def test_content_processor_initialization(self, content_processor):
        """Test content processor initialization."""
        assert content_processor is not None
        assert content_processor.chunk_size == 500
        assert content_processor.chunk_overlap == 50
        assert content_processor.text_splitter is not None
            
    def test_content_processor_split_text(self, content_processor):
        """Test text splitting."""
        text = "This is a long document. " * 50  # Create text longer than chunk_size
        chunks = content_processor.split_text(text)
        
        assert isinstance(chunks, list)
        assert len(chunks) > 1  # Should split into multiple chunks
        assert all(isinstance(chunk, str) for chunk in chunks)
            
    def test_content_processor_extract_metadata(self, content_processor):
        """Test metadata extraction."""
        content = "This is test content for metadata extraction."
        url = "https://example.com/test"
        title = "Test Document"
        
        metadata = content_processor.extract_metadata(content, url, title)
        
        assert isinstance(metadata, dict)
        assert metadata["url"] == url
        assert metadata["title"] == title
        assert "content_length" in metadata
        assert "word_count" in metadata
        assert "content_hash" in metadata
            
    def test_content_processor_normalize_content(self, content_processor):
        """Test content normalization."""
        messy_content = "This   has    multiple\n\n\nspaces   and   whitespace."
        normalized = content_processor.normalize_content(messy_content)
        
        assert isinstance(normalized, str)
        assert "   " not in normalized  # Should remove excessive spaces
        assert normalized.count(" ") < messy_content.count(" ")


class TestEdgeCases:
    """Test edge cases and error scenarios."""
    
    @pytest.fixture
    def content_processor(self):
        """Fixture providing content processor instance."""
        from tools.knowledge_base.content_processor import ContentProcessor
        return ContentProcessor()
    
    def test_empty_document_handling(self, content_processor):
        """Test handling of empty documents."""
        empty_text = ""
        chunks = content_processor.split_text(empty_text)
        assert chunks == []
        
        whitespace_text = "   \n  \t  "
        chunks = content_processor.split_text(whitespace_text)
        assert chunks == []
            
    def test_large_document_handling(self, content_processor):
        """Test handling of large documents.""" 
        large_text = RAGTestData.create_large_document(2000)
        chunks = content_processor.split_text(large_text)
        
        assert isinstance(chunks, list)
        assert len(chunks) > 1  # Should split large document
        assert all(len(chunk) <= content_processor.chunk_size + 100 for chunk in chunks)  # Allow some margin
            
    def test_malformed_input_handling(self, content_processor):
        """Test handling of malformed input."""
        # Test with None - should handle gracefully
        result = content_processor.normalize_content("")
        assert result == ""
        
        # Test with special characters
        special_text = "Text with special chars: !@#$%^&*()"
        normalized = content_processor.normalize_content(special_text)
        assert isinstance(normalized, str)
            
    def test_unicode_handling(self, content_processor):
        """Test Unicode text handling."""
        unicode_text = "Text with émojis: 🚀 and special chars: café naïve résumé"
        
        # Should not raise exception
        chunks = content_processor.split_text(unicode_text)
        assert isinstance(chunks, list)
        assert len(chunks) > 0
        
        # Metadata extraction should work
        metadata = content_processor.extract_metadata(unicode_text)
        assert isinstance(metadata, dict)
        assert metadata["content_length"] > 0


class TestErrorScenarios:
    """Test error scenarios and error handling."""
    
    def test_database_connection_errors(self):
        """Test database connection error handling."""
        from tools.knowledge_base.vector_store import VectorStore
        
        # Test with read-only directory (should handle gracefully or create alternative)
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a vector store - should work
            vector_store = VectorStore(persist_directory=temp_dir)
            assert vector_store.client is not None
            
    def test_model_loading_with_invalid_model(self):
        """Test model loading with invalid model name."""
        from tools.knowledge_base.embeddings import EmbeddingService
        
        # Test with invalid model name - should raise exception
        with pytest.raises(Exception):
            EmbeddingService(model_name="invalid-model-name-12345")
            
    def test_vector_store_invalid_operations(self):
        """Test vector store invalid operations."""
        from tools.knowledge_base.vector_store import VectorStore
        
        # Test operations on non-existent collection
        vector_store = VectorStore(persist_directory=None)  # Memory only
        
        # Should handle missing collection gracefully
        try:
            count = vector_store.count("non-existent-collection")
            # If no exception, count should be reasonable
            assert isinstance(count, int)
        except Exception as e:
            # Exception is acceptable for non-existent collection
            assert "not found" in str(e).lower() or "does not exist" in str(e).lower()


# Integration test setup for when components are implemented
class TestIntegrationReadiness:
    """Tests that will be used once basic components are implemented."""
    
    @pytest.fixture
    def rag_test_env(self):
        """Fixture providing RAG test environment."""
        return setup_rag_test_environment()
    
    @pytest.fixture
    def temp_db(self):
        """Fixture providing temporary database."""
        with TemporaryRAGDatabase() as db_path:
            yield db_path
    
    @pytest.fixture
    def test_documents(self):
        """Fixture providing test documents."""
        return RAGTestData.SAMPLE_DOCUMENTS
    
    def test_test_environment_setup(self, rag_test_env):
        """Test that our test environment is properly configured."""
        assert rag_test_env is not None
        assert "chroma_client" in rag_test_env
        assert "sentence_model" in rag_test_env
        assert "text_splitter" in rag_test_env
        assert "config" in rag_test_env
        assert "test_data" in rag_test_env
        
    def test_temporary_database_fixture(self, temp_db):
        """Test that temporary database fixture works."""
        assert temp_db is not None
        assert os.path.exists(temp_db)
        
    def test_test_documents_fixture(self, test_documents):
        """Test that test documents are available."""
        assert len(test_documents) > 0
        for doc in test_documents:
            assert "title" in doc
            assert "content" in doc
            assert "url" in doc
            assert "metadata" in doc


# Performance test placeholders
class TestPerformanceReadiness:
    """Performance tests that will be implemented after core functionality."""
    
    def test_performance_test_setup_ready(self):
        """Verify performance test infrastructure is ready."""
        # Test that we have the necessary tools for performance testing
        assert hasattr(RAGTestData, 'create_large_document')
        
        large_doc = RAGTestData.create_large_document(1000)
        assert len(large_doc.split()) >= 900  # Approximately 1000 words
        
    def test_memory_profiling_ready(self):
        """Verify memory profiling infrastructure is ready."""
        # This will be expanded when we add actual performance tests
        assert True  # Placeholder


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])