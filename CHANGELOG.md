# Changelog

All notable changes to the Crawl4AI MCP Server project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **RAG Query Feature**: Complete question-answering system combining vector search with LLM response generation
  - HTTP API endpoint `/api/query` for external integrations
  - MCP tool `rag_query` for Claude Desktop integration
  - Support for both OpenAI (cloud) and Ollama (local) LLM providers
  - Graceful degradation to vector-only search when LLM providers are unavailable
  - Comprehensive error handling with structured error responses
- **LLM Provider Abstraction**: Flexible architecture supporting multiple LLM providers through environment configuration
- **AsyncMock Testing Infrastructure**: Robust integration test patterns for async service architectures
- **Automatic Test Cleanup**: Pytest fixture automatically removes test collections even on test failures
- **Stale Sync Detection**: Backend automatically detects and recovers from stuck synchronization operations
- **Enhanced Error Recovery**: Comprehensive timeout and retry mechanisms for vector sync operations
- **Real-time Change Monitoring**: Hash-based file change detection for immediate status updates

### Fixed
- **AsyncMock Integration Test Issues**: Resolved "object Mock can't be used in 'await' expression" errors across all integration tests
- **LLM Service Test Dependencies**: Added proper skip decorators for tests requiring optional OpenAI/Ollama packages
- **Vector Sync Deadlock Resolution**: Collections no longer get permanently stuck in "syncing" status preventing future operations
- **Live Change Detection**: File modifications are now immediately detected and reflected in sync status indicators  
- **Frontend Polling Race Conditions**: Unified recovery mechanism prevents multiple polling functions from conflicting
- **Vector Sync Status Persistence**: Enhanced status management with automatic stale sync detection and 10-minute timeout recovery

### Changed
- **Test Mocking Strategy**: Unified AsyncMock patterns across HTTP and MCP integration tests for consistency
- **Frontend API Migration**: Complete migration to new backend parameter structure with improved error handling
- **Test Infrastructure**: Enhanced MCP E2E tests with guaranteed collection cleanup preventing database pollution
- **Vector Sync UI**: Improved status indicators with graceful fallbacks for edge cases (e.g., "Files changed" when count unavailable)
- **Backend Service Layer**: Migrated vector sync service parameters for better consistency across API and MCP protocols
- **Frontend Refactoring - Enhanced RAG Simplification**: Complete UI simplification achieving 30%+ complexity reduction
  - **Compact Status Design**: 70% space reduction with emoji-based indicators and progressive disclosure tooltips
  - **Settings Removal**: Eliminated 1,002 lines of non-functional enhanced settings UI (11.19 kB bundle reduction)
  - **Chunking Strategy**: Hardcoded optimal `markdown_intelligent` strategy removing user configuration confusion
  - **Component Consolidation**: Replaced duplicate sync components with unified CompactSyncStatus component
  - **Enhanced Test Coverage**: 24 comprehensive tests for CompactSyncStatus with accessibility compliance
- **Settings UI Complete Removal**: Eliminated entire non-functional settings system achieving massive complexity reduction
  - **Settings Page Removal**: Removed SettingsPage.tsx (109 lines) and SettingsPanel.tsx (387 lines)
  - **Settings Architecture Cleanup**: Removed 25+ non-functional configuration options across 4 categories
  - **Navigation Simplification**: Removed settings menu from TopNavigation, kept only functional theme toggle
  - **False Functionality Elimination**: Removed localStorage-only settings that provided no backend integration
  - **Test Suite Updates**: Updated navigation and app tests to reflect simplified interface

### Architecture Decisions
- **LLM Provider Abstraction Strategy**: Multi-provider architecture with OpenAI and Ollama support
  - Decision details: [ADR-002: LLM Provider Abstraction](docs/adr/ADR_2025-01-13_llm-provider-abstraction-strategy.md)
  - Impact: Flexible LLM integration supporting both cloud and local deployment scenarios
  - Environment-based provider switching with zero downtime configuration changes
- **AsyncMock Testing Strategy**: Standardized integration test mocking patterns for async service architectures
  - Decision details: [ADR-003: AsyncMock Testing Strategy](docs/adr/ADR_2025-01-15_asyncmock-testing-strategy.md)
  - Impact: Reliable, maintainable integration tests with consistent AsyncMock patterns
  - Complete resolution of async/await mocking issues across all test suites
