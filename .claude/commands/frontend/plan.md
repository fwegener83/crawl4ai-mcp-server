# Frontend Feature Planning with Deep Context Analysis

## Usage
```bash
/frontend:plan path/to/INITIAL_FRONTEND_SUFFIX.md
/frontend:plan issue-123
```

## Input Processing

### Step 1: Input Analysis
Analyze the provided argument: $ARGUMENTS

**If it's a file path (.md):**
- Read the specified INITIAL file  
- Extract SUFFIX from filename (e.g., `INITIAL_FRONTEND_COLLECTION.md` → `COLLECTION`)
- Use SUFFIX as feature branch name prefix: `frontend/{SUFFIX}`

**If it's an issue reference (issue-123 or just 123):**
- Use `gh issue view <number>` to fetch issue details
- Analyze issue title and content to generate appropriate SUFFIX
- Create meaningful branch name from issue content

### Step 2: Branch Management
Check if feature branch exists:
```bash
git branch --list | grep -q "frontend/{SUFFIX}"
```

**If branch doesn't exist:**
- Create and checkout: `git checkout -b frontend/{SUFFIX}`
- Inform user about new branch creation

**If branch exists:**
- Switch to existing branch: `git checkout frontend/{SUFFIX}`
- Inform user about branch switch

## Phase 1: DEEP EXPLORATION with HYPERTHINKING

### Step 1: Activate Deep Analysis Mode
**HYPERTHINK about this frontend feature using extended reasoning:**

Think deeply about the frontend implementation requirements, user experience patterns, component architecture, testing strategies, and technical constraints. Consider multiple implementation approaches, potential edge cases, accessibility requirements, performance implications, and integration challenges.

### Step 2: Comprehensive Context Gathering

**Context7 MCP Research (PRIORITY 1):**
Use Context7 MCP to gather implementation patterns and documentation:

```bash
# React/TypeScript patterns for similar features
# Component composition best practices  
# Testing strategies for user journey validation
# Accessibility implementation patterns
# Performance optimization techniques
# State management approaches
```

**Web Research (PRIORITY 2):**
If Context7 MCP is unavailable, use web search for:
- React component patterns for similar features
- Frontend testing best practices (Vitest + Playwright)
- Accessibility implementation guides (WCAG compliance)
- Performance optimization strategies
- TypeScript patterns for complex components

**Codebase Analysis (PRIORITY 3):**
Analyze existing frontend codebase:
```bash
# Examine existing components for patterns
find frontend/src/components -name "*.tsx" | head -10

# Review current testing approaches
find frontend/src -name "*.test.*" | head -5

# Check current styling patterns
grep -r "className" frontend/src/components | head -10
```

**Backend Integration Analysis (PRIORITY 4 - CRITICAL):**
Analyze backend APIs and integration patterns for tight coupling:

```bash
# Backend API endpoint analysis
grep -r "@app.route\|@router\|def.*api" server.py crawl4ai_mcp_server/ | head -20

# Existing API calls in frontend
grep -r "axios\|fetch\|api" frontend/src/services/ frontend/src/components/ | head -15

# Data structures and models
find . -name "*.py" -exec grep -l "class.*Model\|@dataclass\|TypedDict" {} \; | head -10

# Backend response formats
grep -r "return.*json\|jsonify\|Response" server.py crawl4ai_mcp_server/ | head -10
```

**Backend Integration Deep Dive:**
1. **API Endpoint Mapping**: Identify all available backend endpoints
2. **Data Contract Analysis**: Understand request/response structures
3. **Authentication & Error Handling**: Backend patterns for auth and errors
4. **Real-time Features**: WebSocket or polling patterns if applicable
5. **Testing Integration**: How to test against real backend APIs

### Step 3: User Journey Deep Analysis

**For each user journey in the initial document:**

1. **Journey Breakdown Analysis:**
   - Map each step to specific UI interactions
   - Identify state changes and data flow
   - Determine API integration points
   - Consider error scenarios and edge cases

2. **Component Architecture Mapping:**
   - Identify all React components needed
   - Define component hierarchy and composition
   - Plan props interfaces and TypeScript types
   - Determine state management requirements

3. **User Experience Considerations:**
   - Accessibility requirements (ARIA, keyboard navigation)
   - Responsive design breakpoints
   - Loading states and user feedback
   - Error handling and recovery flows

4. **Technical Integration Analysis:**
   - API endpoints and data structures needed
   - Existing component reuse opportunities
   - Third-party library requirements
   - Performance and bundle size impact

## Phase 2: INTELLIGENT PLANNING

### Step 1: Frontend Complexity Assessment

**Analyze complexity across multiple dimensions:**

**Component Complexity Score (0-4):**
- Simple modification (1): Single component change, minimal logic
- Moderate feature (2): Few components, basic interactions
- Complex feature (3): Multiple components, complex state
- System feature (4): New workflows, advanced patterns

**User Interaction Complexity Score (0-3):**
- Basic (1): Simple clicks, basic navigation
- Interactive (2): Forms, modals, validation
- Advanced (3): Complex workflows, multi-step processes

