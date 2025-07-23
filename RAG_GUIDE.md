# RAG Knowledge Base - Advanced Guide

Dieses Dokument beschreibt erweiterte Features und Konfigurationsmöglichkeiten der RAG (Retrieval-Augmented Generation) Knowledge Base Funktionalität.

## Architektur Overview

### Komponenten

Die RAG-Implementierung besteht aus vier Hauptkomponenten:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   ContentProcessor │────▶│ EmbeddingService │────▶│   VectorStore   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Text Chunking  │    │ Sentence-BERT    │    │    ChromaDB     │
│   LangChain     │    │   Embeddings     │    │   Persistence   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

#### ContentProcessor (`tools/knowledge_base/content_processor.py`)
- **Zweck**: Zerlegung von Web-Content in semantisch sinnvolle Chunks
- **Engine**: LangChain RecursiveCharacterTextSplitter
- **Features**: Intelligente Textaufteilung mit konfigurierbarem Overlap

#### EmbeddingService (`tools/knowledge_base/embeddings.py`)
- **Zweck**: Umwandlung von Text in hochdimensionale Vektoren
- **Engine**: Sentence-Transformers
- **Standard-Model**: `all-MiniLM-L6-v2` (384 Dimensionen)

#### VectorStore (`tools/knowledge_base/vector_store.py`)
- **Zweck**: Persistente Speicherung und semantische Suche
- **Engine**: ChromaDB mit lokaler Persistierung
- **Features**: Collections, Metadaten, Similarity Search

### Dependency Management (`tools/knowledge_base/dependencies.py`)

Das System implementiert graceful degradation - ohne RAG-Dependencies sind nur die 3 Basis Web-Crawling Tools verfügbar:

```python
# Prüfung der Verfügbarkeit
from tools.knowledge_base.dependencies import is_rag_available

if is_rag_available():
    # 7 Tools verfügbar (3 + 4 RAG)
    print("RAG features enabled")
else:
    # Nur 3 Basis-Tools verfügbar  
    print("RAG features disabled")
```

## Erweiterte Konfiguration

### Environment Variables

Alle RAG-Settings können über Environment Variables konfiguriert werden:

```bash
# .env Datei
RAG_DB_PATH=./custom_knowledge_base      # ChromaDB Speicherort
RAG_MODEL_NAME=all-mpnet-base-v2         # Embedding Model
RAG_CHUNK_SIZE=1500                      # Text Chunk Größe (Token)
RAG_CHUNK_OVERLAP=300                    # Overlap zwischen Chunks
RAG_DEVICE=cuda                          # cpu oder cuda für GPU
RAG_BATCH_SIZE=32                        # Batch-Größe für Embeddings
RAG_MAX_CHUNK_LENGTH=2000                # Maximale Chunk-Länge
```

### Custom Embedding Models

#### Verfügbare Sentence-Transformer Models

```python
# Verschiedene Model-Optionen mit Trade-offs:

# Standard (empfohlen für die meisten Anwendungen)
RAG_MODEL_NAME=all-MiniLM-L6-v2          # 384 dim, schnell, deutsch/englisch
RAG_MODEL_NAME=all-mpnet-base-v2         # 768 dim, besser, langsamer

# Multilinguale Models
RAG_MODEL_NAME=paraphrase-multilingual-MiniLM-L12-v2  # 50+ Sprachen
RAG_MODEL_NAME=distiluse-base-multilingual-cased      # 15 Sprachen

# Spezialisierte Models
RAG_MODEL_NAME=all-distilroberta-v1      # Gut für kurze Texte
RAG_MODEL_NAME=msmarco-distilbert-base-v4 # Optimiert für Suchrelevanz

# Deutsche Models (für deutsche Inhalte)
RAG_MODEL_NAME=T-Systems-onsite/german-roberta-sentence-transformer-v2
```

#### Model Performance Vergleich

| Model | Dimensionen | Speed | Quality | Memory | Sprachen |
|-------|-------------|-------|---------|--------|----------|
| all-MiniLM-L6-v2 | 384 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | EN/DE |
| all-mpnet-base-v2 | 768 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | EN/DE |
| paraphrase-multilingual | 384 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 50+ |
| german-roberta-v2 | 768 | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | DE |