- **Vector Sync Reliability Improvements**: Comprehensive fixes for deadlock issues, change detection, and test infrastructure
  - Decision details: [ADR-001: Vector Sync Reliability](docs/adr/ADR_2025-01-13_vector-sync-reliability-improvements.md)
  - Impact: Transformed unreliable Vector Sync system into robust, user-friendly feature
- **Frontend Refactoring - Enhanced RAG Simplification**: Strategic UI simplification prioritizing optimal defaults over configuration complexity
  - Decision details: [ADR-001: Frontend Chunking Strategy Hardcoding](docs/adr/ADR_2025-01-17_frontend-chunking-strategy-hardcoding.md)
  - Decision details: [ADR-002: Enhanced Settings Component Removal](docs/adr/ADR_2025-01-17_enhanced-settings-component-removal.md)
  - Decision details: [ADR-003: Compact Status Design Pattern](docs/adr/ADR_2025-01-17_compact-status-design-pattern.md)
  - Impact: 30%+ complexity reduction, 70% space savings, better defaults for 95% of users while preserving backend flexibility
- **Settings UI Simplification**: Complete removal of non-functional settings system for user experience clarity
  - Decision details: [ADR-004: Settings UI Simplification](docs/adr/ADR_2025-01-17_settings-ui-simplification.md)
  - Impact: Eliminated 496+ lines of misleading UI, 90%+ of settings had no backend integration, improved user trust
  - Test cleanup: Removed 22 existing test collections and prevents future accumulation

## [1.0.0] - 2025-08-10 - Initial Release

### System Overview

Initial release of the Crawl4AI MCP Server - a **dual-protocol system** that provides both MCP (Model Context Protocol) integration for Claude Desktop and a RESTful API for web clients.

**For detailed architecture information, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**

### Added

#### Core Features
- **Dual-Protocol Support**: MCP server + REST API with shared business logic
- **Professional Configuration**: ~/.context42/ user directory following Unix conventions  
- **Web Content Extraction**: Single page + domain crawling with Crawl4AI integration
- **Collection Management**: Database-only file storage with SQLite persistence
- **Vector Search**: ChromaDB integration for semantic search (optional)
- **React Frontend**: Modern TypeScript UI with file editor and search interface

#### Technical Foundation
- **Clean Architecture**: Application layer with use-case pattern and dependency injection
- **Comprehensive Testing**: 99 tests across all system layers (unit, integration, E2E)
- **Professional Data Organization**: Automatic migration to ~/.context42/ structure
- **Environment Configuration**: Hierarchical config system with environment variable support

### Configuration

**Data Storage:**
```text
~/.context42/
├── databases/vector_sync.db    # SQLite collections & metadata  
├── databases/chromadb/         # Vector embeddings (optional)
├── config/                     # User configuration files
└── logs/                       # Application logs
```

**Key Environment Variables:**
```bash
CONTEXT42_HOME=~/.context42
COLLECTIONS_DB_PATH=${CONTEXT42_HOME}/databases/vector_sync.db
VECTOR_DB_PATH=${CONTEXT42_HOME}/databases/chromadb
```

### Migration Notes

- Existing `vector_sync.db` automatically moved to `~/.context42/databases/`
- Legacy `rag_db/` migrated to `~/.context42/databases/chromadb/`
- No manual migration required

### Dependencies

- **Backend**: Python 3.11+, FastAPI, SQLite
- **Optional RAG**: ChromaDB, sentence-transformers  
- **Frontend**: React 18, TypeScript, Vite, TailwindCSS
- **System**: 2GB RAM, Node.js 18+ (development)

---

## [Unreleased]

### Added
- Custom command system for automated development workflows
- Architecture Decision Records (ADRs) template and directory structure
- Professional documentation pipeline with cross-references

### Changed  
- Enhanced CLAUDE.md with documentation workflow section
- Updated ARCHITECTURE.md with ~/.context42/ configuration details
- Removed legacy collections directory reference

### Architecture Decisions
- [ADR Template System](docs/adr/): Standardized ADR format for future architectural decisions
- **Documentation Workflow**: Automated ADR creation during feature development and finalization during PR completion

---

## Future Releases

All future changes will be documented here using semantic versioning:

- **MAJOR** (x.0.0): Breaking changes requiring user action
- **MINOR** (1.x.0): New features, backward compatible  
- **PATCH** (1.0.x): Bug fixes, security patches

*For detailed technical documentation, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)*