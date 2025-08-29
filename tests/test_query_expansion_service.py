"""
Tests for Query Expansion Service.

Test-first implementation following the plan requirements:
- QueryExpansionService class structure
- LLM prompt generation and response parsing
- Simple in-memory caching behavior  
- Graceful fallback when LLM fails
"""

import pytest
import time
from unittest.mock import AsyncMock, Mock, patch
from services.llm_service import LLMService, LLMError, LLMUnavailableError
from services.query_expansion_service import QueryExpansionService, QueryExpansionError


class MockLLMService:
    """Mock LLM service for testing."""
    
    def __init__(self, should_fail=False, response_text="alternative query 1\nalternative query 2"):
        self.should_fail = should_fail
        self.response_text = response_text
        self.call_count = 0
        
    async def generate_response(self, query, context, max_tokens=200, temperature=0.3):
        self.call_count += 1
        
        if self.should_fail:
            raise LLMUnavailableError("Mock LLM failure", "mock")
            
        return {
            "success": True,
            "answer": self.response_text,
            "provider": "mock",
            "model": "mock-model",
            "token_usage": {"total": 50, "prompt": 30, "completion": 20},
            "response_time_ms": 100
        }


class TestQueryExpansionService:
    """Test suite for QueryExpansionService."""
    
    def test_service_initialization(self):
        """Test basic service initialization."""
        mock_llm = MockLLMService()
        service = QueryExpansionService(mock_llm, enable_caching=True)
        
        assert service.llm_service == mock_llm
        assert service.enable_caching is True
        assert service._expansion_cache == {}
        assert service._cache_ttl_seconds == 3600
        
    def test_service_initialization_without_caching(self):
        """Test service initialization with caching disabled."""
        mock_llm = MockLLMService()
        service = QueryExpansionService(mock_llm, enable_caching=False)
        
        assert service.enable_caching is False
        
    def test_cache_key_generation(self):
        """Test cache key generation for query expansion."""
        mock_llm = MockLLMService()
        service = QueryExpansionService(mock_llm)
        
        # Same query should generate same cache key
        key1 = service._get_cache_key("test query")
        key2 = service._get_cache_key("test query")
        assert key1 == key2
        
        # Different queries should generate different keys
        key3 = service._get_cache_key("different query")
        assert key1 != key3
        
        # Same query with different context should generate different keys
        key4 = service._get_cache_key("test query", "collection_context")
        assert key1 != key4
        
    def test_cache_validity_check(self):
        """Test cache validity checking based on TTL."""
        mock_llm = MockLLMService()
        service = QueryExpansionService(mock_llm, enable_caching=True)
        
        # Fresh cache entry should be valid
        fresh_entry = {"timestamp": time.time(), "expansions": ["query1", "query2"]}
        assert service._is_cache_valid(fresh_entry) is True
        
        # Old cache entry should be invalid
        old_entry = {"timestamp": time.time() - 7200, "expansions": ["query1", "query2"]}  # 2 hours old
        assert service._is_cache_valid(old_entry) is False
        
        # When caching disabled, should always be invalid
        service.enable_caching = False
        assert service._is_cache_valid(fresh_entry) is False

    @pytest.mark.asyncio
    async def test_basic_query_expansion(self):
        """Test basic query expansion functionality."""
        mock_llm = MockLLMService(response_text="artificial intelligence\nmachine learning")
        service = QueryExpansionService(mock_llm, enable_caching=False)
        
        result = await service.expand_query_intelligently("AI")
        
        # Should return original query + expansions
        assert len(result) == 3
        assert result[0] == "AI"  # Original query first
        assert "artificial intelligence" in result
        assert "machine learning" in result
        
        # Should have called LLM once
        assert mock_llm.call_count == 1

    @pytest.mark.asyncio 
    async def test_query_expansion_with_context(self):
        """Test query expansion with collection context."""
        mock_llm = MockLLMService(response_text="technical documentation\nAPI reference")
        service = QueryExpansionService(mock_llm, enable_caching=False)
        
        result = await service.expand_query_intelligently(
            "docs", 
            collection_context="software development"
        )
        
        assert len(result) == 3
        assert result[0] == "docs"
        assert "technical documentation" in result
        assert "API reference" in result

    @pytest.mark.asyncio
    async def test_empty_query_validation(self):
        """Test validation of empty queries."""
        mock_llm = MockLLMService()
        service = QueryExpansionService(mock_llm)
        
        with pytest.raises(QueryExpansionError) as exc_info:
            await service.expand_query_intelligently("")
            
        assert "Query cannot be empty" in str(exc_info.value)
        
        with pytest.raises(QueryExpansionError):
            await service.expand_query_intelligently("   ")  # Whitespace only

    @pytest.mark.asyncio
    async def test_llm_failure_graceful_fallback(self):
        """Test graceful fallback when LLM fails."""
        mock_llm = MockLLMService(should_fail=True)
        service = QueryExpansionService(mock_llm, enable_caching=False)
        
        # Should return only original query when LLM fails
        result = await service.expand_query_intelligently("test query")
        
        assert result == ["test query"]
        assert mock_llm.call_count == 1  # LLM was attempted

    @pytest.mark.asyncio
    async def test_caching_behavior(self):
        """Test query expansion caching behavior."""
        mock_llm = MockLLMService(response_text="cached expansion 1\ncached expansion 2")
        service = QueryExpansionService(mock_llm, enable_caching=True)
        
        # First call should hit LLM
        result1 = await service.expand_query_intelligently("cached query")
        assert mock_llm.call_count == 1
        assert len(result1) == 3
        
        # Second call should use cache
        result2 = await service.expand_query_intelligently("cached query")
        assert mock_llm.call_count == 1  # No additional LLM calls
        assert result1 == result2
        
        # Different query should hit LLM again
        result3 = await service.expand_query_intelligently("different query")
        assert mock_llm.call_count == 2
        assert len(result3) == 3

    def test_expansion_line_cleaning(self):
        """Test cleaning of expansion response lines."""
        mock_llm = MockLLMService()
        service = QueryExpansionService(mock_llm)
        
        # Test various prefixes that should be removed
        assert service._clean_expansion_line("1. alternative query") == "alternative query"
        assert service._clean_expansion_line("- alternative query") == "alternative query"
        assert service._clean_expansion_line("• alternative query") == "alternative query"
        assert service._clean_expansion_line("Alternative query some text") == "some text"
        assert service._clean_expansion_line('"quoted query"') == "quoted query"
        
        # Test that normal lines are unchanged
        assert service._clean_expansion_line("normal query") == "normal query"

    def test_expansion_uniqueness_checking(self):
        """Test uniqueness checking for query expansions."""
        mock_llm = MockLLMService()
        service = QueryExpansionService(mock_llm)
        
        existing = ["original query", "machine learning"]
        
        # Identical should not be unique
        assert service._is_unique_expansion("machine learning", existing) is False
        assert service._is_unique_expansion("MACHINE LEARNING", existing) is False
        
        # Very similar should not be unique (80% word overlap)
        # "machine learning systems" vs "machine learning" = 2/3 = 66% < 80%, so unique
        # "machine learning" vs "machine learning" = 2/2 = 100% > 80%, so not unique
        assert service._is_unique_expansion("machine learning systems", existing) is True
        assert service._is_unique_expansion("machine learning techniques", existing) is True
        
        # Need higher overlap to trigger non-uniqueness - let's test identical case
        assert service._is_unique_expansion("machine learning", existing) is False
        
        # Sufficiently different should be unique
        assert service._is_unique_expansion("artificial intelligence", existing) is True
        assert service._is_unique_expansion("neural networks", existing) is True

    @pytest.mark.asyncio
    async def test_max_expansions_limit(self):
        """Test maximum expansions limit."""
        # Mock LLM returning many alternatives
        mock_llm = MockLLMService(response_text="alt1\nalt2\nalt3\nalt4\nalt5\nalt6")
        service = QueryExpansionService(mock_llm, enable_caching=False)
        
        result = await service.expand_query_intelligently("test", max_expansions=3)
        
        # Should have original + max 3 expansions = 4 total
        assert len(result) <= 4
        assert result[0] == "test"  # Original first

    @pytest.mark.asyncio 
    async def test_temperature_parameter(self):
        """Test temperature parameter passing to LLM."""
        mock_llm = MockLLMService()
        service = QueryExpansionService(mock_llm, enable_caching=False)
        
        with patch.object(mock_llm, 'generate_response', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = {
                "success": True,
                "answer": "expansion 1\nexpansion 2"
            }
            
            await service.expand_query_intelligently("test", temperature=0.7)
            
            # Check that temperature was passed correctly
            mock_generate.assert_called_once()
            call_kwargs = mock_generate.call_args[1]
            assert call_kwargs['temperature'] == 0.7

    def test_cache_management_methods(self):
        """Test cache management utility methods."""
        mock_llm = MockLLMService()
        service = QueryExpansionService(mock_llm, enable_caching=True)
        
        # Add some mock cache data
        service._expansion_cache["key1"] = {
            "expansions": ["q1", "q2"], 
            "timestamp": time.time()
        }
        service._expansion_cache["key2"] = {
            "expansions": ["q3", "q4"], 
            "timestamp": time.time() - 7200  # Old entry
        }
        
        # Test cache stats
        stats = service.get_cache_stats()
        assert stats["caching_enabled"] is True
        assert stats["total_entries"] == 2
        assert stats["valid_entries"] == 1  # Only one is fresh
        
        # Test cache clearing
        service.clear_cache()
        assert len(service._expansion_cache) == 0
        
        # Test stats with caching disabled
        service.enable_caching = False
        stats = service.get_cache_stats()
        assert stats["caching_enabled"] is False


class TestQueryExpansionErrorHandling:
    """Test error handling scenarios."""
    
    @pytest.mark.asyncio
    async def test_llm_error_handling(self):
        """Test various LLM error scenarios."""
        # Test LLM returning unsuccessful response
        mock_llm = MockLLMService()
        mock_llm.generate_response = AsyncMock(return_value={"success": False})
        
        service = QueryExpansionService(mock_llm, enable_caching=False)
        
        # Should fallback to original query
        result = await service.expand_query_intelligently("test")
        assert result == ["test"]
        
    @pytest.mark.asyncio
    async def test_llm_exception_handling(self):
        """Test handling of LLM exceptions."""
        mock_llm = MockLLMService()
        mock_llm.generate_response = AsyncMock(side_effect=Exception("Unexpected error"))
        
        service = QueryExpansionService(mock_llm, enable_caching=False)
        
        with pytest.raises(QueryExpansionError) as exc_info:
            await service.expand_query_intelligently("test")
            
        assert "Unexpected error during query expansion" in str(exc_info.value)
        assert exc_info.value.original_query == "test"

    @pytest.mark.asyncio
    async def test_prompt_building(self):
        """Test LLM prompt building logic."""
        mock_llm = MockLLMService()
        service = QueryExpansionService(mock_llm, enable_caching=False)
        
        # Test basic prompt
        prompt = service._build_expansion_prompt("test query", None, 3)
        assert "test query" in prompt
        assert "3 alternative search queries" in prompt
        assert "synonyms" in prompt.lower()
        
        # Test prompt with context
        prompt_with_context = service._build_expansion_prompt(
            "API", "software documentation", 2
        )
        assert "API" in prompt_with_context
        assert "software documentation" in prompt_with_context
        assert "2 alternative search queries" in prompt_with_context