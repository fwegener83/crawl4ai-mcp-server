# Full-Stack Feature Plan: SQLite Collection Storage Migration

## Planning Overview
- **Input**: .planning/initial-sqlite-migration.md
- **Branch**: feature/sqlite-migration
- **Complexity Score**: 9/15 (Moderate)
- **Test Strategy**: Balanced Full-Stack Strategy
- **Generated**: 2025-08-03T12:30:00Z

## Phase 1: Deep Exploration Results

### HYPERTHINK Analysis Summary

This SQLite migration represents a significant architectural improvement that maintains complete backward compatibility while transitioning from file-based to database-based storage. The key insight is that this is a **backend-only migration from the user perspective** - the frontend, API contracts, and user experience remain completely unchanged.

**Critical Success Factors:**
1. **Perfect API Compatibility**: All HTTP endpoints must return identical responses
2. **Transparent User Experience**: Frontend File Explorer continues working unchanged
3. **Data Integrity**: Zero data loss during migration with comprehensive validation
4. **Performance Improvement**: ≥20% faster operations, especially for metadata queries
5. **Reliable Rollback**: Ability to export data back to file system if needed

### Context Research Findings

#### SQLite Integration Patterns (from libSQL research)
- **Connection Management**: Use `yield` pattern with FastAPI dependencies
- **Transaction Handling**: ACID compliance with proper rollback on exceptions
- **Performance Optimization**: WAL mode, connection pooling, prepared statements
- **Security**: Parameterized queries to prevent SQL injection

#### FastAPI Database Integration (from FastAPI research)
- **Session Management**: `SessionDep = Annotated[Session, Depends(get_session)]` pattern
- **Dependency Injection**: Clean separation of concerns with yield-based cleanup
- **Error Handling**: Proper exception handling in dependencies
- **Connection Pooling**: SQLite with `check_same_thread=False` for FastAPI

#### Current Architecture Analysis
- **File Storage**: `~/.crawl4ai/collections/collection_name/` structure
- **API Layer**: 14 HTTP endpoints for file collection management
- **Data Models**: Pydantic models in `CollectionMetadata` and `FileMetadata`
- **Security**: Path traversal protection and file extension validation
- **Testing**: Comprehensive test suite that must continue passing

### Full-Stack Feature Technical Analysis

#### Backend Requirements

**Database Schema Design:**
```sql
-- Schema versioning
CREATE TABLE schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Collections table
CREATE TABLE collections (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_count INTEGER DEFAULT 0,
    total_size INTEGER DEFAULT 0,
    metadata TEXT  -- JSON blob for extensibility
);

-- Files table  
CREATE TABLE files (
    id TEXT PRIMARY KEY,
    collection_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    folder_path TEXT DEFAULT '',
    content TEXT,
    content_hash TEXT,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_size INTEGER DEFAULT 0,
    FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE,
    UNIQUE(collection_id, folder_path, filename)
);

-- Performance indexes
CREATE INDEX idx_files_collection_id ON files(collection_id);
CREATE INDEX idx_files_folder_path ON files(collection_id, folder_path);
CREATE INDEX idx_files_filename ON files(collection_id, filename);
CREATE INDEX idx_collections_name ON collections(name);
```

**API Endpoints Requiring Migration:**
- `POST /api/file-collections` → **Purpose**: Create collection → **Data**: `{name, description}`
- `GET /api/file-collections` → **Purpose**: List collections → **Data**: `{collections: []}`
- `GET /api/file-collections/{id}` → **Purpose**: Get collection info → **Data**: `{collection details}`
- `DELETE /api/file-collections/{id}` → **Purpose**: Delete collection → **Data**: `{success}`
- `POST /api/file-collections/{id}/files` → **Purpose**: Save file → **Data**: `{filename, content, folder}`
- `GET /api/file-collections/{id}/files/{filename}` → **Purpose**: Read file → **Data**: `{content}`
- `GET /api/file-collections/{id}/files` → **Purpose**: List files → **Data**: `{files: []}`

**Business Logic Requirements:**
- **Validation**: File extension validation (`.md`, `.txt`, `.json`)
- **Security**: SQL injection prevention, content sanitization
- **Processing**: Content hashing, metadata tracking, folder hierarchy

#### Frontend Requirements

**No Changes Required** - This is the key insight. The frontend components continue working unchanged:

- **FileExplorer**: Displays folder tree and files using same API responses
- **EditorArea**: Loads and saves file content through unchanged endpoints
- **CollectionSidebar**: Shows collection list using same data structures
- **Modals**: CreateCollection, AddFile, etc. use same API contracts

**User Experience Preserved:**
- **File Operations**: Same create, read, update, delete workflows
- **Collection Management**: Same collection creation and management flows
- **Error Handling**: Same error messages and user feedback
- **Performance**: Improved response times for listing operations

