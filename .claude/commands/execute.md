# Execute Full-Stack Feature Plan

## Usage
```bash
/execute .planning/PLAN_SUFFIX.md
```

## Input Processing

### Step 1: Plan Document Analysis
Read the comprehensive full-stack plan document: $ARGUMENTS

**Extract Key Information:**
- Feature name and SUFFIX from filename
- Deep exploration results and context research findings
- Backend and frontend requirements with integration specifications
- Complexity assessment and selected test strategy
- Full-stack task breakdown and implementation roadmap
- Success criteria and quality gates
- Current branch context (feature/{SUFFIX})

### Step 2: Full-Stack Progress Tracking Setup
Create or load progress tracking:
```bash
# Create progress file if not exists
.planning/PROGRESS_{SUFFIX}.md
```

**Full-Stack Progress File Structure:**
- Current phase and task with backend + frontend + integration focus
- Completed tasks with test results, coverage, and integration status
- Failed tasks with error details, debugging info, and cross-stack issues
- Commit hashes for each completed task
- Test coverage metrics across backend, frontend, and integration layers
- Performance benchmarks and quality metrics
- Cross-stack validation results

## Full-Stack Plan Execution Strategy

### Phase Execution Loop with Integrated Development
For each phase in the full-stack plan:

**Step 1: Phase Initialization**
- Log phase start in progress file
- Validate full-stack prerequisites (backend environment, frontend tools, database, etc.)
- **Validate cross-stack integration prerequisites**
- Set up phase-specific development environment for entire stack

**Step 2: Plan-Based Task Execution with Cross-Stack Focus**
Execute tasks based on the comprehensive plan's full-stack task breakdown:

**Task Start:**
- Check if task already completed (resume capability)
- Validate full-stack task dependencies are satisfied
- **Verify cross-stack prerequisites for integration tasks**
- Log task start with timestamp, backend/frontend context, and integration requirements

**Task Implementation with Integrated Testing:**
- Execute task following the plan's test-first, full-stack methodology
- **Run cross-stack validation** alongside individual layer testing
- Run validation gates continuously (backend unit -> frontend unit -> integration -> e2e)
- Monitor test results, coverage, performance metrics, and cross-stack integration health

**Full-Stack Task Validation:**
- **Backend validation**: Run backend test suite with coverage reporting
- **Frontend validation**: Run frontend test suite with coverage reporting  
- **Integration validation**: API contract testing, data flow validation
- **E2E validation**: Complete user journey testing with real backend and frontend
- **Cross-stack linting**: Code quality validation across entire stack
- **Build validation**: Ensure production readiness for both backend and frontend
- **Performance validation**: Backend API performance and frontend bundle metrics
- **Security validation**: Authentication flows, data validation, authorization

**Task Completion Validation:**
- Validate all tests pass across the entire stack
- Check test coverage meets plan requirements (complexity-based targets)
- **Verify backend and frontend integration is fully functional**
- **Validate data contracts and API specifications**
- Verify code quality standards met across all languages/frameworks
- Ensure performance benchmarks met
- **Confirm cross-stack user journeys work end-to-end**

**Full-Stack Commit Strategy:**
- Create structured commit message with full-stack context
- Include backend and frontend changes, API contracts, test coverage info
- Add Co-authored-by for AI assistance
- Reference original issue and user journey
- **Tag with cross-stack integration status and validation results**

**Progress Update:**
- Mark task as completed in progress file
- Record commit hash, test coverage across stack, performance metrics
- **Log cross-stack integration validation results**
- Update overall completion percentage
- Log any architectural decisions, integration patterns, or contract changes

### Architecture Decision Tracking (Execution Phase)

If, during execution, a new architectural decision arises that is not already documented in an ADR:
- Create a new ADR file using the `.claude/templates/ADR_TEMPLATE.md` template
  - Filename: `docs/adr/ADR_{date}_{short-title}.md`
  - Status: Proposed
  - Fill Context, Decision, Alternatives, Consequences
  - Leave "Implementation Outcome" empty
- If an existing Proposed ADR is abandoned due to changes, update its status to Rejected and add a short note in "Implementation Outcome".

### Full-Stack Commit Message Strategy

**Conventional Commits for Full-Stack Development:**
```
{type}: {description}

{body}

Backend: {backend components/APIs affected}
Frontend: {frontend components affected}
Integration: {cross-stack integration points}
Coverage: Backend {backend_coverage}%, Frontend {frontend_coverage}%
Performance: {performance_impact}
Co-authored-by: Claude <claude@anthropic.com>
Refs: #{issue_number}
Task: {phase}.{task_number}
Journey: {user_journey_reference}
```

