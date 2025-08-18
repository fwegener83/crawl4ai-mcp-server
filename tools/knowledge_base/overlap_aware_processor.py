"""
Overlap-Aware Markdown Content Processor with configurable chunk overlap.

This module extends the existing MarkdownContentProcessor with sophisticated 
overlap calculation capabilities, providing 20-30% configurable overlap
between consecutive chunks while preserving semantic boundaries.

Implements requirements from the enhanced RAG chunking strategy plan:
- Configurable overlap percentage (20-30%)
- Chunk relationship tracking with metadata
- Performance optimization within plan budgets
- Backward compatibility with existing processor interface
"""

import os
import logging
import hashlib
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

from .markdown_content_processor import MarkdownContentProcessor, ChunkMetadata
from .chunking_config import get_chunking_config
from .dependencies import ensure_rag_available

logger = logging.getLogger(__name__)


@dataclass
class OverlapAwareChunkMetadata(ChunkMetadata):
    """Enhanced metadata for overlap-aware chunks."""
    # Overlap tracking fields
    overlap_sources: List[str]  # IDs of chunks this overlaps with
    overlap_regions: List[Tuple[int, int]]  # Character ranges of overlaps
    overlap_percentage: float  # Actual overlap percentage achieved
    
    # Neighbor relationships
    previous_chunk_id: Optional[str]
    next_chunk_id: Optional[str]
    section_siblings: List[str]
    
    # Context expansion eligibility
    context_expansion_eligible: bool
    expansion_threshold: float  # Score threshold for expansion
    
    # Performance metrics
    storage_efficiency_ratio: float  # Ratio of unique to total content
    processing_time_ms: float  # Time taken to create this chunk


