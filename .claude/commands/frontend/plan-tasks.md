# Generate Frontend Test-First Task Plan from Exploration

## Usage
```bash
/frontend:plan .planning/frontend/EXPLORE_SUFFIX.md
```

## Input Processing

### Step 1: Document Analysis
Read the frontend exploration document: $ARGUMENTS

**Extract Key Information:**
- Feature name and SUFFIX from filename
- User journey complexity and component requirements
- Testing strategy and coverage needs
- API integration complexity
- UI/UX requirements and accessibility needs

### Step 2: Frontend Complexity Assessment

**Analyze frontend-specific complexity indicators:**
- **Component Count**: Number of new/modified React components
- **User Interactions**: Forms, modals, navigation complexity
- **State Complexity**: Local state, context, prop drilling requirements
- **API Integration**: Number of endpoints, data transformation needs
- **UI Complexity**: Responsive design, animations, accessibility features

**Frontend Complexity Classification:**
```bash
# Simple Feature (Score 1-3):
- Single component modification
- Basic user interaction (button, link)
- Minimal state changes
- Simple API call or no API
→ Component Tests + Basic E2E

# Moderate Feature (Score 4-7):
- Multiple component interactions  
- Forms with validation
- Modal management
- API integration with loading states
→ Full Test Pyramid

# Complex Feature (Score 8-10):
- New user workflow
- Complex state management
- Multiple API integrations
- Advanced UI patterns
→ Comprehensive Testing + Performance
```

## Frontend Test Strategy Selection

### Simple Feature Strategy (Score 1-3)
**Philosophy**: Component-focused testing
- **Unit Tests**: Component rendering, props, basic interactions
- **Integration**: Component with immediate children only
- **E2E**: Single happy path test
- **Coverage Target**: 85%

### Moderate Feature Strategy (Score 4-7)
**Philosophy**: User journey focused
- **Unit Tests**: All components, hooks, utilities
- **Integration**: Component interactions, mocked API calls
- **E2E**: Main user flows and error scenarios
- **Visual**: Key UI states and responsive breakpoints
- **Coverage Target**: 90%

### Complex Feature Strategy (Score 8-10)
**Philosophy**: Comprehensive quality assurance
- **Unit Tests**: Complete component coverage with edge cases
- **Integration**: Full component tree interactions
- **E2E**: All user journeys, error flows, edge cases
- **Visual**: All UI states, responsive design, accessibility
- **Performance**: Bundle size, load times, interaction metrics
- **Coverage Target**: 95%

## Frontend Task Generation by Complexity

### Simple Feature Tasks (3-5 Tasks)
```markdown
### Phase 1: Component Foundation
**Task 1.1: Component Unit Tests**
- Test component rendering with default props
- Test user interactions (clicks, inputs)
- Test conditional rendering states
- Mock any API calls or external dependencies

**Task 1.2: Component Implementation**
- Implement component following test specifications
- Ensure TypeScript interfaces are properly defined
- Apply TailwindCSS styling according to design
- Handle basic error states and loading

### Phase 2: Integration Validation
**Task 2.1: Component Integration Tests**
- Test component with parent/child interactions
- Test props passing and event bubbling
- Validate component composition works correctly

**Task 2.2: Basic E2E Test**
- Single happy path user journey
- Verify component works in real browser environment
- Test basic accessibility (keyboard navigation)

### Phase 3: Polish & Deployment
**Task 3.1: Final Quality Check**
- ESLint and TypeScript validation
- Basic performance check (bundle impact)
- Cross-browser compatibility verification
```

