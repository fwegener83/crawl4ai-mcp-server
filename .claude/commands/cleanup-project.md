# Cleanup Project After Successful Merge

## Usage
```bash
/cleanup-project
```

## Overview
Cleans up the repository and development environment after a successful PR merge.
Removes temporary files, archives planning documents, and optimizes the workspace.

## Input Processing

### Step 1: Branch Status Validation
```bash
# Get current branch info
CURRENT_BRANCH=$(git branch --show-current)
FEATURE_NAME=""

# Check if we're on a feature branch or main
if [[ "$CURRENT_BRANCH" =~ ^feature/ ]]; then
    FEATURE_NAME=${CURRENT_BRANCH#feature/}
    echo "🧹 Cleaning up feature branch: $FEATURE_NAME"
    echo "⚠️  Note: You're still on the feature branch"
elif [[ "$CURRENT_BRANCH" == "main" || "$CURRENT_BRANCH" == "master" ]]; then
    echo "🧹 Cleaning up project (on main branch)"
    # Try to determine last feature from git history
    LAST_FEATURE=$(git branch -a --merged | grep "feature/" | tail -1 | sed 's/.*feature\///' | tr -d ' ')
    if [[ -n "$LAST_FEATURE" ]]; then
        FEATURE_NAME="$LAST_FEATURE"
        echo "💡 Detected last feature: $FEATURE_NAME"
    fi
else
    echo "🧹 Cleaning up project (current branch: $CURRENT_BRANCH)"
fi
```

### Step 2: Cleanup Confirmation
```bash
echo "
🗂️  This will clean up:
- Temporary test files and debug scripts
- Python cache directories
- Planning files (will be archived)
- Temporary environments
- Git cleanup commit

Continue? (y/N): "
read -n 1 -r
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "\n❌ Cleanup cancelled"
    exit 0
fi
echo
```

## Repository Cleanup Phase

### Step 1: Remove Temporary Development Files
```bash
echo "🗑️  Removing temporary development files..."

# Remove temporary test files (preserve productive ones)
find . -name "simple_test*.py" -delete 2>/dev/null || true
find . -name "test_*_temp.py" -delete 2>/dev/null || true
find . -name "*_debug.py" -delete 2>/dev/null || true
find . -name "*_scratch.py" -delete 2>/dev/null || true

echo "  ✅ Temporary test files removed"

# Clean Python cache
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

echo "  ✅ Python cache cleaned"

# Remove temporary environments
rm -rf test_env/ temp_env/ debug_env/ .env_temp/ 2>/dev/null || true

echo "  ✅ Temporary environments removed"

# Remove common development artifacts
rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/ 2>/dev/null || true

echo "  ✅ Test artifacts cleaned"
```

### Step 2: Archive Planning Files
```bash
echo "📁 Archiving planning documentation..."

# Create archive directory
mkdir -p .planning/archive/

# Archive planning files if they exist
ARCHIVED_COUNT=0

if [[ -n "$FEATURE_NAME" ]]; then
    # Feature-specific files
    for file in PROGRESS_${FEATURE_NAME}.md TASKS_${FEATURE_NAME}.md EXPLORE_${FEATURE_NAME}.md; do
        if [[ -f ".planning/$file" ]]; then
            mv ".planning/$file" ".planning/archive/"
            echo "  ✅ Archived $file"
            ((ARCHIVED_COUNT++))
        fi
    done
fi

# Generic planning files (if no feature-specific ones found)
if [[ $ARCHIVED_COUNT -eq 0 ]]; then
    for file in PROGRESS.md TASKS.md EXPLORE.md; do
        if [[ -f ".planning/$file" ]]; then
            TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
            mv ".planning/$file" ".planning/archive/${file%.md}_${TIMESTAMP}.md"
            echo "  ✅ Archived $file with timestamp"
            ((ARCHIVED_COUNT++))
        fi
    done
fi

if [[ $ARCHIVED_COUNT -eq 0 ]]; then
    echo "  💡 No planning files found to archive"
else
    echo "  ✅ Archived $ARCHIVED_COUNT planning files"
fi
```

### Step 3: Git Cleanup Commit
```bash
echo "📝 Creating cleanup commit..."

# Stage all cleanup changes
git add -A

# Check if there are changes to commit
if [[ -n $(git status --porcelain) ]]; then
    # Create cleanup commit
    CLEANUP_MESSAGE="chore: cleanup repository after feature completion"
    if [[ -n "$FEATURE_NAME" ]]; then
        CLEANUP_MESSAGE="chore: cleanup repository after $FEATURE_NAME feature merge"
    fi

    git commit -m "$CLEANUP_MESSAGE

- Remove temporary test files and debug scripts
- Clean Python cache and temporary environments
- Archive completed planning documentation
- Optimize repository for continued development

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

    echo "  ✅ Cleanup commit created"
else
    echo "  💡 No changes to commit"
fi
```

## Branch Management

