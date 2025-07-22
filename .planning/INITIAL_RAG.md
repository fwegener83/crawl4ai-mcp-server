# FEATURE: Local RAG Knowledge Base Extension

Erweiterung des Crawl4AI MCP Servers um lokale RAG-Funktionalität zur Persistierung und Durchsuchung von gecrawlten Inhalten. Fokus auf Einfachheit und lokale Ausführung ohne externe APIs.

## KERN-FUNKTIONALITÄT (MVP):

### 1. `store_crawl_results` - Content Speicherung
Verarbeitet und speichert Crawl-Ergebnisse in lokaler Vektordatenbank.

**Parameter:**
- `crawl_results` (required, dict): Output von `domain_deep_crawl` oder `web_content_extract`
- `collection_name` (required, string): Name der Collection zum Speichern
- `overwrite_collection` (optional, bool, default: false): Existierende Collection überschreiben

**Rückgabe:**
```json
{
  "success": true,
  "collection_name": "my_docs",
  "documents_stored": 42,
  "chunks_created": 156,
  "storage_location": "./knowledge_base/my_docs"
}
```

### 2. `search_knowledge_base` - RAG Suche
Durchsucht gespeicherte Inhalte mit semantischer Suche.

**Parameter:**
- `query` (required, string): Suchanfrage in natürlicher Sprache
- `collection_name` (required, string): Zu durchsuchende Collection
- `top_k` (optional, int, default: 5): Anzahl Ergebnisse
- `min_similarity` (optional, float, default: 0.0): Minimale Ähnlichkeit (0.0-1.0)

**Rückgabe:**
```json
{
  "success": true,
  "query": "How to configure crawling?",
  "results": [
    {
      "content": "Crawling can be configured using...",
      "metadata": {
        "source_url": "https://docs.example.com/config",
        "title": "Configuration Guide",
        "chunk_id": "chunk_123",
        "similarity_score": 0.89
      }
    }
  ],
  "total_found": 3
}
```

### 3. `list_collections` - Collection Management
Zeigt verfügbare Collections und deren Status.

**Rückgabe:**
```json
{
  "success": true,
  "collections": [
    {
      "name": "my_docs",
      "document_count": 42,
      "chunk_count": 156,
      "created_at": "2025-07-22T10:30:00Z",
      "last_updated": "2025-07-22T12:45:00Z"
    }
  ]
}
```

### 4. `delete_collection` - Collection Cleanup
Löscht eine Collection komplett.

**Parameter:**
- `collection_name` (required, string): Zu löschende Collection

## TECHNISCHE IMPLEMENTIERUNG (MVP):

### Tech Stack (Lokal):
```python
dependencies = [
    # Bestehende Dependencies...
    "chromadb>=0.4.0",              # Lokale Vektordatenbank
    "sentence-transformers>=2.0.0", # Lokale Embeddings
    "langchain-text-splitters>=0.2.0" # Intelligentes Chunking
]
```

### Architektur:
```
tools/
├── knowledge_base/
│   ├── __init__.py
│   ├── vector_store.py         # Chroma Integration (austauschbar)
│   ├── embeddings.py           # SentenceTransformers (austauschbar)
│   ├── content_processor.py    # Chunking & Metadata
│   └── rag_tools.py           # MCP Tool Definitions
```

### Konfiguration:
```python
# Default-Konfiguration (überschreibbar)
DEFAULT_CONFIG = {
    "vector_store": "chroma",  # Später: "faiss", "qdrant", etc.
    "embedding_model": "all-MiniLM-L6-v2",
    "chunk_size": 512,
    "chunk_overlap": 50,
    "persist_directory": "./knowledge_base"
}
```

### Content Processing Pipeline:
1. **Input Validation**: Crawl-Results Structure prüfen
2. **Content Extraction**: Text aus Markdown extrahieren
3. **Chunking**: Text in semantische Chunks aufteilen
4. **Metadata Enrichment**: URL, Titel, Timestamps hinzufügen
5. **Embedding Generation**: Lokale Vektorisierung
6. **Storage**: Persistierung in Chroma

## ERWEITERBARKEIT (NFAs):

### 1. Pluggable Vector Stores
```python
# Interface für verschiedene Vector DBs
class VectorStoreInterface:
    async def store_documents(self, documents, embeddings, metadata): ...
    async def search(self, query_embedding, top_k): ...
    async def delete_collection(self, collection_name): ...

# Implementierungen:
class ChromaVectorStore(VectorStoreInterface): ...
class FAISSVectorStore(VectorStoreInterface): ...
class QdrantVectorStore(VectorStoreInterface): ...
```

