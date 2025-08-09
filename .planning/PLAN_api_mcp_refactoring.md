# COMPREHENSIVE FULL-STACK PLAN: API-MCP Refactoring

## EXECUTIVE SUMMARY

**Project Goal**: Refactor shared logic between API and MCP endpoints to eliminate code duplication while maintaining API stability and fixing MCP inconsistencies through a unified service/use-case layer.

**Key Deliverables**:
- Centralized use-case layer for all business operations
- Protocol-agnostic service implementations  
- 100% API backward compatibility maintained
- MCP endpoint consistency with API behavior
- Comprehensive test coverage ensuring regression-safe refactoring

**Complexity Assessment**: **MEDIUM**
- **Technical Complexity**: Medium (Simple shared functions, no over-engineering)
- **Business Risk**: Low (Test-first ensures API stability)
- **Timeline**: 2.5 weeks with test-first development

---

## ARCHITECTURE ANALYSIS

### Current State Assessment

**✅ Strengths:**
- Unified server architecture already exists (`unified_server.py`)
- Service interfaces well-defined (`services/interfaces.py`)
- Shared service layer partially implemented
- Comprehensive E2E tests for validation

**🔧 Issues Identified:**
- Logic duplication between API and MCP endpoints
- Inconsistent error handling across protocols
- Different validation patterns (MCP vs API)
- Non-uniform response formatting
- MCP endpoints lack comprehensive testing

**🎯 Target Architecture:**
```
┌─────────────────────┐    ┌─────────────────────┐
│   MCP Protocol      │    │   HTTP/REST API     │
│   (stdio)           │    │   (FastAPI)         │
└─────────┬───────────┘    └─────────┬───────────┘
          │                          │
          └─────────┬──────────────────┘
                    │
    ┌───────────────▼───────────────┐
    │     USE-CASE LAYER            │
    │  (Protocol-agnostic logic)    │
    └───────────────┬───────────────┘
                    │
    ┌───────────────▼───────────────┐
    │     SERVICE LAYER             │
    │  (Business implementations)   │
    └───────────────┬───────────────┘
                    │
    ┌───────────────▼───────────────┐
    │     DATA LAYER                │
    │  (Collections, Vectors, etc.) │
    └───────────────────────────────┘
```

---

## TECHNICAL IMPLEMENTATION STRATEGY (Test-First)

### Phase 1: Test Infrastructure + Simple Use-Case Functions (Week 1)

**1.1 FIRST: Write Tests for Current API Behavior**
```python
# tests/test_vector_search_use_case.py - WRITE THIS FIRST
async def test_search_vectors_validation():
    """Test validation rules that both API and MCP must follow."""
    # Test missing query
    # Test invalid limit 
    # Test invalid threshold
    # Test collection not found

async def test_search_vectors_success_path():
    """Test successful vector search behavior."""
    # Test with collection_name
    # Test without collection_name  
    # Test result format consistency
```

**1.2 Create Simple Use-Case Functions (NOT classes)**
```python
# application_layer/vector_search.py - Simple functions, no base classes
from typing import Optional, List, Dict, Any

class ValidationError(Exception):
    def __init__(self, code: str, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details or {}

async def search_vectors_use_case(
    vector_service, collection_service,
    query: str, collection_name: Optional[str], 
    limit: int, similarity_threshold: float
) -> List[Dict[str, Any]]:
    """Shared vector search logic for API and MCP."""
    
    # Validation (test-driven)
    if not query or not query.strip():
        raise ValidationError("MISSING_QUERY", "Query parameter is required")
    if limit < 1:
        raise ValidationError("INVALID_LIMIT", "Limit must be greater than 0") 
    if not (0 <= similarity_threshold <= 1):
        raise ValidationError("INVALID_THRESHOLD", "Similarity threshold must be between 0 and 1")
    
    if collection_name:
        await collection_service.get_collection(collection_name)  # Will raise if not found
    
    if not vector_service.vector_available:
        raise RuntimeError("Vector sync service is not available")
    
    # Business logic
    results = await vector_service.search_vectors(query, collection_name, limit, similarity_threshold)
    
    # Consistent format
    return [
        {**result.model_dump(), "similarity_score": result.score}
        for result in results
    ]
```

### Phase 2: Test-First API Integration (Week 1.5)

**2.1 FIRST: Write Integration Tests**
```python
# tests/test_api_integration.py - WRITE BEFORE CHANGING API
async def test_api_uses_shared_logic():
    """Verify API endpoint uses shared use-case logic."""
    
async def test_api_response_format_unchanged():
    """Ensure refactoring doesn't break API response format."""
```

**2.2 THEN: Refactor API Endpoints**
```python
# Minimal change to unified_server.py HTTP endpoints
@app.post("/api/vector-sync/search")
async def search_vectors(request: dict):
    try:
        results = await search_vectors_use_case(
            vector_service, collection_service,
            query=request.get("query"),
            collection_name=request.get("collection_name"),
            limit=request.get("limit", 10),
            similarity_threshold=request.get("similarity_threshold", 0.7)
        )
        return {"success": True, "results": results}
    except ValidationError as ve:
        raise HTTPException(status_code=400, detail={
            "error": {"code": ve.code, "message": ve.message, "details": ve.details}
        })
    except RuntimeError as re:
        raise HTTPException(status_code=503, detail=str(re))
```