#### Integration Requirements

**Data Contracts Maintained:**
- **Request/Response Formats**: Exact same JSON structures
- **Error Formats**: Same error message patterns and HTTP status codes
- **URL Encoding**: Same handling of filenames with spaces and special characters
- **Security Validations**: Same path traversal and extension checks

**Migration Flow:**
- **File-to-DB Import**: Scan existing collections, preserve metadata and content
- **Validation**: Verify data integrity with checksums
- **Rollback**: Export capability back to file system if needed

### Full-Stack Architecture Plan

```
┌─────────────────┐    HTTP API     ┌─────────────────┐    Database     ┌─────────────────┐
│                 │◄────────────────┤                 │◄────────────────┤                 │
│   React         │                 │   FastAPI       │                 │   SQLite        │
│   Frontend      │────────────────►│   Backend       │────────────────►│   Database      │
│                 │   Same API      │                 │   New Storage   │                 │
│   (Unchanged)   │   Contracts     │   (Enhanced)    │   Backend       │   (New)         │
└─────────────────┘                 └─────────────────┘                 └─────────────────┘
        │                                    │                                    │
        │                                    │                                    │
   File Explorer                      CollectionManager                   collections.db
   EditorArea                      (SQLite Implementation)             ┌─────────────────┐
   Collections UI                                                      │  collections    │
                                                                       │  files          │
                                                                       │  schema_version │
                                                                       └─────────────────┘
```

### Quality Requirements

**Performance Benchmarks:**
- Database operations ≥20% faster than file operations
- Collection listing <100ms response time
- File content retrieval <200ms for files <1MB
- Bulk operations use transactions for consistency

**Security Standards:**
- All queries use parameterized statements
- Content validation before database storage
- Path traversal protection in database layer
- Database file permissions properly configured

**Reliability Requirements:**
- ACID transactions for data consistency
- Automatic rollback on operation failures
- Database corruption detection and recovery
- Connection pool management for concurrent access

## Phase 2: Intelligent Planning Results

### Complexity Assessment Breakdown
- **Backend Complexity**: 4/5 - Complex database migration with performance optimization
- **Frontend Complexity**: 1/5 - No changes required, transparent operation
- **Integration Complexity**: 4/5 - Critical API compatibility and data migration
- **Total Score**: 9/15 - **Moderate Complexity**

### Selected Test Strategy: Balanced Full-Stack Strategy

This strategy was chosen because:
1. **Backend complexity** requires comprehensive database testing
2. **API compatibility** is critical and needs extensive validation
3. **Frontend unchanged** but needs regression testing to ensure no breaking changes
4. **Data migration** requires specialized testing scenarios

**Testing Approach:**
- **Backend Testing**: Database operations, transaction handling, migration scripts, performance benchmarks
- **Frontend Testing**: Existing test suite must pass unchanged, E2E workflow validation
- **Integration Testing**: API contract validation, data flow testing, error scenario handling
- **E2E Testing**: Complete user journeys, file operations, collection management workflows
- **Migration Testing**: File-to-DB accuracy, rollback functionality, edge case handling
- **Performance Testing**: Response time improvements, concurrent access handling
- **Coverage Target**: 90%

### Task Breakdown by Complexity

#### Phase 1: Database Foundation (Backend Focus)
**Duration**: 2 days **Complexity**: High

1. **Database Schema Implementation**
   - Create SQLite schema with proper indexes
   - Implement schema versioning system
   - Add migration tracking table

2. **Database Manager Class**
   - SQLite connection management with pooling
   - Transaction handling with proper rollback
   - Error handling for SQLite-specific issues

3. **Repository Pattern Implementation**
   - CollectionRepository for collection operations
   - FileRepository for file operations
   - Parameterized queries for security

#### Phase 2: Core Operations Migration (Backend Focus)
**Duration**: 2 days **Complexity**: High

1. **Collection Operations Migration**
   - Update `create_collection()` with database storage
   - Update `list_collections()` with optimized queries
   - Update `get_collection_info()` with relational data
   - Update `delete_collection()` with cascade handling

2. **File Operations Migration**
   - Update `save_file()` with transactional content storage
   - Update `read_file()` with query optimization
   - Update `list_files_in_collection()` with hierarchical queries
   - Maintain exact response formats for API compatibility

3. **API Compatibility Validation**
   - Ensure identical request/response formats
   - Preserve error message consistency
   - Maintain security validations

#### Phase 3: Migration & Rollback System (Backend Focus)
**Duration**: 1 day **Complexity**: Medium

1. **File-to-Database Migration Tool**
   - Scan existing file collections
   - Import metadata and content with validation
   - Handle edge cases and corrupted files
   - Progress tracking and error reporting

