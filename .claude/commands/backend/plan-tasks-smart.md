# Generate Smart Test-First Task Plan from Exploration Document

## Usage
```bash
/plan-tasks-smart .planning/EXPLORE_SUFFIX.md
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

### Step 2: Feature Complexity Assessment

**Analyze complexity indicators:**
- **Dependencies Count**: External libraries, APIs, services
- **Integration Points**: Number of system connections
- **Data Complexity**: Input/output transformations, validation
- **User Interface**: CLI, API endpoints, configuration
- **Risk Factors**: Security, performance, compatibility requirements

**Complexity Classification:**
```bash
# Small Feature (Score 1-3):
- Single function/class
- 1-2 files affected
- Minimal dependencies
- Clear, simple interface
→ Core Tests Only

# Medium Feature (Score 4-7):
- Multiple components
- 3-6 files affected
- Some integration required
- Moderate complexity
→ Core + Integration Tests

# Large Feature (Score 8-10):
- System-wide impact
- 7+ files affected
- Multiple integrations
- High complexity/risk
→ Full Test Suite
```

## Smart Test Strategy Selection

### Small Feature Strategy (Score 1-3)
**Philosophy**: Essential validation only
- **Core Tests**: Basic functionality + edge cases
- **Integration**: Only if external dependencies exist
- **Validation**: Simple pass/fail criteria

### Medium Feature Strategy (Score 4-7)
**Philosophy**: Balanced coverage
- **Core Tests**: Comprehensive unit testing
- **Integration**: Key integration points
- **End-to-End**: Main user workflows
- **Quality Gates**: Basic performance/security

### Large Feature Strategy (Score 8-10)
**Philosophy**: Comprehensive validation
- **Core Tests**: Full unit test coverage
- **Integration**: All integration points
- **System Tests**: Complete workflows
- **Advanced**: Performance, security, compatibility
- **Documentation**: Live examples and validation

## Task Generation by Complexity

### Small Feature Tasks (2-4 Tasks)
```markdown
### Phase 1: Core Validation
**Task 1.1: Essential Tests**
- Write tests for main functionality
- Test critical edge cases and errors
- Basic input/output validation

**Task 1.2: Core Implementation**
- Implement minimal code to pass tests
- Follow Red-Green-Refactor cycle
- Ensure all tests pass

### Phase 2: Integration (if needed)
**Task 2.1: Integration Test** (only if external dependencies)
- Test key integration points
- Validate external service interaction

**Task 2.2: Integration Implementation**
- Complete integration code
- Ensure integration tests pass
```

### Medium Feature Tasks (4-8 Tasks)
```markdown
### Phase 1: Core Foundation
**Task 1.1: Unit Test Suite**
- Comprehensive unit tests for all components
- Edge cases and error handling
- Mock external dependencies

**Task 1.2: Unit Implementation**
- Implement core logic to pass unit tests
- Clean, testable code structure

### Phase 2: Integration Layer
**Task 2.1: Integration Tests**
- Test component interactions
- Database/API integration points
- Configuration loading and validation

**Task 2.2: Integration Implementation**
- Connect components based on test requirements
- Complete integration layer

### Phase 3: End-to-End Validation
**Task 3.1: E2E Test Suite**
- Main user workflows
- Complete data flow validation
- Error handling scenarios

**Task 3.2: E2E Implementation**
- Complete system integration
- Final glue code and polishing

### Phase 4: Quality Assurance
**Task 4.1: Quality Gates**
- Performance baseline tests
- Basic security validation
- Code quality verification
```

### Large Feature Tasks (6-12 Tasks)
```markdown
### Phase 1: Test Foundation
**Task 1.1: Test Infrastructure**
- Set up comprehensive testing framework
- Test data and fixtures
- Continuous testing workflow

### Phase 2: Core Testing
**Task 2.1: Comprehensive Unit Tests**
- Full unit test coverage
- Complex edge cases and scenarios
- Mock strategies for all dependencies

**Task 2.2: Core Implementation**
- Implement all core logic
- High-quality, maintainable code

### Phase 3: Integration Testing
**Task 3.1: Integration Test Suite**
- All integration points tested
- Database and external service integration
- Configuration and environment testing

**Task 3.2: Integration Implementation**
- Complete integration layer
- Robust error handling

### Phase 4: System Testing
**Task 4.1: System Test Development**
- End-to-end workflow testing
- Performance and load testing
- Security validation tests

