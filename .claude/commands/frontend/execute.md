# Execute Frontend Plan with Backend Integration

## Usage
```bash
/frontend:execute .planning/frontend/PLAN_SUFFIX.md
```

## Input Processing

### Step 1: Plan Document Analysis
Read the comprehensive frontend plan document: $ARGUMENTS

**Extract Key Information:**
- Feature name and SUFFIX from filename
- Complexity assessment and selected test strategy
- User journey technical analysis with backend integration
- Component architecture and API integration requirements
- Task breakdown with backend integration phases
- Success criteria including full-stack validation

### Step 2: Frontend Progress Tracking Setup
Create or load progress tracking:
```bash
# Create frontend progress file if not exists
.planning/frontend/PROGRESS_{SUFFIX}.md
```

**Enhanced Progress File Structure:**
- Current phase and task with component and backend API focus
- Completed tasks with test results, coverage, and backend integration status
- Failed tasks with error details and debugging info for both frontend and backend
- Commit hashes for each completed frontend task
- Test coverage metrics and performance benchmarks
- Backend API integration validation status

## Full-Stack Task Execution Strategy

### Phase Execution Loop with Backend-Aware Testing
For each phase in the frontend plan:

**Step 1: Phase Initialization**
- Log phase start in progress file with backend integration context
- Validate full-stack prerequisites (backend running, APIs accessible)
- Set up phase-specific environment (frontend + backend)
- Verify backend API availability and authentication

**Step 2: Task Execution with Backend Integration**
For each task in current phase:

**Task Start:**
- Check if task already completed (resume capability)
- Validate both frontend and backend dependencies are satisfied
- Log task start with timestamp and full-stack context

**Task Implementation with Frontend Testing Agent:**
- **Invoke frontend-tester sub agent** for all testing-related tasks with backend context
- Execute task following component-first, backend-integrated, test-first methodology
- Run validation gates continuously (unit -> integration -> backend -> e2e)
- Monitor test results, coverage, performance metrics, and API integration status

**Full-Stack Task Validation:**
- Run unit tests: `npm run test` with API mocking and coverage reporting
- Run integration tests: API integration with real backend endpoints
- Run E2E tests: `npm run test:e2e` for complete user journey validation
- Run linting: `npm run lint` for code quality
- Run build: `npm run build` to ensure production readiness
- Check bundle size and performance metrics
- **Validate backend API integration**: Test real API calls and data contracts

**Task Completion Validation:**
- Validate all frontend tests pass (unit/integration/e2e)
- **Verify backend API integration works correctly**
- Check test coverage meets requirements (85%/90%/95% based on complexity)
- Verify TypeScript compilation with no errors
- Ensure ESLint passes with no warnings
- Validate accessibility requirements met
- **Confirm data contracts between frontend and backend**

**Full-Stack Commit Strategy:**
- Create structured commit message with frontend and backend context
- Include component references, API endpoints, and test coverage info
- Add Co-authored-by for AI assistance
- Reference original issue and user journey
- Tag with frontend-specific and backend integration metadata

**Progress Update:**
- Mark task as completed in progress file
- Record commit hash, test coverage, performance metrics, and API integration status
- Update overall completion percentage
- Log any component-specific notes, backend integration decisions, or API changes

### Full-Stack Commit Message Strategy

**Conventional Commits for Frontend with Backend Integration:**
```
{type}(frontend): {description}

{body}

Components: {list of components affected}
Backend APIs: {list of API endpoints integrated}
Coverage: {test coverage percentage}
Integration: {backend integration status}
Co-authored-by: Claude <claude@anthropic.com>
Co-authored-by: Frontend-Tester Agent
Refs: #{issue_number}
Task: {phase}.{task_number}
Journey: {user_journey_reference}
```

**Full-Stack Commit Types:**
- `test(frontend)`: Adding or modifying component/e2e tests with backend integration
- `feat(frontend)`: New frontend feature with backend API integration
- `fix(frontend)`: Bug fixes in UI, user interactions, or backend integration
- `api(frontend)`: Frontend changes related to backend API integration
- `style(frontend)`: Styling updates or responsive fixes
- `refactor(frontend)`: Component refactoring with backend integration safety net
- `perf(frontend)`: Performance optimizations including API calls
- `a11y(frontend)`: Accessibility improvements

## Full-Stack Quality Gates

### Pre-Commit Validation for Full-Stack Frontend
Before each commit, run comprehensive frontend and backend integration checks:
```bash
# TypeScript compilation
cd frontend && npm run typecheck

# ESLint with auto-fix
cd frontend && npm run lint

# Unit test execution with coverage (including API mocks)
cd frontend && npm run test -- --coverage --run

# Backend integration validation
cd frontend && npm run test:integration

# Build validation
cd frontend && npm run build

# Bundle size check
cd frontend && npm run build && du -sh dist/

# E2E tests with full backend integration
cd frontend && npm run test:e2e

# Backend API health check
curl -f http://localhost:8000/health || echo "Backend not available"
```

