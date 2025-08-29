"""
RAG Query use-case implementation.

Orchestrates vector search and LLM response generation to provide
comprehensive question-answering capabilities with source attribution.
"""

import os
import time
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator

from application_layer.vector_search import search_vectors_use_case, ValidationError
from services.llm_service import (
    LLMService,
    LLMError,
    LLMUnavailableError,
    LLMRateLimitError,
    LLMInvalidModelError
)


class RAGError(Exception):
    """Base exception for RAG query errors."""
    pass


class RAGValidationError(RAGError):
    """Exception raised when RAG input validation fails."""
    
    def __init__(self, message: str, code: str, details: dict = None):
        super().__init__(message)
        self.code = code
        self.details = details or {}


class RAGUnavailableError(RAGError):
    """Exception raised when RAG service dependencies are unavailable."""
    
    def __init__(self, message: str, service: str):
        super().__init__(message)
        self.service = service


class RAGQueryRequest(BaseModel):
    """Request model for RAG queries."""
    
    query: str = Field(..., description="Natural language question to answer")
    collection_name: Optional[str] = Field(
        None, 
        description="Optional collection to search in (searches all if None)"
    )
    max_chunks: int = Field(
        5, 
        ge=1, 
        le=20, 
        description="Maximum number of document chunks to use for context"
    )
    similarity_threshold: float = Field(
        0.2, 
        ge=0.0, 
        le=1.0, 
        description="Minimum similarity score for including chunks"
    )
    
    # Enhanced RAG Configuration
    enable_query_expansion: Optional[bool] = Field(
        None,
        description="Enable LLM-based query expansion (overrides env var if set)"
    )
    max_query_variants: Optional[int] = Field(
        None,
        ge=1,
        le=10,
        description="Maximum number of query variants to generate"
    )
    enable_reranking: Optional[bool] = Field(
        None,
        description="Enable LLM-based result re-ranking (overrides env var if set)"
    )
    reranking_threshold: Optional[int] = Field(
        None,
        ge=1,
        le=50,
        description="Minimum results count to trigger re-ranking"
    )
    
    @field_validator('query')
    @classmethod
    def query_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()


class RAGQueryResponse(BaseModel):
    """Response model for RAG queries."""
    
    success: bool = Field(..., description="Whether the query was successful")
    answer: Optional[str] = Field(None, description="LLM-generated answer to the question")
    sources: Optional[List[Dict[str, Any]]] = Field(
        None, 
        description="Source documents used to generate the answer"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, 
        description="Query metadata (timing, provider info, etc.)"
    )
    error: Optional[str] = Field(None, description="Error message if query failed")


