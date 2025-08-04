"""
Configuration management for chunking strategies.

This module provides centralized configuration for different chunking strategies,
A/B testing parameters, and performance tuning options.
"""

import os
from typing import Dict, Any, Optional, Literal
from dataclasses import dataclass, asdict

ChunkingStrategy = Literal["baseline", "markdown_intelligent", "auto"]


@dataclass
class ChunkingConfig:
    """Configuration for chunking strategies and A/B testing."""
    
    # Core chunking parameters
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # Strategy selection
    default_strategy: ChunkingStrategy = "auto"
    
    # A/B testing configuration
    enable_ab_testing: bool = True
    quality_threshold: float = 0.7
    performance_threshold: float = 0.5  # Minimum acceptable performance ratio
    
    # Auto-selection parameters
    markdown_detection_threshold: int = 3  # Minimum headers for markdown detection
    code_block_threshold: int = 1  # Minimum code blocks for intelligent processing
    table_threshold: int = 6  # Minimum table cells for table-aware processing
    
    # Performance optimization
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    max_cache_size: int = 1000
    
    # Quality metrics weights
    structure_weight: float = 0.3
    code_weight: float = 0.25
    size_balance_weight: float = 0.2
    metadata_weight: float = 0.15
    language_detection_weight: float = 0.1
    
    @classmethod
    def from_environment(cls) -> 'ChunkingConfig':
        """Create configuration from environment variables."""
        return cls(
            chunk_size=int(os.getenv("RAG_CHUNK_SIZE", "1000")),
            chunk_overlap=int(os.getenv("RAG_CHUNK_OVERLAP", "200")),
            default_strategy=os.getenv("CHUNKING_STRATEGY", "auto"),
            enable_ab_testing=os.getenv("ENABLE_AB_TESTING", "true").lower() == "true",
            quality_threshold=float(os.getenv("QUALITY_THRESHOLD", "0.7")),
            performance_threshold=float(os.getenv("PERFORMANCE_THRESHOLD", "0.5")),
            markdown_detection_threshold=int(os.getenv("MARKDOWN_DETECTION_THRESHOLD", "3")),
            code_block_threshold=int(os.getenv("CODE_BLOCK_THRESHOLD", "1")),
            table_threshold=int(os.getenv("TABLE_THRESHOLD", "6")),
            enable_caching=os.getenv("ENABLE_CHUNKING_CACHE", "true").lower() == "true",
            cache_ttl_seconds=int(os.getenv("CHUNKING_CACHE_TTL", "3600")),
            max_cache_size=int(os.getenv("CHUNKING_CACHE_SIZE", "1000")),
            structure_weight=float(os.getenv("STRUCTURE_WEIGHT", "0.3")),
            code_weight=float(os.getenv("CODE_WEIGHT", "0.25")),
            size_balance_weight=float(os.getenv("SIZE_BALANCE_WEIGHT", "0.2")),
            metadata_weight=float(os.getenv("METADATA_WEIGHT", "0.15")),
            language_detection_weight=float(os.getenv("LANGUAGE_DETECTION_WEIGHT", "0.1"))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return asdict(self)
    
    def validate(self) -> None:
        """Validate configuration parameters."""
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        
        if self.chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")
        
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
        
        if not 0.0 <= self.quality_threshold <= 1.0:
            raise ValueError("quality_threshold must be between 0.0 and 1.0")
        
        if not 0.0 <= self.performance_threshold <= 10.0:
            raise ValueError("performance_threshold must be between 0.0 and 10.0")
        
        # Validate weight sum
        total_weight = (
            self.structure_weight + self.code_weight + self.size_balance_weight +
            self.metadata_weight + self.language_detection_weight
        )
        
        if not 0.95 <= total_weight <= 1.05:  # Allow small floating point errors
            raise ValueError(f"Quality metric weights must sum to ~1.0, got {total_weight}")
    
    def get_auto_selection_config(self) -> Dict[str, Any]:
        """Get configuration for auto-selection algorithm."""
        return {
            "markdown_headers": self.markdown_detection_threshold,
            "code_blocks": self.code_block_threshold,
            "table_cells": self.table_threshold
        }
    
    def get_quality_weights(self) -> Dict[str, float]:
        """Get quality metric weights."""
        return {
            "structure": self.structure_weight,
            "code": self.code_weight,
            "size_balance": self.size_balance_weight,
            "metadata": self.metadata_weight,
            "language_detection": self.language_detection_weight
        }


# Global configuration instance
_global_config: Optional[ChunkingConfig] = None


def get_chunking_config() -> ChunkingConfig:
    """Get global chunking configuration instance."""
    global _global_config
    if _global_config is None:
        _global_config = ChunkingConfig.from_environment()
        _global_config.validate()
    return _global_config


def set_chunking_config(config: ChunkingConfig) -> None:
    """Set global chunking configuration instance."""
    global _global_config
    config.validate()
    _global_config = config


def reset_chunking_config() -> None:
    """Reset global configuration to environment defaults."""
    global _global_config
    _global_config = None


# Predefined configurations for common use cases
FAST_CONFIG = ChunkingConfig(
    chunk_size=500,
    chunk_overlap=50,
    default_strategy="baseline",
    enable_ab_testing=False,
    quality_threshold=0.5
)

QUALITY_CONFIG = ChunkingConfig(
    chunk_size=1500,
    chunk_overlap=300,
    default_strategy="markdown_intelligent",
    enable_ab_testing=True,
    quality_threshold=0.8
)

BALANCED_CONFIG = ChunkingConfig(
    chunk_size=1000,
    chunk_overlap=200,
    default_strategy="auto",
    enable_ab_testing=True,
    quality_threshold=0.7
)

# Configuration presets
PRESETS = {
    "fast": FAST_CONFIG,
    "quality": QUALITY_CONFIG,
    "balanced": BALANCED_CONFIG
}


def get_preset_config(preset: str) -> ChunkingConfig:
    """Get a predefined configuration preset."""
    if preset not in PRESETS:
        available = ", ".join(PRESETS.keys())
        raise ValueError(f"Unknown preset '{preset}'. Available: {available}")
    return PRESETS[preset]


def create_custom_config(**kwargs) -> ChunkingConfig:
    """Create a custom configuration with specified parameters."""
    base_config = get_chunking_config()
    config_dict = base_config.to_dict()
    config_dict.update(kwargs)
    return ChunkingConfig(**config_dict)