# FEATURE: RAG Query API & MCP Tool

Erweitere das bestehende Crawl4AI MCP Server um vollständiges RAG (Retrieval-Augmented Generation) mit LLM-Integration.

## GOAL:

- **API Endpunkt**: `POST /api/query` für RAG-Anfragen
- **MCP Tool**: `rag_query` für Claude Desktop Integration  
- **LLM Support**: OpenAI API und Ollama (lokal)
- **Vector Integration**: Nutzt bestehende ChromaDB/Vector-Search-Infrastruktur
- **Collection Support**: Optional spezifische Collection oder alle Daten durchsuchen

## ARCHITECTURE:

Folgt bestehender 3-Layer-Architektur:

### Application Layer (Use Cases)
- **Neuer Use-Case**: `rag_query_use_case()`
- **Wiederverwendung**: Nutzt bestehenden `search_vectors_use_case()` für Retrieval
- **Pipeline**: Query → Vector Search → Context Building → LLM Generation → Response

### Services Layer  
- **Neuer Service**: `LLMService` (protocol-agnostic)
- **Provider Abstraction**: OpenAI und Ollama support
- **Configuration**: Environment-based config

### Unified Server Integration
- **HTTP**: RESTful API endpoint in bestehender FastAPI app
- **MCP**: Tool in bestehendem MCP server
- **Shared Logic**: Beide nutzen identischen Use-Case

## API SPECIFICATION:

### HTTP Endpoint:
```http
POST /api/query
Content-Type: application/json

{
  "query": "Wie implementiere ich Authentication in FastAPI?",
  "collection_name": "fastapi_docs",  // optional - wenn leer: alle Collections
  "max_chunks": 5,                    // optional, default: 5  
  "similarity_threshold": 0.7         // optional, default: 0.7
}
```

### Response Format:
```json
{
  "success": true,
  "answer": "Basierend auf der FastAPI Dokumentation gibt es mehrere Wege...",
  "sources": [
    {
      "content": "FastAPI supports OAuth2...",
      "similarity_score": 0.89,
      "metadata": {"url": "...", "title": "..."}
    }
  ],
  "metadata": {
    "chunks_used": 3,
    "collection_searched": "fastapi_docs",
    "llm_provider": "ollama", 
    "response_time_ms": 1250
  }
}
```

### MCP Tool:
```python
@mcp_server.tool()
async def rag_query(
    query: str,
    collection_name: Optional[str] = None,
    max_chunks: int = 5,
    similarity_threshold: float = 0.7
) -> str:
    """Generate RAG answer for a query using LLM and vector search."""
```

## LLM INTEGRATION:

### Supported Providers:
- **OpenAI API**: gpt-4o-mini, gpt-4o
- **Ollama**: llama3.1:8b, llama3.1:70b (lokal)

### Configuration (Environment):
```env
# LLM Provider
RAG_LLM_PROVIDER=ollama              # "ollama" or "openai"

# Ollama Config  
RAG_OLLAMA_HOST=http://localhost:11434
RAG_OLLAMA_MODEL=llama3.1:8b

# OpenAI Config
RAG_OPENAI_API_KEY=sk-...
RAG_OPENAI_MODEL=gpt-4o-mini

# RAG Settings
RAG_MAX_CHUNKS=5
RAG_SIMILARITY_THRESHOLD=0.7
RAG_MAX_TOKENS=2000
RAG_TEMPERATURE=0.1
```

### Prompt Template (Initial - Fixed):
```python
SYSTEM_PROMPT = """Du bist ein hilfreicher Assistent, der Fragen basierend auf bereitgestellten Dokumenten beantwortet.

REGELN:
- Antworte nur basierend auf den KONTEXT-DOKUMENTEN unten
- Wenn Informationen fehlen, sage "Das kann ich aus den verfügbaren Dokumenten nicht beantworten"
- Gib bei wichtigen Aussagen die Quelle an
- Sei präzise und vermeide Spekulationen

KONTEXT-DOKUMENTE:
{context}

Beantworte folgende Frage basierend auf den Dokumenten:"""

USER_PROMPT = "{query}"
```

## IMPLEMENTATION FLOW:

### 1. Service Layer (`services/llm_service.py`)
- Provider-abstrahierte LLM-Integration
- Konfigurierbare Models/Endpoints
- Error handling für LLM-Ausfälle

### 2. Application Layer (`application_layer/rag_query.py`)  
- Use-Case: `rag_query_use_case()`
- Nutzt bestehenden `search_vectors_use_case()`
- Context-Building und Response-Kombination

### 3. Unified Server Integration (`unified_server.py`)
- HTTP endpoint `/api/query`
- MCP tool `rag_query`
- Validation und Error-Mapping

## DEPENDENCIES:

Neue Requirements:
```
openai>=1.0.0          # Für OpenAI API
ollama                 # Für Ollama integration (optional)
```

## EXISTING INTEGRATION:

- **Vector Search**: Nutzt bestehende `search_vectors_use_case()` und `VectorSyncService`
- **Collections**: Kompatibel mit bestehender Collection-Management
- **Error Handling**: Folgt bestehenden Patterns (ValidationError, HTTPException)
- **Logging**: Nutzt bestehende Logger-Konfiguration

## SUCCESS CRITERIA:

1. **API funktional**: `POST /api/query` gibt sinnvolle LLM-Antworten basierend auf Vector-Search
2. **MCP funktional**: `rag_query` Tool in Claude Desktop verfügbar und nutzbar
3. **Provider-Support**: Sowohl OpenAI als auch Ollama funktionieren
4. **Collection-Filter**: Suche in spezifischen Collections oder global
5. **Error-Handling**: Graceful degradation bei LLM-Ausfällen
6. **Documentation**: README-Update mit RAG-Anleitung

## NON-GOALS (Initial):

- Streaming responses (Complete responses für Start)
- LLM response caching
- Advanced prompt engineering/templates  
- Query expansion/preprocessing
- Multi-turn conversations
- Response evaluation/scoring

## TESTING APPROACH:

- Unit tests für `LLMService` (mit mock LLM calls)
- Integration tests für `rag_query_use_case`
- End-to-end tests für HTTP endpoint
- MCP tool testing mit bestehendem Test-Framework
