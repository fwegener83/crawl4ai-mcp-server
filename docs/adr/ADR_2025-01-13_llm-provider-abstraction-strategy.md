# ADR-002: LLM Provider Abstraction Strategy for RAG Query Feature

**Status:** Proposed  
**Decision Date:** 2025-01-13  
**Context:** Feature branch `feature/RAG_QUERY`

## Context

The RAG Query feature requires integration with Large Language Model (LLM) providers to generate natural language responses from retrieved vector search results. The system needs to support multiple LLM providers with different characteristics:

1. **OpenAI API**: Cloud-based, high-quality responses, requires API key and network connectivity
2. **Ollama**: Local deployment, privacy-focused, lower latency but requires local setup
3. **Future Providers**: Potential for additional providers (Claude, Gemini, etc.)

Key requirements:
- Seamless switching between providers through configuration
- Consistent error handling across different provider failure modes
- Async operation support for non-blocking API calls
- Provider-specific configuration (API keys, model selection, endpoints)

## Decision

### LLM Service Architecture

Implement a **Provider Abstraction Pattern** with the following components:

#### 1. Abstract LLM Service Protocol
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class LLMService(ABC):
    """Abstract protocol for LLM providers."""
    
    @abstractmethod
    async def generate_response(
        self, 
        query: str, 
        context: str, 
        max_tokens: int = 2000,
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        """Generate LLM response from query and context."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if LLM service is available."""
        pass
```

#### 2. Provider-Specific Implementations
- **OpenAILLMService**: Uses OpenAI's async client with proper error handling
- **OllamaLLMService**: Interfaces with local Ollama API endpoint  
- **Factory Pattern**: Dynamic provider instantiation based on configuration

#### 3. Unified Error Handling
- Provider-agnostic error codes (`LLM_UNAVAILABLE`, `RATE_LIMITED`, `INVALID_MODEL`)
- Graceful degradation strategies (fallback to vector search only)
- Structured error responses with provider context

#### 4. Configuration Management
Environment-based provider selection with validation:
```env
RAG_LLM_PROVIDER=ollama              # "ollama" or "openai"
RAG_OPENAI_API_KEY=sk-...            # Required for OpenAI
RAG_OLLAMA_HOST=http://localhost:11434
RAG_OPENAI_MODEL=gpt-4o-mini
RAG_OLLAMA_MODEL=llama3.1:8b
```

## Alternatives Considered

### 1. Direct Provider Integration
**Approach**: Directly integrate with specific provider APIs in the RAG use-case.
**Rejected Because**: 
- Tight coupling makes provider switching difficult
- Inconsistent error handling across providers
- Code duplication for similar functionality

### 2. LangChain Integration
**Approach**: Use LangChain's LLM abstraction layer.
**Rejected Because**:
- Additional dependency overhead for simple use case
- More complex configuration and error handling
- Existing codebase doesn't use LangChain patterns

### 3. Plugin-Based Architecture
**Approach**: Dynamic plugin loading for LLM providers.
**Rejected Because**:
- Over-engineering for initial two-provider requirement
- Increased complexity for minimal benefit
- Security concerns with dynamic loading

## Implementation Outcome

*This section will be filled during execution phase.*

### Results Achieved
- TBD during implementation

### Files Created/Modified  
- TBD during implementation

### Performance Impact
- TBD during implementation

## Consequences

### Benefits

**Flexibility**: Easy addition of new LLM providers without changing core business logic
**Maintainability**: Clear separation of concerns between LLM integration and RAG orchestration
**Testability**: Easy mocking of LLM responses for comprehensive test coverage
**Configuration**: Simple environment-based provider switching for different deployment scenarios
**Error Handling**: Consistent error experience regardless of underlying provider failures

### Trade-offs

**Initial Complexity**: Additional abstraction layer requires more upfront implementation
**Performance Overhead**: Small abstraction cost compared to direct integration (minimal impact)
**Provider-Specific Features**: Some advanced provider features may require abstraction extension

### Future Considerations

**Multi-Provider Support**: Architecture supports future implementation of provider fallback chains
**Provider Configuration**: Extension points for provider-specific advanced configuration
**Monitoring Integration**: Standardized interface enables consistent metrics collection across providers

This ADR establishes the foundation for a flexible, maintainable LLM integration that supports the RAG Query feature's dual-provider requirements while providing clean extension points for future enhancements.