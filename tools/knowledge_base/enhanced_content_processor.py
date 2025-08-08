"""
Enhanced Content Processor with intelligent chunking strategy selection and A/B testing.

This module provides a unified interface for content processing with configurable
chunking strategies including baseline RecursiveCharacterTextSplitter and the new
intelligent MarkdownContentProcessor.
"""

import os
import logging
import time
from typing import Dict, Any, List, Optional, Union, Literal
from dataclasses import dataclass
from datetime import datetime, timezone

from .content_processor import ContentProcessor
from .markdown_content_processor import MarkdownContentProcessor
from .dependencies import is_rag_available

logger = logging.getLogger(__name__)

ChunkingStrategy = Literal["baseline", "markdown_intelligent", "auto"]


@dataclass
class ChunkingComparisonResult:
    """Results from A/B testing different chunking strategies."""
    baseline_chunks: int
    enhanced_chunks: int
    baseline_time: float
    enhanced_time: float
    baseline_avg_size: float
    enhanced_avg_size: float
    semantic_preservation_score: float
    quality_improvement_ratio: float
    performance_ratio: float
    recommendation: ChunkingStrategy


class EnhancedContentProcessor:
    """
    Enhanced content processor with configurable chunking strategies and A/B testing.
    
    Features:
    - Multiple chunking strategies (baseline, markdown-intelligent, auto-selection)
    - A/B testing framework for strategy comparison
    - Performance benchmarking and quality metrics
    - Configuration-driven strategy selection
    - Backward compatibility with existing ContentProcessor API
    """
    
    def __init__(
        self,
        chunking_strategy: ChunkingStrategy = "auto",
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        enable_ab_testing: bool = True,
        quality_threshold: float = 0.7
    ):
        """Initialize enhanced content processor.
        
        Args:
            chunking_strategy: Strategy to use for chunking
            chunk_size: Maximum chunk size (defaults from env/config)
            chunk_overlap: Chunk overlap size (defaults from env/config)
            enable_ab_testing: Enable A/B testing and comparison features
            quality_threshold: Minimum quality score for auto-selection
        """
        if not is_rag_available():
            raise ImportError("RAG dependencies required for EnhancedContentProcessor")
        
        self.chunking_strategy = chunking_strategy
        self.chunk_size = chunk_size or int(os.getenv("RAG_CHUNK_SIZE", "1000"))
        self.chunk_overlap = chunk_overlap or int(os.getenv("RAG_CHUNK_OVERLAP", "200"))
        self.enable_ab_testing = enable_ab_testing
        self.quality_threshold = quality_threshold
        
        # Initialize processors
        self.baseline_processor = ContentProcessor(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        
        self.markdown_processor = MarkdownContentProcessor(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        
        # Performance tracking
        self.performance_stats = {
            "total_processed": 0,
            "baseline_used": 0,
            "markdown_used": 0,
            "auto_selected": 0,
            "avg_processing_time": 0.0
        }
        
        logger.info(f"EnhancedContentProcessor initialized with strategy='{chunking_strategy}', "
                   f"ab_testing={enable_ab_testing}")
    
    def process_content(
        self,
        content: str,
        source_metadata: Optional[Dict[str, Any]] = None,
        force_strategy: Optional[ChunkingStrategy] = None
    ) -> List[Dict[str, Any]]:
        """
        Process content using the configured or specified chunking strategy.
        
        Args:
            content: Content to process
            source_metadata: Additional metadata (url, title, etc.)
            force_strategy: Override configured strategy for this call
            
        Returns:
            List of enhanced chunks with metadata
        """
        if not content or not content.strip():
            logger.warning("Empty content provided for processing")
            return []
        
        start_time = time.time()
        strategy = force_strategy or self.chunking_strategy
        
        try:
            # Determine effective strategy
            if strategy == "auto":
                strategy = self._select_optimal_strategy(content)
                self.performance_stats["auto_selected"] += 1
            
            # Process with selected strategy
            if strategy == "markdown_intelligent":
                chunks = self._process_with_markdown_strategy(content, source_metadata)
                self.performance_stats["markdown_used"] += 1
            else:  # baseline
                chunks = self._process_with_baseline_strategy(content, source_metadata)
                self.performance_stats["baseline_used"] += 1
            
            # Update performance stats
            processing_time = time.time() - start_time
            self._update_performance_stats(processing_time)
            
            # Add strategy info to metadata
            for chunk in chunks:
                chunk['metadata']['chunking_strategy'] = strategy
                chunk['metadata']['processing_time'] = processing_time
                chunk['metadata']['processor_version'] = 'enhanced'
            
            logger.info(f"Processed content with {strategy} strategy: "
                       f"{len(content)} chars → {len(chunks)} chunks in {processing_time:.3f}s")
            
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to process content with {strategy} strategy: {str(e)}")
            raise
    
    def compare_strategies(
        self,
        content: str,
        source_metadata: Optional[Dict[str, Any]] = None
    ) -> ChunkingComparisonResult:
        """
        Perform A/B testing comparison between chunking strategies.
        
        Args:
            content: Content to test with
            source_metadata: Additional metadata for processing
            
        Returns:
            Detailed comparison results
        """
        if not self.enable_ab_testing:
            raise ValueError("A/B testing is disabled for this processor instance")
        
        if not content or not content.strip():
            raise ValueError("Cannot compare strategies with empty content")
        
        logger.info(f"Starting A/B comparison for {len(content)} character content")
        
        # Test baseline strategy
        start_time = time.time()
        baseline_chunks = self._process_with_baseline_strategy(content, source_metadata)
        baseline_time = time.time() - start_time
        
        # Test enhanced strategy
        start_time = time.time()
        enhanced_chunks = self._process_with_markdown_strategy(content, source_metadata)
        enhanced_time = time.time() - start_time
        
        # Calculate metrics
        baseline_avg_size = (
            sum(len(c['content']) for c in baseline_chunks) / len(baseline_chunks)
            if baseline_chunks else 0
        )
        
        enhanced_avg_size = (
            sum(c['metadata']['character_count'] for c in enhanced_chunks) / len(enhanced_chunks)
            if enhanced_chunks else 0
        )
        
        # Calculate semantic preservation score
        semantic_score = self._calculate_enhanced_semantic_score(enhanced_chunks)
        
        # Quality improvement ratio (enhanced vs baseline)
        quality_improvement = semantic_score if semantic_score > 0 else 0.5
        
        # Performance ratio (time comparison)
        performance_ratio = baseline_time / enhanced_time if enhanced_time > 0 else 1.0
        
        # Generate recommendation
        recommendation = self._generate_strategy_recommendation(
            quality_improvement, performance_ratio, content
        )
        
        result = ChunkingComparisonResult(
            baseline_chunks=len(baseline_chunks),
            enhanced_chunks=len(enhanced_chunks),
            baseline_time=baseline_time,
            enhanced_time=enhanced_time,
            baseline_avg_size=baseline_avg_size,
            enhanced_avg_size=enhanced_avg_size,
            semantic_preservation_score=semantic_score,
            quality_improvement_ratio=quality_improvement,
            performance_ratio=performance_ratio,
            recommendation=recommendation
        )
        
        logger.info(f"A/B comparison complete: {result.recommendation} recommended "
                   f"(quality={quality_improvement:.2f}, perf={performance_ratio:.2f})")
        
        return result
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get processor performance statistics."""
        return {
            **self.performance_stats,
            "configuration": {
                "strategy": self.chunking_strategy,
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap,
                "ab_testing_enabled": self.enable_ab_testing,
                "quality_threshold": self.quality_threshold
            }
        }
    
    def _process_with_baseline_strategy(
        self,
        content: str,
        source_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Process content using baseline RecursiveCharacterTextSplitter."""
        # Use the baseline processor's method
        chunks = self.baseline_processor.split_text(content)
        
        # Convert to enhanced format
        enhanced_chunks = []
        for i, chunk_text in enumerate(chunks):
            metadata = self.baseline_processor.extract_metadata(
                content=chunk_text,
                url=source_metadata.get('url') if source_metadata else None,
                title=source_metadata.get('title') if source_metadata else None,
                additional_metadata={
                    **(source_metadata or {}),
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'chunking_method': 'baseline',
                    'created_at': datetime.now(timezone.utc).isoformat()
                }
            )
            
            # Generate unique chunk ID including collection info
            chunk_id = self.baseline_processor._generate_chunk_id(
                chunk_text, i,
                collection_name=source_metadata.get('collection_name') if source_metadata else None,
                file_path=source_metadata.get('file_path') if source_metadata else None
            )
            
            enhanced_chunks.append({
                'id': chunk_id,
                'content': chunk_text,
                'metadata': metadata
            })
        
        return enhanced_chunks
    
    def _process_with_markdown_strategy(
        self,
        content: str,
        source_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Process content using intelligent MarkdownContentProcessor."""
        return self.markdown_processor.split_markdown_intelligently(
            content, source_metadata
        )
    
    def _select_optimal_strategy(self, content: str) -> ChunkingStrategy:
        """
        Automatically select optimal chunking strategy based on content analysis.
        
        Args:
            content: Content to analyze
            
        Returns:
            Recommended strategy
        """
        # Quick heuristics for strategy selection
        content_lower = content.lower()
        
        # Strong indicators for markdown processing
        if any([
            content.count('#') >= 3,  # Multiple headers
            '```' in content,  # Code blocks
            content.count('|') >= 6,  # Likely tables
            content.count('\n\n') / len(content) > 0.02,  # Well-structured paragraphs
        ]):
            logger.debug("Auto-selected markdown_intelligent strategy (structured content detected)")
            return "markdown_intelligent"
        
        # Default to baseline for simple text
        logger.debug("Auto-selected baseline strategy (simple text detected)")
        return "baseline"
    
    def _calculate_enhanced_semantic_score(self, chunks: List[Dict[str, Any]]) -> float:
        """
        Calculate semantic preservation score for enhanced chunks.
        
        Args:
            chunks: Enhanced chunks to analyze
            
        Returns:
            Semantic score (0.0 to 1.0)
        """
        if not chunks:
            return 0.0
        
        score = 0.0
        total_weight = 0.0
        
        # Structure preservation (30% weight)
        header_chunks = sum(1 for c in chunks if c['metadata'].get('header_hierarchy'))
        structure_score = min(header_chunks / len(chunks), 1.0)
        score += structure_score * 0.3
        total_weight += 0.3
        
        # Code preservation (25% weight)
        code_chunks = sum(1 for c in chunks if c['metadata'].get('contains_code'))
        full_content = ' '.join(c['content'] for c in chunks)
        expected_code_blocks = full_content.count('```') // 2  # Each code block has opening and closing
        code_score = min(code_chunks / max(1, expected_code_blocks), 1.0) if expected_code_blocks > 0 else 0.0
        score += code_score * 0.25
        total_weight += 0.25
        
        # Chunk size balance (20% weight)
        avg_size = sum(c['metadata'].get('character_count', 0) for c in chunks) / len(chunks)
        size_score = 1.0 if 500 <= avg_size <= 1500 else max(0.0, 1.0 - abs(avg_size - 1000) / 1000)
        score += size_score * 0.2
        total_weight += 0.2
        
        # Metadata richness (15% weight)
        avg_metadata_fields = sum(len(c['metadata']) for c in chunks) / len(chunks)
        metadata_score = min(avg_metadata_fields / 15, 1.0)
        score += metadata_score * 0.15
        total_weight += 0.15
        
        # Language detection accuracy (10% weight)
        lang_detected_chunks = sum(1 for c in chunks if c['metadata'].get('programming_language'))
        lang_score = min(lang_detected_chunks / max(1, len([c for c in chunks if '```' in c['content']])), 1.0)
        score += lang_score * 0.1
        total_weight += 0.1
        
        return score / total_weight if total_weight > 0 else 0.0
    
    def _generate_strategy_recommendation(
        self,
        quality_improvement: float,
        performance_ratio: float,
        content: str
    ) -> ChunkingStrategy:
        """
        Generate strategy recommendation based on quality and performance metrics.
        
        Args:
            quality_improvement: Quality improvement ratio
            performance_ratio: Performance ratio (baseline_time / enhanced_time)
            content: Original content for context
            
        Returns:
            Recommended strategy
        """
        # If quality improvement is significant and performance is acceptable
        if quality_improvement >= self.quality_threshold and performance_ratio >= 0.5:
            return "markdown_intelligent"
        
        # If content is clearly markdown-structured, prefer intelligent processing
        if any([
            content.count('#') >= 5,
            '```' in content and content.count('```') >= 4,
            content.count('|') >= 10,  # Tables
        ]):
            return "markdown_intelligent"
        
        # Default to baseline for simple content or performance concerns
        return "baseline"
    
    def _update_performance_stats(self, processing_time: float):
        """Update internal performance statistics."""
        self.performance_stats["total_processed"] += 1
        
        # Update rolling average processing time
        current_avg = self.performance_stats["avg_processing_time"]
        total_processed = self.performance_stats["total_processed"]
        
        self.performance_stats["avg_processing_time"] = (
            (current_avg * (total_processed - 1) + processing_time) / total_processed
        )
    
    # Backward compatibility methods
    def split_text(self, text: str) -> List[str]:
        """Backward compatible split_text method."""
        chunks = self.process_content(text)
        return [chunk['content'] for chunk in chunks]
    
    def extract_metadata(
        self,
        content: str,
        url: Optional[str] = None,
        title: Optional[str] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Backward compatible metadata extraction."""
        return self.baseline_processor.extract_metadata(
            content, url, title, additional_metadata
        )