---
description: Intelligent feature planning with optional parameters
argument-hint: <feature> [--complexity simple|moderate|complex] [--scope frontend|backend|fullstack] [--hyperthink] [--research] [--minimal]
---

# Intelligent Feature Planning

## STEP 1: IMMEDIATE SETUP ACTIONS

**FIRST: Parse the input and create feature branch immediately**

1. **Extract the base feature from arguments:**
   Remove all --flags from $ARGUMENTS to get the core feature input

2. **Generate SUFFIX for branch name:**
   - If input is a file path like `./planning/INITIAL_AUTH.md` → extract `AUTH`
   - If input is issue reference like `issue-123` or `123` → use the number or generate from issue title
   - If input is plain text like "Add user authentication" → convert to kebab-case like `user-authentication`

3. **Create and switch to feature branch NOW:**
   ```bash
   git checkout -b feature/{SUFFIX}
   ```
   Or if branch exists:
   ```bash
   git checkout feature/{SUFFIX}
   ```

4. **Create planning directory:**
   ```bash
   mkdir -p .planning
   ```

## STEP 2: PARAMETER ANALYSIS

Parse arguments from: $ARGUMENTS

**Core Feature Input (Required):**
- File path: `./planning/INITIAL_*.md`
- Issue reference: `issue-123` or `123`
- Plain text description: `"Feature description"`

**Optional Flags:**
- `--complexity [simple|moderate|complex]` - Override complexity assessment
- `--scope [frontend|backend|fullstack]` - Limit planning scope
- `--hyperthink` - Enable extended thinking mode
- `--research` - Enable Context7/web research
- `--minimal` - Generate minimal task-focused plan
- `--adr` - Force creation of Architecture Decision Records

**Default Behavior (no flags):**
- Auto-detect complexity from feature description
- Auto-detect scope from codebase analysis
- Smart decision on research needs
- Standard planning depth

## Implementation Logic

### Step 1: Argument Parsing
```bash
# Extract base feature
FEATURE=$(echo "$ARGUMENTS" | sed 's/--[^ ]*//g' | xargs)

# Check for flags
COMPLEXITY=""
SCOPE=""
ENABLE_HYPERTHINK=false
ENABLE_RESEARCH=false
MINIMAL_MODE=false
FORCE_ADR=false

if echo "$ARGUMENTS" | grep -q "--complexity simple"; then COMPLEXITY="simple"; fi
if echo "$ARGUMENTS" | grep -q "--complexity moderate"; then COMPLEXITY="moderate"; fi
if echo "$ARGUMENTS" | grep -q "--complexity complex"; then COMPLEXITY="complex"; fi

if echo "$ARGUMENTS" | grep -q "--scope frontend"; then SCOPE="frontend"; fi
if echo "$ARGUMENTS" | grep -q "--scope backend"; then SCOPE="backend"; fi
if echo "$ARGUMENTS" | grep -q "--scope fullstack"; then SCOPE="fullstack"; fi

if echo "$ARGUMENTS" | grep -q "--hyperthink"; then ENABLE_HYPERTHINK=true; fi
if echo "$ARGUMENTS" | grep -q "--research"; then ENABLE_RESEARCH=true; fi
if echo "$ARGUMENTS" | grep -q "--minimal"; then MINIMAL_MODE=true; fi
if echo "$ARGUMENTS" | grep -q "--adr"; then FORCE_ADR=true; fi
```

### Step 2: Intelligent Defaults

**Auto-Complexity Detection:**
```
If COMPLEXITY is empty:
- Analyze feature description for keywords
- "simple", "add", "fix", "update" → simple
- "integrate", "refactor", "new endpoint" → moderate  
- "architecture", "migration", "breaking change" → complex
```

**Auto-Scope Detection:**
```
If SCOPE is empty:
- Check feature description and existing codebase
- Only frontend files mentioned → frontend
- Only backend/API mentioned → backend
- Both or unclear → fullstack
```

**Research Decision:**
```
If not explicitly set:
- Enable research for complex features
- Enable research for unfamiliar technology mentions
- Skip research for routine CRUD operations
```

## Planning Modes

### Minimal Mode (--minimal)
```
Generate concise plan with:
- Core requirements only
- Essential tasks (3-5 max)
- Basic test requirements
- No deep analysis or research
- Perfect for routine features
```