### Phase 3: Test-First MCP Integration (Week 2)

**3.1 FIRST: Write MCP Consistency Tests**
```python
# tests/test_mcp_consistency.py - WRITE BEFORE CHANGING MCP  
async def test_mcp_matches_api_results():
    """Ensure MCP and API return identical results for same input."""

async def test_mcp_error_handling_matches_api():
    """Verify MCP error scenarios match API behavior."""
```

**3.2 THEN: Update MCP Tools**
```python
@mcp_server.tool()
async def search_collection_vectors(
    query: str, collection_name: Optional[str] = None,
    limit: int = 10, similarity_threshold: float = 0.7
) -> str:
    try:
        results = await search_vectors_use_case(
            vector_service, collection_service,
            query, collection_name, limit, similarity_threshold
        )
        return json.dumps({"success": True, "results": results})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})
```

---

## SUCCESS CRITERIA & VALIDATION

### Functional Requirements ✅
- [ ] **API Stability**: All existing API tests pass without modification
- [ ] **MCP Consistency**: MCP tools return identical results to corresponding API endpoints
- [ ] **Error Handling**: Uniform error response format across protocols
- [ ] **Performance**: No degradation in response times (±5% acceptable)

### Technical Quality Gates ✅
- [ ] **Test Coverage**: >95% coverage for use-case layer
- [ ] **Code Quality**: All linting and type-checking passes
- [ ] **Documentation**: Complete API docs and architectural documentation
- [ ] **Security**: No new security vulnerabilities introduced

### Business Validation ✅
- [ ] **Zero Downtime**: Deployment with no service interruption
- [ ] **Backward Compatibility**: No breaking changes to public APIs
- [ ] **Feature Completeness**: All existing functionality preserved

---

## RISK ANALYSIS & MITIGATION

### High-Risk Items 🔴
1. **API Stability Risk**
   - *Risk*: Refactoring changes API behavior
   - *Mitigation*: Comprehensive regression testing, feature flags
   - *Contingency*: Quick rollback mechanism

2. **Performance Impact**
   - *Risk*: Additional abstraction layer reduces performance
   - *Mitigation*: Performance benchmarking, optimization review
   - *Contingency*: Direct service access fallback

### Medium-Risk Items 🟡
1. **Complex Error Handling**
   - *Risk*: Inconsistent error translation between protocols
   - *Mitigation*: Standardized exception hierarchy
   
2. **Test Coverage Gaps**
   - *Risk*: Missing edge cases during refactoring
   - *Mitigation*: Incremental testing approach

### Low-Risk Items 🟢
1. **Documentation Maintenance**
2. **Development Team Learning Curve**

---

## RESOURCE REQUIREMENTS

### Development Team
- **Developer**: Implements test-first development (no separate QA needed)

### Timeline Breakdown
- **Week 1**: Test infrastructure + use-case functions (test-first)
- **Week 1.5**: API refactoring (test-first)
- **Week 2**: MCP integration (test-first)
- **Week 2.5**: Final validation and cleanup

---

## IMPLEMENTATION CHECKLIST

### Pre-Implementation ☐
- [ ] Team alignment on architecture approach
- [ ] Development environment setup validation
- [ ] Backup and rollback procedures established

### Phase 1: Test-First Use-Case Layer ☐
- [ ] Write tests for vector search validation 
- [ ] Write tests for vector search success path
- [ ] Implement simple vector search use-case function
- [ ] Verify all tests pass

### Phase 2: Test-First API Integration ☐  
- [ ] Write API integration tests
- [ ] Write API response format tests
- [ ] Refactor API endpoints to use shared function
- [ ] Verify all existing API tests still pass

### Phase 3: Test-First MCP Integration ☐
- [ ] Write MCP consistency tests
- [ ] Write MCP error handling tests
- [ ] Update MCP tools to use shared function  
- [ ] Verify MCP matches API behavior exactly

---

## QUALITY GATES

Each phase must pass these gates before proceeding:

**Gate 1: Tests Written**
- Tests exist before any implementation code
- Tests cover validation and success paths
- All tests are failing (red phase of TDD)

**Gate 2: Implementation Working**
- Implementation makes tests pass (green phase of TDD)
- All existing API tests still pass
- No breaking changes detected

**Gate 3: Final Consistency**
- MCP tools match API behavior exactly
- All new tests pass
- All existing tests still pass

---

## SUCCESS VALIDATION

### Core Metrics
- **API Stability**: All existing API tests pass unchanged
- **Protocol Consistency**: MCP and API return identical results
- **Test Coverage**: >90% for shared use-case functions
- **Performance**: No response time degradation

### Simple Monitoring
- Basic test success rate tracking
- Response time logging (no complex dashboards needed)

---

*This plan provides a comprehensive roadmap for eliminating logic duplication between API and MCP endpoints while maintaining stability and improving consistency. The phased approach minimizes risk while ensuring thorough validation at each step.*

**Next Action**: Execute this plan with `/execute .planning/PLAN_api_mcp_refactoring.md` to begin implementation.