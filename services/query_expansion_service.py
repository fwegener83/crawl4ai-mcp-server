"""
Query Expansion Service for enhanced RAG search capabilities.

Provides intelligent query expansion using LLM-generated alternative search terms
to improve vector search recall and handle terminology mismatches.
"""

import hashlib
import time
from typing import List, Dict, Any, Optional
from services.llm_service import LLMService, LLMError, LLMUnavailableError


class QueryExpansionError(Exception):
    """Base exception for query expansion errors."""
    
    def __init__(self, message: str, original_query: str = None):
        super().__init__(message)
        self.original_query = original_query


class QueryExpansionService:
    """Service for intelligent query expansion using LLM-generated alternatives."""
    
    def __init__(self, llm_service: LLMService, enable_caching: bool = True):
        """
        Initialize query expansion service.
        
        Args:
            llm_service: LLM service instance for generating expansions
            enable_caching: Whether to cache expansion results
        """
        self.llm_service = llm_service
        self.enable_caching = enable_caching
        self._expansion_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl_seconds = 3600  # 1 hour cache TTL
        
    def _get_cache_key(self, query: str, collection_context: Optional[str] = None) -> str:
        """Generate cache key for query expansion."""
        cache_input = f"{query}|{collection_context or ''}"
        return hashlib.md5(cache_input.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid based on TTL."""
        if not self.enable_caching:
            return False
        
        cached_time = cache_entry.get('timestamp', 0)
        return (time.time() - cached_time) < self._cache_ttl_seconds
    
    async def expand_query_intelligently(
        self, 
        query: str, 
        collection_context: Optional[str] = None,
        max_expansions: int = 3,
        temperature: float = 0.3
    ) -> List[str]:
        """
        Generate semantically similar query variants using LLM.
        
        Args:
            query: Original user query
            collection_context: Optional context about the collection being searched
            max_expansions: Maximum number of alternative queries to generate
            temperature: LLM temperature for creative expansion (0.1-0.7 recommended)
            
        Returns:
            List of query variants including the original query
            
        Raises:
            QueryExpansionError: When expansion fails
        """
        if not query or not query.strip():
            raise QueryExpansionError("Query cannot be empty")
        
        query = query.strip()
        
        # Check cache first
        cache_key = self._get_cache_key(query, collection_context)
        if cache_key in self._expansion_cache:
            cache_entry = self._expansion_cache[cache_key]
            if self._is_cache_valid(cache_entry):
                return cache_entry['expansions']
        
        try:
            # Build expansion prompt
            expansion_prompt = self._build_expansion_prompt(
                query, collection_context, max_expansions
            )
            
            # Generate expansions using LLM
            llm_response = await self.llm_service.generate_response(
                query=expansion_prompt,
                context="",  # No context needed for query expansion
                max_tokens=200,  # Short response expected
                temperature=temperature
            )
            
            if not llm_response.get("success"):
                # Graceful degradation: return original query only
                return [query]
            
            # Parse LLM response to extract alternative queries
            expansions = self._parse_expansion_response(
                llm_response.get("answer", ""), query, max_expansions
            )
            
            # Cache the result
            if self.enable_caching:
                self._expansion_cache[cache_key] = {
                    'expansions': expansions,
                    'timestamp': time.time()
                }
            
            return expansions
            
        except LLMUnavailableError as e:
            # Graceful degradation: return original query only
            return [query]
            
        except LLMError as e:
            raise QueryExpansionError(
                f"LLM error during query expansion: {str(e)}",
                original_query=query
            )
            
        except Exception as e:
            raise QueryExpansionError(
                f"Unexpected error during query expansion: {str(e)}",
                original_query=query
            )
    
    def _build_expansion_prompt(
        self, 
        query: str, 
        collection_context: Optional[str], 
        max_expansions: int
    ) -> str:
        """Build LLM prompt for query expansion."""
        
        context_part = ""
        if collection_context:
            context_part = f"\nCollection context: The user is searching within a collection focused on {collection_context}."
        
        return f"""Generate {max_expansions} alternative search queries that capture the same intent as the original query but use different terminology.

Original query: "{query}"{context_part}

Consider these expansion strategies:
- Synonyms and related terms (e.g., "AI" → "Artificial Intelligence", "Machine Learning")
- Technical vs. colloquial language (e.g., "API" → "Application Programming Interface") 
- Abbreviations and full forms (e.g., "ML" → "Machine Learning")
- Domain-specific terminology variations
- Different phrasings of the same concept

Return only the alternative queries, one per line, without numbering or explanation.
Do not include the original query in your response.
Example output:
Alternative query 1
Alternative query 2
Alternative query 3"""
    
    def _parse_expansion_response(
        self, 
        llm_response: str, 
        original_query: str, 
        max_expansions: int
    ) -> List[str]:
        """Parse LLM response to extract alternative queries."""
        
        # Start with original query
        expansions = [original_query]
        
        if not llm_response or not llm_response.strip():
            return expansions
        
        # Split response by lines and clean up
        lines = llm_response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Remove common prefixes/numbering
            line = self._clean_expansion_line(line)
            
            # Skip if it's the same as original query
            if line.lower() == original_query.lower():
                continue
                
            # Skip if it's too similar to existing expansions
            if not self._is_unique_expansion(line, expansions):
                continue
                
            # Add the expansion
            expansions.append(line)
            
            # Stop when we have enough expansions
            if len(expansions) >= max_expansions + 1:  # +1 for original query
                break
        
        return expansions
    
    def _clean_expansion_line(self, line: str) -> str:
        """Clean up expansion line by removing common prefixes and formatting."""
        
        # Remove common prefixes
        prefixes_to_remove = [
            "- ", "* ", "• ",  # Bullet points
            "1. ", "2. ", "3. ", "4. ", "5. ",  # Numbers
            "Alternative query ", "Query ", "Search ",  # Common prefixes
        ]
        
        for prefix in prefixes_to_remove:
            if line.lower().startswith(prefix.lower()):
                line = line[len(prefix):].strip()
        
        # Remove quotes if present
        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1].strip()
            
        return line
    
    def _is_unique_expansion(self, candidate: str, existing: List[str]) -> bool:
        """Check if the candidate expansion is sufficiently unique."""
        
        candidate_lower = candidate.lower()
        
        for existing_query in existing:
            existing_lower = existing_query.lower()
            
            # Skip if identical
            if candidate_lower == existing_lower:
                return False
                
            # Skip if too similar (simple heuristic)
            # Calculate a basic similarity based on word overlap
            candidate_words = set(candidate_lower.split())
            existing_words = set(existing_lower.split())
            
            if len(candidate_words) == 0 or len(existing_words) == 0:
                continue
                
            overlap = len(candidate_words.intersection(existing_words))
            total_unique = len(candidate_words.union(existing_words))
            
            # If more than 80% overlap, consider it too similar
            # For "machine learning AI" vs "machine learning": overlap=2, total=3 -> 66% < 80%, so unique
            if total_unique > 0 and (overlap / total_unique) > 0.8:
                return False
        
        return True
    
    def clear_cache(self) -> None:
        """Clear the expansion cache."""
        self._expansion_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring."""
        if not self.enable_caching:
            return {"caching_enabled": False}
        
        valid_entries = sum(
            1 for entry in self._expansion_cache.values() 
            if self._is_cache_valid(entry)
        )
        
        return {
            "caching_enabled": True,
            "total_entries": len(self._expansion_cache),
            "valid_entries": valid_entries,
            "cache_hit_ratio": valid_entries / max(len(self._expansion_cache), 1),
            "cache_ttl_seconds": self._cache_ttl_seconds
        }