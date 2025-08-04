"""Central dependency management for RAG components."""
import logging
from typing import Optional, Any, Dict

logger = logging.getLogger(__name__)


class RAGDependencies:
    """Manages RAG-related dependencies with graceful fallbacks."""
    
    def __init__(self):
        self.available = False
        self.missing_deps: Dict[str, str] = {}
        self.components: Dict[str, Any] = {}
        self._load_dependencies()
    
    def _load_dependencies(self):
        """Load all RAG dependencies with error handling."""
        success_count = 0
        total_deps = 4
        
        # LangChain Text Splitters
        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
            self.components['RecursiveCharacterTextSplitter'] = RecursiveCharacterTextSplitter
            self.components['MarkdownHeaderTextSplitter'] = MarkdownHeaderTextSplitter
            success_count += 1
        except ImportError as e:
            self.missing_deps['langchain_text_splitters'] = str(e)
        
        # ChromaDB
        try:
            import chromadb
            self.components['chromadb'] = chromadb
            success_count += 1
        except ImportError as e:
            self.missing_deps['chromadb'] = str(e)
        
        # Sentence Transformers
        try:
            from sentence_transformers import SentenceTransformer
            self.components['SentenceTransformer'] = SentenceTransformer
            success_count += 1
        except ImportError as e:
            self.missing_deps['sentence_transformers'] = str(e)
        
        # NumPy
        try:
            import numpy as np
            self.components['numpy'] = np
            success_count += 1
        except ImportError as e:
            self.missing_deps['numpy'] = str(e)
        
        self.available = success_count == total_deps
        
        if self.available:
            logger.info("All RAG dependencies loaded successfully")
        else:
            logger.warning(f"RAG dependencies partially loaded ({success_count}/{total_deps})")
    
    def get_component(self, name: str) -> Any:
        """Get a dependency component by name."""
        if not self.available:
            raise ImportError(f"RAG dependencies not available. Install with: pip install chromadb sentence-transformers langchain-text-splitters numpy")
        return self.components[name]
    
    def check_available(self, raise_on_missing: bool = True) -> bool:
        """Check if all dependencies are available."""
        if not self.available and raise_on_missing:
            missing_list = ", ".join(self.missing_deps.keys())
            raise ImportError(f"RAG dependencies not available. Missing: {missing_list}")
        return self.available


# Global instance
rag_deps = RAGDependencies()

# Convenience functions
def ensure_rag_available():
    """Ensure RAG dependencies are available."""
    rag_deps.check_available(raise_on_missing=True)

def is_rag_available() -> bool:
    """Check if RAG dependencies are available."""
    return rag_deps.check_available(raise_on_missing=False)