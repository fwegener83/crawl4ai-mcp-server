# Execute Frontend Tasks with Testing Agent

## Usage
```bash
/frontend:execute .planning/frontend/TASKS_SUFFIX.md
```

## Input Processing

### Step 1: Task Document Analysis
Read the frontend task plan document: $ARGUMENTS

**Extract Key Information:**
- Feature name and SUFFIX from filename
- All task phases and individual tasks
- Frontend quality gates and validation commands
- Success criteria and component requirements
- Current branch context (frontend/{SUFFIX})

### Step 2: Frontend Progress Tracking Setup
Create or load progress tracking:
```bash
# Create frontend progress file if not exists
.planning/frontend/PROGRESS_{SUFFIX}.md
```

**Frontend Progress File Structure:**
- Current phase and task with component focus
- Completed tasks with test results and coverage
- Failed tasks with error details and debugging info
- Commit hashes for each completed frontend task
- Test coverage metrics and performance benchmarks

## Frontend Task Execution Strategy

### Phase Execution Loop with Testing Agent
For each phase in the frontend task plan:

**Step 1: Phase Initialization**
- Log phase start in progress file
- Validate frontend prerequisites (node_modules, build tools)
- Set up phase-specific frontend environment

**Step 2: Task Execution with Frontend Testing Agent**
For each task in current phase:

**Task Start:**
- Check if task already completed (resume capability)
- Validate frontend task dependencies are satisfied
- Log task start with timestamp and component context

**Task Implementation with Testing Agent:**
- **Invoke frontend-tester sub agent** for all testing-related tasks
- Execute task following component-first, test-first methodology
- Run validation gates continuously (unit -> integration -> e2e)
- Monitor test results, coverage, and performance metrics

**Frontend-Specific Task Validation:**
- Run unit tests: `npm run test` with coverage reporting
- Run E2E tests: `npm run test:e2e` for user journey validation
- Run linting: `npm run lint` for code quality
- Run build: `npm run build` to ensure production readiness
- Check bundle size and performance metrics

**Task Completion Validation:**
- Validate all frontend tests pass (unit/integration/e2e)
- Check test coverage meets requirements (85%/90%/95% based on complexity)
- Verify TypeScript compilation with no errors
- Ensure ESLint passes with no warnings
- Validate accessibility requirements met

**Frontend Commit Strategy:**
- Create structured commit message with frontend context
- Include component references and test coverage info
- Add Co-authored-by for AI assistance
- Reference original issue and user journey
- Tag with frontend-specific metadata

**Progress Update:**
- Mark task as completed in progress file
- Record commit hash, test coverage, and performance metrics
- Update overall completion percentage
- Log any component-specific notes or decisions

### Frontend Commit Message Strategy

**Conventional Commits for Frontend:**
```
{type}(frontend): {description}

{body}

Components: {list of components affected}
Coverage: {test coverage percentage}
Co-authored-by: Claude <claude@anthropic.com>
Co-authored-by: Frontend-Tester Agent
Refs: #{issue_number}
Task: {phase}.{task_number}
Journey: {user_journey_reference}
```

**Frontend Commit Types:**
- `test(frontend)`: Adding or modifying component/e2e tests
- `feat(frontend)`: New frontend feature or component
- `fix(frontend)`: Bug fixes in UI or user interactions
- `style(frontend)`: Styling updates or responsive fixes
- `refactor(frontend)`: Component refactoring with test safety net
- `perf(frontend)`: Performance optimizations
- `a11y(frontend)`: Accessibility improvements

## Frontend Quality Gates

### Pre-Commit Validation for Frontend
Before each commit, run comprehensive frontend checks:
```bash
# TypeScript compilation
npm run typecheck

# ESLint with auto-fix
npm run lint

# Unit test execution with coverage
npm run test -- --coverage --run

# Build validation
npm run build

# Bundle size check
npm run build && du -sh dist/

# E2E tests (for integration tasks)
npm run test:e2e
```

### Frontend Regression Testing
After each task completion:
- Run full test suite (unit + integration + e2e)
- Compare test coverage with previous results
- Ensure no UI regression in existing components
- Validate performance metrics haven't degraded
- Check bundle size impact

### Frontend Progress Monitoring
Regular checks during execution:
- Review recent commits for component changes
- Validate task sequence follows frontend workflow
- Check for skipped accessibility or performance tasks
- Monitor test coverage trends and gaps

## Frontend Testing Agent Integration

### When to Invoke frontend-tester Sub Agent
- **All testing tasks**: Unit, integration, and E2E test development
- **Component implementation**: When tests need to be written first
- **Debugging tasks**: When tests fail or components break
- **Performance tasks**: When optimization needs test validation
- **Accessibility tasks**: When a11y features need test coverage

### Frontend Testing Agent Workflow
```bash
# Example invocation during task execution
> Use the frontend-tester sub agent to develop comprehensive unit tests for the CollectionModal component

# Agent handles:
# 1. Analyzes component requirements
# 2. Writes tests following React Testing Library best practices  
# 3. Ensures proper mocking of API calls
# 4. Validates accessibility features
# 5. Runs tests and reports coverage
```

## Frontend Checkpoint System

