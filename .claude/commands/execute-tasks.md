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

## Task Completion Notification

### Complete Task Execution
When all tasks completed, notify user that execution phase is finished:

```bash
echo "🎉 All tasks completed successfully!"
echo "📊 Final Statistics:"
echo "   - Tasks completed: {total_completed}"
echo "   - Test coverage: {final_coverage}%"
echo "   - Commits created: {commit_count}"
echo ""
echo "📋 Next Steps:"
echo "   1. Run final validation: pytest --tb=short"
echo "   2. Complete feature: /project:complete-feature {SUFFIX}"
echo ""
echo "🔧 Optional Manual Testing:"
echo "   - python test_mcp_tool_call.py"
echo "   - mcp-inspector mcp-inspector-config.json"
```

### Progress File Finalization
Mark the progress file as completed:
```markdown
## Status
- **Current Phase**: COMPLETED
- **Current Task**: ALL TASKS COMPLETED
- **Overall Progress**: 100%
- **Completed**: {completion_timestamp}

## Final Summary
All planned tasks successfully completed. Ready for feature completion workflow.
```

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