### Moderate Feature Tasks (6-10 Tasks)
```markdown
### Phase 1: Component Architecture
**Task 1.1: Core Component Tests**
- Comprehensive unit tests for all new components
- Test all props combinations and edge cases
- Mock external dependencies and API calls
- Test error boundaries and fallback states

**Task 1.2: Core Component Implementation**
- Implement components with proper TypeScript interfaces
- Apply consistent styling with TailwindCSS
- Implement proper error handling and loading states
- Ensure components are properly composed

### Phase 2: User Interaction Layer
**Task 2.1: Form & Interaction Tests**
- Test form validation and submission
- Test modal open/close and focus management
- Test user input handling and state updates
- Mock API responses for different scenarios

**Task 2.2: User Interaction Implementation**  
- Implement forms with proper validation
- Handle modal state and accessibility
- Implement proper loading and error states
- Connect components to API layer

### Phase 3: Integration Testing
**Task 3.1: Component Integration Tests**
- Test component interactions and data flow
- Test API integration with mocked responses
- Test error handling across component boundaries
- Validate state management works correctly

**Task 3.2: API Integration Implementation**
- Connect components to real API endpoints
- Implement proper error handling and retry logic
- Add loading states and user feedback
- Optimize API calls and data caching

### Phase 4: End-to-End Validation
**Task 4.1: E2E Test Suite**
- Test complete user journeys
- Test error scenarios and edge cases
- Test responsive design at different breakpoints
- Validate accessibility with screen readers

**Task 4.2: Performance & Polish**
- Optimize component performance (memo, callbacks)
- Ensure proper code splitting and lazy loading
- Final styling polish and responsive adjustments
- Cross-browser testing and bug fixes
```

### Complex Feature Tasks (8-15 Tasks)
```markdown
### Phase 1: Testing Infrastructure
**Task 1.1: Test Setup & Tooling**
- Configure advanced testing utilities
- Set up comprehensive mocking strategies
- Create reusable test fixtures and factories
- Configure coverage reporting and quality gates

### Phase 2: Component Foundation
**Task 2.1: Core Component Test Suite**
- Comprehensive unit tests with edge cases
- Test component composition and reusability
- Test all prop combinations and TypeScript interfaces
- Mock complex dependencies and API interactions

**Task 2.2: Core Component Implementation**
- Implement robust, reusable components
- Apply consistent design system patterns
- Implement proper error boundaries
- Optimize for performance and accessibility

### Phase 3: State Management & Data Flow  
**Task 3.1: State Management Tests**
- Test complex state updates and side effects
- Test context providers and consumers
- Test custom hooks and their dependencies
- Mock external data sources and APIs

**Task 3.2: State Management Implementation**
- Implement efficient state management
- Create custom hooks for shared logic
- Implement proper data flow patterns
- Handle complex async operations

### Phase 4: User Experience Layer
**Task 4.1: UX Interaction Tests**
- Test complete user workflows
- Test form validation and error handling
- Test modal and navigation interactions
- Test responsive behavior and touch interactions

**Task 4.2: UX Implementation**
- Implement smooth user interactions
- Add proper loading states and feedback
- Implement accessibility features (ARIA, keyboard)
- Add responsive design and mobile optimizations

### Phase 5: Integration & API Layer
**Task 5.1: API Integration Tests**
- Test all API endpoints with various responses
- Test error handling and retry mechanisms
- Test data transformation and validation
- Test concurrent requests and race conditions

**Task 5.2: API Integration Implementation**
- Implement robust API integration layer
- Add proper error handling and user feedback
- Implement data caching and optimization
- Handle offline scenarios and network issues

### Phase 6: End-to-End Quality Assurance
**Task 6.1: Comprehensive E2E Tests**
- Test all user journeys and workflows
- Test error scenarios and edge cases
- Test performance under various conditions
- Automated accessibility and visual regression tests

**Task 6.2: Performance & Production Readiness**
- Optimize bundle size and loading performance
- Implement proper error monitoring
- Add analytics and user behavior tracking
- Final cross-browser and device testing
```

## Frontend Complexity Scoring Algorithm

### Step 1: Component Complexity Analysis
```bash
# Count React components and complexity indicators
COMPONENT_SCORE=0
grep -i "component\|jsx\|tsx\|hook\|state\|props" EXPLORE_FILE | wc -l
# 1-2 components = +1, 3-5 = +2, 6+ = +3
```

### Step 2: User Interaction Complexity
```bash
# Analyze user interaction requirements
INTERACTION_SCORE=0  
grep -i "form\|modal\|navigation\|click\|submit\|validation" EXPLORE_FILE | wc -l
# Simple interactions = +1, Forms/Modals = +2, Complex workflows = +3
```

