# Full-Stack Feature Planning with Deep Context Analysis

## Usage
```bash
/plan path/to/INITIAL_FEATURE_SUFFIX.md
/plan issue-123
```

## Input Processing

### Step 1: Input Analysis
Analyze the provided argument: $ARGUMENTS

**If it's a file path (.md):**
- Read the specified INITIAL file  
- Extract SUFFIX from filename (e.g., `INITIAL_FEATURE_AUTH.md` → `AUTH`)
- Use SUFFIX as feature branch name: `feature/{SUFFIX}`

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

## Phase 1: DEEP EXPLORATION with HYPERTHINKING

### Step 1: Activate Deep Analysis Mode
**HYPERTHINK about this full-stack feature using extended reasoning:**

Think deeply about the complete feature implementation across the entire stack. Consider backend API design, data modeling, business logic, frontend component architecture, user experience patterns, data flow between layers, authentication requirements, error handling strategies, performance implications, security considerations, testing approaches, deployment considerations, and integration challenges. Analyze multiple implementation approaches, potential edge cases, scalability requirements, and maintenance implications.

### Step 2: Comprehensive Context Gathering

**Context7 MCP Research (PRIORITY 1):**
Use Context7 MCP to gather comprehensive implementation patterns:

```bash
# Full-Stack Architecture Patterns
# Backend API design patterns and best practices
# Frontend component architecture approaches
# Database schema design and data modeling
# Authentication and authorization patterns
# Testing strategies across the full stack
# Performance optimization techniques
# Security implementation patterns
# Error handling and logging approaches
# Deployment and DevOps best practices
```

**Web Research (PRIORITY 2):**
If Context7 MCP is unavailable, use web search for:
- Full-stack development best practices for the identified tech stack
- API design patterns and RESTful/GraphQL conventions
- Frontend framework patterns and component design
- Database design and ORM best practices
- Authentication and security implementation guides
- Testing strategies for full-stack applications
- Performance optimization across frontend and backend
- DevOps and deployment patterns

**Monorepo Analysis (PRIORITY 3):**
Analyze the current monorepo structure and existing patterns:
```bash
# Backend structure analysis
find . -name "*.py" -o -name "*.js" -o -name "*.ts" | grep -E "(server|api|backend)" | head -20

# Frontend structure analysis  
find . -name "*.tsx" -o -name "*.jsx" -o -name "*.vue" | head -20

# Database and model analysis
find . -name "*.py" -exec grep -l "class.*Model\|@dataclass\|schema" {} \; | head -10

# API endpoint discovery
grep -r "route\|endpoint\|@app\|@router" . --include="*.py" --include="*.js" --include="*.ts" | head -15

# Frontend API integration patterns
grep -r "fetch\|axios\|api" . --include="*.tsx" --include="*.jsx" --include="*.js" --include="*.ts" | head -15

# Testing patterns across stack
find . -name "*test*" -type f | head -15

# Configuration and environment setup
find . -name "*.json" -o -name "*.yaml" -o -name "*.toml" | grep -E "(config|env)" | head -10
```

### Step 3: Full-Stack Feature Analysis

**For each aspect of the feature:**

1. **Backend Requirements Analysis:**
   - API endpoints needed and their contracts
   - Data models and database schema changes
   - Business logic and validation requirements
   - Authentication and authorization needs
   - External service integrations
   - Performance and scalability considerations

2. **Frontend Requirements Analysis:**
   - User interface components and interactions
   - State management and data flow requirements
   - User experience and accessibility needs
   - Responsive design considerations
   - Performance and bundle size impact
   - Browser compatibility requirements

3. **Integration Analysis:**
   - Data contracts between frontend and backend
   - Real-time communication requirements
   - Error handling across the stack
   - Authentication flow end-to-end
   - API versioning and backward compatibility
   - Development and deployment coordination

4. **Quality and Testing Strategy:**
   - Unit testing requirements for both stacks
   - Integration testing approach
   - End-to-end testing scenarios
   - Performance testing requirements
   - Security testing considerations
   - Accessibility testing needs

## Phase 2: INTELLIGENT COMPLEXITY ASSESSMENT

### Step 1: Multi-Dimensional Complexity Analysis

**Backend Complexity Score (0-5):**
- Simple (1): Single endpoint, basic CRUD operations
- Moderate (2-3): Multiple endpoints, business logic, database operations
- Complex (4-5): Complex business logic, multiple integrations, advanced features

**Frontend Complexity Score (0-5):**
- Simple (1): Basic components, minimal interactions
- Moderate (2-3): Interactive components, forms, state management
- Complex (4-5): Complex UI patterns, advanced interactions, performance optimization

**Integration Complexity Score (0-5):**
- Simple (1): Basic API calls, simple data flow
- Moderate (2-3): Authentication, error handling, data transformation
- Complex (4-5): Real-time features, complex data flow, advanced integration patterns

**Total Complexity Score: {sum}/15**