### Full-Stack Regression Testing
After each task completion:
- Run full test suite (unit + integration + backend + e2e)
- Compare test coverage with previous results
- Ensure no UI regression in existing components
- **Validate backend API contracts haven't broken**
- Validate performance metrics haven't degraded
- Check bundle size impact
- **Test full user journeys with real backend data**

### Full-Stack Progress Monitoring
Regular checks during execution:
- Review recent commits for component and API integration changes
- Validate task sequence follows full-stack workflow
- Check for skipped accessibility, performance, or backend integration tasks
- Monitor test coverage trends and gaps
- **Track backend API integration completeness**

## Backend-Aware Testing Agent Integration

### When to Invoke frontend-tester Sub Agent
- **All testing tasks**: Unit, integration, backend, and E2E test development
- **Component implementation**: When tests need to be written first with backend integration
- **API integration tasks**: When frontend components need backend API connections
- **Debugging tasks**: When tests fail, components break, or API integration fails
- **Performance tasks**: When optimization needs test validation including API performance
- **Accessibility tasks**: When a11y features need test coverage
- **Backend integration validation**: When API contracts need frontend testing

### Backend-Aware Testing Agent Workflow
```bash
# Example invocation during task execution with backend context
> Use the frontend-tester sub agent to develop comprehensive tests for the CollectionModal component including backend API integration for the /api/collections endpoint

# Agent handles:
# 1. Analyzes component requirements including backend API dependencies
# 2. Writes tests following React Testing Library best practices with API mocking
# 3. Creates integration tests for real backend API calls
# 4. Ensures proper error handling for API failures
# 5. Validates data contracts between frontend and backend
# 6. Runs tests and reports coverage including API integration coverage
```

## Full-Stack Checkpoint System

### Enhanced Progress File Structure
```markdown
# Full-Stack Frontend Execution Progress: {Feature Name}

## Status
- **Current Phase**: {phase_number}
- **Current Task**: {task_number}
- **Overall Progress**: {percentage}%
- **Components Modified**: {list of components}
- **Backend APIs Integrated**: {list of API endpoints}
- **Started**: {start_timestamp}
- **Last Updated**: {update_timestamp}

## Test Coverage Metrics
- **Unit Tests**: {unit_coverage}% (including API mocks)
- **Integration Tests**: {integration_coverage}% (with backend APIs)
- **E2E Tests**: {e2e_coverage}% (full-stack workflows)
- **Backend Integration**: {backend_integration_coverage}%
- **Overall Coverage**: {overall_coverage}%

## Backend Integration Status
- **API Endpoints Integrated**: {endpoints_completed}/{endpoints_total}
- **Data Contracts Validated**: {contracts_validated}
- **Authentication Working**: {auth_status}
- **Error Handling**: {error_handling_status}

## Performance Metrics
- **Bundle Size**: {current_bundle_size} (change: {size_delta})
- **Build Time**: {build_time}ms
- **Test Execution Time**: {test_time}ms
- **API Response Times**: {api_performance_metrics}

## Completed Tasks
- [x] Phase 1, Task 1 - Backend API Analysis (APIs: 5, Commit: {hash})
- [x] Phase 1, Task 2 - Component Unit Tests (Coverage: 95%, APIs: mocked, Commit: {hash})
- [x] Phase 2, Task 1 - API Integration Layer (Integration: ✅, Commit: {hash})
- [ ] Phase 3, Task 1 - Full-Stack E2E Tests (In Progress)

## Failed Tasks
- Phase X, Task Y - {error_description} (Retry count: N)
  - Error details: {specific_error_message}
  - Components affected: {component_list}
  - Backend APIs affected: {api_endpoints}
  - Debugging steps: {steps_taken}

## Full-Stack Quality Checks
- [ ] TypeScript: All files compile without errors
- [ ] ESLint: No warnings or errors
- [ ] Tests: All test suites pass (unit/integration/e2e)
- [ ] Build: Production build succeeds
- [ ] Bundle Size: Within acceptable limits
- [ ] Backend APIs: All integrated endpoints working
- [ ] Data Contracts: Frontend/backend data models aligned
- [ ] Authentication: Auth flows working end-to-end
- [ ] Error Handling: API errors properly handled in UI
- [ ] Accessibility: Basic a11y requirements met

## User Journey Validation
- [ ] Journey 1: {journey_name} - E2E test passes with real backend data
- [ ] Journey 2: {journey_name} - E2E test passes with real backend data
- [ ] Error Scenarios: API failures properly handled in UI
- [ ] Authentication: Login/logout flows working
- [ ] Performance: User journeys meet performance benchmarks

## Backend Integration Notes
{Important full-stack observations, API decisions, data contract changes}
```

### Full-Stack Resume Capability
- Automatically detect incomplete frontend and backend integration tasks
- Resume from last successful checkpoint with proper full-stack environment
- Validate current component state and backend API availability before continuing
- Handle partially completed tasks (e.g., tests written but API integration pending)

## Full-Stack Task Completion Notification

### Complete Full-Stack Task Execution
When all frontend tasks with backend integration completed:

