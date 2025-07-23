"""Content processor for text chunking and metadata extraction."""
import os
import logging
import hashlib
import re
from typing import Dict, Any, List, Optional, Union, Tuple
from .dependencies import rag_deps, ensure_rag_available

logger = logging.getLogger(__name__)


class ContentProcessor:
    """Content processor for preparing documents for RAG storage."""
    
    def __init__(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        separators: Optional[List[str]] = None
    ):
        """Initialize the content processor.
        
        Args:
            chunk_size: Maximum size of text chunks.
            chunk_overlap: Overlap between chunks.
            separators: List of separators for text splitting.
        """
        ensure_rag_available()
        
        self.chunk_size = chunk_size or int(os.getenv("RAG_CHUNK_SIZE", "1000"))
        self.chunk_overlap = chunk_overlap or int(os.getenv("RAG_CHUNK_OVERLAP", "200"))
        self.separators = separators or ["\n\n", "\n", " ", ""]
        
        RecursiveCharacterTextSplitter = rag_deps.get_component('RecursiveCharacterTextSplitter')
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.separators,
            length_function=len
        )
        
        logger.info(f"ContentProcessor initialized with chunk_size={self.chunk_size}, overlap={self.chunk_overlap}")
    
    def split_text(self, text: str) -> List[str]:
        """Split text into chunks.
        
        Args:
            text: Input text to split.
            
        Returns:
            List of text chunks.
            
        Raises:
            Exception: If text splitting fails.
        """
        if not text or not text.strip():
            logger.warning("Empty or whitespace-only text provided for splitting")
            return []
        
        try:
            chunks = self.text_splitter.split_text(text)
            logger.debug(f"Split text of length {len(text)} into {len(chunks)} chunks")
            return chunks
        except Exception as e:
            logger.error(f"Failed to split text: {str(e)}")
            raise
    
    def extract_metadata(
        self,
        content: str,
        url: Optional[str] = None,
        title: Optional[str] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Extract metadata from content.
        
        Args:
            content: The content text.
            url: Source URL.
            title: Document title.
            additional_metadata: Additional metadata to include.
            
        Returns:
            Dictionary containing extracted metadata.
        """
        metadata = {}
        
        # Basic metadata
        if url:
            metadata["url"] = url
            metadata["domain"] = self._extract_domain(url)
        
        if title:
            metadata["title"] = title
        
        # Content statistics
        metadata["content_length"] = len(content)
        metadata["word_count"] = len(content.split())
        metadata["paragraph_count"] = len([p for p in content.split('\n\n') if p.strip()])
        
        # Content fingerprint
        metadata["content_hash"] = self._generate_content_hash(content)
        
        # Extract language (basic detection)
        metadata["detected_language"] = self._detect_language(content)
        
        # Content type detection
        metadata["content_type"] = self._detect_content_type(content)
        
        # Merge additional metadata
        if additional_metadata:
            metadata.update(additional_metadata)
        
        logger.debug(f"Extracted metadata with {len(metadata)} fields")
        return metadata
    
    def normalize_content(self, content: str) -> str:
        """Normalize content for better processing.
        
        Args:
            content: Raw content to normalize.
            
        Returns:
            Normalized content.
        """
        if not content:
            return ""
        
        try:
            # Remove excessive whitespace
            normalized = re.sub(r'\s+', ' ', content)
            
            # Remove or replace problematic characters
            normalized = normalized.encode('utf-8', errors='ignore').decode('utf-8')
            
            # Trim whitespace
            normalized = normalized.strip()
            
            logger.debug(f"Normalized content from {len(content)} to {len(normalized)} characters")
            return normalized
        except Exception as e:
            logger.error(f"Failed to normalize content: {str(e)}")
            return content  # Return original if normalization fails
    
    def process_crawl_result(
        self,
        crawl_result: Union[str, Dict[str, Any]],
        collection_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Process crawl result into chunks with metadata.
        
        Args:
            crawl_result: Either string content or dict result from crawling.
            collection_name: Target collection name.
            
        Returns:
            List of processed chunks with metadata.
        """
        try:
            if isinstance(crawl_result, str):
                return self._process_string_result(crawl_result, collection_name)
            elif isinstance(crawl_result, dict):
                return self._process_dict_result(crawl_result, collection_name)
            else:
                raise ValueError(f"Unsupported crawl result type: {type(crawl_result)}")
        except Exception as e:
            logger.error(f"Failed to process crawl result: {str(e)}")
            raise
    
    def _process_string_result(
        self,
        content: str,
        collection_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Process string content (e.g., from web_content_extract).
        
        Args:
            content: String content to process.
            collection_name: Target collection name.
            
        Returns:
            List of processed chunks.
        """
        if not content or not content.strip():
            logger.warning("Empty string content provided")
            return []
        
        # Normalize content
        normalized_content = self.normalize_content(content)
        
        # Split into chunks
        chunks = self.split_text(normalized_content)
        
        # Create processed chunks with metadata
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            metadata = self.extract_metadata(
                content=chunk,
                additional_metadata={
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "collection_name": collection_name,
                    "source_type": "string"
                }
            )
            
            chunk_id = self._generate_chunk_id(chunk, i)
            
            processed_chunks.append({
                "id": chunk_id,
                "content": chunk,
                "metadata": metadata
            })
        
        logger.info(f"Processed string result into {len(processed_chunks)} chunks")
        return processed_chunks
    
    def _process_dict_result(
        self,
        result_dict: Dict[str, Any],
        collection_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Process dict result (e.g., from domain_deep_crawl).
        
        Args:
            result_dict: Dictionary containing crawl results.
            collection_name: Target collection name.
            
        Returns:
            List of processed chunks.
        """
        if not result_dict.get("success", False):
            logger.warning("Processing unsuccessful crawl result")
            return []
        
        results = result_dict.get("results", [])
        if not results:
            logger.warning("No results found in crawl result dict")
            return []
        
        all_processed_chunks = []
        
        for result_index, result in enumerate(results):
            content = result.get("markdown") or result.get("extracted_content", "")
            if not content:
                continue
            
            # Normalize content
            normalized_content = self.normalize_content(content)
            
            # Split into chunks
            chunks = self.split_text(normalized_content)
            
            # Extract base metadata from result
            base_metadata = {
                "url": result.get("url"),
                "title": result.get("title"),
                "collection_name": collection_name,
                "source_type": "dict",
                "result_index": result_index,
                "status_code": result.get("status_code"),
                "success": result.get("success", True)
            }
            
            # Add any additional metadata from the result
            if "metadata" in result:
                base_metadata.update(result["metadata"])
            
            # Create processed chunks
            for chunk_index, chunk in enumerate(chunks):
                metadata = self.extract_metadata(
                    content=chunk,
                    url=base_metadata["url"],
                    title=base_metadata["title"],
                    additional_metadata={
                        **base_metadata,
                        "chunk_index": chunk_index,
                        "total_chunks": len(chunks)
                    }
                )
                
                chunk_id = self._generate_chunk_id(chunk, chunk_index, base_metadata.get("url"))
                
                all_processed_chunks.append({
                    "id": chunk_id,
                    "content": chunk,
                    "metadata": metadata
                })
        
        logger.info(f"Processed dict result into {len(all_processed_chunks)} chunks")
        return all_processed_chunks
    
    def _extract_domain(self, url: str) -> Optional[str]:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return None
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate MD5 hash of content."""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _detect_language(self, content: str) -> str:
        """Basic language detection (placeholder implementation)."""
        # Simple heuristic - could be replaced with proper language detection library
        if any(char in content for char in "ñáéíóúü"):
            return "es"
        elif any(char in content for char in "àâäéèêëïîôùûüÿç"):
            return "fr"
        else:
            return "en"  # Default to English
    
    def _detect_content_type(self, content: str) -> str:
        """Detect content type based on patterns."""
        if content.startswith("#") or "##" in content[:100]:
            return "markdown"
        elif content.startswith("<!DOCTYPE") or "<html" in content[:100]:
            return "html"
        elif content.startswith("{") or content.startswith("["):
            return "json"
        else:
            return "text"
    
    def _generate_chunk_id(
        self,
        chunk: str,
        chunk_index: int,
        url: Optional[str] = None
    ) -> str:
        """Generate unique ID for a chunk."""
        # Create a unique identifier based on content hash and index
        content_hash = hashlib.md5(chunk.encode('utf-8')).hexdigest()[:8]
        
        if url:
            url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()[:4]
            return f"{url_hash}_{content_hash}_{chunk_index}"
        else:
            return f"{content_hash}_{chunk_index}"