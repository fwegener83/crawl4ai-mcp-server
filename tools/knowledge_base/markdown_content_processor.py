"""
Enhanced Markdown Content Processor with intelligent chunking.

This module implements a two-stage intelligent splitting approach:
1. MarkdownHeaderTextSplitter for structure-aware segmentation
2. RecursiveCharacterTextSplitter for size-controlled chunking

Based on research findings:
- Context7 MCP: markdown2 library (Trust Score 9.2, 275 code examples)
- LangChain best practices: Header-aware splitting with size control
- Performance target: <500ms for 1MB files, optimal embedding chunks
"""

import os
import logging
import hashlib
import re
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone

from .dependencies import rag_deps, ensure_rag_available, is_rag_available

logger = logging.getLogger(__name__)


@dataclass
class ChunkMetadata:
    """Enhanced metadata for markdown chunks."""
    chunk_index: int
    total_chunks: int
    chunk_type: str  # 'header_section', 'code_block', 'list', 'paragraph'
    content_hash: str
    header_hierarchy: List[str]  # ['# Main', '## Sub']
    contains_code: bool
    programming_language: Optional[str]
    word_count: int
    character_count: int
    created_at: str


class MarkdownContentProcessor:
    """
    Enhanced content processor with intelligent markdown-aware chunking.
    
    Features:
    - Two-stage splitting: structure → size control
    - Header hierarchy preservation 
    - Code block integrity maintenance
    - Language detection for code blocks
    - Rich metadata for better search
    """
    
    def __init__(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        preserve_code_blocks: bool = True,
        preserve_tables: bool = True
    ):
        """Initialize enhanced markdown processor.
        
        Args:
            chunk_size: Maximum size of text chunks (default: 1000 for optimal embeddings)
            chunk_overlap: Overlap between chunks (default: 200)
            preserve_code_blocks: Whether to keep code blocks intact
            preserve_tables: Whether to keep tables intact
        """
        ensure_rag_available()
        
        self.chunk_size = chunk_size or int(os.getenv("RAG_CHUNK_SIZE", "1000"))
        self.chunk_overlap = chunk_overlap or int(os.getenv("RAG_CHUNK_OVERLAP", "200"))
        self.preserve_code_blocks = preserve_code_blocks
        self.preserve_tables = preserve_tables
        
        # Initialize markdown2 parser with comprehensive extras
        markdown2 = rag_deps.get_component('markdown2')
        self.markdown_parser = markdown2.Markdown(extras=[
            'fenced-code-blocks',    # ```python code```
            'header-ids',            # Header ID generation
            'tables',                # GFM tables
            'code-friendly',         # Better code handling
            'cuddled-lists',         # List formatting
            'metadata',              # YAML front matter
            'footnotes',             # Footnote support
            'task_list'              # GitHub-style checkboxes
        ])
        
        # Initialize LangChain components for intelligent splitting
        MarkdownHeaderTextSplitter = rag_deps.get_component('MarkdownHeaderTextSplitter')
        RecursiveCharacterTextSplitter = rag_deps.get_component('RecursiveCharacterTextSplitter')
        
        # Configure header-aware splitting
        self.header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "Header 1"),
                ("##", "Header 2"), 
                ("###", "Header 3"),
                ("####", "Header 4"),
                ("#####", "Header 5"),
                ("######", "Header 6"),
            ],
            strip_headers=False,  # Preserve header context for better search
            return_each_line=False
        )
        
        # Configure size-controlled splitting with markdown-optimized separators
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=[
                "\n\n",      # Paragraphs (highest priority)
                "\n",        # Lines
                ". ",        # Sentences
                ", ",        # Clauses  
                " ",         # Words
                ""           # Characters (last resort)
            ],
            length_function=len,
            is_separator_regex=False
        )
        
        logger.info(f"MarkdownContentProcessor initialized: chunk_size={self.chunk_size}, "
                   f"overlap={self.chunk_overlap}, preserve_code={preserve_code_blocks}")
    
    def split_markdown_intelligently(self, content: str, source_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Perform intelligent two-stage markdown splitting.
        
        Args:
            content: Markdown content to split
            source_metadata: Additional metadata (url, title, etc.)
            
        Returns:
            List of enhanced chunks with rich metadata
        """
        if not content or not content.strip():
            logger.warning("Empty content provided for markdown splitting")
            return []
        
        try:
            # Stage 1: Structure-aware splitting by headers
            logger.debug(f"Stage 1: Header-based splitting for {len(content)} characters")
            header_splits = self._split_by_headers(content)
            
            # Stage 2: Size-controlled splitting while preserving structure
            logger.debug(f"Stage 2: Size-controlled splitting of {len(header_splits)} sections")
            final_chunks = []
            
            for section_idx, section in enumerate(header_splits):
                section_chunks = self._split_section_intelligently(
                    section, 
                    section_idx, 
                    source_metadata or {}
                )
                final_chunks.extend(section_chunks)
            
            # Stage 3: Generate comprehensive metadata
            enhanced_chunks = self._enhance_chunks_with_metadata(final_chunks, content, source_metadata)
            
            logger.info(f"Markdown splitting complete: {len(content)} chars → {len(enhanced_chunks)} chunks")
            return enhanced_chunks
            
        except Exception as e:
            logger.error(f"Failed to split markdown content: {str(e)}")
            raise
    
    def _split_by_headers(self, content: str) -> List[Dict[str, Any]]:
        """Split content by markdown headers using LangChain's MarkdownHeaderTextSplitter."""
        try:
            # Use LangChain's header splitter for structure recognition
            docs = self.header_splitter.split_text(content)
            
            sections = []
            for doc in docs:
                # Extract header hierarchy from metadata
                header_hierarchy = []
                for i in range(1, 7):  # H1 to H6
                    header_key = f"Header {i}"
                    if header_key in doc.metadata:
                        header_hierarchy.append(doc.metadata[header_key])
                
                sections.append({
                    'content': doc.page_content,
                    'header_hierarchy': header_hierarchy,
                    'metadata': doc.metadata
                })
            
            return sections
            
        except Exception as e:
            logger.warning(f"Header splitting failed, falling back to basic splitting: {str(e)}")
            # Fallback: treat entire content as single section
            return [{'content': content, 'header_hierarchy': [], 'metadata': {}}]
    
    def _split_section_intelligently(self, section: Dict[str, Any], section_idx: int, source_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split a header section while preserving code blocks and other structures."""
        content = section['content']
        
        # Check if section contains code blocks
        if self.preserve_code_blocks and self._contains_code_blocks(content):
            return self._split_with_code_preservation(section, section_idx, source_metadata)
        
        # Check if section contains tables
        if self.preserve_tables and self._contains_tables(content):
            return self._split_with_table_preservation(section, section_idx, source_metadata)
        
        # Standard recursive splitting for text content
        return self._split_text_content(section, section_idx, source_metadata)
    
    def _split_with_code_preservation(self, section: Dict[str, Any], section_idx: int, source_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split content while keeping code blocks intact."""
        content = section['content']
        chunks = []
        
        # Split by code block boundaries
        code_block_pattern = r'(```[\s\S]*?```|`[^`\n]+`)'
        parts = re.split(code_block_pattern, content)
        
        current_chunk = ""
        
        for part in parts:
            # If this part is a code block, handle specially
            if re.match(code_block_pattern, part):
                # If adding this code block would exceed chunk size, finalize current chunk
                if current_chunk and len(current_chunk + part) > self.chunk_size:
                    chunks.append(self._create_chunk(current_chunk, section, section_idx, len(chunks)))
                    current_chunk = part
                else:
                    current_chunk += part
            else:
                # Regular text - can be split normally
                if not part.strip():
                    current_chunk += part
                    continue
                
                # If adding this text would exceed chunk size, split it
                if current_chunk and len(current_chunk + part) > self.chunk_size:
                    chunks.append(self._create_chunk(current_chunk, section, section_idx, len(chunks)))
                    current_chunk = ""
                
                # Split the text part if it's too long
                if len(part) > self.chunk_size:
                    text_chunks = self.text_splitter.split_text(part)
                    for i, text_chunk in enumerate(text_chunks):
                        if i == 0:
                            current_chunk += text_chunk
                        else:
                            if current_chunk:
                                chunks.append(self._create_chunk(current_chunk, section, section_idx, len(chunks)))
                            current_chunk = text_chunk
                else:
                    current_chunk += part
        
        # Add final chunk if any content remains
        if current_chunk.strip():
            chunks.append(self._create_chunk(current_chunk, section, section_idx, len(chunks)))
        
        return chunks
    
    def _split_with_table_preservation(self, section: Dict[str, Any], section_idx: int, source_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split content while keeping tables intact."""
        content = section['content']
        
        # Simple table detection - more sophisticated version could use markdown2 parsing
        # Note: markdown2 is accessed via rag_deps.get_component('markdown2')
        table_pattern = r'(\n\|.*\|\n(\|.*\|\n)*)'
        parts = re.split(table_pattern, content)
        
        chunks = []
        current_chunk = ""
        
        for part in parts:
            if not part:
                continue
                
            # If this looks like a table, preserve it
            if re.match(table_pattern, part):
                if current_chunk and len(current_chunk + part) > self.chunk_size:
                    chunks.append(self._create_chunk(current_chunk, section, section_idx, len(chunks)))
                    current_chunk = part
                else:
                    current_chunk += part
            else:
                # Regular text splitting
                if len(current_chunk + part) > self.chunk_size:
                    if current_chunk:
                        chunks.append(self._create_chunk(current_chunk, section, section_idx, len(chunks)))
                    
                    # Split the part if it's too long
                    if len(part) > self.chunk_size:
                        text_chunks = self.text_splitter.split_text(part)
                        for i, text_chunk in enumerate(text_chunks):
                            if i == len(text_chunks) - 1:
                                current_chunk = text_chunk
                            else:
                                chunks.append(self._create_chunk(text_chunk, section, section_idx, len(chunks)))
                    else:
                        current_chunk = part
                else:
                    current_chunk += part
        
        if current_chunk.strip():
            chunks.append(self._create_chunk(current_chunk, section, section_idx, len(chunks)))
        
        return chunks
    
    def _split_text_content(self, section: Dict[str, Any], section_idx: int, source_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split regular text content using RecursiveCharacterTextSplitter."""
        content = section['content']
        
        # Use LangChain's recursive splitter for optimal text splitting
        text_chunks = self.text_splitter.split_text(content)
        
        chunks = []
        for chunk_idx, chunk_text in enumerate(text_chunks):
            chunks.append(self._create_chunk(chunk_text, section, section_idx, chunk_idx))
        
        return chunks
    
    def _create_chunk(self, content: str, section: Dict[str, Any], section_idx: int, chunk_idx: int) -> Dict[str, Any]:
        """Create a chunk dictionary with basic structure."""
        return {
            'content': content,
            'section_index': section_idx,
            'chunk_index': chunk_idx,
            'header_hierarchy': section.get('header_hierarchy', []),
            'section_metadata': section.get('metadata', {})
        }
    
    def _enhance_chunks_with_metadata(self, chunks: List[Dict[str, Any]], original_content: str, source_metadata: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add comprehensive metadata to each chunk."""
        enhanced_chunks = []
        
        for i, chunk in enumerate(chunks):
            content = chunk['content']
            
            # Detect chunk type
            chunk_type = self._detect_chunk_type(content)
            
            # Detect programming language for any chunk that contains code
            programming_language = self._detect_programming_language(content) if ('```' in content or '`' in content) else None
            
            # Generate content hash for change detection
            content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
            
            # Create comprehensive metadata
            metadata = ChunkMetadata(
                chunk_index=i,
                total_chunks=len(chunks),
                chunk_type=chunk_type,
                content_hash=content_hash,
                header_hierarchy=chunk.get('header_hierarchy', []),
                contains_code='```' in content or '`' in content,
                programming_language=programming_language,
                word_count=len(content.split()),
                character_count=len(content),
                created_at=datetime.now(timezone.utc).isoformat()
            )
            
            # Combine with source metadata
            final_metadata = {
                **metadata.__dict__,
                **(source_metadata or {}),
                **(chunk.get('section_metadata', {}))
            }
            
            enhanced_chunks.append({
                'id': self._generate_chunk_id(content, i),
                'content': content,
                'metadata': final_metadata
            })
        
        return enhanced_chunks
    
    def _contains_code_blocks(self, content: str) -> bool:
        """Check if content contains code blocks."""
        return bool(re.search(r'```[\s\S]*?```', content)) or bool(re.search(r'    .+', content, re.MULTILINE))
    
    def _contains_tables(self, content: str) -> bool:
        """Check if content contains markdown tables."""
        return bool(re.search(r'\n\|.*\|\n', content))
    
    def _detect_chunk_type(self, content: str) -> str:
        """Detect the type of content in a chunk."""
        content_stripped = content.strip()
        
        if re.match(r'^```[\s\S]*```$', content_stripped):
            return 'code_block'
        elif re.search(r'\n\|.*\|\n', content):
            return 'table'
        elif re.match(r'^#{1,6}\s', content_stripped):
            return 'header_section'
        elif re.search(r'^\s*[-*+]\s', content_stripped, re.MULTILINE):
            return 'list'
        elif re.search(r'^\s*\d+\.\s', content_stripped, re.MULTILINE):
            return 'ordered_list'
        elif re.search(r'^>\s', content_stripped, re.MULTILINE):
            return 'blockquote'
        else:
            return 'paragraph'
    
    def _detect_programming_language(self, content: str) -> Optional[str]:
        """Detect programming language from code block."""
        # Extract language from fenced code block
        match = re.match(r'^```(\w+)', content.strip())
        if match:
            return match.group(1).lower()
        
        # Simple heuristic-based detection for indented code blocks
        if 'def ' in content and ':' in content:
            return 'python'
        elif 'function ' in content and '{' in content:
            return 'javascript'
        elif '#include' in content and 'int main' in content:
            return 'c'
        elif 'public class' in content and '{' in content:
            return 'java'
        
        return None
    
    def _generate_chunk_id(self, content: str, chunk_index: int) -> str:
        """Generate unique ID for a chunk."""
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()[:8]
        return f"chunk_{content_hash}_{chunk_index}"
    
    def compare_with_baseline(self, content: str, baseline_processor) -> Dict[str, Any]:
        """
        Compare this processor with the baseline RecursiveCharacterTextSplitter.
        
        Args:
            content: Test content
            baseline_processor: Original ContentProcessor instance
            
        Returns:
            Comparison metrics
        """
        import time
        
        # Time our processor
        start_time = time.time()
        our_chunks = self.split_markdown_intelligently(content)
        our_time = time.time() - start_time
        
        # Time baseline processor
        start_time = time.time()
        baseline_chunks = baseline_processor.split_text(content)
        baseline_time = time.time() - start_time
        
        # Calculate metrics
        return {
            'our_chunks': len(our_chunks),
            'baseline_chunks': len(baseline_chunks),
            'our_time': our_time,
            'baseline_time': baseline_time,
            'time_ratio': our_time / baseline_time if baseline_time > 0 else float('inf'),
            'chunk_ratio': len(our_chunks) / len(baseline_chunks) if baseline_chunks else float('inf'),
            'our_avg_chunk_size': sum(len(c['content']) for c in our_chunks) / len(our_chunks) if our_chunks else 0,
            'baseline_avg_chunk_size': sum(len(c) for c in baseline_chunks) / len(baseline_chunks) if baseline_chunks else 0,
            'semantic_preservation_score': self._calculate_semantic_score(our_chunks)
        }
    
    def _calculate_semantic_score(self, chunks: List[Dict[str, Any]]) -> float:
        """Calculate a semantic preservation score based on chunk types and structure."""
        if not chunks:
            return 0.0
        
        score = 0.0
        
        # Reward preserved code blocks
        code_chunks = sum(1 for c in chunks if c['metadata']['chunk_type'] == 'code_block')
        score += (code_chunks / len(chunks)) * 0.3
        
        # Reward preserved header hierarchy
        header_chunks = sum(1 for c in chunks if c['metadata']['header_hierarchy'])
        score += (header_chunks / len(chunks)) * 0.3
        
        # Reward balanced chunk sizes (not too small, not too large)
        avg_size = sum(c['metadata']['character_count'] for c in chunks) / len(chunks)
        if 500 <= avg_size <= 1500:  # Optimal range for embeddings
            score += 0.2
        
        # Reward metadata richness
        avg_metadata_fields = sum(len(c['metadata']) for c in chunks) / len(chunks)
        score += min(avg_metadata_fields / 20, 0.2)  # Cap at 0.2
        
        return min(score, 1.0)  # Cap at 1.0