### Step 1: Merged Branch Cleanup
```bash
echo "🌿 Managing branches..."

# Update main branch
if [[ "$CURRENT_BRANCH" != "main" && "$CURRENT_BRANCH" != "master" ]]; then
    echo "  🔄 Fetching latest changes..."
    git fetch origin main 2>/dev/null || git fetch origin master 2>/dev/null || true
fi

# Find merged feature branches
MERGED_BRANCHES=$(git branch --merged main 2>/dev/null | grep "feature/" | grep -v "\*" | tr -d ' ' || true)
if [[ -z "$MERGED_BRANCHES" ]]; then
    MERGED_BRANCHES=$(git branch --merged master 2>/dev/null | grep "feature/" | grep -v "\*" | tr -d ' ' || true)
fi

if [[ -n "$MERGED_BRANCHES" ]]; then
    echo "  🗑️  Found merged feature branches:"
    echo "$MERGED_BRANCHES" | sed 's/^/    - /'
    
    echo -n "  Delete merged feature branches? (y/N): "
    read -n 1 -r
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo
        echo "$MERGED_BRANCHES" | xargs -I {} git branch -d {}
        echo "    ✅ Merged branches deleted"
    else
        echo -e "\n    💡 Keeping merged branches"
    fi
else
    echo "  💡 No merged feature branches found"
fi
```

### Step 2: Remote Branch Cleanup
```bash
# Clean up remote tracking branches
echo "  🔄 Cleaning remote tracking branches..."
git remote prune origin 2>/dev/null || true
echo "    ✅ Remote tracking branches cleaned"
```

### Step 3: Main Branch Switch (Optional)
```bash
if [[ "$CURRENT_BRANCH" =~ ^feature/ ]]; then
    echo -n "  🔄 Switch to main branch? (y/N): "
    read -n 1 -r
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo
        git checkout main 2>/dev/null || git checkout master 2>/dev/null || echo "    ⚠️  Could not switch to main"
        git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || echo "    ⚠️  Could not pull latest"
        echo "    ✅ Switched to updated main branch"
        
        # Offer to delete the feature branch
        echo -n "    🗑️  Delete feature branch '$CURRENT_BRANCH'? (y/N): "
        read -n 1 -r
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo
            git branch -d "$CURRENT_BRANCH" 2>/dev/null && echo "      ✅ Feature branch deleted" || echo "      ⚠️  Could not delete feature branch (may have unmerged changes)"
        else
            echo
        fi
    else
        echo
        echo "    💡 Staying on current branch"
    fi
fi
```

## Environment Optimization

### Step 1: Dependencies Check
```bash
echo "🔧 Environment optimization..."

# Check for requirements updates (if file exists)
if [[ -f "requirements.txt" ]]; then
    echo "  💡 Consider updating dependencies:"
    echo "    pip list --outdated"
    echo "    pip install -U package_name"
fi

# Check for poetry updates (if using poetry)
if [[ -f "pyproject.toml" ]] && command -v poetry >/dev/null; then
    echo "  💡 Consider updating poetry dependencies:"
    echo "    poetry show --outdated"
    echo "    poetry update"
fi
```

### Step 2: Tool Preservation Check
```bash
echo "🛠️  Verifying preserved development tools..."

# Check that important tools are still present
PRESERVED_TOOLS=()
[[ -f "test_mcp_tool_call.py" ]] && PRESERVED_TOOLS+=("test_mcp_tool_call.py")
[[ -f "start_server.sh" ]] && PRESERVED_TOOLS+=("start_server.sh")
[[ -f "mcp-inspector-config.json" ]] && PRESERVED_TOOLS+=("mcp-inspector-config.json")

if [[ ${#PRESERVED_TOOLS[@]} -gt 0 ]]; then
    echo "  ✅ Development tools preserved:"
    printf '    - %s\n' "${PRESERVED_TOOLS[@]}"
else
    echo "  💡 No common development tools detected"
fi
```

## Success Summary

### Step 1: Cleanup Report
```bash
echo "
✨ Repository cleanup completed!

📊 Cleanup Summary:
  - ✅ Temporary files removed
  - ✅ Python cache cleaned
  - ✅ Planning files archived
  - ✅ Git cleanup committed
  - ✅ Branches managed
  - ✅ Environment optimized

📁 Archived Files:
  Location: .planning/archive/
  Access: ls .planning/archive/

🔧 Development Ready:
  - Clean workspace for next feature
  - All productive tools preserved
  - Git history maintained

🚀 Next Steps:
  1. Start new feature: git checkout -b feature/new-feature-name
  2. Plan new work: /project:explore
  3. Continue development cycle
"
```

### Step 2: Optional Git Status
```bash
# Show final git status
echo "📊 Final repository status:"
git status --short
echo
git log --oneline -5
```

## Error Handling

### File Permission Issues
```bash
handle_permission_error() {
    echo "⚠️  Permission error during cleanup
    
🔧 Try:
1. Check file permissions: ls -la
2. Run with appropriate permissions
3. Skip problematic files and continue"
}
```

### Git Issues
```bash
handle_git_error() {
    echo "⚠️  Git operation failed
    
🔧 Common solutions:
1. Fetch latest: git fetch --all
2. Check remote: git remote -v
3. Manual cleanup: git reset --hard HEAD"
}
```

## Success Criteria

This command succeeds when:
- ✅ Repository is clean of temporary development artifacts
- ✅ Planning documentation is properly archived
- ✅ Git history is clean with appropriate cleanup commit
- ✅ Development tools are preserved
- ✅ Workspace is optimized for next development cycle

**Key Focus:** Complete repository hygiene while preserving all productive development tools and maintaining clean git history.