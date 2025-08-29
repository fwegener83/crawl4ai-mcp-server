# RAG/Vector Search Verbesserungs-Roadmap

> **Ziel**: Erhebliche Verbesserung der RAG-Query-Qualität und Vector-Search-Präzision durch intelligente Query-Expansion und Multi-Stage-Retrieval.

## Problem Statement

**Aktueller Zustand:**
- Single-Shot Vector Search: User Query → direktes Embedding → ChromaDB → Top-K Results  
- Terminology Gap: User nutzt andere Begriffe als in Dokumenten stehen
- Keine Query-Refinement oder Multi-Query-Strategien
- Suboptimale RAG-Antworten durch unzureichenden Retrieval

**Identifizierte Schwachstellen:**
1. **Terminology Mismatch**: "KI" vs "Artificial Intelligence" vs "Machine Learning"
2. **Abkürzungen**: "API" wird nicht zu "Application Programming Interface" erweitert  
3. **Context-Blindheit**: Domain-spezifische Begriffe werden nicht verstanden
4. **Single Vector Space**: Keine collection-spezifische Terminologie-Anpassung

## Implementierungs-Roadmap

### 🚀 Phase 1: Multi-Query Search mit LLM Expansion (Sofort)

**Ziel**: Query-Expansion durch LLM-generierte alternative Suchbegriffe

**Implementation Location**: 
- `application_layer/vector_search.py` - Erweitern der `search_vectors_use_case`
- Neue Funktion: `expand_query_intelligently()`

**Technischer Ansatz:**
```python
async def expand_query_intelligently(query: str, collection_context: str = None) -> List[str]:
    """Generate semantically similar query variants using LLM."""
    
    expansion_prompt = f"""
    Original query: "{query}"
    {f"Collection context: {collection_context}" if collection_context else ""}
    
    Generate 2-3 alternative search queries that capture the same intent
    but use different terminology. Consider:
    - Synonyms and related terms
    - Technical vs. colloquial language  
    - Abbreviations and full forms
    - Domain-specific terminology
    
    Return only the alternative queries, one per line.
    """
    
    expansions = await llm_service.generate_expansions(expansion_prompt)
    return [query] + expansions  # Original + alternatives

async def multi_query_vector_search(
    vector_service, query: str, collection_name: str, limit: int, threshold: float
) -> List[Dict[str, Any]]:
    """Enhanced vector search using multiple query variants."""
    
    # Generate query variants
    query_variants = await expand_query_intelligently(query, collection_name)
    
    # Search with all variants
    all_results = []
    for variant in query_variants:
        results = await vector_service.search_vectors(variant, collection_name, limit, threshold)
        all_results.extend(results)
    
    # Deduplicate and merge scores
    return deduplicate_and_rank_results(all_results, original_query=query)
```

**Success Metrics:**
- 20-30% Verbesserung der Retrieval-Qualität (subjektive Bewertung)
- Höhere Abdeckung relevanter Dokumente
- Bessere Handhabung von Synonymen und Abkürzungen

---

### 🔄 Phase 2: LLM Re-Ranking der Top-K Ergebnisse (Woche 2)

**Ziel**: Intelligente Relevanz-Bewertung der gefundenen Chunks durch LLM

**Implementation Location**:
- `application_layer/rag_query.py` - Integration in RAG-Pipeline
- Neue Funktion: `rerank_results_by_relevance()`

**Technischer Ansatz:**
```python
async def rerank_results_by_relevance(
    results: List[Dict], original_query: str, top_k: int = 5
) -> List[Dict]:
    """Re-rank search results using LLM for better relevance scoring."""
    
    # Get more results initially (e.g., top-20 instead of top-5)
    if len(results) <= top_k:
        return results
    
    # Format chunks for LLM evaluation
    chunks_text = "\n\n".join([
        f"Chunk {i+1}:\n{result.get('content', '')[:500]}..."
        for i, result in enumerate(results)
    ])
    
    rerank_prompt = f"""
    Query: "{original_query}"
    
    Rank these text chunks by relevance to the query. Consider:
    - Direct answer potential
    - Contextual relevance  
    - Information completeness
    
    Text chunks:
    {chunks_text}
    
    Return the chunk numbers in order of relevance (most relevant first):
    Example: 3, 1, 5, 2, 4
    """
    
    ranking = await llm_service.rank_chunks(rerank_prompt)
    return reorder_results_by_ranking(results, ranking)[:top_k]
```

**Integration in RAG Pipeline:**
- Retrieve top-20 Chunks statt top-5
- LLM re-rankt basierend auf Query-Relevanz  
- Return top-5 der re-gerankten Ergebnisse

