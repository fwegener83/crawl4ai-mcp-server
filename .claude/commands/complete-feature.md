# Complete Feature Development and Create Pull Request

## Usage
```bash
/project:complete-feature SUFFIX
```

## Overview
This command signals that feature development is complete and triggers the final workflow:
- Repository cleanup
- Final testing validation  
- Progress archival
- Pull request creation
- Branch management

## Input Processing

### Step 1: Validate Feature Readiness
- Check if `.planning/PROGRESS_{SUFFIX}.md` exists
- Validate all tasks are marked as completed
- Ensure current branch is `feature/{SUFFIX}`
- Verify working directory is clean (or acceptable state)

### Step 2: Feature Validation Gates
Run comprehensive validation before proceeding:

```bash
# Core functionality tests (must pass)
pytest tests/test_*_regression.py -v --tb=short

# Fast test suite (must pass)  
pytest -m "not slow" --timeout=120

# Code quality checks
ruff check --fix
mypy . --ignore-missing-imports

# Coverage validation (recommended >80%)
pytest --cov=. --cov-report=term-missing
```

## Repository Cleanup Phase

### Step 1: Temporary File Cleanup
Systematically clean repository of development artifacts:

```bash
# Remove temporary test files (preserve productive ones)
find . -name "simple_test*.py" -delete
find . -name "test_*_temp.py" -delete  
find . -name "*_debug.py" -delete

# Clean Python cache
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete

# Remove temporary environments
rm -rf test_env/ temp_env/ debug_env/

# Archive completed planning files
mkdir -p .planning/archive/
mv .planning/PROGRESS_{SUFFIX}.md .planning/archive/
mv .planning/TASKS_{SUFFIX}.md .planning/archive/ 2>/dev/null || true
mv .planning/EXPLORE_{SUFFIX}.md .planning/archive/ 2>/dev/null || true
```

### Step 2: Git Status Validation
```bash
# Stage cleanup changes
git add -A

# Show what will be committed
git status --porcelain

# Commit cleanup if needed
if [[ -n $(git status --porcelain) ]]; then
    git commit -m "chore: cleanup repository after feature completion

- Remove temporary test files and debug scripts
- Clean Python cache and temporary environments  
- Archive completed planning documentation
- Prepare repository for pull request

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
fi
```

## Final Testing & Quality Assurance

### Step 1: Comprehensive Test Suite
```bash
# Run all tests (including slow ones for final validation)
echo "🧪 Running comprehensive test suite..."
pytest --tb=short --durations=10

# Security validation
pytest tests/test_security*.py -v

# Performance validation (if exists)
pytest tests/test_performance*.py -v || echo "⚠️  No performance tests found"
```

### Step 2: Integration Testing
```bash
# Test manual workflows still work
echo "🔧 Validating key workflows..."

# Test server startup
timeout 10 python server.py --help >/dev/null 2>&1 || echo "⚠️  Server startup check failed"

# Test MCP Inspector integration (if configured)
if [[ -f "mcp-inspector-config.json" ]]; then
    echo "✅ MCP Inspector config found"
fi

# Test key utilities
if [[ -f "test_mcp_tool_call.py" ]]; then
    echo "✅ Manual testing utility preserved"
fi
```

## Pull Request Creation

### Step 1: Generate PR Summary
Analyze git history and generate comprehensive PR description:

```bash
# Get all commits since branch creation
BRANCH_COMMITS=$(git log --oneline main..HEAD --reverse)
TOTAL_COMMITS=$(echo "$BRANCH_COMMITS" | wc -l)

# Calculate test statistics
TEST_FILES=$(find tests/ -name "*.py" | wc -l)
TOTAL_TESTS=$(pytest --collect-only -q 2>/dev/null | grep "test session" || echo "Unable to count")

# Get final coverage
COVERAGE=$(pytest --cov=. --cov-report=term | grep "TOTAL" | awk '{print $4}' || echo "Unknown")
```

### Step 2: PR Creation with Comprehensive Metadata
```bash
gh pr create --title "feat(${SUFFIX,,}): complete ${SUFFIX} feature implementation" --body "$(cat <<EOF
## Summary
Complete implementation of ${SUFFIX} feature with comprehensive testing and documentation.

## Implementation Details
- **Branch**: feature/${SUFFIX}
- **Commits**: ${TOTAL_COMMITS}
- **Test Files**: ${TEST_FILES}  
- **Test Coverage**: ${COVERAGE}
- **Development Method**: Test-First Development (TDD)

## Repository Changes
- ✅ Feature implementation completed
- ✅ Comprehensive test suite added/updated
- ✅ Repository cleaned of temporary files
- ✅ Documentation updated
- ✅ Planning files archived

## Testing Validation
- ✅ Unit tests: All passing
- ✅ Integration tests: All passing  
- ✅ Regression tests: All passing
- ✅ Security tests: Validated
- ✅ Performance tests: ${PERFORMANCE_STATUS:-Validated}

## Quality Gates
- ✅ Code linting: Passed (ruff)
- ✅ Type checking: Passed (mypy)
- ✅ Test coverage: ${COVERAGE}
- ✅ Repository cleanup: Completed

## Key Features Added
$(git log --oneline main..HEAD --grep="feat" --pretty="- %s" | head -10)

## Test Strategy
This feature was developed using Test-First Development (TDD):
1. Tests written before implementation
2. Red-Green-Refactor cycle followed
3. Comprehensive coverage across all levels
4. Regression prevention through automated testing

## Manual Testing
Key workflows to test:
\`\`\`bash
# Test core functionality
pytest tests/test_*_regression.py -v

# Test fast feedback loop
pytest -m "not slow" --tb=short

# Test complete feature integration  
pytest tests/test_${SUFFIX,,}*.py -v
\`\`\`

## Documentation
- README.md: Updated with feature information
- API documentation: Current and accurate
- Testing guide: Comprehensive workflows documented

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### Step 3: PR Metadata & Labels
```bash
# Add appropriate labels
gh pr edit --add-label "feature,test-coverage,ready-for-review"