**Full-Stack Commit Types:**
- `feat`: New feature spanning backend and/or frontend
- `test`: Adding or modifying tests across the stack
- `fix`: Bug fixes in backend, frontend, or integration
- `api`: Backend API changes with frontend integration updates
- `ui`: Frontend changes with backend integration considerations
- `refactor`: Code refactoring with cross-stack test safety net
- `perf`: Performance optimizations across the stack
- `security`: Security improvements in backend, frontend, or integration
- `docs`: Documentation updates for full-stack features

## Full-Stack Quality Gates

### Pre-Commit Validation for Complete Stack
Before each commit, run comprehensive validation across entire stack:
```bash
# Backend validation
echo "🔍 Validating backend..."
# Run backend-specific linting and type checking
# Run backend test suite with coverage
# Check backend security and performance

# Frontend validation  
echo "🔍 Validating frontend..."
# Run frontend-specific linting and type checking
# Run frontend test suite with coverage
# Validate frontend build and bundle size

# Integration validation
echo "🔍 Validating integration..."
# Run API contract tests
# Validate data flow between layers
# Check authentication and authorization flows

# End-to-end validation
echo "🔍 Validating end-to-end functionality..."
# Run E2E tests with real backend and frontend
# Validate complete user journeys
# Check cross-browser compatibility

# Performance validation
echo "🔍 Validating performance..."
# Backend API performance tests
# Frontend bundle size and load time checks
# Database query optimization validation
```

### Full-Stack Regression Testing
After each task completion:
- Run complete test suite across backend, frontend, and integration
- **Validate cross-stack data flow and API contracts**
- **Test complete user journeys end-to-end**
- Compare test coverage with previous results across all layers
- Ensure no regression in backend APIs or frontend components
- **Validate no breaking changes in cross-stack communication**
- Validate performance metrics haven't degraded
- Check security measures remain intact
- **Confirm all integration points still function correctly**

### Full-Stack Progress Monitoring
Regular checks during execution:
- Review recent commits for backend, frontend, and integration changes
- Validate task sequence follows the comprehensive plan workflow
- **Monitor cross-stack communication health and performance**
- Check for skipped testing, security, or performance tasks
- Monitor test coverage trends across all layers
- **Track integration health and contract compliance**
- Monitor build and deployment readiness

## Full-Stack Testing Integration

### Cross-Stack Testing Scenarios
- **Backend Unit Testing**: API endpoints, business logic, data models
- **Frontend Unit Testing**: Components, utilities, state management
- **Integration Testing**: API contracts, data transformation, error handling
- **E2E Testing**: Complete user workflows with real backend and frontend
- **Performance Testing**: Backend API response times, frontend load times
- **Security Testing**: Authentication, authorization, data validation
- **Accessibility Testing**: Frontend accessibility with backend data
- **Cross-Browser Testing**: Frontend compatibility with backend integration

### Testing Agent Integration
```bash
# Example comprehensive testing workflow
> Run comprehensive testing across the entire stack for the user authentication feature

# Testing approach:
# 1. Backend API tests for authentication endpoints
# 2. Frontend component tests for login/register forms
# 3. Integration tests for auth flow with mocked and real APIs
# 4. E2E tests for complete authentication user journeys
# 5. Security tests for authentication vulnerabilities
# 6. Performance tests for auth API response times
# 7. Accessibility tests for auth UI components
```

## Full-Stack Checkpoint System

