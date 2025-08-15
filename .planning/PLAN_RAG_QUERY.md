# Full-Stack Feature Plan: RAG Query API & MCP Tool

## Planning Overview
- **Input**: .planning/RAG_QUERY_INITIAL.md
- **Branch**: feature/RAG_QUERY
- **Complexity Score**: 6/15 (Moderate)
- **Test Strategy**: Essential Test-First Development
- **Generated**: 2025-01-13T21:00:00Z

## Phase 1: Deep Exploration Results

### HYPERTHINK Analysis Summary

The RAG Query feature represents a strategic enhancement that introduces LLM-powered question-answering capabilities while leveraging the existing mature vector search infrastructure. The implementation exhibits excellent architectural alignment with the current unified server design, enabling seamless dual-protocol support (HTTP API + MCP tool) through shared business logic.

**Key Architectural Insights:**
- Perfect integration with existing 3-layer architecture (Application/Services/Infrastructure)
- Reuses battle-tested vector search infrastructure completely
- Follows established dependency injection and error handling patterns
- LLM provider abstraction enables flexible deployment (OpenAI vs Ollama)

### Context Research Findings

#### FastAPI Integration Patterns
From Context7 research on `/tiangolo/fastapi`:
- **Async Dependencies**: Use `async def` dependencies for LLM service injection
- **Error Handling**: Leverage FastAPI's `HTTPException` with structured error responses
- **Request Validation**: Pydantic models for request/response validation
- **Configuration**: Environment-based configuration with `Settings` dependency injection

#### OpenAI Python SDK Integration  
From Context7 research on `/openai/openai-python`:
- **Async Client**: `AsyncOpenAI` for non-blocking LLM calls
- **Error Handling**: Comprehensive error types (`APIConnectionError`, `RateLimitError`, etc.)
- **Configuration**: Environment variables with fallback to explicit API keys
- **Streaming**: Support available but not required for initial implementation

#### ChromaDB Integration Patterns
From Context7 research on `/chroma-core/chroma`:
- **Async Operations**: `AsyncHttpClient` for non-blocking vector operations
- **Collection Management**: Existing `get_or_create_collection` patterns
- **Query Interface**: Consistent `query(query_texts=..., n_results=...)` API
- **Error Handling**: Well-defined exceptions for missing collections

#### RAG Implementation Reference
From Context7 research on `/danny-avila/rag_api`:
- **Architecture**: FastAPI + Langchain + PostgreSQL/pgvector pattern
- **Configuration**: Environment-based LLM provider switching
- **Error Format**: Consistent JSON error responses with structured details
- **Response Structure**: LLM answer + source documents + metadata pattern

### Full-Stack Feature Technical Analysis

#### Backend Requirements

**LLM Service Layer:**
- `LLMService` abstract protocol with OpenAI and Ollama implementations
- Configuration: Environment variables for provider selection and API keys
- Error handling: Graceful degradation on LLM failures
- Response format: Structured answer + confidence metadata

**RAG Use Case:**
- `rag_query_use_case()` orchestrating vector search + LLM generation
- Input validation: Query required, optional collection filtering
- Pipeline: Query → Vector Search → Context Assembly → LLM → Response
- Reuses: Existing `search_vectors_use_case()` for retrieval component

**API Endpoints:**
- **HTTP**: `POST /api/query` following existing RESTful patterns
- **MCP**: `rag_query` tool following existing tool registration patterns
- **Shared Logic**: Both use identical `rag_query_use_case()` function

#### Frontend Requirements

**Top Navigation Enhancement:**
- Add "Search" tab next to existing "File Collections" tab in TopNavigation component
- Search icon integration following existing design patterns
- Page state management for search functionality
- Navigation flow: File Collections ↔ Search

**RAG Query Component (Search Page):**
- Text input for natural language queries
- Collection selector (optional filtering) - reuse existing collection selection patterns
- Advanced options: max_chunks, similarity_threshold
- Response display: LLM answer + expandable source documents with metadata
- Query history functionality (optional enhancement)

**API Integration:**
- Extend `useApi.ts` with `queryRAG()` method
- Loading states during LLM processing
- Error handling for LLM failures and timeouts
- Response caching for repeated queries

**Navigation Integration:**
- Update App.tsx page routing to handle 'search' page state
- Search page component structure similar to existing collection management
- Consistent UI patterns with file collections interface

**Configuration UI:**
- Settings panel for LLM provider selection (OpenAI/Ollama)
- API key configuration for OpenAI
- Model selection dropdown
- Connection status indicators

#### Integration Requirements

**Data Contracts:**
```typescript
// Request
interface RAGQueryRequest {
  query: string;
  collection_name?: string;
  max_chunks?: number;
  similarity_threshold?: number;
}

// Response  
interface RAGQueryResponse {
  success: boolean;
  answer?: string;
  sources?: Array<{
    content: string;
    similarity_score: number;
    metadata: Record<string, any>;
  }>;
  metadata?: {
    chunks_used: number;
    collection_searched: string;
    llm_provider: string;
    response_time_ms: number;
  };
  error?: string;
}
```