**API Integration Complexity Score (0-2):**
- None (0): No API integration required
- Simple (1): Single endpoint, straightforward data
- Complex (2): Multiple endpoints, complex data flow

**UI/UX Complexity Score (0-3):**
- Basic (1): Standard components, simple styling
- Enhanced (2): Custom components, responsive design
- Advanced (3): Animations, complex layouts, accessibility

**Total Complexity Score: {sum}/12**

### Step 2: Test Strategy Selection

**Based on complexity score, determine test approach:**

**Score 1-3 (Simple):** Component-Focused Testing
- **Unit Tests**: Core component logic, props, basic interactions
- **Integration**: Key parent-child interactions only
- **E2E**: Single happy path validation
- **Coverage Target**: 85%

**Score 4-7 (Moderate):** Balanced Testing Strategy  
- **Unit Tests**: Comprehensive component coverage
- **Integration**: API integration with mocks, component composition
- **E2E**: Main user journeys plus key error scenarios
- **Accessibility**: Basic a11y validation
- **Coverage Target**: 90%

**Score 8-12 (Complex):** Comprehensive Quality Assurance
- **Unit Tests**: Complete coverage with edge cases
- **Integration**: Full component tree, complex state scenarios
- **E2E**: All user journeys, error flows, responsive testing
- **Accessibility**: Full WCAG compliance validation
- **Performance**: Bundle size, interaction timing, load testing
- **Coverage Target**: 95%

### Step 3: Task Generation Based on Strategy

**Generate phase-based tasks appropriate to complexity:**

## Planning Document Generation

### Create Comprehensive Plan Document
Save complete plan as: `.planning/frontend/PLAN_{SUFFIX}.md`

### Frontend Plan Document Structure:
```markdown
# Frontend Feature Plan: {Feature Name}

## Planning Overview
- **Input**: {file_path or issue_number}
- **Branch**: frontend/{SUFFIX}
- **Complexity Score**: {total_score}/12
- **Test Strategy**: {selected_strategy}
- **Generated**: {timestamp}

## Phase 1: Deep Exploration Results

### HYPERTHINK Analysis Summary
{Key insights from extended reasoning about the feature}

### Context Research Findings
{Comprehensive research results from Context7 MCP / Web Search / Codebase}

#### Implementation Patterns Discovered
{React/TypeScript patterns, component architectures, best practices}

#### Testing Strategies Researched  
{Testing approaches, tools, coverage strategies, accessibility patterns}

#### Backend Integration Insights (CRITICAL)
{Complete analysis of backend APIs, data contracts, authentication patterns}

**Available API Endpoints:**
{List all discovered backend endpoints with their purposes}

**Data Contracts & Models:**
{Backend data structures, request/response formats, TypeScript interfaces needed}

**Authentication & Security:**
{Backend auth patterns, error handling, security considerations}

**Integration Patterns:**
{How existing frontend components integrate with backend, best practices}

#### Performance & Accessibility Insights
{Optimization techniques, a11y requirements, responsive design approaches}

### User Journey Technical Analysis

#### Journey 1: {Journey Name}
**Steps & Technical Requirements:**
1. {Step} → **Components**: {components_needed} → **Backend API**: {specific_endpoints} → **Data Flow**: {request_response_format} → **State**: {state_changes}
2. {Step} → **Components**: {components_needed} → **Backend API**: {specific_endpoints} → **Data Flow**: {request_response_format} → **State**: {state_changes}

**Technical Complexity:**
- **Components**: {component_list_with_complexity}
- **Backend Integration**: {api_endpoints_required_with_data_contracts}
- **State Management**: {state_requirements_including_api_state}
- **API Integration**: {endpoint_requirements_with_error_handling}
- **Error Scenarios**: {error_handling_needs_backend_and_frontend}

{Repeat for each journey}

### Component Architecture Plan
{Complete component hierarchy, props interfaces, composition patterns}

### API Integration Requirements
{Specific backend endpoints needed, data structures, error handling, loading states}

**Backend API Mapping:**
- **Endpoint**: {method} {path} - **Purpose**: {description} - **Request**: {request_format} - **Response**: {response_format}
- **Error Handling**: {backend_error_codes_and_frontend_handling}
- **Authentication**: {auth_requirements_and_patterns}
- **Rate Limiting**: {backend_limits_and_frontend_handling}

**Data Flow Integration:**
- **TypeScript Interfaces**: {backend_data_models_as_typescript_types}
- **API Service Layer**: {frontend_service_architecture_for_backend_calls}
- **State Synchronization**: {how_backend_state_maps_to_frontend_state}
- **Real-time Updates**: {websocket_polling_or_other_realtime_patterns}

### Accessibility Requirements
{ARIA patterns, keyboard navigation, screen reader support}

### Performance Considerations
{Bundle impact, lazy loading, optimization strategies}

## Phase 2: Intelligent Planning Results

### Complexity Assessment Breakdown
- **Component Complexity**: {score}/4 - {reasoning}
- **User Interactions**: {score}/3 - {reasoning}  
- **API Integration**: {score}/2 - {reasoning}
- **UI/UX Requirements**: {score}/3 - {reasoning}
- **Total Score**: {total}/12 - **{classification}**

### Selected Test Strategy: {strategy_name}
{Detailed explanation of why this strategy was chosen}

**Testing Approach:**
- **Unit Testing**: {specific_unit_test_requirements_including_api_mocking}
- **Integration Testing**: {specific_integration_requirements_with_backend_api_testing}
- **E2E Testing**: {specific_e2e_requirements_with_full_stack_flows}
- **Backend Integration Testing**: {testing_against_real_backend_apis_and_data}
- **Additional Testing**: {accessibility_performance_visual_testing}
- **Coverage Target**: {target_percentage}%

### Task Breakdown by Complexity

{Generate appropriate task structure based on complexity score}

### Frontend Quality Gates
**Required validations before each commit:**
- `npm run typecheck` - TypeScript compilation
- `npm run lint` - ESLint validation  
- `npm run test:run` - Unit test suite
- `npm run build` - Production build validation
- `npm run test:e2e` - E2E validation (integration+ tasks)

### Success Criteria
**Feature completion requirements:**
- All user journeys implemented and tested
- **Backend integration fully functional with real APIs**
- **Data contracts validated between frontend and backend**
- Test coverage meets target ({target_percentage}%)
- TypeScript compilation with zero errors
- Accessibility requirements satisfied
- Performance benchmarks met
- Cross-browser compatibility validated
- **Full-stack integration tested end-to-end**

## Implementation Roadmap

### Development Sequence
1. **Backend Analysis & Integration Setup**: API contracts, TypeScript interfaces, service layer
2. **Component Architecture**: Component structure following backend data models
3. **Core Implementation**: Components with backend integration, test-first approach
4. **API Integration Layer**: Service layer, error handling, authentication, real API testing
5. **User Experience**: Styling, accessibility, responsive design with backend data
6. **Full-Stack Quality Assurance**: End-to-end testing, performance with real backend

### Risk Mitigation
{Identified risks and mitigation strategies based on complexity analysis}

**Backend Integration Risks:**
- **API Contract Changes**: Version API contracts, use TypeScript interfaces
- **Backend Availability**: Local development setup, API mocking for testing
- **Data Structure Mismatches**: Validate data contracts in integration tests
- **Authentication Issues**: Test auth flows in both frontend and backend

### Dependencies & Prerequisites
{External dependencies, API requirements, design system needs}

## Execution Instructions

**To execute this plan:**
```bash
/frontend:execute .planning/frontend/PLAN_{SUFFIX}.md
```

**The execution will:**
- Follow task sequence with frontend-tester sub agent
- Implement test-first development approach
- Validate quality gates at each step
- Track progress with comprehensive metrics
- Ensure all success criteria are met

## Quality Validation

### Plan Quality Assessment
- [ ] All user journeys mapped to technical requirements
- [ ] Component architecture is clear and implementable
- [ ] Test strategy matches complexity appropriately
- [ ] Quality gates are comprehensive and executable
- [ ] Success criteria are measurable and achievable
- [ ] Context research provided sufficient implementation guidance

**Plan Confidence Score**: {score}/10 for supporting successful feature implementation

**Remember**: This plan combines deep contextual research with intelligent complexity-based planning to ensure efficient, high-quality frontend development that meets both user needs and technical standards.
```

