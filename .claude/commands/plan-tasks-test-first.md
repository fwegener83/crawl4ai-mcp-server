# Generate Test-First Task Plan from Exploration Document

## Usage
```bash
/project:plan-tasks-test-first .planning/EXPLORE_SUFFIX.md
```

## Input Processing

### Step 1: Document Analysis
Read the exploration document: $ARGUMENTS

**Extract Key Information:**
- Feature name and SUFFIX from filename
- Technical requirements and dependencies
- Architecture context and integration points
- Success criteria and validation gates
- Code patterns and implementation knowledge

### Step 2: Test-First Planning Strategy

**Core Principle:** Write tests before implementation code
- Define expected behavior through tests
- Implement minimal code to pass tests
- Refactor with confidence using test safety net
- Validate integration at each step

## Test-First Task Generation

### Phase 1: Test Foundation Setup
**Task 1.1: Test Environment Setup**
- Set up testing framework and dependencies
- Configure test runners and coverage tools
- Create test directory structure
- Set up continuous testing workflow

**Task 1.2: Test Data & Fixtures**
- Create test data sets and fixtures
- Set up mock objects and stubs
- Prepare test databases/resources
- Define test configuration

### Phase 2: Unit Test Development
**Task 2.1: Core Logic Unit Tests**
- Write unit tests for main feature logic
- Test edge cases and error conditions
- Validate input/output transformations
- Test configuration and setup methods

**Task 2.2: Unit Test Implementation**
- Implement minimal code to pass unit tests
- Follow Red-Green-Refactor cycle
- Ensure all unit tests pass
- Validate test coverage meets requirements

### Phase 3: Integration Test Development
**Task 3.1: Integration Test Design**
- Write tests for component interactions
- Test database/external service integration
- Validate API endpoint behavior
- Test configuration loading and validation

**Task 3.2: Integration Implementation**
- Implement integration layer code
- Connect components based on test requirements
- Ensure all integration tests pass
- Validate end-to-end data flow

### Phase 4: System Test Development
**Task 4.1: System Test Creation**
- Write end-to-end system tests
- Test complete user workflows
- Validate system performance requirements
- Test error handling and recovery

**Task 4.2: System Implementation**
- Complete system integration
- Implement remaining glue code
- Ensure all system tests pass
- Validate system meets acceptance criteria

### Phase 5: Advanced Testing
**Task 5.1: Performance Testing**
- Create performance benchmarks
- Test under expected load conditions
- Validate response time requirements
- Test resource usage and memory leaks

**Task 5.2: Security Testing**
- Write security validation tests
- Test input sanitization and validation
- Validate authentication/authorization
- Test for common vulnerabilities

**Task 5.3: Compatibility Testing**
- Test across different environments
- Validate dependency compatibility
- Test version upgrade scenarios
- Cross-platform compatibility validation

### Phase 6: Documentation & Maintenance Tests
**Task 6.1: Documentation Tests**
- Test code examples in documentation
- Validate API documentation accuracy
- Test installation and setup instructions
- Ensure examples work as documented

**Task 6.2: Maintenance Test Suite**
- Create regression test suite
- Set up automated test execution
- Configure test result reporting
- Establish test maintenance procedures

## Task Document Generation

### Step 1: Extract SUFFIX
Extract SUFFIX from exploration document filename:
- `EXPLORE_CRAWLER.md` → `CRAWLER`
- Use same SUFFIX for task document

### Step 2: Generate Task Plan
Save comprehensive task plan as: `.planning/TASKS_{SUFFIX}.md`

### Task Document Structure:
```markdown
# Test-First Task Plan: {Feature Name}

## Source
- **Exploration Document**: {exploration_file_path}
- **Planning Method**: Test-First Development
- **Generated**: {timestamp}

## Overview
{Summary of feature and test-first approach}

## Test Strategy
{Overall testing approach and methodology}

## Task Breakdown

### Phase 1: Test Foundation
{Detailed tasks for test setup}

### Phase 2: Unit Testing
{Unit test development and implementation tasks}

### Phase 3: Integration Testing
{Integration test development and implementation tasks}

### Phase 4: System Testing
{System test development and implementation tasks}

### Phase 5: Advanced Testing
{Performance, security, compatibility testing tasks}

### Phase 6: Documentation & Maintenance
{Documentation and maintenance testing tasks}

## Validation Gates
{Executable commands for each phase}

## Success Criteria
{Clear completion criteria for each phase}

## Task Dependencies
{Task dependency mapping and prerequisites}

## Estimated Timeline
{Rough time estimates for planning}
```

## Task Quality Assurance

### Task Completeness Checklist
- [ ] All phases include both test creation and implementation
- [ ] Each task has clear input/output requirements
- [ ] Validation gates are executable and specific
- [ ] Dependencies between tasks are clearly defined
- [ ] Success criteria are measurable and testable

### Test-First Methodology Validation
- [ ] Tests are written before implementation code
- [ ] Each implementation task references specific tests
- [ ] Red-Green-Refactor cycle is clearly defined
- [ ] Test coverage requirements are specified
- [ ] Integration points are tested at appropriate levels

### Task Granularity Check
- [ ] Tasks are small enough to complete in reasonable time
- [ ] Each task has single, clear responsibility
- [ ] Tasks can be validated independently
- [ ] Dependencies are minimized and explicit
- [ ] Parallel execution opportunities identified

## Implementation Notes

**Test-First Benefits:**
- Ensures comprehensive test coverage
- Defines clear API contracts upfront
- Reduces debugging time through early validation
- Provides safety net for refactoring
- Documents expected behavior through tests

**Execution Guidelines:**
- Follow Red-Green-Refactor cycle strictly
- Run tests continuously during development
- Maintain test suite as first-class code
- Use test failures to guide implementation
- Refactor with confidence using test safety net

## Quality Assessment
Rate the task plan on a scale of 1-10 for:
- **Completeness**: All necessary testing phases covered
- **Clarity**: Tasks are clear and actionable
- **Test-First Adherence**: Properly follows TDD methodology
- **Feasibility**: Tasks can be executed as planned

**Remember:** The goal is to create a comprehensive test-first task plan that ensures high-quality implementation through systematic testing at every level.