**Authentication Flow:**
- Environment-based API key management for OpenAI
- Local model access for Ollama
- No additional authentication required (uses existing patterns)

### Full-Stack Architecture Plan

```
┌─────────────────────────────────────────────────────┐
│                    Frontend (React)                 │
├─────────────────────────────────────────────────────┤
│  TopNavigation: [File Collections] [Search] <--NEW │
│  ├── Search Page (when Search tab selected)        │
│  │   ├── RAG Query Input & Collection Selector     │
│  │   ├── Response Display (Answer + Sources)       │
│  │   └── Query History (optional)                  │
│  └── Configuration UI (Provider/Model Selection)   │
└─────────────────────────────────────────────────────┘
                            │
                         HTTP API
                            │
┌─────────────────────────────────────────────────────┐
│                UnifiedServer (FastAPI + FastMCP)    │
├─────────────────────────────────────────────────────┤
│  HTTP: POST /api/query                             │
│  MCP:  rag_query tool                              │
│  └── Both → rag_query_use_case()                   │
└─────────────────────────────────────────────────────┘
                            │
                     Application Layer
                            │
┌─────────────────────────────────────────────────────┐
│                  Services Layer                     │
├─────────────────────────────────────────────────────┤
│  LLMService (OpenAI | Ollama)                      │
│  VectorSyncService (existing)                      │  
│  CollectionService (existing)                      │
└─────────────────────────────────────────────────────┘
                            │
                      Infrastructure
                            │
┌─────────────────────────────────────────────────────┐
│              External Services                      │
├─────────────────────────────────────────────────────┤
│  ChromaDB (existing)                               │
│  OpenAI API (new)                                  │
│  Ollama (new, local)                               │
└─────────────────────────────────────────────────────┘
```

### Quality Requirements

**Performance:**
- LLM response time: < 10 seconds (with user feedback)
- Vector search latency: < 2 seconds (existing performance)  
- Frontend responsiveness: Loading states during processing

**Reliability:**
- LLM failure graceful degradation with error messages
- Fallback to vector search only if LLM unavailable
- Retry logic for transient API failures

**Security:**
- API key secure storage in environment variables
- No logging of API keys or sensitive model inputs
- Input sanitization for prompt injection prevention

## Phase 2: Intelligent Planning Results

### Complexity Assessment Breakdown
- **Backend Complexity**: 2/5 - Moderate service integration with established patterns
- **Frontend Complexity**: 2/5 - New components building on existing UI patterns  
- **Integration Complexity**: 2/5 - Linear pipeline with existing infrastructure reuse
- **Total Score**: 6/15 - **Moderate Complexity**

### Selected Test Strategy: Essential Test-First Development
Chosen for 6/15 complexity score to ensure quality without over-engineering.

**Testing Approach:**
- **Backend Testing**: Unit tests for LLM service + RAG use-case before implementation
- **Frontend Testing**: Component tests alongside component development
- **Integration Testing**: API contract tests parallel to API implementation
- **Additional Testing**: Mock LLM responses, error scenario validation
- **Coverage Target**: 85% achieved incrementally

### Task Breakdown by Complexity

#### Phase 1: Backend Test-First Implementation
1. **Write LLM Service Tests** → Implement LLM Service (OpenAI + Ollama providers)
2. **Write RAG Use-Case Tests** → Implement RAG orchestration logic  
3. **Write API Contract Tests** → Implement HTTP endpoint in UnifiedServer
4. **Write MCP Tool Tests** → Implement MCP tool in UnifiedServer

#### Phase 2: Frontend Test-First Implementation  
5. **Write Component Tests** → Implement RAG Query UI component
6. **Write API Hook Tests** → Extend useApi.ts with RAG methods
7. **Write Integration Tests** → Implement configuration UI

#### Phase 3: System Integration
8. **End-to-End Testing** → Validate complete RAG pipeline
9. **Error Scenario Testing** → LLM failures, network issues, invalid inputs
10. **Performance Testing** → Response time validation, load testing

### Full-Stack Quality Gates
**Required validations before each commit:**
- **Backend**: All unit tests pass, type checking, linting
- **Frontend**: Component tests pass, build succeeds, type checking
- **Integration**: API contract tests pass, E2E scenarios work
- **Performance**: Response time < 10s, no memory leaks
- **Security**: No API keys in logs, input validation working

### Success Criteria
**Feature completion requirements:**
- RAG queries work through both HTTP API and MCP tool interfaces
- LLM integration functional with both OpenAI and Ollama providers
- Frontend provides intuitive Search tab in top navigation alongside File Collections
- Search page allows natural language queries with optional collection filtering
- Response display shows LLM answers with expandable source documents
- Error handling graceful across all failure scenarios (LLM, network, validation)
- Test coverage meets 85% target across all components
- Configuration UI allows provider switching without code changes
- Navigation flow between File Collections and Search pages works seamlessly
- Documentation updated with RAG usage examples

## Implementation Roadmap