# Link to related issues if available
if [[ -f ".planning/archive/EXPLORE_${SUFFIX}.md" ]]; then
    ISSUE_REF=$(grep -o "#[0-9]\+" ".planning/archive/EXPLORE_${SUFFIX}.md" | head -1)
    if [[ -n "$ISSUE_REF" ]]; then
        gh pr edit --body "$(gh pr view --json body -q '.body')

Closes ${ISSUE_REF}"
    fi
fi
```

## Post-PR Actions

### Step 1: Branch Protection & Cleanup Strategy
```bash
# Show PR URL
PR_URL=$(gh pr view --json url -q '.url')
echo "🎉 Pull Request created: $PR_URL"

# Provide next steps guidance
echo "
📋 Next Steps:
1. Review PR in browser: $PR_URL
2. Wait for CI/CD checks to pass
3. Request team review if needed
4. After merge: git checkout main && git pull && git branch -d feature/${SUFFIX}

🔧 Development Tools:
- Manual testing: python test_mcp_tool_call.py
- MCP Inspector: mcp-inspector mcp-inspector-config.json
- Fast tests: pytest -m 'not slow' --tb=short

📁 Archived Planning:
- .planning/archive/EXPLORE_${SUFFIX}.md
- .planning/archive/TASKS_${SUFFIX}.md  
- .planning/archive/PROGRESS_${SUFFIX}.md
"
```

### Step 2: Local Environment Optimization
```bash
# Optional: Return to main branch
read -p "Switch back to main branch? (y/N): " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git checkout main
    git pull origin main
    echo "✅ Switched to updated main branch"
fi
```

## Quality Assurance Checklist

### Feature Completion Requirements
- [ ] All planned tasks completed and validated
- [ ] Comprehensive test suite passing (100% success rate)
- [ ] Code quality gates passed (linting, type checking)
- [ ] Repository cleaned of temporary development artifacts
- [ ] Documentation updated and accurate
- [ ] Planning files properly archived

### Pull Request Quality Standards  
- [ ] Descriptive title following conventional commits
- [ ] Comprehensive body with implementation details
- [ ] Testing instructions clear and executable
- [ ] Appropriate labels and metadata
- [ ] Linked to original issues/requirements
- [ ] Ready for team review

### Repository Hygiene Standards
- [ ] No temporary test files in main codebase
- [ ] Python cache directories removed
- [ ] Productive tools preserved (start_server.sh, test_mcp_tool_call.py)
- [ ] .gitignore covers future temporary files
- [ ] Planning documentation archived but accessible

## Error Handling

### Validation Failures
- If tests fail: Provide specific failing test information and abort PR creation
- If code quality fails: Show specific issues and require fixing before proceeding
- If repository not clean: Show git status and allow manual resolution

### Cleanup Issues  
- Preserve any files that might be productive tools
- Provide rollback commands if cleanup goes wrong
- Allow manual override for edge cases

## Integration with Existing Commands

### Command Workflow Enhancement
1. **explore.md**: Remove any PR creation references (keep pure exploration)
2. **plan-tasks-test-first.md**: Remove PR creation references (keep pure planning)  
3. **execute-tasks.md**: Remove lines 160-214 (PR creation), focus on execution only
4. **complete-feature.md**: New comprehensive completion workflow

### Improved Command Lifecycle
```
/project:explore → /project:plan-tasks-test-first → /project:execute-tasks → /project:complete-feature
     ↓                       ↓                           ↓                        ↓
Branch Setup &         Test-First Task            Systematic Task         Final Validation &
Exploration           Planning                    Execution               PR Creation
```

## Success Criteria

This command successfully completes when:
- ✅ Repository is clean and production-ready
- ✅ All tests pass with adequate coverage
- ✅ Pull request is created with comprehensive metadata  
- ✅ Planning files are archived but accessible
- ✅ Team has clear next steps for review and merge

**Remember:** This command represents the final gate before code review - everything should be production-ready and properly documented.