### Enhanced Progress File Structure
```markdown
# Full-Stack Feature Execution Progress: {Feature Name}

## Status
- **Current Phase**: {phase_number}
- **Current Task**: {task_number}
- **Overall Progress**: {percentage}%
- **Backend Components**: {backend_components_modified}
- **Frontend Components**: {frontend_components_modified}
- **Integration Points**: {integration_points_implemented}
- **Started**: {start_timestamp}
- **Last Updated**: {update_timestamp}

## Test Coverage Metrics
- **Backend Tests**: {backend_coverage}%
- **Frontend Tests**: {frontend_coverage}%
- **Integration Tests**: {integration_coverage}%
- **E2E Tests**: {e2e_coverage}%
- **Overall Coverage**: {overall_coverage}%

## Cross-Stack Integration Status
- **API Endpoints**: {implemented}/{total_planned}
- **Data Contracts**: {validated_contracts}
- **Authentication**: {auth_integration_status}
- **Error Handling**: {error_handling_coverage}
- **Performance**: {performance_benchmarks_status}

## Performance Metrics
- **Backend API Response Time**: {avg_api_response}ms
- **Frontend Bundle Size**: {bundle_size}kb (change: {size_delta})
- **Frontend Load Time**: {load_time}ms
- **Database Query Performance**: {db_performance}ms
- **Build Time**: {build_time}ms

## Completed Tasks
- [x] Phase 1, Task 1 - Backend API Tests (Coverage: 95%, Commit: {hash})
- [x] Phase 1, Task 2 - Frontend Component Tests (Coverage: 92%, Commit: {hash})
- [x] Phase 2, Task 1 - Backend Implementation (Integration: ✅, Commit: {hash})
- [x] Phase 2, Task 2 - Frontend Implementation (API Integration: ✅, Commit: {hash})
- [ ] Phase 3, Task 1 - E2E Integration Testing (In Progress)

## Failed Tasks
- Phase X, Task Y - {error_description} (Retry count: N)
  - Error details: {specific_error_message}
  - Backend issues: {backend_problems}
  - Frontend issues: {frontend_problems}
  - Integration issues: {cross_stack_problems}
  - Debugging steps: {steps_taken}

## Quality Validation Status
### Backend Quality Checks
- [ ] Code quality: All linting and type checking passes
- [ ] Test coverage: Meets target requirements
- [ ] Performance: API response times within benchmarks
- [ ] Security: Authentication and authorization validated

### Frontend Quality Checks  
- [ ] Code quality: All linting and type checking passes
- [ ] Test coverage: Meets target requirements
- [ ] Build: Production build succeeds
- [ ] Bundle size: Within acceptable limits
- [ ] Accessibility: WCAG compliance validated

### Integration Quality Checks
- [ ] API contracts: All contracts validated and tested
- [ ] Data flow: Cross-stack data flow tested
- [ ] Authentication: End-to-end auth flows work
- [ ] Error handling: Cross-stack error handling comprehensive
- [ ] Performance: Full-stack performance meets requirements

## User Journey Validation
- [ ] Journey 1: {journey_name} - Complete stack E2E test passes
- [ ] Journey 2: {journey_name} - Complete stack E2E test passes
- [ ] Error Scenarios: Comprehensive error handling tested across stack
- [ ] Performance: All journeys meet performance requirements
- [ ] Accessibility: All journeys accessible and compliant

## Notes
{Important observations, architectural decisions, integration patterns, or cross-stack considerations}
```

### Full-Stack Resume Capability
- Automatically detect incomplete tasks across backend, frontend, and integration
- Resume from last successful checkpoint with proper full-stack environment
- Validate current state across entire stack before continuing
- Handle partially completed tasks (e.g., backend done but frontend pending)
- **Verify cross-stack contracts and integration points haven't changed**

## Full-Stack Task Completion Notification

### Complete Full-Stack Feature Execution
When all plan tasks completed, provide comprehensive summary:

```bash
echo "🎉 Full-stack feature execution completed successfully!"
echo "📊 Final Full-Stack Statistics:"
echo "   - Tasks completed: {total_completed}"
echo "   - Backend coverage: {backend_coverage}%"
echo "   - Frontend coverage: {frontend_coverage}%"
echo "   - Integration coverage: {integration_coverage}%"
echo "   - E2E tests passing: {e2e_count}"
echo "   - Performance benchmarks: {performance_status}"
echo ""
echo "🏗️ Backend Summary:"
echo "   - API endpoints implemented: {api_count}"
echo "   - Data models created/updated: {model_count}"
echo "   - Average API response time: {avg_response}ms"
echo ""
echo "🎨 Frontend Summary:"
echo "   - Components implemented: {component_count}"
echo "   - Bundle size: {bundle_size}kb"
echo "   - Accessibility compliance: {a11y_status}"
echo ""
echo "🔗 Integration Summary:"
echo "   - API contracts validated: {contract_count}"
echo "   - Authentication flows: {auth_status}"
echo "   - Error handling coverage: {error_coverage}"
echo ""
echo "📋 Next Steps:"
echo "   1. Run full stack validation: Run complete test suite"
echo "   2. Manual testing: Test all user journeys manually"
echo "   3. Performance review: Validate all performance benchmarks"
echo "   4. Security review: Conduct security assessment"
echo "   5. Documentation: Update feature documentation"
echo ""
echo "🔧 Manual Testing Checklist:"
echo "   - Test all user journeys with real data"
echo "   - Validate responsive design across devices"
echo "   - Check accessibility with assistive technologies"
echo "   - Verify error handling in various scenarios"
echo "   - Test performance under load"
echo "   - Confirm security measures are effective"
echo "   - Validate cross-browser compatibility"
echo "   - Test offline/connectivity scenarios"
```

