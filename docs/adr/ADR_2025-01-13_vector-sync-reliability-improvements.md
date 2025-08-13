# ADR-001: Vector Sync Reliability and Test Infrastructure Improvements

**Status:** Accepted  
**Decision Date:** 2025-01-13  
**Context:** Feature branch `frontend_anpassung`

## Context

The Vector Sync system experienced critical reliability issues that prevented proper synchronization and polling:

1. **Deadlock Issues**: Collections would get permanently stuck in "syncing" status, preventing any future sync operations
2. **Missing Change Detection**: File changes weren't detected in real-time, causing status to remain "in_sync" after modifications
3. **Race Conditions**: Multiple recovery functions would overwrite each other's polling operations
4. **Test Pollution**: MCP tests were creating collections that weren't cleaned up, cluttering the database

## Decision

### 1. Backend Deadlock Prevention

- **Stale Sync Detection**: Implement 10-minute timeout detection for stuck sync operations
- **Automatic Status Reset**: Convert stale "syncing" status to "sync_error" to unblock future operations
- **Live Change Detection**: Add real-time file change detection using hash comparison in `get_collection_sync_status()`

### 2. Frontend Recovery Unification

- **Unified Recovery Function**: Create single `createRecoveryPollingFunction` to prevent race conditions
- **Graceful Fallback**: Show "Files changed" instead of "0 files changed" when count is unavailable
- **Enhanced Error Handling**: Implement proper timeout and error recovery mechanisms

### 3. Test Infrastructure Enhancement

- **Automatic Test Cleanup**: Implement `@pytest_asyncio.fixture` for guaranteed collection cleanup
- **Database Consistency**: Use same `CollectionService` architecture as production code  
- **Error Tolerance**: Cleanup continues even if individual deletions fail

## Alternatives Considered

1. **Manual Sync Reset**: Rejected due to poor user experience
2. **Frontend-only Fixes**: Rejected as root cause was in backend
3. **Test Collection Namespacing**: Rejected in favor of automatic cleanup

## Implementation Outcome

### Results Achieved

- ✅ **Deadlock Resolution**: Collections no longer get permanently stuck in syncing state
- ✅ **Live Change Detection**: File modifications are immediately reflected in sync status
- ✅ **Race Condition Prevention**: Single unified recovery mechanism prevents conflicts  
- ✅ **Test Database Cleanliness**: Automatic cleanup removed 22 existing test collections and prevents future accumulation

### Files Modified

- `tools/vector_sync_api.py`: Added stale sync detection with 10-minute timeout
- `tools/knowledge_base/intelligent_sync_manager.py`: Implemented live change detection
- `frontend/src/hooks/useVectorSync.ts`: Unified recovery polling function
- `frontend/src/components/collection/VectorSyncIndicator.tsx`: Graceful counter fallback
- `tests/test_mcp_e2e_integration.py`: Enhanced pytest fixture with guaranteed cleanup

### Performance Impact

- **Positive**: Eliminated unnecessary network requests from stuck polling
- **Minimal**: Live change detection adds <100ms to status checks via hash comparison
- **Maintenance**: Reduced debugging time through improved error handling

## Consequences

### Benefits

- **Reliability**: Vector Sync system is now robust against edge cases and failures
- **User Experience**: Clear status feedback and automatic recovery from error states
- **Development Velocity**: Clean test environment prevents debugging false issues
- **Maintainability**: Unified error handling patterns across frontend and backend

### Trade-offs

- **Complexity**: Additional logic for stale detection and change monitoring
- **Performance**: Slight overhead from hash-based change detection
- **Dependencies**: Test cleanup relies on specific service architecture

This ADR documents the architectural decisions made to transform an unreliable Vector Sync system into a robust, user-friendly feature with comprehensive test infrastructure.