```bash
echo "🎉 Full-stack frontend tasks completed successfully!"
echo "📊 Final Full-Stack Statistics:"
echo "   - Tasks completed: {total_completed}"
echo "   - Test coverage: {final_coverage}%"
echo "   - Components added/modified: {component_count}"
echo "   - Backend APIs integrated: {api_count}"
echo "   - Bundle size impact: {bundle_impact}"
echo "   - E2E tests passing: {e2e_count}"
echo "   - Data contracts validated: {contract_count}"
echo ""
echo "📋 Next Steps:"
echo "   1. Run full test suite: npm run test:all"
echo "   2. Validate in browser with backend: npm run dev (ensure backend running)"
echo "   3. Check production build: npm run build && npm run preview"
echo "   4. Test API integration manually: Check network tab"
echo "   5. Review accessibility: Check keyboard navigation and screen reader"
echo ""
echo "🔧 Manual Testing Checklist:"
echo "   - Test user journeys with real backend data in different browsers"
echo "   - Validate responsive design on mobile devices"
echo "   - Check accessibility with keyboard-only navigation"
echo "   - Verify error handling for API failures"
echo "   - Test performance with real backend response times"
echo "   - Validate authentication flows work correctly"
echo "   - Test offline/network error scenarios"
```

### Full-Stack Progress File Finalization
Mark the full-stack progress file as completed:
```markdown
## Status
- **Current Phase**: COMPLETED
- **Current Task**: ALL FULL-STACK TASKS COMPLETED
- **Overall Progress**: 100%
- **Final Coverage**: {final_coverage}%
- **Backend Integration**: COMPLETE
- **Completed**: {completion_timestamp}

## Final Full-Stack Summary
All planned frontend tasks with backend integration successfully completed.
Components are production-ready with proper backend integration, accessibility, and performance.
All API contracts validated and working. Ready for user acceptance testing and deployment.

## Deployment Checklist
- [ ] All tests passing (unit/integration/backend/e2e)
- [ ] Bundle size optimized
- [ ] Backend APIs integrated and tested
- [ ] Data contracts validated
- [ ] Authentication working
- [ ] Error handling comprehensive
- [ ] Accessibility validated
- [ ] Cross-browser compatibility confirmed
- [ ] Performance metrics acceptable (including API calls)
- [ ] Full-stack integration tested end-to-end
```

## Full-Stack Error Handling & Recovery

### Full-Stack Task Failure Recovery
- Log detailed error information with component and backend API context
- Capture test output and error messages for both frontend and backend
- Take screenshots for UI-related failures
- Log API response errors and status codes
- Increment retry counter with specific full-stack context
- Suggest component-specific and API integration fixes
- Allow manual intervention point for debugging both frontend and backend issues

### Full-Stack Rollback Mechanism
- Can revert to previous successful full-stack state
- Maintains clean git history for frontend changes
- Preserves test coverage metrics and API integration status
- Allows for task plan adjustments based on backend API changes

## Full-Stack Execution Monitoring

### Full-Stack Progress Reporting
- Real-time progress updates with component and backend API context
- Estimated time to completion based on full-stack task complexity
- Current test coverage metrics across all test types including backend integration
- Recent frontend commit activity summary with API integration status
- Bundle size trends and performance impact including API call performance

### Full-Stack Deviation Detection
- Compare actual vs planned component and API integration sequence
- Identify skipped accessibility, performance, or backend integration tasks
- Flag potential UI/UX or API integration issues early
- Suggest corrective actions specific to full-stack development

## Full-Stack Success Criteria

### Full-Stack Task Completion Requirements
- All frontend quality gates pass
- Component tests demonstrate expected behavior
- **Backend API integration fully functional**
- User journeys validated through full-stack E2E tests
- Code quality meets frontend standards (TypeScript, ESLint)
- Test coverage meets complexity-based requirements
- Accessibility requirements satisfied
- Performance benchmarks met (including API performance)
- **Data contracts between frontend and backend validated**

### Full-Stack Feature Completion Requirements
- All planned frontend tasks with backend integration completed
- Full test suite passes (unit + integration + backend + e2e)
- Component test coverage requirements met
- **Backend API integration tested and working**
- Performance benchmarks satisfied (including API call performance)
- Accessibility validation passed
- Cross-browser compatibility confirmed
- Bundle size impact acceptable
- **Full-stack user journey documentation complete and accurate**
- **Authentication and error handling working end-to-end**

## Quality Assessment for Full-Stack Execution

Rate the full-stack execution plan on a scale of 1-10 for:
- **Component Quality**: Well-tested, reusable, accessible components with backend integration
- **User Experience**: Smooth, intuitive user interactions with real backend data
- **Test Coverage**: Comprehensive testing across all levels including backend integration
- **Performance**: Optimized bundle size, runtime performance, and API call performance
- **Accessibility**: Inclusive design with proper ARIA and keyboard support
- **Backend Integration**: Seamless frontend-backend communication with proper error handling
- **Maintainability**: Clean, documented, TypeScript-safe code with clear API contracts

**Remember:** Full-stack frontend execution prioritizes seamless integration between frontend components and backend APIs, ensuring user-centric development with comprehensive testing that validates the complete system works as intended, maintaining both technical excellence and exceptional user experience.