### Step 2: Adaptive Test Strategy Selection

**Based on total complexity score, determine comprehensive test approach:**

**Score 1-5 (Simple):** Essential Full-Stack Testing
- **Backend Tests**: Core API functionality, basic data validation
- **Frontend Tests**: Component rendering, basic user interactions
- **Integration Tests**: Happy path API integration, basic E2E
- **Coverage Target**: 85%

**Score 6-10 (Moderate):** Balanced Full-Stack Strategy  
- **Backend Tests**: Comprehensive API coverage, business logic validation
- **Frontend Tests**: Component interactions, state management, user workflows
- **Integration Tests**: API contract validation, error scenarios, authentication flows
- **E2E Tests**: Main user journeys, cross-browser testing
- **Coverage Target**: 90%

**Score 11-15 (Complex):** Comprehensive Full-Stack Quality Assurance
- **Backend Tests**: Complete coverage with edge cases, performance testing
- **Frontend Tests**: Advanced component testing, accessibility validation
- **Integration Tests**: Full API contract testing, complex data flow validation
- **E2E Tests**: All user journeys, error flows, performance testing
- **Security Tests**: Authentication, authorization, data validation
- **Performance Tests**: Backend API performance, frontend bundle optimization
- **Coverage Target**: 95%

### Step 3: Full-Stack Task Generation

**Generate phase-based tasks appropriate to complexity:**

## Planning Document Generation

### Create Comprehensive Full-Stack Plan
Save complete plan as: `.planning/PLAN_{SUFFIX}.md`

### Full-Stack Plan Document Structure:
```markdown
# Full-Stack Feature Plan: {Feature Name}

## Planning Overview
- **Input**: {file_path or issue_number}
- **Branch**: feature/{SUFFIX}
- **Complexity Score**: {total_score}/15
- **Test Strategy**: {selected_strategy}
- **Generated**: {timestamp}

## Phase 1: Deep Exploration Results

### HYPERTHINK Analysis Summary
{Key insights from extended reasoning about the full-stack feature}

### Context Research Findings
{Comprehensive research results from Context7 MCP / Web Search / Monorepo Analysis}

#### Full-Stack Architecture Patterns
{Discovered patterns for backend APIs, frontend components, and integration}

#### Backend Implementation Insights
{API design patterns, data modeling approaches, business logic patterns}

#### Frontend Implementation Insights  
{Component architectures, state management patterns, user experience approaches}

#### Integration Patterns
{Data contracts, authentication flows, real-time communication, error handling}

#### Testing Strategies Researched
{Testing approaches across the stack, tools, coverage strategies}

#### Performance & Security Insights
{Optimization techniques, security requirements, scalability considerations}

### Full-Stack Feature Technical Analysis

#### Backend Requirements
**API Endpoints Needed:**
- {Endpoint} → **Purpose**: {description} → **Data**: {request_response_format}

**Data Models:**
- {Model} → **Fields**: {schema} → **Relationships**: {connections}

**Business Logic:**
- {Logic} → **Validation**: {rules} → **Processing**: {workflow}

#### Frontend Requirements  
**Components Needed:**
- {Component} → **Purpose**: {description} → **Props**: {interface} → **State**: {requirements}

**User Experience:**
- {Journey} → **Interactions**: {user_actions} → **Feedback**: {responses} → **Accessibility**: {a11y_requirements}

#### Integration Requirements
**Data Contracts:**
- {Contract} → **Format**: {structure} → **Validation**: {rules} → **Error Handling**: {approach}

**Authentication Flow:**
- {Flow} → **Frontend**: {auth_UI} → **Backend**: {auth_API} → **Security**: {measures}

### Full-Stack Architecture Plan
{Complete architecture spanning backend APIs, frontend components, and integration layer}

### Quality Requirements
{Testing requirements, performance benchmarks, security standards, accessibility compliance}

## Phase 2: Intelligent Planning Results

### Complexity Assessment Breakdown
- **Backend Complexity**: {score}/5 - {reasoning}
- **Frontend Complexity**: {score}/5 - {reasoning}  
- **Integration Complexity**: {score}/5 - {reasoning}
- **Total Score**: {total}/15 - **{classification}**

### Selected Test Strategy: {strategy_name}
{Detailed explanation of why this strategy was chosen for this full-stack feature}

**Testing Approach:**
- **Backend Testing**: {specific_backend_test_requirements}
- **Frontend Testing**: {specific_frontend_test_requirements}
- **Integration Testing**: {specific_integration_requirements}
- **E2E Testing**: {specific_e2e_requirements}
- **Additional Testing**: {security_performance_accessibility_testing}
- **Coverage Target**: {target_percentage}%

### Task Breakdown by Complexity

{Generate appropriate task structure based on complexity score}

### Full-Stack Quality Gates
**Required validations before each commit:**
- **Backend**: Test suite, linting, type checking, security scans
- **Frontend**: Test suite, linting, type checking, build validation
- **Integration**: API contract tests, E2E validation
- **Performance**: Backend performance, frontend bundle size
- **Security**: Authentication flows, data validation

### Success Criteria
**Feature completion requirements:**
- All user journeys implemented and tested across the stack
- Backend API fully functional with comprehensive test coverage
- Frontend components fully functional with user experience validation
- Full-stack integration tested end-to-end
- Test coverage meets target ({target_percentage}%)
- Performance benchmarks met for both backend and frontend
- Security requirements satisfied
- Accessibility standards met
- Cross-browser compatibility validated

## Implementation Roadmap

### Development Sequence
1. **Foundation & Test Infrastructure**: Backend and frontend test setup, CI/CD preparation
2. **Backend Core Development**: API endpoints, data models, business logic (test-first)
3. **Frontend Core Development**: Components, user interactions, state management (test-first)  
4. **Integration Layer**: API integration, authentication, error handling
5. **User Experience**: Styling, accessibility, responsive design, performance optimization
6. **Full-Stack Quality Assurance**: End-to-end testing, security validation, performance optimization

### Risk Mitigation
{Identified risks and mitigation strategies based on complexity analysis}

**Technical Risks:**
- **API Contract Changes**: Version contracts, use type-safe interfaces
- **Performance Issues**: Implement monitoring, set performance budgets
- **Security Vulnerabilities**: Regular security audits, automated scanning
- **Cross-Stack Communication**: Comprehensive integration testing

### Dependencies & Prerequisites
{External dependencies, infrastructure requirements, development environment setup}

## Execution Instructions

**To execute this plan:**
```bash
/execute .planning/PLAN_{SUFFIX}.md
```

**The execution will:**
- Follow task sequence with appropriate testing at each phase
- Implement test-first development across the entire stack
- Validate quality gates at each step
- Track progress with comprehensive metrics
- Ensure all success criteria are met
- Maintain focus on full-stack integration

## Quality Validation

### Plan Quality Assessment
- [ ] All aspects of the full-stack feature are thoroughly analyzed
- [ ] Backend and frontend requirements are clearly defined
- [ ] Integration points and data contracts are specified
- [ ] Test strategy matches complexity appropriately
- [ ] Quality gates are comprehensive and executable
- [ ] Success criteria are measurable and achievable
- [ ] Context research provided sufficient implementation guidance
- [ ] Risk mitigation strategies are practical and actionable

**Plan Confidence Score**: {score}/10 for supporting successful full-stack feature implementation

**Remember**: This plan combines deep contextual research with intelligent complexity-based planning to ensure efficient, high-quality full-stack development that delivers complete, integrated features meeting both technical and user requirements.
```