## Quality Assurance for Frontend Planning

### Planning Validation Checklist
- [ ] HYPERTHINK analysis provided deep insights into implementation approach
- [ ] Context7 MCP / Web research gathered comprehensive implementation patterns
- [ ] User journeys mapped to specific technical requirements
- [ ] Component architecture is detailed and implementable
- [ ] Complexity assessment accurately reflects feature scope
- [ ] Test strategy is appropriate for complexity level
- [ ] Task breakdown enables systematic implementation
- [ ] Quality gates ensure consistent code quality
- [ ] Success criteria are specific and measurable

### Context Research Quality
- [ ] Implementation patterns discovered from authoritative sources
- [ ] Testing strategies researched from best practice documentation
- [ ] Accessibility requirements based on WCAG guidelines
- [ ] Performance optimization techniques from reliable sources
- [ ] Component patterns align with React/TypeScript best practices

## Implementation Notes

**Single-Command Benefits:**
- Seamless flow from analysis to planning without context loss
- HYPERTHINK ensures deep consideration of implementation challenges
- Context7 MCP provides authoritative implementation guidance
- Complexity-based planning prevents over/under-engineering
- Comprehensive document supports systematic execution

**Execution Integration:**
- Plan document contains all information needed for implementation
- Task breakdown enables systematic progress tracking
- Quality gates ensure consistent standards throughout
- Success criteria provide clear completion validation

## Success Criteria

Rate the planning effectiveness on:
- **Depth**: HYPERTHINK analysis provides comprehensive insights (9+/10)
- **Research**: Context gathering provides actionable implementation guidance (9+/10)
- **Planning**: Task breakdown enables efficient implementation (9+/10)
- **Quality**: Success criteria ensure feature excellence (9+/10)

**Remember**: Great frontend planning combines deep analysis with practical implementation guidance, enabling efficient development of high-quality, user-centric features.
