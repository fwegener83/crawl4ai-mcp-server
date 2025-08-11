# Changelog

All notable changes to the Crawl4AI MCP Server project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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