### 2. Pluggable Embedding Models
```python
# Interface für verschiedene Embedding Provider
class EmbeddingInterface:
    def encode(self, texts: List[str]) -> np.ndarray: ...
    def encode_query(self, query: str) -> np.ndarray: ...

# Implementierungen:
class SentenceTransformerEmbeddings(EmbeddingInterface): ...
class OpenAIEmbeddings(EmbeddingInterface): ...  # Für später
class HuggingFaceEmbeddings(EmbeddingInterface): ...
```

### 3. Pluggable Chunking Strategies
```python
class ChunkingInterface:
    def split_text(self, text: str, metadata: dict) -> List[dict]: ...

# Implementierungen:
class RecursiveChunking(ChunkingInterface): ...
class SemanticChunking(ChunkingInterface): ...  # Für später
class FixedSizeChunking(ChunkingInterface): ...
```

### 4. Configuration Management
```python
# .env Unterstützung für Konfiguration
VECTOR_STORE=chroma
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=512
PERSIST_DIRECTORY=./knowledge_base

# Programmatische Konfiguration
from tools.knowledge_base import configure_rag
configure_rag(
    vector_store="chroma",
    embedding_model="all-mpnet-base-v2"
)
```

## BEISPIELE:

### Basis-Workflow:
```json
// 1. Domain crawlen
{"name": "domain_deep_crawl", "arguments": {"domain_url": "https://docs.example.com"}}

// 2. Ergebnisse speichern  
{"name": "store_crawl_results", "arguments": {"crawl_results": "...", "collection_name": "docs"}}

// 3. Durchsuchen
{"name": "search_knowledge_base", "arguments": {"query": "How to configure?", "collection_name": "docs"}}
```

### Einzelseiten-Workflow:
```json
// 1. Einzelne Seite crawlen
{"name": "web_content_extract", "arguments": {"url": "https://blog.example.com/post1"}}

// 2. Speichern (Tool muss beide Input-Formate unterstützen)
{"name": "store_crawl_results", "arguments": {"crawl_results": "...", "collection_name": "blog"}}
```

## ENTWICKLUNGSSCHRITTE:

### Phase 1: MVP (Chroma + SentenceTransformers)
- Basis RAG-Tools implementieren
- Lokale Chroma Integration
- Einfaches Chunking
- Basic Tests

### Phase 2: Robustheit
- Error Handling & Validation
- Collection Management
- Content Deduplication
- Performance Optimierung

### Phase 3: Erweiterbarkeit (Falls benötigt)
- Plugin-Architektur implementieren
- Alternative Vector Stores
- Erweiterte Chunking-Strategien
- Configuration Management

## TESTING STRATEGY:

### Fast Tests (Mock-basiert):
- Unit Tests für Content Processing
- Mock Vector Store Tests
- Input Validation Tests

### Integration Tests:
- Echte Chroma Integration
- End-to-End RAG Pipeline
- Performance Tests mit größeren Datasets

### Storage Tests:
- Persistierung zwischen Restarts
- Collection Management
- Data Integrity

## YAGNI PRINZIPIEN:

### Was JETZT implementiert wird:
- ✅ Chroma als einzige Vector DB
- ✅ SentenceTransformers als einziges Embedding
- ✅ Recursive Chunking als einzige Strategie
- ✅ Basis-Tools ohne erweiterte Features

### Was SPÄTER implementiert wird (falls benötigt):
- ❌ Multiple Vector DB Unterstützung
- ❌ LLM-basierte Chunking Strategien
- ❌ Erweiterte Similarity Search Algorithmen
- ❌ Query Expansion und Re-ranking
- ❌ Multi-modal Embeddings (Text + Bilder)

## DATENSPEICHERUNG:

```
knowledge_base/
├── chroma.sqlite3              # Chroma Metadaten
├── collections/
│   ├── docs/                   # Collection "docs"
│   └── blog/                   # Collection "blog"
└── models/                     # Heruntergeladene Embedding Models
    └── sentence-transformers_all-MiniLM-L6-v2/
```

**Ziel**: Einfache, funktionierende RAG-Lösung die 80% der Use Cases abdeckt und bei Bedarf erweitert werden kann, ohne dass bestehender Code umgeschrieben werden muss.
