# Crawl4AI MCP Server - Architektur Dokumentation

> **System Überblick**: Unified Server Architektur mit dual-protocol Support (MCP + HTTP), Clean Architecture Patterns und umfassendem Vector-RAG-System für Web-Content-Management.

## Inhaltsverzeichnis
1. [System Überblick](#system-überblick)
2. [Statische Architektur](#statische-architektur)
3. [Dynamische Request-Flows](#dynamische-request-flows)
4. [Datenfluss und Integration](#datenfluss-und-integration)
5. [Persistierung](#persistierung)
6. [Deployment](#deployment)

---

## System Überblick

### Unified Server Pattern

Das System implementiert eine **einheitliche Server-Architektur** die MCP (Model Context Protocol) und HTTP REST parallel bedient:

```puml
@startuml system_overview
!theme plain

package "Clients" {
  [Claude Desktop] as Claude
  [React Frontend] as React
  [External APIs] as External
}

package "Unified Server" as Server {
  [FastMCP Handler] as MCP
  [FastAPI Handler] as HTTP
  [Application Layer] as Apps
}

package "Services" {
  [Collection Service] as CollService
  [Web Crawling Service] as WebService  
  [Vector Sync Service] as VectorService
  [LLM Service] as LLMService
}

package "Infrastructure" {
  database [SQLite] as DB
  database [ChromaDB] as Vector
  database [File System] as FS
  cloud [Crawl4AI Engine] as Crawl
}

Claude --> MCP : stdio
React --> HTTP : REST API
External --> HTTP : REST API

MCP --> Apps : Use Cases
HTTP --> Apps : Use Cases

Apps --> CollService
Apps --> WebService
Apps --> VectorService
Apps --> LLMService

CollService --> DB
CollService --> FS
WebService --> Crawl
VectorService --> Vector
VectorService --> DB
LLMService --> Crawl

note right of Server
  **Dual Protocol Design:**
  • Shared business logic
  • Consistent error handling  
  • Protocol-agnostic use cases
  • Single deployment unit
end note

@enduml
```

### Kernprinzipien

- **Clean Architecture**: Schichtentrennung mit Dependency Inversion
- **Protocol-Agnostik**: Business Logic unabhängig vom Transport
- **Unified Deployment**: Ein Server-Prozess für beide Protokolle
- **Graceful Degradation**: Optional dependencies (RAG, LLM)
- **Professional Configuration**: `~/.context42/` Benutzerverzeichnis

---

## Statische Architektur

### Backend - Clean Architecture Layers

```puml
@startuml backend_architecture
!theme plain

package "Protocol Layer" #FFE0B2 {
  class UnifiedServer {
    +setup_mcp_server(): FastMCP
    +setup_http_app(): FastAPI
    +run_unified(): None
  }
  
  class FastMCP {
    +web_content_extract()
    +create_collection()
    +sync_collection_to_vectors()
    +rag_query()
  }
  
  class FastAPI {
    +/api/extract
    +/api/file-collections
    +/api/vector-sync/search
    +/api/query
  }
}

package "Application Layer" #E3F2FD {
  class CollectionManagement {
    +create_collection_use_case()
    +list_collections_use_case()
    +delete_collection_use_case()
  }
  
  class FileManagement {
    +save_file_use_case()
    +get_file_use_case()
    +list_files_use_case()
  }
  
  class WebCrawling {
    +extract_content_use_case()
    +deep_crawl_use_case()
    +link_preview_use_case()
  }
  
  class VectorSearch {
    +sync_collection_use_case()
    +search_vectors_use_case()
    +get_sync_status_use_case()
  }
  
  class RAGQuery {
    +rag_query_use_case()
    +RAGQueryRequest
    +RAGQueryResponse
  }
}

package "Service Layer" #FFF3E0 {
  interface ICollectionService
  interface IWebCrawlingService
  interface IVectorSyncService
  interface ILLMService
  
  class DatabaseCollectionManager
  class WebCrawlingManager
  class IntelligentSyncManager
  class LLMServiceFactory
}

package "Infrastructure" #F3E5F5 {
  class SQLiteDB
  class ChromaDB
  class FileSystem
  class Crawl4AI
  class Context42Config
}

UnifiedServer --> FastMCP
UnifiedServer --> FastAPI
UnifiedServer --> "Container\n(DI)"

FastMCP --> CollectionManagement
FastMCP --> WebCrawling
FastMCP --> VectorSearch
FastMCP --> RAGQuery

FastAPI --> CollectionManagement
FastAPI --> FileManagement
FastAPI --> WebCrawling
FastAPI --> VectorSearch
FastAPI --> RAGQuery

CollectionManagement --> ICollectionService
FileManagement --> ICollectionService
WebCrawling --> IWebCrawlingService
VectorSearch --> IVectorSyncService
RAGQuery --> IVectorSyncService
RAGQuery --> ILLMService

ICollectionService <|-- DatabaseCollectionManager
IWebCrawlingService <|-- WebCrawlingManager
IVectorSyncService <|-- IntelligentSyncManager
ILLMService <|-- LLMServiceFactory

DatabaseCollectionManager --> SQLiteDB
DatabaseCollectionManager --> FileSystem
WebCrawlingManager --> Crawl4AI
IntelligentSyncManager --> ChromaDB
LLMServiceFactory --> Crawl4AI

note right of "Application Layer"
  **Use Case Pattern:**
  • Input validation mit ValidationError
  • Protocol-agnostische Geschäftslogik
  • Konsistente Fehlerbehandlung
  • Service-Komposition
end note

@enduml
```

### Frontend - React Component Architektur

```puml
@startuml frontend_architecture
!theme plain

package "App Shell" #E8F5E8 {
  class NewApp {
    +Providers orchestration
    +Error boundaries
    +Theme management
  }
  
  class CollectionProvider {
    -state: CollectionState
    -dispatch: Dispatch
    +useCollectionOperations()
  }
}

package "Pages (Route Handlers)" #E3F2FD {
  class FileCollectionsPage {
    +Collection management UI
    +File explorer integration
  }
  
  class RAGQueryPage {
    +RAG query interface
    +Vector search results
  }
}

package "Complex Components" #FFF3E0 {
  class CollectionSidebar {
    +Collection tree view
    +Navigation logic
  }
  
  class MainContent {
    +File editor (Monaco)
    +Content viewer
  }
  
  class EnhancedSyncControls {
    +Vector sync operations
    +Status monitoring
  }
  
  class VectorSearchPanel {
    +Semantic search UI
    +Results display
  }
}

package "UI Components" #FFE0B2 {
  class Button
  class TextField
  class Typography
  class LoadingButton
}

package "Services" #FFEBEE {
  class APIService {
    +HTTP client wrapper
    +Error handling
    +Type-safe responses
  }
  
  class CustomHooks {
    +useCollectionOperations
    +useVectorSync
    +useApi
  }
}

NewApp --> CollectionProvider
NewApp --> FileCollectionsPage

FileCollectionsPage --> CollectionSidebar
FileCollectionsPage --> MainContent

RAGQueryPage --> EnhancedSyncControls
RAGQueryPage --> VectorSearchPanel

CollectionSidebar --> Button
MainContent --> TextField
EnhancedSyncControls --> LoadingButton

CustomHooks --> APIService
CollectionProvider --> CustomHooks

note right of CollectionProvider
  **State Management:**
  • Context + useReducer pattern
  • 42 action types mit TypeScript
  • Optimistic updates
  • Error recovery
end note

@enduml
```

---

## Dynamische Request-Flows

### Unified Protocol Request Flow

```puml
@startuml request_flow
!theme plain

participant "Client\n(Claude/Frontend)" as Client
participant "UnifiedServer" as Server
participant "Protocol Handler\n(MCP/HTTP)" as Protocol
participant "Use Case" as UC
participant "Service" as Service
participant "Infrastructure" as Infra

== Request Processing ==
Client -> Server: Request (MCP stdio / HTTP REST)
Server -> Protocol: Route to protocol handler
Protocol -> UC: Call use-case with validation

note over UC
  **Protocol-Agnostic Logic:**
  Same use-case handles both
  MCP and HTTP requests
end note

UC -> Service: Business operation
Service -> Infra: Data persistence/retrieval
Infra --> Service: Result
Service --> UC: Domain object
UC --> Protocol: Structured response

== Protocol-Specific Response Formatting ==
alt MCP Protocol
  Protocol --> Server: JSON string
  Server --> Client: stdio response
else HTTP Protocol  
  Protocol --> Server: HTTP response object
  Server --> Client: REST JSON
end

note over Protocol
  **Error Consistency:**
  Validation errors mapped to
  appropriate protocol format
end note

@enduml
```

### Collection Management Workflow

```puml
@startuml collection_workflow
!theme plain

participant "User" as User
participant "Frontend" as FE
participant "REST API" as API
participant "Collection UC" as UC
participant "Collection Service" as CS
participant "SQLite + FS" as Storage

== Collection Creation ==
User -> FE: Create "Research Notes"
FE -> API: POST /api/file-collections\n{"name": "Research Notes"}
API -> UC: create_collection_use_case(service, name)
UC -> UC: validate_collection_name()
UC -> CS: create_collection(name, description)
CS -> Storage: INSERT collection metadata
CS -> Storage: CREATE directory structure
Storage --> CS: Collection created
CS --> UC: CollectionInfo
UC --> API: CollectionInfo
API --> FE: {"success": true, "data": {...}}

== File Operations ==
User -> FE: Save "analysis.md"
FE -> API: POST /api/file-collections/{id}/files
API -> UC: save_file_use_case(service, collection_id, filename, content)
UC -> CS: save_file(collection_name, filename, content, folder)
CS -> Storage: WRITE file to filesystem
CS -> Storage: UPDATE file metadata in SQLite
CS -> CS: calculate_file_hash(content)
Storage --> CS: File saved
CS --> UC: FileInfo
UC --> API: FileInfo
API --> FE: {"success": true, "data": {...}}

@enduml
```

### Vector Search + RAG Integration

```puml
@startuml rag_workflow
!theme plain

participant "User" as User
participant "Frontend" as FE
participant "REST API" as API
participant "RAG Use Case" as RAG
participant "Vector Service" as VS
participant "LLM Service" as LLM
participant "ChromaDB" as CDB

== Vector Synchronization ==
User -> FE: Sync "Research Notes" to vectors
FE -> API: POST /api/vector-sync/collections/{name}/sync
API -> VS: sync_collection(collection_name, config)
VS -> VS: load_collection_files()
VS -> VS: chunk_content(strategy="sentence")
VS -> VS: generate_embeddings(chunks)
VS -> CDB: upsert_documents(chunks, embeddings)
CDB --> VS: Sync complete
VS --> API: SyncResult
API --> FE: {"success": true, "sync_result": {...}}

== RAG Query Processing ==
User -> FE: Query "What are the main findings?"
FE -> API: POST /api/query\n{"query": "...", "collection_name": "Research Notes"}
API -> RAG: rag_query_use_case(vector_service, llm_service, request)

RAG -> VS: search_vectors(query, collection, limit, threshold)
VS -> VS: generate_query_embedding(query)
VS -> CDB: similarity_search(embedding, filters)
CDB --> VS: similar_chunks_with_scores
VS --> RAG: VectorSearchResults

RAG -> RAG: prepare_context(search_results)
RAG -> LLM: generate_response(query, context, max_tokens)
LLM --> RAG: Generated answer
RAG --> API: RAGQueryResponse
API --> FE: {"success": true, "answer": "...", "sources": [...]}

@enduml
```

### Web Crawling Integration

```puml
@startuml crawling_workflow
!theme plain

participant "User" as User
participant "Frontend" as FE
participant "REST API" as API
participant "Crawl UC" as CUC
participant "Web Service" as WS
participant "Collection Service" as CS
participant "Crawl4AI" as C4AI

== Content Extraction ==
User -> FE: Extract "https://example.com"
FE -> API: POST /api/extract {"url": "https://example.com"}
API -> CUC: extract_content_use_case(web_service, url)
CUC -> CUC: validate_url_format(url)
CUC -> WS: extract_content(url)
WS -> C4AI: crawl(url, extraction_strategy="NoExtractionStrategy")
C4AI --> WS: raw_content, metadata
WS -> WS: process_content(raw_content)
WS --> CUC: CrawlResult(url, content, metadata, error)
CUC --> API: CrawlResult
API --> FE: {"success": true, "data": {"content": "...", "metadata": {...}}}

== Save to Collection ==
User -> FE: Save to "Research Notes"
FE -> API: POST /api/crawl/single/{collection_id}
API -> CUC: crawl_single_page_to_collection_use_case()
CUC -> WS: extract_content(url)
WS --> CUC: CrawlResult
CUC -> CS: save_file(collection_name, filename, content)
CS --> CUC: FileInfo
CUC --> API: {"success": true, "file": {...}}

@enduml
```

---

## Datenfluss und Integration

### Service Layer Integration

```puml
@startuml service_integration
!theme plain

package "Dependency Injection Container" {
  class Container {
    +collection_service: Singleton
    +web_crawling_service: Singleton
    +vector_sync_service: Singleton
    +llm_service: Factory
  }
}

package "Service Implementations" {
  class DatabaseCollectionManager {
    -collections_dir: Path
    -db_manager: DatabaseManager
    +create_collection()
    +save_file()
  }
  
  class IntelligentSyncManager {
    -vector_store: VectorStore
    -embedding_service: EmbeddingService
    +sync_collection()
    +search_vectors()
  }
  
  class WebCrawlingManager {
    -crawler: AsyncWebCrawler
    +extract_content()
    +deep_crawl()
  }
  
  class LLMServiceFactory {
    +create_ollama_service()
    +create_openai_service()
    +health_check()
  }
}

Container --> DatabaseCollectionManager
Container --> IntelligentSyncManager  
Container --> WebCrawlingManager
Container --> LLMServiceFactory

note right of Container
  **Shared State Management:**
  Services als Singletons für
  konsistente Datenoperationen
  zwischen MCP und HTTP
end note

@enduml
```

### Error Handling Strategy

```puml
@startuml error_handling
!theme plain

participant "Client" as Client
participant "Protocol Handler" as Protocol  
participant "Use Case" as UC
participant "Service" as Service

== Validation Error ==
Client -> Protocol: Invalid request
Protocol -> UC: use_case_function(invalid_params)
UC -> UC: validate_input()
UC --> Protocol: ValidationError(code, message, details)

alt MCP Protocol
  Protocol --> Client: {"success": false, "error": message, "code": code}
else HTTP Protocol
  Protocol --> Client: HTTPException(400, {"error": {"code": code, "message": message}})
end

== Service Error ==
Client -> Protocol: Valid request
Protocol -> UC: use_case_function(params)
UC -> Service: service_method(params)
Service --> UC: Exception("Service failed")
UC --> Protocol: Exception

alt MCP Protocol
  Protocol --> Client: {"success": false, "error": "Service failed"}
else HTTP Protocol
  Protocol --> Client: HTTPException(500, "Internal Server Error")
end

== Business Logic Error ==
Client -> Protocol: Business constraint violation
Protocol -> UC: use_case_function(params)
UC -> UC: business_validation()
UC --> Protocol: ValidationError("BUSINESS_RULE_VIOLATION", details)

alt MCP Protocol
  Protocol --> Client: {"success": false, "error": message, "code": "BUSINESS_RULE_VIOLATION"}
else HTTP Protocol
  Protocol --> Client: HTTPException(400, structured_error)
end

@enduml
```

---

## Persistierung

### User Directory Structure

```text
~/.context42/
├── databases/
│   ├── vector_sync.db              # SQLite: Collections & Sync Status
│   └── chromadb/                   # ChromaDB: Vector Store
│       └── crawl4ai_documents/
├── config/
│   ├── default.env                 # Standard-Konfiguration
│   └── user.env                    # Benutzer-Overrides
├── logs/
│   └── crawl4ai-mcp.log           # Zentralisiertes Logging
└── cache/
    └── crawling/                   # Optional: Crawling Cache
```

### Data Model Relationships

```puml
@startuml data_model
!theme plain

class FileCollection {
  +id: str
  +name: str
  +description: str
  +created_at: datetime
  +file_count: int
}

class FileInfo {
  +name: str
  +path: str
  +content: str
  +size: int
  +collection_name: str
  +file_hash: str
  +created_at: datetime
}

class VectorSyncStatus {
  +collection_name: str
  +sync_status: "never_synced" | "in_sync" | "out_of_sync"
  +vector_count: int
  +last_sync: datetime
  +sync_version: int
}

class VectorDocument {
  +id: UUID
  +collection_name: str
  +source_file: str
  +chunk_content: str
  +embedding: float[]
  +metadata: dict
  +chunk_index: int
}

class CrawlResult {
  +url: str
  +content: str
  +metadata: dict
  +error: str?
  +success: bool
}

FileCollection ||--o{ FileInfo : contains
FileCollection ||--o| VectorSyncStatus : has_sync_status
VectorSyncStatus ||--o{ VectorDocument : tracks_vectors
FileInfo ||--o{ VectorDocument : chunked_into
CrawlResult ..> FileInfo : can_be_saved_as

note bottom of VectorDocument
  **Chunking Strategies:**
  • sentence: Satzbasiert mit NLTK
  • paragraph: Absatzbasiert  
  • baseline: Fixed-size mit Overlap
  • overlap-aware: Intelligent chunking
end note

@enduml
```

### Storage Architecture

```puml
@startuml storage_architecture
!theme plain

package "Storage Layer" {
  database "SQLite\n(~/.context42/databases/)" as SQLite {
    table collections {
      id: TEXT PRIMARY KEY
      name: TEXT UNIQUE
      description: TEXT
      created_at: TEXT
      file_count: INTEGER
    }
    
    table collection_files {
      id: TEXT PRIMARY KEY
      collection_name: TEXT
      filename: TEXT
      folder: TEXT
      content: TEXT
      size: INTEGER
    }
    
    table vector_sync_status {
      collection_name: TEXT PRIMARY KEY
      sync_status: TEXT
      vector_count: INTEGER
      last_sync: TEXT
    }
  }
  
  database "ChromaDB\n(~/.context42/databases/chromadb/)" as ChromaDB {
    collection crawl4ai_documents {
      id: UUID
      embedding: VECTOR
      metadata: JSON
      document: TEXT
    }
  }
  
  package "File System" as FS {
    file "Collection Files\n(content storage)"
    file "Config Files\n(~/.context42/config/)"
    file "Logs\n(~/.context42/logs/)"
  }
}

package "Service Access" {
  class DatabaseCollectionManager {
    +SQLite operations
    +File system operations
  }
  
  class IntelligentSyncManager {
    +ChromaDB operations
    +Embedding operations
  }
  
  class Context42Config {
    +Configuration management
    +Directory setup
  }
}

DatabaseCollectionManager --> SQLite
DatabaseCollectionManager --> FS
IntelligentSyncManager --> ChromaDB
Context42Config --> FS

@enduml
```

---

## Deployment

### Development vs Production Setup

```puml
@startuml deployment
!theme plain

package "Development Environment" {
  node "Local Machine" {
    [React Dev Server\n:3000] as ReactDev
    [Unified Server\n:8000] as ServerDev
    [SQLite DB] as DBDev
    [ChromaDB] as VectorDev
  }
  
  [Claude Desktop] as ClaudeDev
  [Browser] as BrowserDev
}

package "Production Environment" {
  node "Server/Container" {
    [Built React App\n(static)] as ReactProd
    [Unified Server\n:8000] as ServerProd
    [SQLite DB] as DBProd
    [ChromaDB] as VectorProd
  }
  
  [MCP Clients] as MCPProd
  [Web Clients] as WebProd
}

== Development Mode ==
BrowserDev -> ReactDev : http://localhost:3000
ReactDev -> ServerDev : API calls to :8000
ClaudeDev -> ServerDev : MCP stdio protocol

ServerDev -> DBDev : SQLite operations
ServerDev -> VectorDev : Vector operations

== Production Mode ==
WebProd -> ReactProd : Static file serving
WebProd -> ServerProd : REST API
MCPProd -> ServerProd : MCP protocol

ServerProd -> DBProd : SQLite operations
ServerProd -> VectorProd : Vector operations

note right of ServerDev
  **Development Features:**
  • CORS enabled für Frontend
  • Debug logging
  • Hot reload mit Vite
  • Concurrent protocols
end note

note right of ServerProd
  **Production Features:**
  • Process management
  • Error tracking  
  • Performance monitoring
  • Security headers
end note

@enduml
```

### Configuration Management

```puml
@startuml configuration
!theme plain

class Context42Config {
  +CONTEXT42_HOME: Path
  +databases_dir: Path
  +config_dir: Path
  +logs_dir: Path
  
  +setup_directories()
  +migrate_legacy_data()
  +load_environment_config()
}

package "Configuration Hierarchy" {
  [Environment Variables] as ENV
  [~/.context42/config/user.env] as UserEnv
  [~/.context42/config/default.env] as DefaultEnv
  [Code Defaults] as CodeDefaults
}

ENV --> Context42Config : Highest priority
UserEnv --> Context42Config : User overrides
DefaultEnv --> Context42Config : System defaults
CodeDefaults --> Context42Config : Fallback values

note right of "Configuration Hierarchy"
  **Priority Order:**
  1. Environment Variables (höchste)
  2. User Config (~/.context42/config/user.env)
  3. Default Config (~/.context42/config/default.env) 
  4. Code Defaults (niedrigste)
end note

@enduml
```

---

## Komponenten-Referenz

### Backend Service/Use-Case Mapping

| Funktionalität | Use-Case Funktion | Service Methode | API Endpoint |
|----------------|-------------------|-----------------|--------------|
| **Collections** |
| Erstellen | `create_collection_use_case` | `CollectionService.create_collection` | `POST /api/file-collections` |
| Auflisten | `list_collections_use_case` | `CollectionService.list_collections` | `GET /api/file-collections` |
| Abrufen | `get_collection_use_case` | `CollectionService.get_collection` | `GET /api/file-collections/{id}` |
| Löschen | `delete_collection_use_case` | `CollectionService.delete_collection` | `DELETE /api/file-collections/{id}` |
| **Files** |
| Speichern | `save_file_use_case` | `CollectionService.save_file` | `POST /api/file-collections/{id}/files` |
| Abrufen | `get_file_use_case` | `CollectionService.get_file` | `GET /api/file-collections/{id}/files/{name}` |
| Aktualisieren | `update_file_use_case` | `CollectionService.save_file` | `PUT /api/file-collections/{id}/files/{name}` |
| **Web Crawling** |
| Content extrahieren | `extract_content_use_case` | `WebCrawlingService.extract_content` | `POST /api/extract` |
| Deep Crawling | `deep_crawl_use_case` | `WebCrawlingService.deep_crawl` | `POST /api/deep-crawl` |
| Link Preview | `link_preview_use_case` | `WebCrawlingService.preview_links` | `POST /api/link-preview` |
| **Vector Operations** |
| Synchronisieren | `sync_collection_use_case` | `VectorSyncService.sync_collection` | `POST /api/vector-sync/collections/{name}/sync` |
| Status abrufen | `get_sync_status_use_case` | `VectorSyncService.get_sync_status` | `GET /api/vector-sync/collections/{name}/status` |
| Durchsuchen | `search_vectors_use_case` | `VectorSyncService.search_vectors` | `POST /api/vector-sync/search` |
| **RAG Query** |
| RAG Anfrage | `rag_query_use_case` | `LLMService.generate_response` | `POST /api/query` |

### Frontend Komponenten-Mapping

| UI Bereich | Komponente | Zweck | Key Props/State |
|------------|------------|-------|-----------------|
| **Hauptlayout** |
| App Shell | `NewApp` | Root mit Providern | theme, error boundaries |
| Navigation | `TopNavigation` | Haupt-Navigationsleiste | current route, actions |
| Sidebar | `CollectionSidebar` | Collections & Dateibaum | selected collection, files |
| Content | `MainContent` | Editor/Search Bereich | active view, content |
| **Collections** |
| Collection List | Sidebar integration | Liste aller Collections | collections, loading |
| File Tree | `FileExplorer` | Hierarchische Dateien | files, folders, selection |
| **File Operations** |
| Editor | `MarkdownEditor` (Monaco) | Datei-Editor | content, language, save |
| **Vector & RAG** |
| Vector Search | `VectorSearchPanel` | Semantische Suche | query, results, filters |
| Sync Controls | `EnhancedSyncControls` | Vector Sync Management | sync state, progress |

Diese Architektur bietet eine solide Grundlage für die Weiterentwicklung des Systems bei gleichzeitiger Beibehaltung der Flexibilität für sich entwickelnde Anforderungen.