### Standard Mode (default)
```
Balanced planning with:
- Requirement analysis
- Codebase pattern review
- Appropriate task breakdown
- Test strategy matching complexity
- Selective research if needed
```

### Deep Mode (--hyperthink --research)
```
Comprehensive analysis with:
- Extended thinking about the feature
- Context7 research for best practices
- Alternative approach considerations
- Architectural decision documentation
- Comprehensive test planning
```

## Scope-Specific Planning

### Frontend Scope (--scope frontend)
- Focus on React components and UI patterns
- State management considerations
- User experience and accessibility
- Frontend testing strategies
- Integration points with existing backend

### Backend Scope (--scope backend)  
- API endpoint design
- Data model changes
- Business logic implementation
- Backend testing and validation
- Database migrations if needed

### Fullstack Scope (--scope fullstack)
- End-to-end feature analysis
- Frontend + backend coordination
- Data contracts and API design
- Complete user journey planning
- Integration and E2E testing

## Planning Document Structure

The generated plan adapts its structure based on the selected options:

**Minimal Plan Structure:**
```markdown
# Feature Plan: {Feature Name}

## Requirements
{What needs to be done}

## Tasks
1. {Essential task 1}
2. {Essential task 2}
3. {Essential task 3}

## Success Criteria
- [ ] Core functionality works
- [ ] Tests pass
```

**Standard Plan Structure:**
```markdown
# Feature Plan: {Feature Name}

## Overview
- Complexity: {assessed/specified}
- Scope: {detected/specified}
- Planning Mode: Standard

## Requirements Analysis
{User requirements + existing pattern analysis}

## Implementation Tasks
{Scope-appropriate task breakdown}

## Quality Requirements
{Testing and validation appropriate to complexity}

## Success Criteria
{Clear, measurable completion criteria}
```

**Deep Plan Structure:**
```markdown
# Feature Plan: {Feature Name}

## Overview
- Complexity: {assessed/specified}
- Scope: {detected/specified}  
- Planning Mode: Deep Analysis

## Extended Analysis
{Hyperthink results if enabled}

## Research Findings
{Context7/web research if enabled}

## Architecture Decisions
{ADRs if complex or forced}

## Detailed Implementation Plan
{Comprehensive task breakdown}

## Quality & Testing Strategy
{Extensive testing requirements}

## Success Criteria
{Detailed completion validation}
```

## Command Benefits

**Flexibility**: Use simple or complex planning as needed
**Efficiency**: Skip unnecessary analysis for routine features  
**Consistency**: Always generates executable plans
**Smart Defaults**: Works well even without parameters
**Scope-Aware**: Focuses on relevant parts of the stack
**User Control**: Override AI decisions when you know better

## Examples

```bash
# Quick backend fix
/plan "Fix user login bug" --scope backend --minimal

# New feature with full analysis
/plan ./planning/INITIAL_PAYMENT.md --complexity complex --scope fullstack --hyperthink --research --adr

# Let AI decide everything
/plan issue-456

# Frontend-focused with research
/plan "Redesign user dashboard" --scope frontend --research
```

---

**This flexible planning approach adapts to your specific needs while maintaining intelligent defaults for efficiency.**

## EXECUTION INSTRUCTIONS

**AFTER completing the analysis above, you MUST immediately execute these steps:**

### Step 1: Branch Setup (if not done already)
```bash
# Check current branch
git branch --show-current

# Create or switch to feature branch using the SUFFIX you determined
git checkout -b feature/{SUFFIX}  # Or git checkout feature/{SUFFIX} if exists
```

### Step 2: Create Planning Directory
```bash
mkdir -p .planning
```

### Step 3: Generate and Save Plan Document
**Write the complete plan document to:** `.planning/PLAN_{SUFFIX}.md`

**Use the appropriate plan structure** (minimal/standard/deep) based on the selected mode.

**The plan document must include:**
- Clear feature description and requirements
- Task breakdown with specific, actionable steps
- Success criteria and quality gates
- Execution instruction at the end

### Step 4: Confirm Execution Path
**End your response with:**
```
Plan saved to .planning/PLAN_{SUFFIX}.md
Branch: feature/{SUFFIX}

To execute:
/execute .planning/PLAN_{SUFFIX}.md
```

**CRITICAL**: The planning document must be created and saved. This is not optional - it's the core output of this command.
