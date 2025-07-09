# Execute Tasks from Task Plan

## Usage
```bash
/project:execute-tasks .planning/TASKS_SUFFIX.md
```

## Input Processing

### Step 1: Task Document Analysis
Read the task plan document: $ARGUMENTS

**Extract Key Information:**
- Feature name and SUFFIX from filename
- All task phases and individual tasks
- Validation gates for each phase
- Success criteria and dependencies
- Current branch context

### Step 2: Progress Tracking Setup
Create or load progress tracking:
```bash
# Create progress file if not exists
.planning/PROGRESS_{SUFFIX}.md
```

**Progress File Structure:**
- Current phase and task
- Completed tasks with timestamps
- Failed tasks with error details
- Commit hashes for each completed task
- Overall completion status

## Task Execution Strategy

### Phase Execution Loop
For each phase in the task plan:

**Step 1: Phase Initialization**
- Log phase start in progress file
- Validate prerequisites are met
- Set up phase-specific environment

**Step 2: Task Execution**
For each task in current phase:

**Task Start:**
- Check if task already completed (resume capability)
- Validate task dependencies are satisfied
- Log task start with timestamp

**Task Implementation:**
- Execute task following test-first methodology
- Run validation gates continuously
- Monitor test results and coverage

**Task Completion Validation:**
- Run all relevant tests (unit/integration/system)
- Validate test coverage meets requirements
- Check code quality gates (linting, type-checking)
- Verify acceptance criteria are met

**Task Commit:**
- Create structured commit message
- Include task reference and description
- Add Co-authored-by for AI assistance
- Reference original issue if applicable

**Progress Update:**
- Mark task as completed in progress file
- Record commit hash and timestamp
- Update overall completion percentage

### Commit Message Strategy

**Conventional Commits Format:**
```
{type}({scope}): {description}

{body}

Co-authored-by: Claude <claude@anthropic.com>
Refs: #{issue_number}
Task: {phase}.{task_number}
```

**Commit Types:**
- `test`: Adding or modifying tests
- `feat`: New feature implementation
- `fix`: Bug fixes during implementation
- `docs`: Documentation updates
- `refactor`: Code refactoring with test safety net

## Quality Gates

### Pre-Commit Validation
Before each commit, run:
```bash
# Code quality checks
ruff check --fix
mypy .

# Test execution
uv run pytest tests/ -v --cov

# Coverage validation
coverage report --fail-under=80
```

### Regression Testing
After each task completion:
- Run full test suite
- Compare with previous test results
- Ensure no regression in functionality
- Validate performance hasn't degraded

### Progress Monitoring
Regular checks during execution:
- Review recent commits to detect skipped tasks
- Validate task sequence follows plan
- Check for unexpected deviations
- Monitor test coverage trends

## Checkpoint System

### Progress File Structure
```markdown
# Task Execution Progress: {Feature Name}

## Status
- **Current Phase**: {phase_number}
- **Current Task**: {task_number}
- **Overall Progress**: {percentage}%
- **Started**: {start_timestamp}
- **Last Updated**: {update_timestamp}

## Completed Tasks
- [x] Phase 1, Task 1 - {description} (Commit: {hash})
- [x] Phase 1, Task 2 - {description} (Commit: {hash})
- [ ] Phase 2, Task 1 - {description} (In Progress)

## Failed Tasks
- Phase X, Task Y - {error_description} (Retry count: N)

## Test Coverage History
- Phase 1: 85%
- Phase 2: 88%

## Notes
{Any important observations or deviations}
```

### Resume Capability
- Automatically detect incomplete tasks
- Resume from last successful checkpoint
- Validate current state before continuing
- Handle partially completed tasks

## Final Validation & PR Creation

### Complete Feature Validation
Before creating PR, ensure:
- All tasks marked as completed
- Full test suite passes (100% success rate)
- Code coverage meets requirements
- All quality gates pass
- Documentation is updated

### Pull Request Creation
When all tasks completed:

**PR Title Format:**
```
feat({scope}): {feature_summary}
```

**PR Description Template:**
```markdown
## Feature Summary
{Brief description of implemented feature}

## Implementation Details
- **Source**: {original_issue_or_file}
- **Tasks Completed**: {total_task_count}
- **Test Coverage**: {final_coverage}%
- **Commits**: {commit_count}

## Testing
- [x] Unit tests passing
- [x] Integration tests passing
- [x] System tests passing
- [x] Performance tests passing
- [x] Security tests passing

## Quality Gates
- [x] Linting passed
- [x] Type checking passed
- [x] Code coverage >= 80%
- [x] Documentation updated

## Changes Made
{Auto-generated summary of key changes}

## Testing Instructions
{How to test the feature}

Closes #{issue_number}
```

**PR Labels & Metadata:**
- Automatic labels based on feature type
- Link to original issue
- Assign to appropriate milestone
- Add relevant project boards

## Error Handling & Recovery

### Task Failure Recovery
- Log detailed error information
- Increment retry counter
- Suggest potential fixes
- Allow manual intervention point

### Rollback Mechanism
- Can revert to previous successful checkpoint
- Maintains clean git history
- Preserves progress tracking
- Allows for task plan adjustments

## Execution Monitoring

### Progress Reporting
- Real-time progress updates
- Estimated time to completion
- Current test coverage metrics
- Recent commit activity summary

### Deviation Detection
- Compare actual vs planned task sequence
- Identify skipped or out-of-order tasks
- Flag potential issues early
- Suggest corrective actions

## Success Criteria

### Task Completion Requirements
- All validation gates pass
- Tests demonstrate expected behavior
- Code quality meets standards
- Documentation is current
- Progress is properly tracked

### Feature Completion Requirements
- All planned tasks completed
- Full test suite passes
- Code coverage requirements met
- Performance benchmarks satisfied
- Security validation passed
- Documentation complete and accurate

## Quality Assessment
Rate the execution plan on a scale of 1-10 for:
- **Reliability**: Robust error handling and recovery
- **Traceability**: Clear progress tracking and history
- **Quality**: Comprehensive validation at each step
- **Efficiency**: Minimal overhead while maintaining quality

**Remember:** The goal is systematic, high-quality feature implementation with complete traceability and the ability to resume from any point in the process.