### Step 3: API Integration Complexity
```bash
# Check API integration requirements
API_SCORE=0
grep -i "api\|endpoint\|fetch\|axios\|loading\|error" EXPLORE_FILE | wc -l
# No API = +0, Simple API = +1, Complex API = +2
```

### Step 4: UI/UX Complexity
```bash
# Assess UI/UX requirements
UI_SCORE=0
grep -i "responsive\|animation\|accessibility\|performance\|mobile" EXPLORE_FILE | wc -l
# Basic UI = +1, Responsive = +2, Advanced UX = +3
```

## Task Document Generation

### Step 1: Calculate Frontend Complexity Score
```bash
TOTAL_SCORE=$((COMPONENT_SCORE + INTERACTION_SCORE + API_SCORE + UI_SCORE))

if [[ $TOTAL_SCORE -le 3 ]]; then
    COMPLEXITY="Simple"
    STRATEGY="Component-focused testing"
elif [[ $TOTAL_SCORE -le 7 ]]; then
    COMPLEXITY="Moderate"
    STRATEGY="User journey focused" 
else
    COMPLEXITY="Complex"
    STRATEGY="Comprehensive quality assurance"
fi
```

### Step 2: Generate Frontend Task Plan
Save task plan as: `.planning/frontend/TASKS_{SUFFIX}.md`

### Frontend Task Document Structure:
```markdown
# Frontend Test-First Plan: {Feature Name}

## Complexity Assessment
- **Score**: {TOTAL_SCORE}/11
- **Classification**: {COMPLEXITY}
- **Strategy**: {STRATEGY}

## Scoring Breakdown  
- Components: {COMPONENT_SCORE}/3
- Interactions: {INTERACTION_SCORE}/3
- API Integration: {API_SCORE}/2
- UI/UX: {UI_SCORE}/3

## Frontend Test-First Approach
✅ Component tests written before implementation
✅ User interaction tests drive UI development
✅ E2E tests validate complete user journeys  
✅ Accessibility tests ensure inclusive design
✅ Performance tests maintain quality standards

## Task Breakdown
{Selected task structure based on frontend complexity}

## Frontend Quality Gates
{Component-specific validation commands}
- `npm run test` - Unit test suite
- `npm run test:e2e` - Playwright E2E tests
- `npm run lint` - ESLint and TypeScript checks
- `npm run build` - Production build validation

## Success Criteria
{Frontend-specific completion criteria}
```

## Quality Assurance for Frontend Planning

### Frontend Planning Validation
- [ ] Component complexity accurately assessed
- [ ] Testing strategy matches user interaction complexity
- [ ] Task count proportional to UI/UX requirements
- [ ] API integration properly scoped
- [ ] Accessibility requirements included in planning
- [ ] Performance considerations addressed

### Test-First Frontend Integrity
- [ ] Component tests drive implementation design
- [ ] User interaction tests validate UX requirements
- [ ] E2E tests cover complete user journeys
- [ ] Visual tests prevent UI regressions
- [ ] Accessibility tests ensure inclusive design
- [ ] Performance tests maintain quality standards

## Implementation Notes

**Frontend-Specific Benefits:**
- Prevents component over-engineering through focused testing
- Ensures user-centric design through interaction-driven tests
- Maintains accessibility standards through automated testing
- Optimizes performance through measurement-driven development
- Reduces bug rates through comprehensive test coverage

**Complexity Assessment Guide:**
- **Simple**: Single component change, basic interaction
- **Moderate**: Multi-component feature, forms, API integration
- **Complex**: New user workflow, complex state, advanced UI patterns

## Success Criteria

Rate the frontend planning on:
- **User Focus**: Tasks align with user journey requirements (8+/10)
- **Technical Quality**: Comprehensive testing strategy (8+/10)
- **Accessibility**: Inclusive design considerations (8+/10)
- **Performance**: Optimization and quality gates (8+/10)

**Remember:** Frontend test planning ensures user-centric development with technical excellence, balancing comprehensive testing with development efficiency.
