# ADR-003: AsyncMock Testing Strategy for Integration Tests

**Status:** Accepted  
**Decision Date:** 2025-01-15  
**Context:** Feature branch `feature/RAG_QUERY`

## Context

During the implementation of the RAG Query feature, significant testing challenges emerged around async function mocking in integration tests. The root issue manifested as:

```
ERROR unified_server:unified_server.py:1264 HTTP rag_query error: object Mock can't be used in 'await' expression
```

This error revealed fundamental inconsistencies in our testing approach between HTTP and MCP protocol integration tests, leading to:

1. **Inconsistent Mocking Strategies**: HTTP tests tried to mock services while MCP tests patched use-cases
2. **Mock vs AsyncMock Confusion**: Regular `Mock()` objects used for async service methods
3. **Provider Pattern Issues**: Dependency injection container providers incorrectly mocked
4. **Test Fragility**: Different test types using incompatible mocking approaches

## Decision

### Standardized AsyncMock Testing Architecture

Implement a **Unified Integration Test Mocking Strategy** with these principles:

#### 1. Use-Case Level Patching for Integration Tests
```python
# ✅ Correct: Patch the use-case function directly
with patch('unified_server.rag_query_use_case', mock_rag_use_case):
    server = UnifiedServer()
    # Test the API endpoint, mock the business logic
```

#### 2. AsyncMock for All Async Services
```python
# ✅ Correct: Use AsyncMock for services with async methods  
mock_llm_service = AsyncMock()
mock_llm_service.generate_response = AsyncMock(return_value={...})
mock_llm_service.health_check = AsyncMock(return_value=True)
```

#### 3. Lambda Provider Pattern for DI Containers
```python
# ✅ Correct: Mock providers as lambda functions
server.container.llm_service = lambda: mock_llm_service
server.container.vector_sync_service = lambda: mock_vector_service

# ❌ Incorrect: Mock providers as Mock(return_value=...)
server.container.llm_service = Mock(return_value=mock_llm_service)  # Breaks at runtime
```

#### 4. Consistent Strategy Across Protocols
- **HTTP Tests**: Patch `unified_server.rag_query_use_case` 
- **MCP Tests**: Patch `unified_server.rag_query_use_case`
- **Unit Tests**: Mock individual service dependencies
- **E2E Tests**: Use real services, mock only external APIs

## Alternatives Considered

### 1. Service-Level Mocking Only
**Approach**: Mock individual services instead of use-case functions.
**Rejected Because**: 
- Complex provider pattern interactions in dependency injection
- AsyncMock configuration becomes error-prone
- Inconsistent behavior between different service types

### 2. Real Services with External Mocking
**Approach**: Use real service instances, mock only external dependencies.
**Rejected Because**:
- Integration tests become slow and complex
- External dependency setup required in CI/CD
- Harder to test specific error conditions

### 3. Test-Specific Mocking Strategies
**Approach**: Different mocking approaches per test file.
**Rejected Because**:
- Inconsistent developer experience
- Knowledge required about internal implementation details
- Maintenance burden when services change

## Implementation Outcome

The AsyncMock testing strategy was successfully implemented across all integration tests.

### Results Achieved

- ✅ **All Tests Green**: RAG API integration tests now pass consistently (15/15)
- ✅ **Consistent Strategy**: HTTP and MCP tests use identical mocking patterns
- ✅ **AsyncMock Mastery**: Complete resolution of async/await mocking issues
- ✅ **Knowledge Documentation**: Best practices captured in `tests/.claude.md`
- ✅ **Developer Experience**: Clear patterns for future test development

### Files Modified

- `tests/test_rag_api_integration.py`: Unified HTTP and MCP mocking strategies with AsyncMock
- `tests/.claude.md`: Comprehensive AsyncMock best practices and troubleshooting guide
- `tests/test_llm_service.py`: Enhanced with proper dependency-aware skip decorators

### Performance Impact

- **Test Reliability**: Eliminated flaky tests caused by mocking inconsistencies
- **CI/CD Stability**: All integration tests now pass consistently in CI environment  
- **Development Velocity**: Clear mocking patterns reduce debugging time for new tests
- **Maintenance**: Unified approach reduces cognitive load when modifying tests

## Consequences

### Benefits

**Reliability**: Integration tests now pass consistently without flaking
**Developer Experience**: Clear, documented patterns for async service mocking
**Maintainability**: Unified strategy reduces complexity when adding new tests
**Knowledge Sharing**: Comprehensive documentation prevents future similar issues
**CI/CD Stability**: Consistent test results across local and remote environments

### Trade-offs

**Learning Curve**: Developers must understand AsyncMock vs Mock distinctions
**Pattern Discipline**: Requires adherence to documented mocking strategies
**Documentation Maintenance**: Best practices documentation needs regular updates

### Future Considerations

**Test Architecture Evolution**: Established patterns can guide testing strategy for new features
**Mock Library Upgrades**: AsyncMock patterns provide foundation for pytest-asyncio updates
**Integration Test Expansion**: Standardized approach supports adding more complex integration scenarios

This ADR establishes the testing foundation that ensures reliable, maintainable integration tests for async service architectures in the RAG Query system and beyond.