async def rag_query_use_case(
    vector_service,
    collection_service,
    llm_service: LLMService,
    request: RAGQueryRequest
) -> RAGQueryResponse:
    """
    Execute RAG query combining vector search with LLM response generation.
    
    This function orchestrates the complete RAG pipeline:
    1. Validate input parameters
    2. Perform vector search to find relevant documents
    3. Combine found documents into context
    4. Generate LLM response based on context and query
    5. Return structured response with sources and metadata
    
    Implements graceful degradation: if LLM fails, returns vector results only.
    
    Args:
        vector_service: Vector search service instance
        collection_service: Collection management service instance  
        llm_service: LLM service instance for response generation
        request: RAG query request with validated parameters
        
    Returns:
        RAGQueryResponse with answer, sources, and metadata
        
    Raises:
        RAGValidationError: When input validation fails
        RAGUnavailableError: When required services are unavailable
        RAGError: For other RAG-specific errors
    """
    start_time = time.time()
    
    try:
        # Step 1: Perform vector search to find relevant documents
        # Request more results initially if re-ranking is enabled to allow for better selection
        
        # Determine enhancement settings: API parameters override environment variables
        reranking_enabled = (request.enable_reranking 
                           if request.enable_reranking is not None 
                           else os.getenv('RAG_AUTO_RERANKING_ENABLED', 'false').lower() == 'true')
        reranking_threshold = (request.reranking_threshold 
                             if request.reranking_threshold is not None 
                             else int(os.getenv('RAG_RERANKING_THRESHOLD', '8')))
        
        # If re-ranking enabled, request more results to have candidates for re-ranking
        search_limit = request.max_chunks
        if reranking_enabled and request.max_chunks <= reranking_threshold:
            search_limit = min(reranking_threshold + 5, 20)  # Request more but cap at 20
            
        vector_results = await search_vectors_use_case(
            vector_service=vector_service,
            collection_service=collection_service,
            query=request.query,
            collection_name=request.collection_name,
            limit=search_limit,
            similarity_threshold=request.similarity_threshold,
            enable_query_expansion=request.enable_query_expansion,
            max_query_variants=request.max_query_variants
        )
        
        # Step 2: Check if we found any relevant documents
        if not vector_results:
            return RAGQueryResponse(
                success=False,
                sources=[],
                error="No relevant information found for your query. Try adjusting your search terms or similarity threshold.",
                metadata={
                    "chunks_used": 0,
                    "collection_searched": request.collection_name,
                    "llm_provider": None,
                    "response_time_ms": int((time.time() - start_time) * 1000)
                }
            )
        
        # Step 2.5: Optional LLM-based re-ranking of results
        vector_results = await _apply_reranking_if_enabled(
            llm_service, request.query, vector_results, request.max_chunks
        )
        
        # Step 3: Build context from vector results
        context_parts = []
        for i, result in enumerate(vector_results, 1):
            source_info = result.get('metadata', {}).get('source', 'Unknown source')
            content = result.get('content', '')
            context_parts.append(f"Source {i} ({source_info}):\n{content}")
        
        combined_context = "\n\n".join(context_parts)
        
        # Step 4: Generate LLM response (with graceful degradation)
        llm_response = None
        llm_error = None
        llm_provider = None
        
        try:
            llm_result = await llm_service.generate_response(
                query=request.query,
                context=combined_context
            )
            
            if llm_result.get("success"):
                llm_response = llm_result.get("answer")
                llm_provider = llm_result.get("provider")
            else:
                llm_error = "LLM returned unsuccessful response"
                
        except LLMUnavailableError as e:
            llm_error = f"LLM temporarily unavailable: {str(e)}"
            
        except LLMRateLimitError as e:
            if e.retry_after:
                llm_error = f"Rate limit exceeded. Please retry after {e.retry_after} seconds."
            else:
                llm_error = "Rate limit exceeded. Please try again later."
                
        except LLMInvalidModelError as e:
            llm_error = f"LLM model configuration error: {str(e)}"
            
        except LLMError as e:
            llm_error = f"LLM error: {str(e)}"
            
        except Exception as e:
            llm_error = f"Unexpected LLM error: {str(e)}"
        
        # Step 5: Build response with sources and metadata
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Transform vector results to response format
        sources = []
        for result in vector_results:
            source_entry = {
                "content": result.get("content", ""),
                "similarity_score": result.get("similarity_score", 0.0),
                "metadata": result.get("metadata", {}),
                "collection_name": result.get("collection_name"),
                "file_path": result.get("file_path")
            }
            # Remove None values for cleaner response
            sources.append({k: v for k, v in source_entry.items() if v is not None})
        
        metadata = {
            "chunks_used": len(vector_results),
            "collection_searched": request.collection_name,
            "llm_provider": llm_provider,
            "response_time_ms": response_time_ms
        }
        
        # Return successful response (even if LLM failed, we have vector results)
        return RAGQueryResponse(
            success=True,
            answer=llm_response,
            sources=sources,
            metadata=metadata,
            error=llm_error  # Include LLM error as warning, not failure
        )
        
    except ValidationError as e:
        # Vector search validation failed
        raise RAGValidationError(
            message=e.message,
            code=e.code,
            details=e.details
        )
        
    except RuntimeError as e:
        # Service unavailability (vector service, etc.)
        if "Vector sync service" in str(e):
            raise RAGUnavailableError(str(e), service="vector")
        else:
            raise RAGUnavailableError(str(e), service="unknown")
            
    except Exception as e:
        # Any other error
        error_message = str(e)
        if "not found" in error_message.lower():
            raise RAGError(f"Collection or resource error: {error_message}")
        else:
            raise RAGError(f"RAG query failed: {error_message}")


async def build_context_from_sources(sources: List[Dict[str, Any]]) -> str:
    """
    Build a well-formatted context string from vector search results.
    
    Args:
        sources: List of vector search results
        
    Returns:
        Formatted context string suitable for LLM prompt
    """
    if not sources:
        return ""
    
    context_parts = []
    for i, source in enumerate(sources, 1):
        # Extract source information
        content = source.get('content', '')
        metadata = source.get('metadata', {})
        source_name = metadata.get('source', f'Document {i}')
        
        # Build formatted context entry
        context_part = f"Source {i} - {source_name}:\n{content}"
        context_parts.append(context_part)
    
    return "\n\n".join(context_parts)


