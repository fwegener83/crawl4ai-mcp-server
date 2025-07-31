# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Crawl4AI MCP (Model Context Protocol) Server with a React frontend for web content extraction, domain crawling, and file collection management. The project consists of:

- **Backend**: Python MCP server using FastMCP framework with crawl4ai integration
- **Frontend**: React/TypeScript application with Vite, TailwindCSS, and comprehensive testing
- **Architecture**: Dual-mode system supporting both RAG knowledge base and file-based collections

## Essential Commands

### Backend Development
```bash
# Start MCP server
uv run python server.py

# Install dependencies  
uv install
playwright install

# Testing
pytest                           # All tests
pytest -m "not slow"            # Fast tests only (recommended for development)  
pytest --cov=. --cov-report=html # With coverage
pytest tests/test_rag_integration.py tests/test_knowledge_base.py # RAG-specific tests

# RAG tools availability check
python3 -c "from tools.knowledge_base.dependencies import is_rag_available; print('RAG available:', is_rag_available())"
```

### Frontend Development
```bash
cd frontend

# Development server
npm run dev

# Build and quality checks
npm run build                    # TypeScript compilation + Vite build
npm run typecheck               # TypeScript type checking
npm run lint                    # ESLint
npm run quality:check           # Lint + typecheck + test + build

# Testing
npm run test                    # Vitest unit tests
npm run test:coverage           # Coverage report
npm run test:e2e                # Playwright E2E tests
npm run test:e2e:ui            # Playwright UI mode
npm run test:all               # Unit + E2E tests

# Combined development
npm run start:all              # Backend + frontend concurrently
```

## Architecture Overview

### MCP Server Structure (`server.py`)
- **FastMCP Integration**: Uses FastMCP for tool registration and protocol handling
- **Conditional RAG Tools**: RAG functionality available only when optional dependencies are installed
- **Collection Management**: File-based collection system for organizing crawled content
- **Tool Categories**:
  - Web extraction tools (always available)
  - Domain crawling tools (always available) 
  - RAG knowledge base tools (conditional)
  - File collection management tools (always available)

### Frontend Architecture
- **Component Structure**: Organized by feature areas (`components/`, `pages/`, `contexts/`)
- **State Management**: React Context for collection management
- **Testing Strategy**: Unit tests with Vitest + React Testing Library, E2E with Playwright
- **Routing**: Manual page state management (no react-router)
- **Collection-Centric UI**: File explorer, editor area, and sidebar navigation

### Key Backend Modules
- `tools/web_extract.py`: Single page content extraction
- `tools/mcp_domain_tools.py`: Domain crawling and link preview
- `tools/collection_manager.py`: File-based collection operations
- `tools/knowledge_base/`: RAG functionality (ChromaDB + sentence-transformers)

### Testing Architecture
- **Backend**: pytest with asyncio support, factory patterns for test data
- **Frontend**: Vitest for unit tests, Playwright for E2E
- **Test Markers**: `slow`, `security`, `regression` for selective testing
- **CI Configuration**: Quality checks pipeline in package.json

## RAG vs File Collections

The system supports two collection paradigms:

1. **RAG Collections** (optional): Vector-based semantic search using ChromaDB
2. **File Collections** (always available): File system-based with Markdown editor integration

File collections are the primary focus for the frontend interface, providing a file-explorer-like experience with in-browser editing capabilities.

## Development Patterns

### Error Handling
- All MCP tools return JSON strings with consistent `{"success": boolean, ...}` format
- Frontend uses error boundaries and toast notifications
- Backend logs all operations with structured logging

### Security Considerations
- Collection names are sanitized to prevent path traversal
- File extensions are validated (.md, .txt, .json only)
- Content is stored as UTF-8 with hash validation

### Testing Best Practices
- Use factory patterns for test data generation (`tests/factories.py`)
- Mock external dependencies (crawl4ai, chromadb)
- Separate fast and slow tests with pytest markers
- E2E tests focus on critical user workflows

## Important Configuration

### Environment Variables
```bash
# RAG Configuration (optional)
RAG_DB_PATH=./rag_db              # ChromaDB storage path
RAG_MODEL_NAME=all-MiniLM-L6-v2   # Embedding model
RAG_CHUNK_SIZE=1000               # Text chunking
RAG_DEVICE=cpu                    # cpu or cuda

# Crawl4AI Configuration
CRAWL4AI_USER_AGENT=custom-agent
CRAWL4AI_TIMEOUT=30
```

### Claude Desktop Integration
Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "crawl4ai": {
      "command": "uv",
      "args": ["run", "--directory", "/absolute/path/to/crawl4ai-mcp-server", "python", "server.py"]
    }
  }
}
```

## File Structure Context

- `server.py`: Main MCP server entry point
- `tools/`: Backend tool implementations
- `frontend/src/`: React application source
- `tests/`: Python test suite
- `frontend/src/e2e/`: Playwright E2E tests
- Collections stored in `./collections/` directory by default