**Task 4.2: System Implementation**
- Final system integration
- Performance optimization
- Security implementation

### Phase 5: Advanced Validation
**Task 5.1: Advanced Testing**
- Compatibility testing
- Stress testing
- Documentation validation

**Task 5.2: Production Readiness**
- Final optimizations
- Monitoring and logging
- Deployment preparation
```

## Complexity Scoring Algorithm

### Step 1: Dependency Analysis
```bash
# Count indicators from exploration document
DEPENDENCY_SCORE=0
grep -i "import\|library\|dependency\|api\|service" EXPLORE_FILE | wc -l
# 1-2 deps = +1, 3-5 deps = +2, 6+ deps = +3
```

### Step 2: Integration Complexity
```bash
# Analyze integration points
INTEGRATION_SCORE=0
grep -i "integration\|connect\|interface\|endpoint\|database" EXPLORE_FILE | wc -l
# 1-2 integrations = +1, 3-4 = +2, 5+ = +3
```

### Step 3: Implementation Scope
```bash
# Estimate implementation scope
SCOPE_SCORE=0
grep -i "file\|class\|function\|component\|module" EXPLORE_FILE | wc -l
# Small scope = +1, Medium = +2, Large = +3
```

### Step 4: Risk Assessment
```bash
# Check for risk indicators
RISK_SCORE=0
grep -i "security\|performance\|compatibility\|critical\|production" EXPLORE_FILE | wc -l
# Low risk = +0, Medium = +1, High = +2
```

## Task Document Generation

### Step 1: Calculate Total Score
```bash
TOTAL_SCORE=$((DEPENDENCY_SCORE + INTEGRATION_SCORE + SCOPE_SCORE + RISK_SCORE))

if [[ $TOTAL_SCORE -le 3 ]]; then
    COMPLEXITY="Small"
    STRATEGY="Essential validation only"
elif [[ $TOTAL_SCORE -le 7 ]]; then
    COMPLEXITY="Medium" 
    STRATEGY="Balanced coverage"
else
    COMPLEXITY="Large"
    STRATEGY="Comprehensive validation"
fi
```

### Step 2: Generate Appropriate Task Plan
Save task plan as: `.planning/TASKS_{SUFFIX}.md`

### Task Document Structure:
```markdown
# Smart Test-First Plan: {Feature Name}

## Complexity Assessment
- **Score**: {TOTAL_SCORE}/10
- **Classification**: {COMPLEXITY}
- **Strategy**: {STRATEGY}

## Scoring Breakdown
- Dependencies: {DEPENDENCY_SCORE}/3
- Integration: {INTEGRATION_SCORE}/3  
- Scope: {SCOPE_SCORE}/3
- Risk: {RISK_SCORE}/2

## Test-First Approach
✅ Tests written before implementation
✅ Red-Green-Refactor methodology
✅ Appropriate test coverage for complexity
✅ Quality gates matched to feature importance

## Task Breakdown
{Selected task structure based on complexity}

## Validation Gates
{Complexity-appropriate validation commands}

## Success Criteria
{Realistic completion criteria for feature size}
```

## Quality Assurance

### Smart Planning Validation
- [ ] Complexity assessment reflects actual feature scope
- [ ] Test strategy matches implementation requirements
- [ ] Task count is proportional to feature complexity
- [ ] Validation gates are executable and relevant
- [ ] Success criteria are achievable and measurable

### Test-First Integrity
- [ ] All implementation follows test creation
- [ ] Red-Green-Refactor cycle maintained
- [ ] Test coverage appropriate for complexity level
- [ ] Quality gates prevent over-engineering
- [ ] Essential functionality always covered

## Implementation Notes

**Smart Benefits:**
- Prevents test over-engineering for simple features
- Ensures adequate coverage for complex features
- Maintains test-first discipline
- Adapts effort to actual requirements
- Reduces development overhead

**Complexity Indicators Guide:**
- **Small**: Single utility function, simple config change
- **Medium**: New API endpoint, database integration
- **Large**: New service, major architecture change

## Success Criteria

Rate the smart planning on:
- **Accuracy**: Complexity assessment matches reality (8+/10)
- **Efficiency**: Task count appropriate for scope (8+/10)  
- **Quality**: Test coverage adequate but not excessive (8+/10)
- **Maintainability**: Sustainable long-term approach (8+/10)

**Remember:** Smart test planning maintains test-first benefits while preventing test bloat through intelligent complexity assessment.
