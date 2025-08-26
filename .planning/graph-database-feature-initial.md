# Graph Database Feature - Initial Planning

## Überblick

Integration einer Graph-Datenbank (Neo4j) für Collections, um Inhalte als vernetzte Entitäten zu visualisieren und semantische Beziehungen zwischen Dokumenteninhalten zu erkunden.

## Backend Integration

### Neo4j Integration
- **Python-Treiber**: `neo4j` oder `py2neo` für Graph-Operationen
- **MERGE-basierte Pipeline**: Konsistente Daten-Persistierung ohne Duplikate
- **Optional Dependencies**: Analog zu ChromaDB/RAG - nur verfügbar wenn installiert
- **Connection Management**: Singleton-Pattern für DB-Verbindungen

### Entity Extraction Pipeline
- **NLP Processing**: SpaCy für Named Entity Recognition aus Markdown-Inhalten
- **Alternative**: Lokales LLM (Ollama) für komplexere Entitätserkennung
- **Content Parsing**: Überschriften, Absätze, Listen aus .md-Dateien extrahieren
- **Relationship Detection**: Automatische Erkennung von Verbindungen zwischen Entitäten

### Graph Schema Design
```cypher
# Knoten-Typen
(:Section {title, content, file_path, line_number})
(:Entity {name, type, confidence_score})

# Beziehungs-Typen  
(:Section)-[:MENTIONS]->(:Entity)
(:Entity)-[:RELATED_TO]->(:Entity)
(:Section)-[:FOLLOWS]->(:Section)
```

### Graph Sync API
- **Endpoint**: `/api/graph-sync/collections/{name}/sync`
- **Manual Trigger**: Analog zur Vector-Sync-Logik, kein Auto-Sync
- **Status Tracking**: `/api/graph-sync/collections/{name}/status`
- **Error Handling**: Konsistent mit bestehender API-Struktur

## Frontend Erweiterung

### Navigation Integration
- **Neuer Tab**: "Graph" in der Hauptnavigation (neben Collections, RAG)
- **Collection Selection**: Dropdown für Graph-Ansicht pro Collection
- **Conditional Rendering**: Nur anzeigen wenn Neo4j verfügbar (ähnlich RAG)

### Graph Visualisierung
- **Library**: D3.js, vis.js oder react-graph-vis für interaktive Darstellung
- **Layout Algorithmen**: Force-directed, hierarchical oder circular layouts
- **Interaktivität**: Node-Click für Details, Zoom/Pan, Filter-Optionen

### Graph API Endpoints
```
GET /api/graph/collections/{name}/nodes
GET /api/graph/collections/{name}/relationships  
GET /api/graph/collections/{name}/full-graph
POST /api/graph/search/entities
```

## Architektur-Prinzipien

### Parallel zu bestehenden Systemen
- **Eigenständiges Modul**: Unabhängig von RAG/Vector-System
- **Gleiche Patterns**: Sync-Button, Status-Indicator, Error-Handling
- **Service Layer**: Trennung von Graph-Logik und API-Layer

### Integration Points
- **Collection Manager**: Erweitern für Graph-Metadaten
- **File Processing**: Hooks in bestehende Markdown-Pipeline
- **API Consistency**: Status Codes und Error-Format wie Vector-Sync

## Implementierungs-Phasen

1. **Backend Foundation**: Neo4j-Integration, Entity-Extraction, Graph-Schema
2. **API Layer**: RESTful Endpoints für Graph-Operationen
3. **Frontend Base**: Graph-Tab, Collection-Selection, API-Integration
4. **Visualization**: Graph-Rendering, Interaktivität, Layout-Optionen
5. **Polish**: Error-Handling, Loading-States, Performance-Optimierung

## Technische Überlegungen

### Dependencies
- **Optional Installation**: `pip install neo4j spacy` für Graph-Features
- **Graceful Degradation**: UI versteckt Graph-Tab wenn nicht verfügbar
- **Model Downloads**: SpaCy-Modelle lazy-loading bei erstem Sync

### Performance
- **Lazy Loading**: Graph-Daten nur bei Bedarf laden
- **Caching**: Client-side Caching für wiederholte Graph-Abfragen  
- **Batch Processing**: Große Collections in Chunks verarbeiten

### Security
- **Input Sanitization**: Collection-Namen und Entity-Extraktion absichern
- **Query Validation**: Cypher-Injection-Schutz bei direkten Queries
- **Access Control**: Graph-Zugriff pro Collection beschränken