class OverlapAwareMarkdownProcessor(MarkdownContentProcessor):
    """
    Enhanced MarkdownContentProcessor with configurable chunk overlap.
    
    Extends the base processor with:
    - 20-30% configurable overlap between consecutive chunks
    - Intelligent overlap boundary detection (respects sentences/paragraphs)
    - Chunk relationship tracking and metadata enhancement
    - Performance monitoring and optimization
    - Backward compatibility with existing API
    """
    
    def __init__(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        overlap_percentage: Optional[float] = None,
        preserve_code_blocks: bool = True,
        preserve_tables: bool = True,
        enable_relationship_tracking: bool = True,
        context_expansion_threshold: float = 0.75
    ):
        """Initialize overlap-aware processor.
        
        Args:
            chunk_size: Maximum size of text chunks (default from config)
            chunk_overlap: Overlap between chunks (calculated from percentage if not provided)
            overlap_percentage: Percentage overlap (0.2-0.3, default: 0.25)
            preserve_code_blocks: Whether to keep code blocks intact
            preserve_tables: Whether to keep tables intact
            enable_relationship_tracking: Whether to track chunk relationships
            context_expansion_threshold: Score threshold for context expansion (default: 0.75)
        """
        ensure_rag_available()
        
        # Get configuration
        config = get_chunking_config()
        
        # Set overlap parameters with validation
        self.overlap_percentage = overlap_percentage or 0.25
        if not 0.2 <= self.overlap_percentage <= 0.3:
            raise ValueError(f"Overlap percentage {self.overlap_percentage} must be between 0.2 and 0.3")
        
        # Calculate chunk parameters
        self._chunk_size = chunk_size or config.chunk_size
        self._chunk_overlap = chunk_overlap or int(self._chunk_size * self.overlap_percentage)
        
        # Validate overlap is less than chunk size
        if self._chunk_overlap >= self._chunk_size:
            raise ValueError(f"Chunk overlap {self._chunk_overlap} must be less than chunk size {self._chunk_size}")
        
        # Initialize base processor with calculated parameters
        super().__init__(
            chunk_size=self._chunk_size,
            chunk_overlap=self._chunk_overlap,
            preserve_code_blocks=preserve_code_blocks,
            preserve_tables=preserve_tables
        )
        
        # Overlap-specific configuration
        self.enable_relationship_tracking = enable_relationship_tracking
        self.context_expansion_threshold = context_expansion_threshold
        
        # Performance tracking
        self._chunks_created = 0
        self._total_processing_time = 0.0
        
        logger.info(f"OverlapAwareMarkdownProcessor initialized: "
                   f"chunk_size={self._chunk_size}, overlap={self._chunk_overlap} "
                   f"({self.overlap_percentage:.1%}), threshold={context_expansion_threshold}")
    
    def split_markdown_intelligently_with_overlap(
        self, 
        content: str, 
        source_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Enhanced markdown splitting with overlap calculation.
        
        This is the main entry point that adds overlap functionality to the
        base intelligent splitting while maintaining backward compatibility.
        
        Args:
            content: Markdown content to split
            source_metadata: Additional metadata (url, title, etc.)
            
        Returns:
            List of enhanced chunks with overlap metadata
        """
        if not content or not content.strip():
            logger.warning("Empty content provided for overlap-aware splitting")
            return []
        
        import time
        start_time = time.time()
        
        try:
            logger.debug(f"Starting overlap-aware splitting for {len(content)} characters")
            
            # Stage 1: Get base chunks using parent implementation
            base_chunks = super().split_markdown_intelligently(content, source_metadata)
            
            if not base_chunks:
                logger.warning("No base chunks created from content")
                return []
            
            # Stage 2: Apply overlap calculation to base chunks
            overlapped_chunks = self._apply_overlap_to_chunks(base_chunks, content)
            
            # Stage 3: Generate relationships and enhanced metadata
            if self.enable_relationship_tracking:
                enhanced_chunks = self._generate_chunk_relationships(overlapped_chunks, content, source_metadata)
            else:
                enhanced_chunks = overlapped_chunks
            
            # Stage 4: Performance and quality metrics
            processing_time = (time.time() - start_time) * 1000  # Convert to ms
            self._update_performance_metrics(enhanced_chunks, processing_time)
            
            logger.info(f"Overlap-aware splitting complete: {len(content)} chars → "
                       f"{len(enhanced_chunks)} chunks with {self.overlap_percentage:.1%} overlap "
                       f"({processing_time:.1f}ms)")
            
            return enhanced_chunks
            
        except Exception as e:
            logger.error(f"Failed overlap-aware markdown splitting: {str(e)}")
            raise
    
    def _apply_overlap_to_chunks(self, base_chunks: List[Dict[str, Any]], original_content: str) -> List[Dict[str, Any]]:
        """Apply conservative overlap calculation to base chunks."""
        if len(base_chunks) <= 1:
            # Single chunk or no chunks - no overlap needed
            return self._convert_to_overlap_format(base_chunks)
        
        overlapped_chunks = []
        
        for i, chunk in enumerate(base_chunks):
            chunk_content = chunk.get('content', '')
            
            # Apply more conservative overlap strategy
            overlapped_content, overlap_metadata = self._create_conservative_overlap(
                chunk_content, base_chunks, i
            )
            
            # Convert to overlap-aware format
            overlap_chunk = self._create_overlap_chunk(
                chunk, overlapped_content, overlap_metadata, i, len(base_chunks)
            )
            
            overlapped_chunks.append(overlap_chunk)
        
        return overlapped_chunks
    
    def _create_conservative_overlap(
        self, 
        chunk_content: str, 
        all_chunks: List[Dict[str, Any]], 
        chunk_index: int
    ) -> Tuple[str, Dict[str, Any]]:
        """Create conservative overlap that respects storage budget."""
        overlapped_content = chunk_content
        overlap_metadata = {
            'overlap_sources': [],
            'overlap_regions': [],
            'overlap_percentage_achieved': 0.0
        }
        
        # Balanced overlap: meaningful context while respecting storage budget
        base_overlap = min(self._chunk_overlap, len(chunk_content) // 3)  # Up to 1/3 of chunk size
        max_overlap_chars = max(50, min(base_overlap, 200))  # Ensure minimum meaningful overlap
        
        # Add overlap from previous chunk (if meaningful)
        if chunk_index > 0:
            prev_chunk = all_chunks[chunk_index - 1]
            prev_content = prev_chunk.get('content', '')
            prev_chunk_id = prev_chunk.get('metadata', {}).get('chunk_id', f'chunk_{chunk_index-1}')
            
            # Take reasonable overlap from end of previous chunk
            actual_overlap = min(max_overlap_chars, len(prev_content) // 2)
            if actual_overlap >= 30 and len(prev_content) > actual_overlap:
                overlap_text = prev_content[-actual_overlap:].strip()
                
                # Add if it provides meaningful context
                if len(overlap_text.split()) >= 2:  # At least 2 words
                    overlapped_content = overlap_text + " " + overlapped_content
                    overlap_metadata['overlap_sources'].append(prev_chunk_id)
                    overlap_metadata['overlap_regions'].append((0, len(overlap_text) + 1))
        
        # Calculate achieved overlap percentage
        if len(overlapped_content) > len(chunk_content):
            total_overlap = len(overlapped_content) - len(chunk_content)
            overlap_metadata['overlap_percentage_achieved'] = total_overlap / len(overlapped_content)
        
        return overlapped_content, overlap_metadata
    
    def _calculate_overlap_positions(
        self, 
        current_chunk: Dict[str, Any], 
        all_chunks: List[Dict[str, Any]], 
        chunk_index: int,
        original_content: str
    ) -> Tuple[int, int]:
        """Calculate optimal overlap positions for current chunk."""
        chunk_content = current_chunk.get('content', '')
        
        # Default positions (no overlap)
        overlap_start = 0
        overlap_end = len(chunk_content)
        
        # Calculate overlap with previous chunk
        if chunk_index > 0:
            prev_chunk = all_chunks[chunk_index - 1]
            prev_content = prev_chunk.get('content', '')
            
            # Find optimal overlap boundary with previous chunk
            overlap_start = self._find_optimal_overlap_boundary(
                prev_content, chunk_content, is_start=True
            )
        
        # Calculate overlap with next chunk
        if chunk_index < len(all_chunks) - 1:
            next_chunk = all_chunks[chunk_index + 1]
            next_content = next_chunk.get('content', '')
            
            # Find optimal overlap boundary with next chunk
            overlap_end = len(chunk_content) - self._find_optimal_overlap_boundary(
                chunk_content, next_content, is_start=False
            )
        
        return overlap_start, overlap_end
    
    def _find_optimal_overlap_boundary(self, content1: str, content2: str, is_start: bool) -> int:
        """Find optimal overlap boundary respecting semantic boundaries."""
        # Calculate target overlap based on the smaller content to avoid excessive overlap
        base_length = min(len(content1), len(content2), self._chunk_size)
        target_overlap_chars = min(int(base_length * self.overlap_percentage), self._chunk_overlap)
        
        if target_overlap_chars <= 0:
            return 0
        
        # Ensure overlap doesn't exceed reasonable limits
        max_reasonable_overlap = min(len(content1) // 3, len(content2) // 3, self._chunk_overlap)
        target_overlap_chars = min(target_overlap_chars, max_reasonable_overlap)
        
        # Look for semantic boundaries (sentences, paragraphs)
        if is_start and len(content1) > target_overlap_chars:
            # Find boundary from the end of content1
            search_start = max(0, len(content1) - target_overlap_chars - 50)
            search_content = content1[search_start:]
            
            # Prefer paragraph breaks, then sentence breaks
            boundaries = [
                (search_content.rfind('\n\n'), 2),  # Paragraph break
                (search_content.rfind('. '), 2),    # Sentence break
                (search_content.rfind('\n'), 1),    # Line break
                (search_content.rfind(' '), 0),     # Word break
            ]
            
            for boundary_pos, boundary_offset in boundaries:
                if boundary_pos != -1:
                    absolute_pos = search_start + boundary_pos + boundary_offset
                    overlap_size = len(content1) - absolute_pos
                    
                    # Check if overlap size is reasonable (stricter bounds)
                    if target_overlap_chars * 0.5 <= overlap_size <= target_overlap_chars * 1.2:
                        return overlap_size
        
        # Fallback to conservative character-based overlap
        return min(target_overlap_chars, len(content1) // 4, len(content2) // 4)
    
    def _create_overlapped_content(
        self, 
        base_content: str, 
        all_chunks: List[Dict[str, Any]], 
        chunk_index: int,
        overlap_start: int, 
        overlap_end: int
    ) -> Tuple[str, Dict[str, Any]]:
        """Create overlapped content and metadata."""
        overlapped_content = base_content
        overlap_metadata = {
            'overlap_sources': [],
            'overlap_regions': [],
            'overlap_percentage_achieved': 0.0
        }
        
        # Add overlap from previous chunk
        if chunk_index > 0 and overlap_start > 0:
            prev_chunk = all_chunks[chunk_index - 1]
            prev_content = prev_chunk.get('content', '')
            prev_chunk_id = prev_chunk.get('metadata', {}).get('chunk_id', f'chunk_{chunk_index-1}')
            
            if len(prev_content) >= overlap_start:
                overlap_text = prev_content[-overlap_start:]
                overlapped_content = overlap_text + overlapped_content
                
                overlap_metadata['overlap_sources'].append(prev_chunk_id)
                overlap_metadata['overlap_regions'].append((0, len(overlap_text)))
        
        # Add overlap from next chunk
        if chunk_index < len(all_chunks) - 1 and overlap_end < len(base_content):
            next_chunk = all_chunks[chunk_index + 1]
            next_content = next_chunk.get('content', '')
            next_chunk_id = next_chunk.get('metadata', {}).get('chunk_id', f'chunk_{chunk_index+1}')
            
            overlap_size = len(base_content) - overlap_end
            if len(next_content) >= overlap_size:
                overlap_text = next_content[:overlap_size]
                overlapped_content = overlapped_content + overlap_text
                
                overlap_metadata['overlap_sources'].append(next_chunk_id)
                overlap_metadata['overlap_regions'].append((len(overlapped_content) - len(overlap_text), len(overlapped_content)))
        
        # Calculate achieved overlap percentage
        if len(base_content) > 0:
            total_overlap = sum(region[1] - region[0] for region in overlap_metadata['overlap_regions'])
            overlap_metadata['overlap_percentage_achieved'] = total_overlap / len(overlapped_content)
        
        return overlapped_content, overlap_metadata
    
    def _create_overlap_chunk(
        self, 
        base_chunk: Dict[str, Any], 
        overlapped_content: str,
        overlap_metadata: Dict[str, Any], 
        chunk_index: int, 
        total_chunks: int
    ) -> Dict[str, Any]:
        """Create overlap-aware chunk with enhanced metadata."""
        # Generate unique chunk ID
        chunk_id = f"overlap_chunk_{hashlib.md5(overlapped_content.encode()).hexdigest()[:8]}_{chunk_index}"
        
        # Create enhanced metadata
        base_metadata = base_chunk.get('metadata', {})
        
        enhanced_metadata = OverlapAwareChunkMetadata(
            # Base metadata from parent
            chunk_index=chunk_index,
            total_chunks=total_chunks,
            chunk_type=base_metadata.get('chunk_type', 'paragraph'),
            content_hash=hashlib.md5(overlapped_content.encode()).hexdigest(),
            header_hierarchy=base_metadata.get('header_hierarchy', []),
            contains_code=self._contains_code_blocks(overlapped_content),
            programming_language=self._detect_programming_language(overlapped_content),
            word_count=len(overlapped_content.split()),
            character_count=len(overlapped_content),
            created_at=datetime.now(timezone.utc).isoformat(),
            
            # Overlap-specific metadata
            overlap_sources=overlap_metadata['overlap_sources'],
            overlap_regions=overlap_metadata['overlap_regions'],
            overlap_percentage=overlap_metadata['overlap_percentage_achieved'],
            
            # Relationship metadata (to be filled by relationship tracking)
            previous_chunk_id=None,  # Will be set in relationship generation
            next_chunk_id=None,      # Will be set in relationship generation
            section_siblings=[],     # Will be set in relationship generation
            
            # Context expansion metadata
            context_expansion_eligible=self._is_context_expansion_eligible(overlapped_content, base_metadata),
            expansion_threshold=self.context_expansion_threshold,
            
            # Performance metadata
            storage_efficiency_ratio=len(base_chunk.get('content', '')) / len(overlapped_content) if overlapped_content else 1.0,
            processing_time_ms=0.0  # Will be set later
        )
        
        return {
            'content': overlapped_content,
            'metadata': asdict(enhanced_metadata),
            'chunk_id': chunk_id
        }
    
    def _generate_chunk_relationships(
        self, 
        chunks: List[Dict[str, Any]], 
        original_content: str,
        source_metadata: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate bidirectional relationships between chunks."""
        if len(chunks) <= 1:
            return chunks
        
        enhanced_chunks = []
        
        for i, chunk in enumerate(chunks):
            metadata = chunk['metadata'].copy()
            
            # Set previous/next chunk relationships
            if i > 0:
                metadata['previous_chunk_id'] = chunks[i-1]['chunk_id']
            if i < len(chunks) - 1:
                metadata['next_chunk_id'] = chunks[i+1]['chunk_id']
            
            # Find section siblings (chunks with same header hierarchy)
            current_hierarchy = metadata.get('header_hierarchy', [])
            siblings = []
            
            for j, other_chunk in enumerate(chunks):
                if i != j:
                    other_hierarchy = other_chunk['metadata'].get('header_hierarchy', [])
                    if current_hierarchy == other_hierarchy:
                        siblings.append(other_chunk['chunk_id'])
            
            metadata['section_siblings'] = siblings
            
            enhanced_chunks.append({
                **chunk,
                'metadata': metadata
            })
        
        return enhanced_chunks
    
    def _is_context_expansion_eligible(self, content: str, metadata: Dict[str, Any]) -> bool:
        """Determine if chunk is eligible for context expansion."""
        chunk_type = metadata.get('chunk_type', 'paragraph')
        word_count = len(content.split())
        
        # Check if content contains code blocks (more reliable than chunk_type)
        if self._contains_code_blocks(content):
            return False
        
        # Eligibility criteria based on plan requirements
        eligible_types = ['header_section', 'paragraph', 'list']
        ineligible_types = ['code_block']
        
        if chunk_type in ineligible_types:
            return False
        
        if chunk_type not in eligible_types:
            return False
        
        # Short chunks are good candidates for expansion
        if word_count < 300:  # Configurable threshold
            return True
        
        return False
    
    def _convert_to_overlap_format(self, base_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert base chunks to overlap format when no overlap is needed."""
        converted_chunks = []
        
        for i, chunk in enumerate(base_chunks):
            overlap_chunk = self._create_overlap_chunk(
                chunk, 
                chunk.get('content', ''), 
                {'overlap_sources': [], 'overlap_regions': [], 'overlap_percentage_achieved': 0.0},
                i, 
                len(base_chunks)
            )
            converted_chunks.append(overlap_chunk)
        
        return converted_chunks
    
    def _update_performance_metrics(self, chunks: List[Dict[str, Any]], processing_time: float) -> None:
        """Update performance tracking metrics."""
        self._chunks_created += len(chunks)
        self._total_processing_time += processing_time
        
        # Update per-chunk processing time
        per_chunk_time = processing_time / max(len(chunks), 1)
        for chunk in chunks:
            chunk['metadata']['processing_time_ms'] = per_chunk_time
        
        # Log performance metrics
        avg_processing_time = self._total_processing_time / max(self._chunks_created, 1)
        logger.debug(f"Performance metrics: {len(chunks)} chunks created in {processing_time:.1f}ms "
                    f"(avg: {avg_processing_time:.1f}ms/chunk)")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for monitoring."""
        return {
            'total_chunks_created': self._chunks_created,
            'total_processing_time_ms': self._total_processing_time,
            'average_processing_time_ms': self._total_processing_time / max(self._chunks_created, 1),
            'overlap_percentage': self.overlap_percentage,
            'chunk_size': self._chunk_size,
            'chunk_overlap': self._chunk_overlap
        }
    
    # Backward compatibility: delegate to overlap-aware method
    def split_markdown_intelligently(self, content: str, source_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Backward compatible interface - delegates to overlap-aware implementation."""
        return self.split_markdown_intelligently_with_overlap(content, source_metadata)


def create_overlap_aware_processor(**kwargs) -> OverlapAwareMarkdownProcessor:
    """Factory function for creating overlap-aware processors with configuration."""
    config = get_chunking_config()
    
    # Merge configuration with provided arguments
    processor_args = {
        'chunk_size': config.chunk_size,
        'overlap_percentage': 0.25,  # Default 25% overlap
        'preserve_code_blocks': True,
        'preserve_tables': True,
        'enable_relationship_tracking': True,
        'context_expansion_threshold': 0.75
    }
    processor_args.update(kwargs)
    
    return OverlapAwareMarkdownProcessor(**processor_args)