### ChromaDB Advanced Configuration

#### Persistenz-Optionen

```python
# Standard lokale Persistierung
RAG_DB_PATH=./rag_knowledge_base

# Netzwerk-Persistierung (für Teams)
RAG_DB_PATH=/shared/network/drive/knowledge_base

# Memory-only (für Tests, ohne Persistierung)
RAG_DB_PATH=:memory:
```

#### Collection Strategies

```python
# Verschiedene Collection-Strategien:

# 1. Domain-basiert
collection_name = "python_docs"
collection_name = "react_docs" 
collection_name = "company_internal"

# 2. Zeit-basiert
collection_name = f"crawl_{datetime.now().strftime('%Y_%m')}"

# 3. Themen-basiert
collection_name = "tutorials"
collection_name = "api_references"
collection_name = "troubleshooting"
```

## Performance Tuning

### Chunk-Optimierung

#### Text Chunking Strategies

```python
# Für verschiedene Content-Typen:

# Lange Artikel/Dokumentation
RAG_CHUNK_SIZE=2000
RAG_CHUNK_OVERLAP=400

# API Dokumentation (strukturiert)
RAG_CHUNK_SIZE=800  
RAG_CHUNK_OVERLAP=100

# Chat/Dialoge (kurze Texte)
RAG_CHUNK_SIZE=500
RAG_CHUNK_OVERLAP=50

# Code-Dokumentation
RAG_CHUNK_SIZE=1200
RAG_CHUNK_OVERLAP=200
```

#### Chunk Quality Analysis

```python
# Chunk-Qualität prüfen
def analyze_chunk_quality(chunks):
    """Analysiert die Qualität der Text-Chunks."""
    stats = {
        'avg_length': sum(len(c) for c in chunks) / len(chunks),
        'length_variance': np.var([len(c) for c in chunks]),
        'empty_chunks': sum(1 for c in chunks if len(c.strip()) < 50),
        'code_chunks': sum(1 for c in chunks if '```' in c or 'def ' in c)
    }
    return stats
```

### Similarity Search Tuning

#### Similarity Threshold Guidelines

```python
# Verschiedene Anwendungsfälle:

# Exakte Treffer (FAQ, spezifische Fragen)
similarity_threshold = 0.8

# Thematische Ähnlichkeit (Recherche, Brainstorming)  
similarity_threshold = 0.6

# Verwandte Konzepte (Discovery, Ideenfindung)
similarity_threshold = 0.4

# Experimentell (sehr breite Suche)
similarity_threshold = 0.2
```

#### Advanced Search Patterns

```python
# Multi-Query Search (für bessere Recall)
queries = [
    "machine learning algorithms",
    "ML classification methods", 
    "supervised learning techniques"
]

# Weighted Search (verschiedene Query-Gewichtungen)
results = []
for query, weight in queries:
    partial_results = search_knowledge_base(query, n_results=10)
    for result in partial_results:
        result['weighted_score'] = result['similarity'] * weight
    results.extend(partial_results)

# Re-ranking basierend auf gewichteten Scores
results.sort(key=lambda x: x['weighted_score'], reverse=True)
```

### Memory und CPU Optimization

#### Batch Processing

```python
# Für große Datenmengen:
RAG_BATCH_SIZE=64    # Größere Batches für GPU
RAG_BATCH_SIZE=16    # Kleinere Batches für CPU/wenig RAM

# GPU Memory Management
RAG_DEVICE=cuda                    # Nutze GPU falls verfügbar
CUDA_VISIBLE_DEVICES=0             # Spezifische GPU auswählen
```

#### Storage Optimization

```bash
# ChromaDB Komprimierung
export CHROMA_COMPRESSION=true

# Index-Optimierung (nach vielen Inserts)
python3 -c "
from tools.knowledge_base.vector_store import VectorStore
vs = VectorStore()
vs.optimize_all_collections()  # Kompaktiert Indizes
"
```

## Advanced Use Cases

### 1. Multi-Domain Knowledge Fusion

```python
# Verschiedene Domains in separaten Collections
domains = [
    ("python_docs", "https://docs.python.org"),
    ("django_docs", "https://docs.djangoproject.com"), 
    ("react_docs", "https://react.dev")
]