### Frontend Progress File Structure
```markdown
# Frontend Task Execution Progress: {Feature Name}

## Status
- **Current Phase**: {phase_number}
- **Current Task**: {task_number}
- **Overall Progress**: {percentage}%
- **Components Modified**: {list of components}
- **Started**: {start_timestamp}
- **Last Updated**: {update_timestamp}

## Test Coverage Metrics
- **Unit Tests**: {unit_coverage}%
- **Integration Tests**: {integration_coverage}%
- **E2E Tests**: {e2e_coverage}%
- **Overall Coverage**: {overall_coverage}%

## Performance Metrics
- **Bundle Size**: {current_bundle_size} (change: {size_delta})
- **Build Time**: {build_time}ms
- **Test Execution Time**: {test_time}ms

## Completed Tasks
- [x] Phase 1, Task 1 - Component Unit Tests (Coverage: 95%, Commit: {hash})
- [x] Phase 1, Task 2 - Component Implementation (Build: ✅, Commit: {hash})
- [ ] Phase 2, Task 1 - Integration Tests (In Progress)

## Failed Tasks
- Phase X, Task Y - {error_description} (Retry count: N)
  - Error details: {specific_error_message}
  - Components affected: {component_list}
  - Debugging steps: {steps_taken}

## Frontend Quality Checks
- [ ] TypeScript: All files compile without errors
- [ ] ESLint: No warnings or errors
- [ ] Tests: All test suites pass
- [ ] Build: Production build succeeds
- [ ] Bundle Size: Within acceptable limits
- [ ] Accessibility: Basic a11y requirements met

## User Journey Validation
- [ ] Journey 1: {journey_name} - E2E test passes
- [ ] Journey 2: {journey_name} - E2E test passes
- [ ] Error Scenarios: Proper error handling tested

## Notes
{Any important frontend-specific observations or architectural decisions}
```

### Frontend Resume Capability
- Automatically detect incomplete frontend tasks
- Resume from last successful checkpoint with proper environment
- Validate current component state before continuing
- Handle partially completed tasks (e.g., tests written but implementation pending)

## Frontend Task Completion Notification

### Complete Frontend Task Execution
When all frontend tasks completed, provide comprehensive summary:

```bash
echo "🎉 Frontend tasks completed successfully!"
echo "📊 Final Frontend Statistics:"
echo "   - Tasks completed: {total_completed}"
echo "   - Test coverage: {final_coverage}%"
echo "   - Components added/modified: {component_count}"
echo "   - Bundle size impact: {bundle_impact}"
echo "   - E2E tests passing: {e2e_count}"
echo ""
echo "📋 Next Steps:"
echo "   1. Run full test suite: npm run test && npm run test:e2e"
echo "   2. Validate in browser: npm run dev"
echo "   3. Check production build: npm run build && npm run preview"
echo "   4. Review accessibility: Check keyboard navigation and screen reader"
echo ""
echo "🔧 Manual Testing Checklist:"
echo "   - Test user journeys in different browsers"
echo "   - Validate responsive design on mobile devices"
echo "   - Check accessibility with keyboard-only navigation"
echo "   - Verify error handling scenarios"
echo "   - Test performance on slower devices"
```

### Frontend Progress File Finalization
Mark the frontend progress file as completed:
```markdown
## Status
- **Current Phase**: COMPLETED
- **Current Task**: ALL FRONTEND TASKS COMPLETED
- **Overall Progress**: 100%
- **Final Coverage**: {final_coverage}%
- **Completed**: {completion_timestamp}

## Final Frontend Summary
All planned frontend tasks successfully completed with comprehensive testing.
Components are production-ready with proper accessibility and performance.
Ready for user acceptance testing and deployment.

## Deployment Checklist
- [ ] All tests passing (unit/integration/e2e)
- [ ] Bundle size optimized
- [ ] Accessibility validated
- [ ] Cross-browser compatibility confirmed
- [ ] Performance metrics acceptable
- [ ] Error handling comprehensive
```

## Frontend Error Handling & Recovery

### Frontend Task Failure Recovery
- Log detailed error information with component context
- Capture test output and error messages
- Take screenshots for UI-related failures
- Increment retry counter with specific frontend context
- Suggest component-specific fixes
- Allow manual intervention point for debugging

### Frontend Rollback Mechanism
- Can revert to previous successful component state
- Maintains clean git history for frontend changes
- Preserves test coverage metrics
- Allows for task plan adjustments based on frontend complexity

## Frontend Execution Monitoring

### Frontend Progress Reporting
- Real-time progress updates with component context
- Estimated time to completion based on frontend task complexity
- Current test coverage metrics across test types
- Recent frontend commit activity summary
- Bundle size trends and performance impact

### Frontend Deviation Detection
- Compare actual vs planned component development sequence
- Identify skipped accessibility or performance tasks
- Flag potential UI/UX issues early
- Suggest corrective actions specific to frontend development

## Frontend Success Criteria

### Frontend Task Completion Requirements
- All frontend quality gates pass
- Component tests demonstrate expected behavior
- User journeys validated through E2E tests
- Code quality meets frontend standards (TypeScript, ESLint)
- Test coverage meets complexity-based requirements
- Accessibility requirements satisfied
- Performance benchmarks met

### Frontend Feature Completion Requirements
- All planned frontend tasks completed
- Full test suite passes (unit + integration + e2e)
- Component test coverage requirements met
- Performance benchmarks satisfied
- Accessibility validation passed
- Cross-browser compatibility confirmed
- Bundle size impact acceptable
- User journey documentation complete and accurate

## Quality Assessment for Frontend Execution

Rate the frontend execution plan on a scale of 1-10 for:
- **Component Quality**: Well-tested, reusable, accessible components
- **User Experience**: Smooth, intuitive user interactions
- **Test Coverage**: Comprehensive testing across all levels
- **Performance**: Optimized bundle size and runtime performance
- **Accessibility**: Inclusive design with proper ARIA and keyboard support
- **Maintainability**: Clean, documented, TypeScript-safe code

**Remember:** Frontend task execution prioritizes user-centric development with comprehensive testing, ensuring both technical excellence and exceptional user experience while maintaining development velocity.