2. **Database-to-File Export Tool**
   - Export all database content to file system
   - Preserve folder structure and metadata
   - Rollback capability for production issues

3. **Schema Migration System**
   - Version tracking for future updates
   - Safe migration execution with rollback
   - Database integrity validation

#### Phase 4: Integration & Performance (Full-Stack Focus)
**Duration**: 1 day **Complexity**: Medium

1. **HTTP API Integration**
   - Update FastAPI endpoints with database backend
   - Implement proper error handling and logging
   - Connection pool configuration

2. **Performance Optimization**
   - Query optimization with proper indexes
   - Connection pooling for concurrent requests
   - Memory usage optimization

3. **Frontend Compatibility Validation**
   - All existing E2E tests must pass
   - File Explorer functionality unchanged
   - Editor operations work correctly

#### Phase 5: Testing & Production Readiness (Full-Stack Focus)
**Duration**: 1 day **Complexity**: Medium

1. **Comprehensive Test Implementation**
   - All existing tests pass with database backend
   - New database-specific test cases
   - Performance regression testing
   - Migration and rollback testing

2. **Production Deployment Preparation**
   - Database backup and recovery procedures
   - Monitoring and logging configuration
   - Documentation updates
   - Rollback procedures

### Full-Stack Quality Gates

**Required validations before each commit:**
- **Backend**: Test suite passes, linting clean, type checking passes, security scan clear
- **Frontend**: All existing tests pass unchanged, build succeeds, no bundle size regression
- **Integration**: API contract tests pass, E2E workflows work, performance benchmarks met
- **Database**: Migration testing passes, rollback capability verified, data integrity confirmed

### Success Criteria

**Feature completion requirements:**
- All existing API tests pass with database backend
- Frontend File Explorer works without any modifications
- File editing and collection management unchanged from user perspective
- Performance improves by ≥20% for metadata operations
- Complete data migration capability with zero data loss
- Reliable rollback capability to file system
- Test coverage maintains ≥90% across all components
- Production deployment ready with monitoring and backup procedures

## Implementation Roadmap

### Development Sequence
1. **Database Foundation**: Schema, connection management, repositories (test-first)
2. **Core Operations**: Collection and file operations with API compatibility (test-first)
3. **Migration System**: File-to-DB and DB-to-file with validation
4. **Integration**: FastAPI integration with performance optimization
5. **Quality Assurance**: Comprehensive testing, performance validation, production readiness

### Risk Mitigation

**Technical Risks:**
- **API Breaking Changes**: Comprehensive contract testing, staged rollout with file backup
- **Data Loss**: Complete backup before migration, checksum validation, tested rollback
- **Performance Issues**: Benchmark-driven development, index optimization, connection pooling
- **Frontend Regression**: Complete E2E test coverage, gradual rollout capability

**Mitigation Strategies:**
- **Blue-Green Deployment**: Keep file system as backup during initial period
- **Feature Flagging**: Environment variable to switch between file/database backends
- **Monitoring**: Comprehensive logging and performance metrics
- **Rollback Plan**: Well-tested export capability back to file system

### Dependencies & Prerequisites

**Development Environment:**
- Python 3.8+ with SQLite support
- FastAPI and Pydantic for API layer
- pytest for comprehensive testing
- Existing frontend build pipeline unchanged

**Production Environment:**
- Database file permissions and backup strategy
- Monitoring setup for database operations
- Performance monitoring for API response times
- Error tracking for database-specific issues

## Execution Instructions

**To execute this plan:**
```bash
/execute .planning/PLAN_sqlite-migration.md
```

**The execution will:**
- Follow task sequence with database-first, API-compatibility-focused approach
- Implement test-first development for all database operations
- Validate API contract compatibility at each step
- Track progress with comprehensive metrics including performance benchmarks
- Ensure zero user-facing changes while delivering significant backend improvements
- Maintain focus on data integrity and rollback capability

## Quality Validation

### Plan Quality Assessment
- [x] All aspects of the SQLite migration thoroughly analyzed
- [x] Backend database requirements clearly defined with schema and operations
- [x] Frontend compatibility requirements specify zero changes needed
- [x] Integration points focus on API contract preservation
- [x] Test strategy matches moderate complexity with comprehensive coverage
- [x] Quality gates ensure API compatibility and performance improvements
- [x] Success criteria are measurable and focused on transparency to users
- [x] Context research provided authoritative SQLite and FastAPI integration guidance
- [x] Risk mitigation strategies are practical with tested rollback procedures
- [x] Migration system ensures data integrity with validation and error handling

**Plan Confidence Score**: 9/10 for supporting successful SQLite migration with zero user impact

**Key Success Factors**: Perfect API compatibility, comprehensive testing, reliable data migration, and transparent user experience while delivering significant performance and reliability improvements through database backend.