# Cross-Domain Search
def search_all_domains(query):
    results = []
    for domain_name, _ in domains:
        domain_results = search_knowledge_base(
            query, 
            collection_name=domain_name,
            n_results=3
        )
        results.extend(domain_results)
    
    # Re-rank across domains
    return sorted(results, key=lambda x: x['similarity'], reverse=True)
```

### 2. Temporal Knowledge Management

```python
# Zeit-basierte Collection-Rotation
def rotate_collections():
    """Rotiert Collections basierend auf Alter."""
    current_month = datetime.now().strftime('%Y_%m')
    
    # Neue Collection für aktuellen Monat
    current_collection = f"knowledge_{current_month}"
    
    # Archiviere alte Collections (> 6 Monate)
    cutoff_date = datetime.now() - timedelta(days=180)
    old_collections = [
        name for name in list_collections()
        if parse_collection_date(name) < cutoff_date
    ]
    
    for old_collection in old_collections:
        archive_collection(old_collection)
```

### 3. Content Quality Scoring

```python
def score_content_quality(content):
    """Bewertet Content-Qualität für besseres Ranking."""
    score = 0.0
    
    # Länge (optimal 500-2000 Zeichen)
    length = len(content)
    if 500 <= length <= 2000:
        score += 0.3
    elif length > 100:
        score += 0.1
        
    # Struktur-Features
    if '##' in content or '###' in content:  # Headers
        score += 0.2
    if '```' in content:  # Code blocks
        score += 0.2
    if content.count('.') > 3:  # Sätze
        score += 0.1
    if any(word in content.lower() for word in ['beispiel', 'example', 'tutorial']):
        score += 0.2
        
    return min(score, 1.0)
```

### 4. Semantic Clustering

```python
# Automatische Themen-Erkennung in Collections
def analyze_collection_topics(collection_name, n_clusters=5):
    """Findet automatisch Themen-Cluster in einer Collection."""
    
    # Alle Dokumente aus Collection laden
    all_docs = get_all_documents(collection_name)
    
    # Embeddings extrahieren
    embeddings = [doc['embedding'] for doc in all_docs]
    
    # K-Means Clustering
    from sklearn.cluster import KMeans
    kmeans = KMeans(n_clusters=n_clusters)
    clusters = kmeans.fit_predict(embeddings)
    
    # Topic-Labels generieren
    topics = {}
    for i, cluster_id in enumerate(clusters):
        if cluster_id not in topics:
            topics[cluster_id] = []
        topics[cluster_id].append(all_docs[i]['content'][:200])
    
    return topics
```

## Troubleshooting & Debugging

### Performance Diagnostics

```python
# Performance-Monitoring für RAG-Operations
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        
        print(f"{func.__name__} took {duration:.2f}s")
        return result
    return wrapper

# Usage
@monitor_performance
def store_large_dataset(data):
    # RAG storage operation
    pass