### Full-Stack Progress File Finalization
Mark progress file as completed with comprehensive status:
```markdown
## Status
- **Current Phase**: COMPLETED
- **Current Task**: ALL FULL-STACK TASKS COMPLETED
- **Overall Progress**: 100%
- **Final Backend Coverage**: {backend_coverage}%
- **Final Frontend Coverage**: {frontend_coverage}%
- **Integration Validation**: FULLY TESTED
- **Performance Benchmarks**: ALL MET
- **Security Validation**: COMPREHENSIVE
- **Completed**: {completion_timestamp}

## Final Full-Stack Summary
All planned full-stack tasks successfully completed with comprehensive testing across backend, frontend, and integration layers. Feature is production-ready with proper performance, security, accessibility, and cross-stack integration. All user journeys validated end-to-end.

## Production Readiness Checklist
- [ ] Backend: All APIs tested, performant, and secure
- [ ] Frontend: All components tested, accessible, and optimized
- [ ] Integration: All contracts validated and data flow tested
- [ ] E2E: All user journeys work seamlessly
- [ ] Performance: All benchmarks met across the stack
- [ ] Security: Comprehensive security measures in place
- [ ] Accessibility: WCAG compliance validated
- [ ] Documentation: Feature fully documented
- [ ] Monitoring: Observability and logging in place
```

## Enhanced Error Handling & Recovery

### Full-Stack Task Failure Recovery
- Log detailed error information with backend, frontend, and integration context
- Capture test output, error messages, and cross-stack failures
- **Log API errors, UI errors, and integration failures**
- Take screenshots for UI issues and capture API response details
- **Capture network requests, database queries, and system logs**
- Increment retry counter with specific full-stack context
- Suggest layer-specific and integration fixes
- Allow manual intervention for complex cross-stack debugging

### Full-Stack Rollback Mechanism
- Can revert to previous successful state across entire stack
- Maintains clean git history for all changes
- Preserves test coverage metrics and integration status
- **Validates cross-stack compatibility after rollback**
- Allows for plan adjustments based on cross-stack complexity

## Enhanced Success Criteria

### Full-Stack Task Completion Requirements
- All quality gates pass across backend, frontend, and integration
- Tests demonstrate expected behavior at all layers
- **Backend APIs fully functional and performant**
- **Frontend components fully functional and accessible**
- **Cross-stack integration fully tested and validated**
- User journeys validated through comprehensive E2E tests
- Code quality meets standards across all technologies
- Test coverage meets complexity-based requirements
- Performance benchmarks met across the entire stack
- Security requirements satisfied end-to-end

### Full-Stack Feature Completion Requirements
- All planned tasks completed according to comprehensive plan
- Complete test suite passes (backend + frontend + integration + e2e)
- Test coverage requirements met across all layers
- **Cross-stack integration coverage requirements met**
- Performance benchmarks satisfied for entire stack
- Accessibility validation passed
- Security measures validated end-to-end
- **Data contracts validated and documented**
- **Authentication and authorization tested across stack**
- User journey documentation complete with full-stack details
- Production deployment readiness confirmed

## Quality Assessment for Full-Stack Execution

Rate the full-stack execution on a scale of 1-10 for:
- **Backend Quality**: Well-tested, performant, secure APIs and business logic
- **Frontend Quality**: Accessible, responsive, user-friendly interface
- **Integration Quality**: Seamless, robust cross-stack communication
- **User Experience**: Smooth, intuitive workflows with real data
- **Test Coverage**: Comprehensive testing across all layers and scenarios
- **Performance**: Optimized response times, bundle sizes, and resource usage
- **Security**: Comprehensive security measures across the entire stack
- **Maintainability**: Clean, documented, well-architected code across all layers

**Remember**: Full-stack execution prioritizes integrated development with comprehensive testing at every phase, ensuring no untested code exists and delivering complete, production-ready features that work seamlessly across the entire technology stack.