### Development Sequence (Test-First Mandatory)

#### Sprint 1: Core Backend Infrastructure (Week 1)
1. **LLM Service Foundation**
   - Write comprehensive tests for LLMService protocol
   - Implement OpenAI provider with async client
   - Implement Ollama provider with local API
   - Test provider switching and error handling

2. **RAG Use-Case Implementation**  
   - Write tests for rag_query_use_case function
   - Implement vector search integration (reuse existing)
   - Implement context building and LLM orchestration
   - Test complete RAG pipeline with mocked LLM

#### Sprint 2: API Integration (Week 2)
3. **UnifiedServer Enhancement**
   - Write API contract tests for HTTP endpoint
   - Write MCP tool tests with FastMCP
   - Implement `/api/query` endpoint 
   - Implement `rag_query` MCP tool
   - Test dual-protocol shared logic

#### Sprint 3: Frontend Implementation (Week 2)
4. **Top Navigation & Search Page Structure**
   - Write tests for TopNavigation component extensions (Search tab)
   - Add "Search" tab to navigationTabs array with SearchIcon
   - Implement page routing for 'search' state in App.tsx
   - Create SearchPage component structure following existing patterns
   - Test navigation flow between File Collections and Search

5. **RAG Query Component Development**
   - Write component tests for RAGQueryComponent within SearchPage
   - Implement query input and collection selection (reuse existing patterns)
   - Implement response display with source documents and metadata
   - Test user interactions and loading states

6. **API Integration & Configuration**
   - Write tests for useApi.ts extensions
   - Implement RAG API integration hooks
   - Implement configuration UI for provider selection
   - Test error handling and response caching

#### Sprint 4: Integration & Polish (Week 1)
7. **End-to-End Integration**
   - Write E2E tests for complete user journeys including navigation flow
   - Validate HTTP API → Frontend flow  
   - Validate MCP tool functionality in Claude Desktop
   - Performance testing and optimization

8. **Error Handling & Documentation**
   - Test all error scenarios (LLM failures, network issues)
   - Implement graceful degradation strategies
   - Update README with RAG configuration guide
   - Create usage examples for both interfaces
   - Document navigation flow and search functionality

### Risk Mitigation
**Technical Risks:**
- **LLM API Rate Limits**: Implement retry logic with exponential backoff
- **Provider Switching**: Abstract interface ensures consistent behavior
- **Response Time Variability**: User feedback during processing, timeout handling
- **ChromaDB Integration**: Reuse existing tested infrastructure

**Development Risks:**
- **Test Coverage**: Continuous monitoring, fail builds below 85%
- **Configuration Complexity**: Environment-based with sensible defaults
- **Cross-Platform Compatibility**: Test both OpenAI and Ollama paths

### Dependencies & Prerequisites
**External Dependencies:**
- `openai>=1.0.0` - OpenAI Python SDK
- `ollama` - Ollama Python client (optional)
- Existing ChromaDB and vector sync infrastructure

**Environment Setup:**
```env
# LLM Provider Configuration
RAG_LLM_PROVIDER=ollama              # "ollama" or "openai"
RAG_OPENAI_API_KEY=sk-...            # Required for OpenAI
RAG_OLLAMA_HOST=http://localhost:11434
RAG_OLLAMA_MODEL=llama3.1:8b
RAG_OPENAI_MODEL=gpt-4o-mini

# RAG Configuration  
RAG_MAX_CHUNKS=5
RAG_SIMILARITY_THRESHOLD=0.7
RAG_MAX_TOKENS=2000
RAG_TEMPERATURE=0.1
```

## Execution Instructions

**To execute this plan:**
```bash
/execute .planning/PLAN_RAG_QUERY.md
```

**The execution will:**
- Implement strict test-first development for all components
- Ensure 85% test coverage achieved incrementally during implementation
- Validate quality gates continuously throughout development
- Maintain focus on reusing existing tested infrastructure
- Ensure both HTTP API and MCP tool interfaces work identically

**CRITICAL EXECUTION RULE**: Every component must have passing tests before implementation proceeds to the next component.

## Quality Validation

### Plan Quality Assessment
- [✓] Backend architecture leverages existing proven patterns and infrastructure
- [✓] Frontend integration extends current collection management UI appropriately  
- [✓] LLM provider abstraction enables flexible deployment scenarios
- [✓] Test strategy matches complexity level with appropriate coverage targets
- [✓] Quality gates ensure consistent standards across full-stack implementation
- [✓] Success criteria are specific, measurable, and comprehensive
- [✓] Context research provided authoritative implementation guidance from FastAPI, OpenAI, and ChromaDB
- [✓] Risk mitigation strategies address both technical and development challenges

**Plan Confidence Score**: 9/10 for supporting successful full-stack RAG feature implementation

**This plan combines comprehensive technical research with intelligent complexity-based planning to ensure efficient, high-quality development of a complete RAG query feature that seamlessly integrates with existing architecture while providing powerful LLM capabilities through both programmatic and interactive interfaces.**