```

### Common Issues & Solutions

#### 1. ChromaDB Lock Issues
```bash
# Problem: "database is locked"
# Lösung: Process cleanup
ps aux | grep python | grep server.py | awk '{print $2}' | xargs kill
rm -f ./rag_db/*.lock
```

#### 2. Memory Issues bei großen Dokumenten
```python
# Problem: OutOfMemoryError
# Lösung: Streaming Processing
def process_large_document_streaming(large_text):
    chunk_size = 10000  # Kleinere Chunks
    for i in range(0, len(large_text), chunk_size):
        chunk = large_text[i:i+chunk_size]
        yield process_chunk(chunk)
```

#### 3. Similarity Search liefert schlechte Ergebnisse
```python
# Debugging: Embedding-Qualität prüfen
def debug_embeddings(texts):
    embeddings = embedding_service.encode_texts(texts)
    
    # Ähnlichkeitsmatrix
    from sklearn.metrics.pairwise import cosine_similarity
    similarity_matrix = cosine_similarity(embeddings)
    
    print("Similarity Matrix:")
    print(similarity_matrix)
    
    # Analyse
    avg_similarity = similarity_matrix.mean()
    print(f"Average similarity: {avg_similarity:.3f}")
```

### Health Checks

```python
# RAG System Health Check
def health_check():
    """Vollständiger RAG-System Health Check."""
    
    health_status = {
        "dependencies": is_rag_available(),
        "vector_store": False,
        "embedding_service": False,
        "collections": []
    }
    
    try:
        # Vector Store Test
        vs = VectorStore()
        health_status["vector_store"] = True
        health_status["collections"] = vs.list_collections()
        
        # Embedding Service Test
        es = EmbeddingService()
        test_embedding = es.encode_text("test")
        health_status["embedding_service"] = len(test_embedding) > 0
        
    except Exception as e:
        health_status["error"] = str(e)
    
    return health_status

# CLI Health Check
if __name__ == "__main__":
    import json
    print(json.dumps(health_check(), indent=2))
```

## Integration Patterns

### 1. FastAPI Integration

```python
from fastapi import FastAPI
from tools.knowledge_base.rag_tools import get_rag_service

app = FastAPI()
rag_service = get_rag_service()

@app.post("/api/store")
async def store_content(content: str, collection: str = "default"):
    return rag_service.store_content(content, collection)

@app.get("/api/search")
async def search_content(query: str, collection: str = "default"):
    return rag_service.search_content(query, collection)
```

### 2. Claude Desktop Custom Tools

```json
{
  "mcpServers": {
    "crawl4ai": {
      "command": "uv",
      "args": ["run", "python", "server.py"],
      "env": {
        "RAG_MODEL_NAME": "all-mpnet-base-v2",
        "RAG_CHUNK_SIZE": "1500",
        "RAG_DB_PATH": "/Users/username/Documents/knowledge_base"
      }
    }
  }
}
```

### 3. Batch Processing Scripts

```python
#!/usr/bin/env python3
"""Batch processing script für große Crawling-Jobs."""

import asyncio
from tools.knowledge_base.rag_tools import get_rag_service

async def batch_crawl_and_store(urls, collection_name):
    """Crawlt mehrere URLs und speichert sie in RAG."""
    rag_service = get_rag_service()
    
    for url in urls:
        try:
            # Web content crawlen
            content = await web_content_extract(url)
            
            # In RAG speichern  
            result = rag_service.store_content(content, collection_name)
            print(f"✅ {url}: {result['chunks_stored']} chunks")
            
        except Exception as e:
            print(f"❌ {url}: {str(e)}")
            
        # Pause zwischen Requests
        await asyncio.sleep(1)

# Usage
urls = [
    "https://docs.python.org/3/tutorial/",
    "https://docs.python.org/3/library/",
    # ... mehr URLs
]

asyncio.run(batch_crawl_and_store(urls, "python_documentation"))
```

## Best Practices

### 1. Collection Naming
```python
# Empfohlene Naming-Konventionen:
"domain_docs"          # Einfach, beschreibend
"python_tutorial_2024" # Mit Zeitstempel für Versionierung  
"company_internal_kb"  # Klar getrennte Bereiche
"user_12345_research"  # User-spezifische Collections
```

### 2. Content Preprocessing
```python
def preprocess_web_content(content):
    """Optimiert Web-Content vor RAG-Speicherung."""
    
    # Navigation/Footer entfernen
    content = remove_navigation_elements(content)
    
    # Code-Blöcke normalisieren
    content = normalize_code_blocks(content)
    
    # Duplicate Content Detection
    content = remove_duplicate_sections(content)
    
    # Metadata anreichern
    metadata = extract_metadata(content)
    
    return content, metadata
```

### 3. Monitoring & Analytics
```python
# RAG Usage Analytics
class RAGAnalytics:
    def __init__(self):
        self.query_log = []
        self.storage_log = []
    
    def log_query(self, query, results_count, response_time):
        self.query_log.append({
            'timestamp': datetime.now(),
            'query': query,
            'results_count': results_count,
            'response_time': response_time
        })
    
    def generate_report(self):
        # Top queries, performance metrics, etc.
        pass
```

Diese erweiterte Dokumentation sollte als Referenz für Power-User und Entwickler dienen, die das RAG-System optimal nutzen und erweitern möchten.