def calculate_context_stats(sources: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate statistics about the context used for RAG.
    
    Args:
        sources: List of vector search results
        
    Returns:
        Dictionary with context statistics
    """
    if not sources:
        return {
            "total_sources": 0,
            "avg_similarity": 0.0,
            "total_chars": 0,
            "unique_collections": 0
        }
    
    total_chars = sum(len(source.get('content', '')) for source in sources)
    similarities = [source.get('similarity_score', 0.0) for source in sources]
    avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0
    
    collections = set()
    for source in sources:
        collection = source.get('collection_name')
        if collection:
            collections.add(collection)
    
    return {
        "total_sources": len(sources),
        "avg_similarity": round(avg_similarity, 3),
        "total_chars": total_chars,
        "unique_collections": len(collections)
    }


async def _apply_reranking_if_enabled(
    llm_service: LLMService, 
    query: str, 
    vector_results: List[Dict[str, Any]], 
    max_chunks: int
) -> List[Dict[str, Any]]:
    """
    Apply LLM-based re-ranking to vector search results if enabled and above threshold.
    
    Args:
        llm_service: LLM service instance for re-ranking
        query: Original user query
        vector_results: Results from vector search
        max_chunks: Maximum number of chunks to return
        
    Returns:
        Re-ranked results or original results if re-ranking disabled/failed
    """
    
    # Check if re-ranking is enabled
    reranking_enabled = os.getenv('RAG_AUTO_RERANKING_ENABLED', 'false').lower() == 'true'
    if not reranking_enabled:
        return vector_results
    
    # Check if results exceed threshold for re-ranking
    reranking_threshold = int(os.getenv('RAG_RERANKING_THRESHOLD', '8'))
    if len(vector_results) <= reranking_threshold:
        return vector_results
    
    try:
        # Perform LLM-based re-ranking
        reranked_results = await _rerank_with_llm(
            llm_service, query, vector_results, max_chunks
        )
        return reranked_results
    except Exception:
        # Graceful fallback to original results on any re-ranking error
        return vector_results


async def _rerank_with_llm(
    llm_service: LLMService,
    query: str,
    results: List[Dict[str, Any]],
    target_count: int
) -> List[Dict[str, Any]]:
    """
    Re-rank search results using LLM-based relevance scoring.
    
    Args:
        llm_service: LLM service instance
        query: Original user query
        results: Vector search results to re-rank
        target_count: Target number of results to return
        
    Returns:
        Re-ranked results limited to target_count
        
    Raises:
        Exception: When LLM re-ranking fails
    """
    
    if len(results) <= target_count:
        return results
    
    # Build re-ranking prompt with chunks
    chunks_text = ""
    for i, result in enumerate(results):
        content = result.get('content', '')[:400]  # Limit content for token efficiency
        source = result.get('metadata', {}).get('source', f'Doc{i+1}')
        chunks_text += f"\n\nChunk {i+1} ({source}):\n{content}"
    
    rerank_prompt = f"""Query: "{query}"

Please rank these text chunks by their relevance to the query. Consider:
- Direct answer potential
- Contextual relevance to the question
- Information completeness and quality

Text chunks:{chunks_text}

Return only the chunk numbers in order of relevance (most relevant first), separated by commas.
Example: 3, 1, 5, 2, 4

Ranking:"""
    
    # Get LLM ranking
    try:
        llm_response = await llm_service.generate_response(
            query=rerank_prompt,
            context="",  # No additional context needed
            max_tokens=100,  # Short response expected
            temperature=0.1  # Low temperature for consistent ranking
        )
        
        if not llm_response.get("success"):
            raise Exception("LLM re-ranking returned unsuccessful response")
        
        # Parse ranking from LLM response
        ranking_text = llm_response.get("answer", "").strip()
        ranking_indices = _parse_ranking_response(ranking_text, len(results))
        
        # Reorder results based on LLM ranking
        reranked_results = []
        for idx in ranking_indices[:target_count]:
            if 0 <= idx < len(results):
                reranked_results.append(results[idx])
        
        # Fill remaining slots with original order if needed
        used_indices = set(ranking_indices[:target_count])
        for i, result in enumerate(results):
            if len(reranked_results) >= target_count:
                break
            if i not in used_indices:
                reranked_results.append(result)
        
        return reranked_results[:target_count]
        
    except Exception as e:
        # Re-raise to trigger fallback in calling function
        raise Exception(f"LLM re-ranking failed: {str(e)}")


def _parse_ranking_response(ranking_text: str, total_chunks: int) -> List[int]:
    """
    Parse LLM ranking response to extract chunk indices.
    
    Args:
        ranking_text: LLM response with ranking
        total_chunks: Total number of chunks that were ranked
        
    Returns:
        List of 0-indexed chunk positions in ranked order
    """
    
    # Extract numbers from the response
    import re
    numbers = re.findall(r'\d+', ranking_text)
    
    # Convert to 0-indexed and validate
    ranking_indices = []
    for num_str in numbers:
        try:
            # Convert to 0-indexed (LLM uses 1-indexed)
            idx = int(num_str) - 1
            if 0 <= idx < total_chunks and idx not in ranking_indices:
                ranking_indices.append(idx)
        except ValueError:
            continue
    
    # Fill missing indices with original order
    for i in range(total_chunks):
        if i not in ranking_indices:
            ranking_indices.append(i)
    
    return ranking_indices