**Success Metrics:**
- Verbesserte Antwort-Qualität in RAG-Responses
- Höhere Precision bei returned Chunks
- Reduzierung irrelevanter Kontext-Information

---

### 🔍 Phase 3: Hybrid Semantic+Keyword Search (Woche 3)

**Ziel**: Kombination von semantischer Suche mit traditioneller Keyword-Suche für bessere Precision

**Implementation Location**:
- Neue Service: `services/keyword_search_service.py`
- Integration in `application_layer/vector_search.py`

**Technischer Ansatz:**
```python
class KeywordSearchService:
    """Simple keyword search using TF-IDF or BM25 scoring."""
    
    async def search_keywords(
        self, query: str, collection_name: str, limit: int
    ) -> List[Dict[str, Any]]:
        """Perform keyword-based search on collection documents."""
        
        # Implementation using simple TF-IDF scoring
        # or integrate with existing search libraries
        pass

async def hybrid_search_strategy(
    vector_service, keyword_service, query: str, collection_name: str, limit: int, threshold: float
) -> List[Dict[str, Any]]:
    """Hybrid search combining semantic and keyword approaches."""
    
    # Parallel semantic and keyword search
    semantic_results = await vector_service.search_vectors(query, collection_name, limit, threshold)
    keyword_results = await keyword_service.search_keywords(query, collection_name, limit)
    
    # Weighted combination (70% semantic, 30% keyword)
    combined_results = combine_search_scores(
        semantic_results, 
        keyword_results, 
        weights=[0.7, 0.3]
    )
    
    return combined_results[:limit]
```

**Benefits:**
- **Exact Match Handling**: Bessere Ergebnisse bei spezifischen Begriffen/Namen
- **Complement Semantic Gaps**: Keyword-Search fängt auf, wo Embeddings versagen  
- **Robust Retrieval**: Fallback-Mechanismus für edge cases

**Success Metrics:**
- Verbesserte Handling von Eigennamen und spezifischen Begriffen
- Höhere Recall-Rate bei wichtigen Keywords
- Robustere Performance across verschiedene Query-Types

---

## Implementation Notes

### Technische Überlegungen

**LLM Service Integration:**
- Nutze bereits vorhandenen `LLMService` (Ollama/OpenAI)
- Kurze, effiziente Prompts für Query-Expansion und Re-Ranking
- Graceful Degradation falls LLM nicht verfügbar

**Performance Considerations:**
- Multi-Query Search: Parallel execution der Query-Varianten
- Caching von Query-Expansions für häufige Begriffe
- Timeout-Handling für LLM-Calls

**Backward Compatibility:**
- Neue Features als opt-in Parameter
- Fallback auf aktuellen Single-Query Search
- Keine Breaking Changes in bestehenden APIs

### Testing Strategy

**Phase 1 Testing:**
- Unit Tests für Query-Expansion Logic
- Integration Tests mit verschiedenen Query-Types
- Performance Tests: Latency-Impact von Multi-Query

**Phase 2 Testing:**  
- A/B Testing: Re-ranked vs. Original Results
- Subjektive Qualitäts-Bewertung der RAG-Antworten
- Edge Case Testing: Leere Results, LLM Failures

**Phase 3 Testing:**
- Hybrid Search vs. Pure Semantic Benchmarks  
- Keyword-Heavy vs. Semantic-Heavy Query Performance
- Integration Testing aller drei Phasen zusammen

---

## Verzichtete Features

### Statisches Glossar/Synonym-System

**Warum nicht implementiert:**
- **Maintenance Overhead**: Manuelle Pflege von Glossaren nicht skalierbar
- **Context-Insensitivität**: Statische Mappings verstehen keinen Kontext
- **Modern Alternative**: LLM-basierte Dynamic Expansion ist wartungsärmer und intelligenter

**Mögliche Zukunfts-Implementation:**
- Minimales Glossar für super-kritische Domain-Terms (MCP → Model Context Protocol)
- Collection-spezifische Terminologie-Listen
- Auto-generierte Glossare basierend auf Collection-Content-Analyse

---

## Success Definition

**Qualitative Metriken:**
- Subjektiv bessere RAG-Antworten bei typischen User-Queries
- Höhere Relevanz der returned Vector-Search Results  
- Verbesserte Handhabung von Abkürzungen und Synonymen

**Quantitative Metriken:**
- Latency-Impact < 2x der aktuellen Response-Zeit
- Höhere Diversity der gefundenen Dokumente
- Reduzierung von "No results found"-Fällen

**Implementation Success:**
- Alle drei Phasen erfolgreich deployed
- Backward Compatibility erhalten
- Robuste Error-Handling und Graceful Degradation implementiert