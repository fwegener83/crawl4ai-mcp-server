# Prepare Pull Request

## Usage
```bash
/prepare-pr
```

## Overview
Runs local tests, validates feature readiness, and creates a pull request for the current feature branch.
No cleanup - keeps development environment intact for potential changes.

## Input Processing

### Step 1: Branch Validation
```bash
# Get current branch and validate it's a feature branch
CURRENT_BRANCH=$(git branch --show-current)
if [[ ! "$CURRENT_BRANCH" =~ ^feature/ ]]; then
    echo "❌ Error: Not on a feature branch. Current: $CURRENT_BRANCH"
    echo "Expected: feature/some-name"
    exit 1
fi

FEATURE_NAME=${CURRENT_BRANCH#feature/}
echo "🔄 Preparing PR for feature: $FEATURE_NAME"
```

### Step 2: Working Directory Check
```bash
# Check git status
GIT_STATUS=$(git status --porcelain)
if [[ -n "$GIT_STATUS" ]]; then
    echo "⚠️  Working directory has uncommitted changes:"
    git status --short
    read -p "Continue anyway? (y/N): " -n 1 -r
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "\n❌ Aborted. Commit or stash changes first."
        exit 1
    fi
    echo
fi
```

## Test Validation Phase

### Step 1: Core Functionality Tests
```bash
echo "🧪 Running core functionality tests..."
if ! pytest tests/test_*_regression.py -v --tb=short 2>/dev/null; then
    echo "❌ Regression tests failed - fix before creating PR"
    exit 1
fi
echo "✅ Regression tests passed"
```

### Step 2: Fast Test Suite
```bash
echo "🧪 Running fast test suite..."
if ! pytest -m "not slow" --timeout=120 --tb=short; then
    echo "❌ Fast tests failed - fix before creating PR"
    exit 1
fi
echo "✅ Fast tests passed"
```

### Step 3: Code Quality Checks
```bash
echo "🔍 Running code quality checks..."

# Linting
echo "  - Running ruff..."
if ! ruff check --fix; then
    echo "❌ Linting failed - fix issues before creating PR"
    exit 1
fi

# Type checking
echo "  - Running mypy..."
if ! mypy . --ignore-missing-imports; then
    echo "❌ Type checking failed - fix issues before creating PR"
    exit 1
fi

echo "✅ Code quality checks passed"
```

### Step 4: Coverage Check
```bash
echo "🧪 Checking test coverage..."
COVERAGE_OUTPUT=$(pytest --cov=. --cov-report=term-missing --tb=no -q 2>/dev/null)
COVERAGE=$(echo "$COVERAGE_OUTPUT" | grep "TOTAL" | awk '{print $4}' | sed 's/%//' || echo "0")

if [[ -n "$COVERAGE" && "$COVERAGE" -gt 0 ]]; then
    echo "✅ Test coverage: ${COVERAGE}%"
    if [[ "$COVERAGE" -lt 80 ]]; then
        echo "⚠️  Coverage below 80% - consider adding more tests"
    fi
else
    echo "⚠️  Could not determine coverage"
fi
```

## Git History Analysis

### Step 1: Collect Branch Information
```bash
# Get commits since branching from main
BRANCH_COMMITS=$(git log --oneline main..HEAD --reverse)
TOTAL_COMMITS=$(echo "$BRANCH_COMMITS" | wc -l | tr -d ' ')

# Get changed files
CHANGED_FILES=$(git diff --name-only main..HEAD | wc -l | tr -d ' ')

# Count test files
TEST_FILES=$(find tests/ -name "*.py" 2>/dev/null | wc -l | tr -d ' ')

echo "📊 Branch statistics:"
echo "  - Commits: $TOTAL_COMMITS"
echo "  - Changed files: $CHANGED_FILES"
echo "  - Test files: $TEST_FILES"
```

## Pull Request Creation