## Quality Assurance for Full-Stack Planning

### Planning Validation Checklist
- [ ] HYPERTHINK analysis provided comprehensive insights across the entire stack
- [ ] Context7 MCP / Web research gathered authoritative full-stack patterns
- [ ] Monorepo analysis identified existing patterns and integration points
- [ ] Backend requirements mapped to specific technical implementations
- [ ] Frontend requirements mapped to user experience and component needs
- [ ] Integration complexity accurately assessed
- [ ] Test strategy appropriate for full-stack complexity level
- [ ] Task breakdown enables systematic full-stack development
- [ ] Quality gates ensure consistent standards across the stack
- [ ] Success criteria are specific, measurable, and comprehensive

### Context Research Quality
- [ ] Full-stack architecture patterns from authoritative sources
- [ ] Backend and frontend best practices from reliable documentation
- [ ] Integration patterns based on proven approaches
- [ ] Security and performance guidance from expert sources
- [ ] Testing strategies from comprehensive testing documentation

## Implementation Notes

**Full-Stack Benefits:**
- Seamless flow from analysis to planning without artificial stack separation
- HYPERTHINK ensures deep consideration of cross-stack challenges
- Context7 MCP provides authoritative implementation guidance for entire stack
- Complexity-based planning prevents over/under-engineering across layers
- Comprehensive document supports systematic full-stack execution
- Integration-first approach ensures cohesive feature development

**Execution Integration:**
- Plan document contains all information needed for full-stack implementation
- Task breakdown enables systematic progress tracking across backend and frontend
- Quality gates ensure consistent standards throughout the entire stack
- Success criteria provide clear completion validation for integrated features

## Success Criteria

Rate the full-stack planning effectiveness on:
- **Depth**: HYPERTHINK analysis provides comprehensive cross-stack insights (9+/10)
- **Research**: Context gathering provides actionable implementation guidance (9+/10)
- **Integration**: Backend and frontend requirements are properly coordinated (9+/10)
- **Planning**: Task breakdown enables efficient full-stack implementation (9+/10)
- **Quality**: Success criteria ensure feature excellence across the stack (9+/10)

**Remember**: Great full-stack planning combines deep analysis with practical implementation guidance, enabling efficient development of high-quality, fully integrated features that work seamlessly across the entire technology stack.
