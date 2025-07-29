# Explore Feature from Initial File or GitHub Issue

## Usage
```bash
/project:explore path/to/INITIAL_SUFFIX.md
/project:explore issue-123
```

## Input Processing

### Step 1: Input Analysis
Analyze the provided argument: $ARGUMENTS

**If it's a file path (.md):**
- Read the specified INITIAL file
- Extract SUFFIX from filename (e.g., `INITIAL_CRAWLER.md` → `CRAWLER`)
- Use SUFFIX as feature branch name

**If it's an issue reference (issue-123 or just 123):**
- Use `gh issue view <number>` to fetch issue details
- Analyze issue title and content to generate appropriate SUFFIX
- Create meaningful branch name from issue content

### Step 2: Branch Management
Check if feature branch exists:
```bash
git branch --list | grep -q "feature/{SUFFIX}"
```

**If branch doesn't exist:**
- Create and checkout: `git checkout -b feature/{SUFFIX}`
- Inform user about new branch creation

**If branch exists:**
- Switch to existing branch: `git checkout feature/{SUFFIX}`
- Inform user about branch switch

## Research Process - ULTRATHINK Phase

### 1. **Context Discovery**
- **Feature Requirements**: Deep analysis of initial file or issue content
- **Technical Dependencies**: Identify all required libraries, frameworks, tools
- **Architecture Patterns**: Search codebase for similar implementations
- **Integration Points**: Find where feature connects to existing system
- **Data Flow**: Understand input/output requirements and transformations

### 2. **Documentation Research**
- **Primary Documentation**: Load official docs for all identified technologies
- **API References**: Fetch specific API documentation sections
- **Examples Repository**: Search for implementation examples
- **Best Practices**: Research recommended patterns and approaches
- **Common Pitfalls**: Document known issues and solutions

### 3. **Codebase Analysis**
- **Similar Features**: Search for existing patterns to follow
- **File Structure**: Analyze current project organization
- **Test Patterns**: Identify testing approaches and conventions
- **Configuration**: Find existing config patterns and requirements
- **Dependencies**: Map out existing library usage and versions

### 4. **External Research**
- **GitHub Examples**: Search for similar implementations
- **Stack Overflow**: Find common issues and solutions
- **Blog Posts**: Technical articles about implementation approaches
- **Library Comparisons**: Alternative approaches and trade-offs
- **Performance Considerations**: Benchmarks and optimization patterns

### 5. **Technical Constraints Analysis**
- **Library Compatibility**: Version requirements and conflicts
- **Performance Requirements**: Expected load and response times
- **Security Considerations**: Authentication, validation, sanitization
- **Error Handling**: Exception patterns and recovery strategies
- **Scalability**: Future growth considerations

## Exploration Output Generation

### Step 1: Create Planning Directory
```bash
mkdir -p .planning
```

### Step 2: Generate Exploration Document
Save comprehensive exploration as: `.planning/EXPLORE_{SUFFIX}.md`

### Exploration Document Structure:
```markdown
# Feature Exploration: {Feature Name}

## Source Information
- **Input**: {file_path or issue_number}
- **Branch**: feature/{SUFFIX}
- **Generated**: {timestamp}

## Feature Overview
{High-level description and objectives}

## Technical Requirements
{All identified dependencies, tools, frameworks}

## Architecture Context
{How feature fits into existing system}

## Implementation Knowledge Base
{All research findings, documentation links, examples}

## Code Patterns & Examples
{Relevant code snippets from codebase and external sources}

## Configuration Requirements
{Environment setup, config files, dependencies}

## Testing Considerations
{Test patterns, validation approaches, edge cases}

## Integration Points
{How feature connects to existing components}

## Technical Constraints
{Performance, security, compatibility considerations}

## Success Criteria
{Clear completion and acceptance criteria}

## High-Level Approach
{General implementation strategy - NO detailed steps}

## Validation Gates
{Executable validation commands for quality assurance}
```

## Quality Assurance

### Exploration Completeness Checklist
- [ ] All technical dependencies identified and documented
- [ ] Relevant documentation URLs collected with specific sections
- [ ] Code examples from codebase and external sources included
- [ ] Integration points clearly mapped
- [ ] Configuration requirements understood
- [ ] Testing patterns identified
- [ ] Performance and security considerations documented
- [ ] Error handling strategies researched
- [ ] Alternative approaches evaluated

### Knowledge Transfer Validation
- [ ] Sufficient context for multiple implementation approaches
- [ ] Clear understanding of feature requirements
- [ ] Technical constraints well-documented
- [ ] Integration requirements understood
- [ ] Validation approach defined

## Future Planning Methods Support

This exploration document provides the foundation for various implementation approaches:

**Test-First Development:**
- Testing patterns and examples documented
- Validation gates defined
- Success criteria established

**Code-First Development:**
- Implementation examples and patterns provided
- Architecture context established
- Integration points mapped

**Documentation-First Development:**
- API requirements and interfaces defined
- User interaction patterns documented
- System boundaries clarified

**Iterative Development:**
- Feature broken into logical components
- Dependencies clearly identified
- Validation checkpoints established

## Confidence Assessment
Rate the exploration completeness on a scale of 1-10 for supporting successful implementation regardless of chosen development methodology.

**Remember:** The goal is to create a comprehensive knowledge base that enables flexible implementation planning while avoiding premature commitment to specific implementation steps.