### Step 1: Generate PR Title and Description
```bash
# Create PR title
PR_TITLE="feat(${FEATURE_NAME}): implement ${FEATURE_NAME} feature"

# Generate comprehensive PR body
PR_BODY="## Summary
Complete implementation of ${FEATURE_NAME} feature with comprehensive testing and validation.

## Implementation Details
- **Branch**: ${CURRENT_BRANCH}
- **Commits**: ${TOTAL_COMMITS}
- **Changed Files**: ${CHANGED_FILES}
- **Test Files**: ${TEST_FILES}
- **Test Coverage**: ${COVERAGE:-Unknown}%

## Testing Validation
- ✅ Regression tests: All passing
- ✅ Fast test suite: All passing
- ✅ Code quality: Passed (ruff + mypy)
- ✅ Test coverage: ${COVERAGE:-Unknown}%

## Key Changes
$(git log --oneline main..HEAD --pretty="- %s" | head -8)

## Manual Testing
Key workflows to validate:
\`\`\`bash
# Test core functionality
pytest tests/test_*_regression.py -v

# Test fast feedback loop
pytest -m \"not slow\" --tb=short

# Test specific feature
pytest tests/test_${FEATURE_NAME}*.py -v 2>/dev/null || pytest tests/ -k \"${FEATURE_NAME}\" -v
\`\`\`

## Quality Gates
- ✅ All automated tests passing
- ✅ Code linting clean
- ✅ Type checking clean
- ✅ Ready for code review

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Step 2: Create Pull Request
```bash
echo "🚀 Creating pull request..."

# Create PR
if gh pr create --title "$PR_TITLE" --body "$PR_BODY"; then
    PR_URL=$(gh pr view --json url -q '.url')
    echo "✅ Pull request created successfully!"
    echo "🔗 PR URL: $PR_URL"
else
    echo "❌ Failed to create pull request"
    exit 1
fi
```

### Step 3: Add Labels and Metadata
```bash
echo "🏷️  Adding labels and metadata..."

# Add labels
gh pr edit --add-label "feature,test-coverage,ready-for-review" 2>/dev/null || echo "⚠️  Could not add labels (optional)"

# Check for planning files that might reference issues
PLANNING_FILES=(.planning/PROGRESS*.md .planning/TASKS*.md .planning/EXPLORE*.md)
for file in "${PLANNING_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        ISSUE_REF=$(grep -o "#[0-9]\+" "$file" 2>/dev/null | head -1)
        if [[ -n "$ISSUE_REF" ]]; then
            echo "🔗 Found issue reference: $ISSUE_REF"
            gh pr edit --body "$PR_BODY

Closes $ISSUE_REF" 2>/dev/null || echo "⚠️  Could not link issue (optional)"
            break
        fi
    fi
done
```

## Success Summary

### Step 1: Next Steps Guidance
```bash
echo "
🎉 Pull Request Ready!

📋 Next Steps:
1. Review PR in browser: $PR_URL
2. Wait for CI/CD checks to complete
3. Request team review if needed
4. Address any review feedback
5. After approval: merge and run /cleanup-project

🔧 Development continues:
- Keep working on this branch if changes needed
- All dev files and environment preserved
- Run tests anytime: pytest -m 'not slow' --tb=short

💡 Remember: No cleanup done yet - your workspace stays intact for any PR feedback!"
```

## Error Handling

### Test Failures
```bash
# If any test phase fails, provide specific guidance
handle_test_failure() {
    echo "
❌ Tests failed - PR creation aborted

🔧 Debug steps:
1. Run failing tests with more detail: pytest -v --tb=long
2. Check specific test output: pytest tests/test_specific.py -v
3. Fix issues and run /prepare-pr again

💡 Tip: Use pytest -x to stop on first failure"
}
```

### Git Issues
```bash
# Handle common git issues
handle_git_issues() {
    echo "
❌ Git issue detected

🔧 Common fixes:
1. Not on feature branch: git checkout -b feature/your-feature-name
2. Uncommitted changes: git add . && git commit -m 'WIP: feature progress'
3. Branch not pushed: git push -u origin ${CURRENT_BRANCH}

💡 Then run /prepare-pr again"
}
```

## Success Criteria

This command succeeds when:
- ✅ All tests pass locally
- ✅ Code quality checks pass
- ✅ Pull request created with comprehensive metadata
- ✅ Team has clear testing instructions
- ✅ Development environment preserved for potential changes

**Key Difference:** This command does NOT clean up the repository - that's handled separately by `/cleanup-project` after successful merge.