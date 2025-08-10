# Crawl4AI MCP Server - Architecture Documentation

## Inhaltsverzeichnis
1. [System Überblick](#system-überblick)
2. [Frontend Architektur](#frontend-architektur)
3. [Backend Architektur](#backend-architektur)
4. [Protokoll Integration](#protokoll-integration)
5. [Datenfluss und Workflows](#datenfluss-und-workflows)
6. [Persistierung](#persistierung)
7. [Deployment Architektur](#deployment-architektur)

---

## System Überblick

Das Crawl4AI MCP Server System implementiert eine **Dual-Protokoll Architektur** mit geteilter Business Logic:

```puml
@startuml System Overview
!theme plain

package "Frontend (React + TypeScript)" {
  [Collection Manager UI]
  [Vector Search Interface]
  [File Editor]
}

package "Backend (Python)" {
  [Unified Server] 
  [Application Layer]
  [Service Layer]
}

package "Infrastructure" {
  [Crawl4AI Engine]
  [ChromaDB Vectors]
  [SQLite Database]
  [File System]
}

[Collection Manager UI] --> [Unified Server] : REST API
[Claude Desktop] --> [Unified Server] : MCP Protocol
[Unified Server] --> [Application Layer] : Use Cases
[Application Layer] --> [Service Layer] : Service Interfaces
[Service Layer] --> [Crawl4AI Engine]
[Service Layer] --> [ChromaDB Vectors]
[Service Layer] --> [SQLite Database]
[Service Layer] --> [File System]

note right of [Unified Server]
  **Dual Protocol Support:**
  • REST API für Frontend
  • MCP für Claude Desktop
  • Geteilte Business Logic
end note

@enduml
```

### Kernprinzipien
- **Protokoll-Agnostik**: Business Logic unabhängig von Transport Protocol
- **Clean Architecture**: Klare Schichtentrennung mit Dependency Inversion
- **Dual Protocol Support**: MCP (stdio) + REST API (HTTP) parallel
- **Optional Dependencies**: Graceful Degradation bei fehlenden Features

---

## Frontend Architektur

### Komponent Hierarchie

```puml
@startuml Frontend Component Hierarchy
!theme plain

package "App Shell" {
  [NewApp] as App
  [AppThemeProvider] as Theme
  [ErrorBoundary] as Error
  [NotificationProvider] as Notify
  [CollectionProvider] as Context
}

package "Main Interface" {
  [CollectionFileManager] as FileManager
  [CollectionSidebar] as Sidebar
  [MainContent] as Main
  [FileEditor] as Editor
  [VectorSearch] as Search
}

package "UI Components" {
  [LoadingButton] as Loading
  [ConfirmDialog] as Dialog
  [FileTree] as Tree
  [StatusIndicator] as Status
}

package "Forms" {
  [CollectionForm] as ColForm
  [FileUpload] as Upload
  [SearchForm] as SearchF
}

App --> Theme
Theme --> Error
Error --> Notify
Notify --> Context
Context --> FileManager

FileManager --> Sidebar
FileManager --> Main
FileManager --> Dialog

Sidebar --> Tree
Sidebar --> ColForm

Main --> Editor
Main --> Search
Main --> Upload

Search --> SearchF
Dialog --> Loading
Tree --> Status

note right of Context
  **State Management:**
  • React Context + useReducer
  • 42 Action Types
  • Immutable State Updates
  • Error Boundaries
end note

@enduml
```

### State Management Architektur

```puml
@startuml State Management
!theme plain

class CollectionState {
  +collections: FileCollection[]
  +selectedCollection: string | null
  +files: FileNode[]
  +folders: FolderNode[]
  +editor: EditorState
  +vectorSync: VectorSyncState
  +ui: UIState
}

class CollectionActions {
  +CREATE_COLLECTION_SUCCESS
  +SET_SELECTED_COLLECTION
  +UPDATE_FILE_CONTENT
  +SET_VECTOR_SEARCH_RESULTS
  +SET_LOADING_STATE
  +SET_ERROR_MESSAGE
  ... (42 total actions)
}

class CollectionProvider {
  -state: CollectionState
  -dispatch: Dispatch<CollectionAction>
  +useCollectionState()
  +updateCollections()
  +selectCollection()
  +saveFile()
  +searchVectors()
}

CollectionProvider --> CollectionState : manages
CollectionProvider --> CollectionActions : dispatches
CollectionProvider --> "React Components" : provides state

note right of CollectionActions
  **Action Pattern:**
  • Request/Success/Error triplets
  • Optimistic updates
  • Rollback on errors
  • Consistent loading states
end note

@enduml
```

### API Service Layer

```puml
@startuml Frontend API Layer
!theme plain

class APIService {
  -baseURL: string
  +extractWebContent(url): Promise<ExtractResult>
  +createFileCollection(data): Promise<CollectionInfo>
  +saveFileToCollection(id, file): Promise<FileInfo>
  +searchVectors(query): Promise<VectorSearchResult[]>
  +syncCollectionToVectors(id): Promise<SyncResult>
}

class CollectionService {
  +createCollection()
  +listCollections()
  +getCollection()
  +deleteCollection()
}

class FileService {
  +listFiles()
  +getFile()
  +saveFile()
  +deleteFile()
}

class WebCrawlingService {
  +extractContent()
  +deepCrawl()
  +previewLinks()
}

class VectorService {
  +syncCollection()
  +searchVectors()
  +getStatus()
}

APIService --> CollectionService
APIService --> FileService
APIService --> WebCrawlingService
APIService --> VectorService

note right of APIService
  **HTTP Client Features:**
  • Axios-based requests
  • Error interceptors
  • Request/Response transformation
  • Loading state management
end note

@enduml
```

---

## Backend Architektur

### Unified Server Design

```puml
@startuml Backend Architecture
!theme plain

package "Protocol Layer" {
  [FastAPI Server] as HTTP
  [FastMCP Server] as MCP
  [Unified Server] as Unified
}

package "Application Layer" {
  [Collection Use Cases] as CollUC
  [File Use Cases] as FileUC
  [Web Crawling Use Cases] as WebUC
  [Vector Search Use Cases] as VecUC
  [Crawl Integration Use Cases] as IntUC
}

package "Service Layer" {
  interface ICollectionService
  interface IWebCrawlingService  
  interface IVectorSyncService
  
  [Collection Service Impl] as CollImpl
  [Web Crawling Service Impl] as WebImpl
  [Vector Sync Service Impl] as VecImpl
}

package "Infrastructure" {
  [File System] as FS
  [SQLite Database] as DB
  [ChromaDB] as Vector
  [Crawl4AI] as Crawler
}

Unified --> HTTP : "configures"
Unified --> MCP : "configures"

HTTP --> CollUC : "calls use cases"
HTTP --> FileUC
HTTP --> WebUC
HTTP --> VecUC
HTTP --> IntUC

MCP --> CollUC : "calls use cases"
MCP --> FileUC
MCP --> WebUC
MCP --> VecUC
MCP --> IntUC

CollUC --> ICollectionService
FileUC --> ICollectionService
WebUC --> IWebCrawlingService
VecUC --> IVectorSyncService
IntUC --> IWebCrawlingService
IntUC --> ICollectionService

ICollectionService <|-- CollImpl
IWebCrawlingService <|-- WebImpl
IVectorSyncService <|-- VecImpl

CollImpl --> FS
CollImpl --> DB
WebImpl --> Crawler
VecImpl --> Vector
VecImpl --> DB

note right of "Application Layer"
  **Use Case Pattern:**
  • Protocol-agnostic business logic
  • Input validation with ValidationError
  • Consistent error handling
  • Service composition
end note

note right of "Service Layer"
  **Dependency Injection:**
  • Interface-based design
  • Singleton service instances
  • Graceful degradation
  • Testable boundaries
end note

@enduml
```

### Use Case Layer Detail

```puml
@startuml Use Case Layer
!theme plain

package "Collection Management" {
  class CollectionUseCases {
    +create_collection_use_case(service, name, description): CollectionInfo
    +list_collections_use_case(service): List[CollectionInfo]
    +get_collection_use_case(service, id): CollectionInfo
    +delete_collection_use_case(service, id): DeleteResult
  }
}

package "File Management" {
  class FileUseCases {
    +list_files_use_case(service, collection_id): List[FileInfo]
    +get_file_use_case(service, collection_id, filename, folder): FileInfo
    +save_file_use_case(service, collection_id, filename, content, folder): FileInfo
    +update_file_use_case(service, collection_id, filename, content, folder): FileInfo
    +delete_file_use_case(service, collection_id, filename, folder): DeleteResult
  }
}

package "Web Crawling" {
  class WebCrawlingUseCases {
    +extract_content_use_case(service, url): CrawlResult
    +deep_crawl_use_case(service, domain_url, config): List[CrawlResult]
    +link_preview_use_case(service, domain_url, include_external): LinkPreview
  }
}

package "Vector Search" {
  class VectorSearchUseCases {
    +sync_collection_use_case(service, name, force_reprocess, chunking_strategy): SyncResult
    +get_sync_status_use_case(service, name): SyncStatus
    +get_all_sync_statuses_use_case(service): Dict[str, SyncStatus]
    +search_vectors_use_case(service, query, collection_name, limit, threshold): List[VectorResult]
    +delete_collection_vectors_use_case(service, name): DeleteResult
  }
}

package "Integration" {
  class IntegrationUseCases {
    +crawl_single_page_to_collection_use_case(web_service, collection_service, name, url, folder): FileInfo
  }
}

class ValidationError {
  +code: string
  +message: string
  +details: dict
}

CollectionUseCases --> ValidationError : raises
FileUseCases --> ValidationError : raises
WebCrawlingUseCases --> ValidationError : raises
VectorSearchUseCases --> ValidationError : raises
IntegrationUseCases --> ValidationError : raises

note bottom of ValidationError
  **Consistent Error Codes:**
  • INVALID_COLLECTION_NAME_TYPE
  • MISSING_URL
  • INVALID_URL_FORMAT
  • CRAWL_FAILED
  • SYNC_FAILED
  • SERVICE_UNAVAILABLE
end note

@enduml
```

### Service Interface Design

```puml
@startuml Service Interfaces
!theme plain

interface ICollectionService {
  +create_collection(name: str, description: str): CollectionInfo
  +list_collections(): List[CollectionInfo]
  +get_collection_by_id(collection_id: str): CollectionInfo
  +delete_collection(collection_id: str): DeleteResult
  +save_file(collection_name: str, filename: str, content: str, folder: str): FileInfo
  +get_file(collection_name: str, filename: str, folder: str): FileInfo
  +list_files(collection_name: str): List[FileInfo]
  +delete_file(collection_name: str, filename: str, folder: str): DeleteResult
}

interface IWebCrawlingService {
  +extract_content(url: str): CrawlResult
  +deep_crawl(config: DeepCrawlConfig): List[CrawlResult] 
  +preview_links(domain_url: str, include_external: bool): LinkPreview
}

interface IVectorSyncService {
  +sync_collection(collection_name: str, force_reprocess: bool, chunking_strategy: str): SyncResult
  +get_sync_status(collection_name: str): SyncStatus
  +get_all_sync_statuses(): Dict[str, SyncStatus]
  +search_vectors(query: str, collection_name: Optional[str], limit: int, similarity_threshold: float): List[VectorResult]
  +delete_collection_vectors(collection_name: str): DeleteResult
}

class DatabaseCollectionManager {
  -collections_dir: str
  -db_path: str
}

class WebCrawlingManager {
  -user_agent: str
  -timeout: int
}

class IntelligentSyncManager {
  -vector_store: VectorStore
  -persistent_manager: PersistentSyncManager
  -embedding_model: str
}

ICollectionService <|-- DatabaseCollectionManager
IWebCrawlingService <|-- WebCrawlingManager  
IVectorSyncService <|-- IntelligentSyncManager

note right of DatabaseCollectionManager
  **Features:**
  • File-based collections
  • SQLite metadata storage
  • Atomic operations
  • Path validation
end note

note right of IntelligentSyncManager
  **Features:**
  • ChromaDB integration
  • Intelligent chunking
  • Incremental sync
  • Optional dependency handling
end note

@enduml
```

---

## Protokoll Integration

### Dual-Protocol Request Handling

```puml
@startuml Protocol Integration
!theme plain

actor "React Frontend" as Frontend
actor "Claude Desktop" as Claude

participant "FastAPI Server" as HTTP
participant "FastMCP Server" as MCP
participant "Use Case Layer" as UC
participant "Service Layer" as Service

== REST API Request ==
Frontend -> HTTP: POST /api/file-collections
HTTP -> UC: create_collection_use_case(service, name, description)
UC -> Service: create_collection(name, description)
Service --> UC: CollectionInfo
UC --> HTTP: CollectionInfo
HTTP --> Frontend: {"success": true, "data": {...}}

== MCP Tool Request ==  
Claude -> MCP: create_collection(name="test", description="test desc")
MCP -> UC: create_collection_use_case(service, name, description)
UC -> Service: create_collection(name, description)
Service --> UC: CollectionInfo
UC --> MCP: CollectionInfo
MCP --> Claude: {"success": true, "collection": {...}}

note over UC
  **Shared Business Logic:**
  Same use-case function handles
  both protocols with identical
  validation and processing
end note

@enduml
```

### Error Handling Consistency

```puml
@startuml Error Handling
!theme plain

participant "Protocol Handler" as Protocol
participant "Use Case" as UC
participant "Service" as Service

== Happy Path ==
Protocol -> UC: use_case_function(params)
UC -> Service: service_method(params)
Service --> UC: Success Result
UC --> Protocol: Domain Object
Protocol --> "Client": Protocol-specific Success Response

== Validation Error ==
Protocol -> UC: use_case_function(invalid_params)
UC --> Protocol: ValidationError(code, message, details)
alt REST Protocol
  Protocol --> "Client": HTTPException(400, structured_error)
else MCP Protocol  
  Protocol --> "Client": {"success": false, "error": message, "code": code}
end

== Service Error ==
Protocol -> UC: use_case_function(params)
UC -> Service: service_method(params)
Service --> UC: Exception("Service failed")
UC --> Protocol: Exception("Service failed")
alt REST Protocol
  Protocol --> "Client": HTTPException(500, "Internal Server Error")
else MCP Protocol
  Protocol --> "Client": {"success": false, "error": "Service failed"}
end

note over UC
  **Consistent Error Codes:**
  • ValidationError for input validation
  • Structured error details
  • Protocol-specific serialization
end note

@enduml
```

### API Endpoint vs MCP Tool Mapping

| Functionality | REST API Endpoint | MCP Tool | Shared Use Case |
|---------------|-------------------|----------|-----------------|
| **Collections** |
| Create | `POST /api/file-collections` | `create_file_collection` | `create_collection_use_case` |
| List | `GET /api/file-collections` | `list_file_collections` | `list_collections_use_case` |
| Get | `GET /api/file-collections/{id}` | `get_file_collection` | `get_collection_use_case` |
| Delete | `DELETE /api/file-collections/{id}` | `delete_file_collection` | `delete_collection_use_case` |
| **Files** |
| Save | `POST /api/file-collections/{id}/files` | `save_to_collection` | `save_file_use_case` |
| Get | `GET /api/file-collections/{id}/files/{file}` | `read_from_collection` | `get_file_use_case` |
| Update | `PUT /api/file-collections/{id}/files/{file}` | *(use save_to_collection)* | `update_file_use_case` |
| List | `GET /api/file-collections/{id}/files` | *(use get_collection_info)* | `list_files_use_case` |
| **Web Crawling** |
| Extract | `POST /api/extract` | `web_content_extract` | `extract_content_use_case` |
| Deep Crawl | `POST /api/deep-crawl` | `domain_deep_crawl_tool` | `deep_crawl_use_case` |
| Link Preview | `POST /api/link-preview` | `domain_link_preview_tool` | `link_preview_use_case` |
| Crawl to Collection | `POST /api/crawl/single/{id}` | `crawl_single_page_to_collection` | `crawl_single_page_to_collection_use_case` |
| **Vector Search** |
| Sync | `POST /api/vector-sync/collections/{name}/sync` | `sync_collection_to_vectors` | `sync_collection_use_case` |
| Status | `GET /api/vector-sync/collections/{name}/status` | `get_collection_sync_status` | `get_sync_status_use_case` |
| Search | `POST /api/vector-sync/search` | `search_collection_vectors` | `search_vectors_use_case` |

---

## Datenfluss und Workflows

### Web Content Extraction Workflow

```puml
@startuml Web Content Extraction
!theme plain

actor User
participant "Frontend" as FE
participant "REST API" as API
participant "Use Case" as UC
participant "Web Service" as WS
participant "Crawl4AI" as C4AI

User -> FE: Enter URL for extraction
FE -> API: POST /api/extract {"url": "https://example.com"}

API -> UC: extract_content_use_case(web_service, url)

note over UC: **Input Validation**
UC -> UC: validate_url_format(url)
UC -> UC: validate_url_protocol(url)

UC -> WS: extract_content(url)
WS -> C4AI: crawl(url, extraction_strategy)
C4AI --> WS: raw_content, metadata
WS -> WS: process_content(raw_content)
WS --> UC: CrawlResult(url, content, metadata, error)

alt Success
  UC --> API: CrawlResult
  API --> FE: {"success": true, "data": {"content": "...", "metadata": {...}}}
  FE -> FE: display_content(content)
else URL Validation Error
  UC --> API: ValidationError("INVALID_URL_FORMAT", details)
  API --> FE: 400 {"error": {"code": "INVALID_URL_FORMAT", ...}}
  FE -> FE: show_error_message()
else Crawling Error
  UC --> API: CrawlResult(error="Network timeout")
  API --> FE: 500 {"error": {"code": "EXTRACTION_FAILED", ...}}
  FE -> FE: show_error_message()
end

@enduml
```

### Collection Management Workflow

```puml
@startuml Collection Management
!theme plain

actor User
participant "Frontend" as FE
participant "Collection Context" as CTX
participant "API Service" as API
participant "REST Endpoint" as REST
participant "Use Case" as UC
participant "Collection Service" as CS
participant "File System" as FS

== Collection Creation ==
User -> FE: Create new collection "My Research"
FE -> CTX: dispatch(CREATE_COLLECTION_REQUEST)
CTX -> API: createFileCollection({name: "My Research"})
API -> REST: POST /api/file-collections
REST -> UC: create_collection_use_case(service, name, description)
UC -> CS: create_collection(name, description)
CS -> FS: create_directory("./collections/My Research")
CS -> CS: generate_collection_id()
CS --> UC: CollectionInfo(id, name, created_at)
UC --> REST: CollectionInfo
REST --> API: {"success": true, "data": CollectionInfo}
API --> CTX: CollectionInfo
CTX -> CTX: dispatch(CREATE_COLLECTION_SUCCESS, CollectionInfo)
CTX --> FE: Updated state with new collection

== File Save Operation ==
User -> FE: Save file "notes.md" with content
FE -> CTX: dispatch(SAVE_FILE_REQUEST)
CTX -> API: saveFileToCollection(collection_id, file_data)
API -> REST: POST /api/file-collections/{id}/files
REST -> UC: save_file_use_case(service, collection_id, filename, content, folder)
UC -> CS: save_file(collection_name, filename, content, folder)
CS -> FS: write_file("./collections/My Research/notes.md", content)
CS -> CS: calculate_file_hash(content)
CS -> CS: update_metadata(filename, hash, timestamp)
CS --> UC: FileInfo(name, path, size, created_at)
UC --> REST: FileInfo
REST --> API: {"success": true, "data": FileInfo}
API --> CTX: FileInfo
CTX -> CTX: dispatch(SAVE_FILE_SUCCESS, FileInfo)
CTX -> CTX: update_file_tree(FileInfo)
CTX --> FE: Updated state with saved file

@enduml
```

### Vector Search Integration Workflow

```puml
@startuml Vector Search Workflow
!theme plain

actor User
participant "Frontend" as FE
participant "REST API" as API
participant "Vector Use Case" as VUC
participant "Vector Service" as VS
participant "Collection Service" as CS
participant "ChromaDB" as CDB

== Collection Sync ==
User -> FE: Sync collection "My Research" to vectors
FE -> API: POST /api/vector-sync/collections/my-research/sync
API -> VUC: sync_collection_use_case(vector_service, collection_name)

VUC -> VS: sync_collection(collection_name, force_reprocess=false)
VS -> CS: list_files(collection_name)
CS --> VS: List[FileInfo]

loop for each file
  VS -> CS: get_file(collection_name, filename)
  CS --> VS: file_content
  VS -> VS: chunk_content(file_content, strategy="sentence")
  VS -> VS: generate_embeddings(chunks)
  VS -> CDB: add_documents(chunks, embeddings, metadata)
end

VS -> VS: update_sync_status(collection_name, "in_sync")
VS --> VUC: SyncResult(vector_count=42, processed_files=5)
VUC --> API: SyncResult
API --> FE: {"success": true, "sync_result": SyncResult}

== Vector Search ==
User -> FE: Search "machine learning concepts"
FE -> API: POST /api/vector-sync/search
API -> VUC: search_vectors_use_case(service, query, collection_name, limit, threshold)
VUC -> VS: search_vectors(query, collection_name, limit, similarity_threshold)

VS -> VS: generate_query_embedding(query)
VS -> CDB: query(query_embedding, limit, where_filter)
CDB --> VS: similar_documents_with_scores

VS -> VS: filter_by_similarity_threshold(results, threshold)
VS -> VS: format_search_results(filtered_results)
VS --> VUC: List[VectorSearchResult]
VUC --> API: List[VectorSearchResult]
API --> FE: {"success": true, "results": [...]}
FE -> FE: display_search_results(results)

note over VS
  **Optional Dependency Handling:**
  If ChromaDB not available:
  • Graceful degradation
  • Clear error messages  
  • Feature remains optional
end note

@enduml
```

---

## Persistierung

### Datenbank und Speicher Architektur

```puml
@startuml Data Persistence
!theme plain

package "File Collections" {
  [Collections Directory] as CollDir
  [Markdown Files] as MD
  [JSON Files] as JSON
  [Text Files] as TXT
}

package "Metadata Storage" {
  database "SQLite Database" as DB {
    table "file_mappings" {
      * file_path: TEXT
      * file_hash: TEXT  
      * collection_name: TEXT
      * last_modified: TIMESTAMP
      * metadata: JSON
    }
    
    table "sync_statuses" {
      * collection_name: TEXT
      * sync_status: TEXT
      * vector_count: INTEGER
      * last_sync: TIMESTAMP
      * sync_version: INTEGER
    }
  }
}

package "Vector Storage" {
  database "ChromaDB" as Vector {
    collection "crawl4ai_documents" {
      * id: UUID
      * embedding: VECTOR
      * metadata: JSON
      * document: TEXT
    }
  }
}

package "Configuration" {
  [Environment Variables] as ENV
  [CLAUDE.md] as Config
}

CollDir --> DB : "metadata tracking"
MD --> DB : "file hashes"
JSON --> DB : "modification times"
TXT --> DB : "collection mapping"

DB --> Vector : "sync status coordination"
Vector --> DB : "vector count updates"

ENV --> CollDir : "collections_dir path"
ENV --> DB : "database path"  
ENV --> Vector : "vector DB path"
Config --> ENV : "project configuration"

note right of DB
  **SQLite Features:**
  • Atomic transactions
  • File integrity tracking
  • Sync status persistence
  • Metadata indexing
end note

note right of Vector
  **ChromaDB Features:**
  • Semantic embeddings
  • Similarity search
  • Metadata filtering
  • Optional dependency
end note

@enduml
```

### Daten-Modell Relationships

```puml
@startuml Data Model
!theme plain

class FileCollection {
  +id: UUID
  +name: string
  +description: string
  +created_at: datetime
  +updated_at: datetime
  +file_count: int
  +total_size: int
}

class FileInfo {
  +name: string
  +path: string  
  +content: string
  +size: int
  +metadata: dict
  +created_at: datetime
  +updated_at: datetime
  +collection_name: string
  +file_hash: string
}

class VectorSyncStatus {
  +collection_name: string
  +sync_status: "never_synced" | "in_sync" | "out_of_sync"
  +vector_count: int
  +last_sync: datetime
  +sync_version: int
  +error_message: string?
}

class VectorDocument {
  +id: UUID
  +collection_name: string
  +source_file: string
  +chunk_content: string
  +embedding: float[]
  +metadata: dict
  +chunk_index: int
  +total_chunks: int
}

class CrawlResult {
  +url: string
  +content: string
  +metadata: dict
  +error: string?
  +success: boolean
}

FileCollection ||--o{ FileInfo : "contains"
FileCollection ||--o| VectorSyncStatus : "has sync status"
VectorSyncStatus ||--o{ VectorDocument : "tracks vectors"
FileInfo ||--o{ VectorDocument : "chunked into"
CrawlResult ..> FileInfo : "can be saved as"

note bottom of VectorDocument
  **Chunking Strategy:**
  • Sentence-based chunking
  • Paragraph-based chunking
  • Fixed-size chunking
  • Overlap handling
end note

@enduml
```

---

## Deployment Architektur

### Entwicklung vs. Produktion

```puml
@startuml Deployment Architecture
!theme plain

package "Development Environment" {
  node "Local Machine" {
    [React Dev Server] as ReactDev
    [Python Unified Server] as PyDev
    [SQLite DB] as DBDev
    [ChromaDB] as VectorDev
    [File System] as FSDev
  }
  
  [Claude Desktop] as ClaudeDev
}

package "Production Environment" {
  node "Server/Container" {
    [Built React App] as ReactProd
    [Python Unified Server] as PyProd
    [SQLite DB] as DBProd
    [ChromaDB] as VectorProd
    [File System] as FSProd
  }
  
  [External Clients] as ClientsProd
}

== Development ==
ClaudeDev -> PyDev : MCP Protocol (stdio)
ReactDev -> PyDev : REST API (http://localhost:8000)

PyDev -> DBDev : SQLite operations
PyDev -> VectorDev : Vector operations
PyDev -> FSDev : File operations

== Production ==
ClientsProd -> ReactProd : Static files
ClientsProd -> PyProd : REST API
[MCP Clients] -> PyProd : MCP Protocol

PyProd -> DBProd : SQLite operations  
PyProd -> VectorProd : Vector operations
PyProd -> FSProd : File operations

note right of PyDev
  **Development Features:**
  • Hot reload
  • Debug logging
  • CORS enabled
  • Concurrent protocols
end note

note right of PyProd
  **Production Features:**
  • Process management
  • Error tracking
  • Performance monitoring
  • Security headers
end note

@enduml
```

### MCP Integration Setup

```puml
@startuml MCP Integration
!theme plain

actor "User" as User
participant "Claude Desktop" as Claude
participant "MCP Protocol" as MCP
participant "Crawl4AI Server" as Server

== Configuration ==
User -> Claude: Configure MCP server in settings
note right of Claude
  **claude_desktop_config.json:**
  ```json
  {
    "mcpServers": {
      "crawl4ai": {
        "command": "uv",
        "args": ["run", "--directory", "/path/to/server", "python", "server.py"]
      }
    }
  }
  ```
end note

== Communication ==
Claude -> MCP: Connect via stdio
MCP -> Server: Initialize MCP server
Server --> MCP: Tool list registration
MCP --> Claude: Available tools

== Tool Usage ==
User -> Claude: "Extract content from https://example.com"
Claude -> MCP: Call web_content_extract tool
MCP -> Server: execute_tool("web_content_extract", {"url": "https://example.com"})
Server -> Server: extract_content_use_case(web_service, url)
Server --> MCP: {"success": true, "content": "...", "metadata": {...}}
MCP --> Claude: Tool execution result
Claude --> User: Formatted response with extracted content

note over Server
  **Available MCP Tools:**
  • web_content_extract
  • domain_deep_crawl_tool
  • domain_link_preview_tool
  • create_file_collection
  • save_to_collection
  • read_from_collection
  • get_file_collection
  • list_file_collections
  • sync_collection_to_vectors
  • search_collection_vectors
  • get_collection_sync_status
end note

@enduml
```

---

## Komponentenkommunikation für bessere Anforderungsanalyse

### Frontend Komponenten Mapping

**Für visuelle Anforderungen verwende diese Komponentennamen:**

| UI Bereich | Komponente | Zweck | Wichtige Props/State |
|------------|------------|--------|---------------------|
| **Hauptlayout** |
| App Shell | `NewApp` | Root-Komponente mit Providern | theme, error boundaries |
| Navigation | `TopNavigation` | Haupt-Navigationsleiste | current route, user actions |
| Sidebar | `CollectionSidebar` | Collections & Dateibaum | selected collection, file tree |
| Content Area | `MainContent` | Hauptbereich für Editor/Search | active view, content type |
| **Collection Management** |
| Collection List | `CollectionList` | Liste aller Collections | collections, loading state |
| Collection Form | `CollectionForm` | Create/Edit Collection Dialog | form data, validation |
| File Tree | `FileTree` | Hierarchische Dateiansicht | files, folders, selection |
| **File Operations** |
| File Editor | `FileEditor` | Monaco-Editor für Dateien | content, language, save state |
| File Upload | `FileUpload` | Drag & Drop Upload | files, progress, validation |
| File Actions | `FileActions` | Rename/Delete/Download | file info, permissions |
| **Search & Vectors** |
| Vector Search | `VectorSearch` | Semantic Search Interface | query, results, filters |
| Search Results | `SearchResults` | Search Result Display | results, pagination, sorting |
| Sync Status | `SyncStatus` | Vector Sync Status Indicator | sync state, progress, errors |
| **Web Crawling** |
| URL Input | `URLInput` | URL Eingabe für Crawling | url, validation, submit |
| Crawl Progress | `CrawlProgress` | Crawling Fortschritt | status, progress, results |
| Link Preview | `LinkPreview` | Preview verfügbarer Links | links, selection, filtering |

### Backend Service/Use-Case Mapping

**Für Backend-Anforderungen verwende diese Service-/Use-Case-Namen:**

| Funktionalität | Use-Case Funktion | Service Methode | API Endpoint |
|----------------|-------------------|-----------------|--------------|
| **Collection Management** |
| Collection erstellen | `create_collection_use_case` | `CollectionService.create_collection` | `POST /api/file-collections` |
| Collections auflisten | `list_collections_use_case` | `CollectionService.list_collections` | `GET /api/file-collections` |
| Collection abrufen | `get_collection_use_case` | `CollectionService.get_collection_by_id` | `GET /api/file-collections/{id}` |
| Collection löschen | `delete_collection_use_case` | `CollectionService.delete_collection` | `DELETE /api/file-collections/{id}` |
| **File Management** |
| Datei speichern | `save_file_use_case` | `CollectionService.save_file` | `POST /api/file-collections/{id}/files` |
| Datei abrufen | `get_file_use_case` | `CollectionService.get_file` | `GET /api/file-collections/{id}/files/{name}` |
| Dateien auflisten | `list_files_use_case` | `CollectionService.list_files` | `GET /api/file-collections/{id}/files` |
| Datei löschen | `delete_file_use_case` | `CollectionService.delete_file` | `DELETE /api/file-collections/{id}/files/{name}` |
| **Web Crawling** |
| Content extrahieren | `extract_content_use_case` | `WebCrawlingService.extract_content` | `POST /api/extract` |
| Deep Crawling | `deep_crawl_use_case` | `WebCrawlingService.deep_crawl` | `POST /api/deep-crawl` |
| Links vorschau | `link_preview_use_case` | `WebCrawlingService.preview_links` | `POST /api/link-preview` |
| **Vector Operations** |
| Collection synchronisieren | `sync_collection_use_case` | `VectorSyncService.sync_collection` | `POST /api/vector-sync/collections/{name}/sync` |
| Sync Status abrufen | `get_sync_status_use_case` | `VectorSyncService.get_sync_status` | `GET /api/vector-sync/collections/{name}/status` |
| Vektoren durchsuchen | `search_vectors_use_case` | `VectorSyncService.search_vectors` | `POST /api/vector-sync/search` |

### Persistierung Layers

**Für Daten-/Persistierungsanforderungen:**

| Datentyp | Storage Layer | Technologie | Zuständigkeit |
|----------|---------------|-------------|---------------|
| **File Collections** | `DatabaseCollectionManager` | File System + SQLite | Collection CRUD, File Storage |
| **Vector Embeddings** | `IntelligentSyncManager` | ChromaDB | Semantic Search, Embeddings |
| **Sync Metadata** | `PersistentSyncManager` | SQLite | Sync Status, File Mappings |
| **Crawling Results** | `WebCrawlingManager` | Temporary + File System | Content Extraction, URL Processing |

---

### Beispiel: Wie Anforderungen formuliert werden sollten

**❌ Unpräzise Anforderung:**
> "Die Search Funktion soll besser werden"

**✅ Präzise Anforderung mit Architektur-Kontext:**
> "Die `VectorSearch` Komponente im Frontend soll erweitert werden: Der `search_vectors_use_case` soll zusätzliche Filter-Parameter unterstützen (Zeitraum, Dateityp). Das `VectorSyncService.search_vectors` Interface muss entsprechend erweitert werden, und die ChromaDB-Abfrage in `IntelligentSyncManager` soll Metadata-Filter verwenden."

**❌ Vage Änderungsanfrage:**
> "File Upload funktioniert nicht richtig"

**✅ Spezifische Problemanalyse:**
> "Die `FileUpload` Komponente im `MainContent` Bereich hat ein Problem beim Aufruf von `save_file_use_case`. Der `CollectionService.save_file` in der Service Layer wirft wahrscheinlich einen Validierungsfehler, der nicht korrekt in der `CollectionContext` State Management abgefangen wird."

Diese Architektur-Dokumentation ermöglicht es dir, präzise zu kommunizieren welche Teile des Systems geändert werden sollen, und mir dabei zu helfen, Duplikationen und Inkonsistenzen wie bei der MCP/API-Logik frühzeitig zu erkennen.