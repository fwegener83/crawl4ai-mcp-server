# Frontend Feature Exploration from Initial Scenarios

## Usage
```bash
/frontend:explore path/to/INITIAL_FRONTEND_SUFFIX.md
/frontend:explore issue-123
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

## Research Process - FRONTEND ULTRATHINK Phase

### 1. **User Journey Analysis**
- **Scenario Breakdown**: Deep analysis of each user journey step
- **Component Mapping**: Identify all React components involved in scenarios
- **State Flow Analysis**: Track data flow and state changes through journeys
- **User Interaction Points**: Map all clickable elements, forms, modals
- **Navigation Patterns**: Understand routing and navigation requirements

### 2. **Frontend Technology Research**
- **React Patterns**: Research component composition, hooks usage, context patterns
- **Testing Strategies**: Unit testing with Vitest, E2E testing with Playwright
- **Styling System**: TailwindCSS patterns, responsive design considerations
- **State Management**: Component state, props drilling, context usage patterns
- **Build Tooling**: Vite configuration, TypeScript setup, ESLint rules

### 3. **Component Architecture Discovery**
- **Existing Components**: Analyze current component structure and patterns
- **Component Hierarchy**: Map parent-child relationships and props flow
- **Reusable Patterns**: Identify shared UI components and utility functions
- **Hook Dependencies**: Custom hooks and their usage patterns
- **Type Definitions**: TypeScript interfaces and type safety requirements

### 4. **Testing Infrastructure Research**
- **Unit Testing**: Vitest configuration, React Testing Library patterns
- **Integration Testing**: Component interaction testing strategies
- **E2E Testing**: Playwright test structure, page object patterns
- **Test Data**: Mock data strategies, API mocking approaches
- **Coverage Requirements**: Testing pyramid for frontend applications

### 5. **API Integration Research**
- **Backend Endpoints**: Available API endpoints and data structures
- **HTTP Client**: Axios configuration, error handling patterns
- **Loading States**: UI patterns for async operations
- **Error Handling**: User-friendly error display strategies
- **Data Transformation**: Response processing and validation

### 6. **Performance & Accessibility Research**
- **Performance**: Code splitting, lazy loading, bundle optimization
- **Accessibility**: ARIA patterns, keyboard navigation, screen reader support
- **Responsive Design**: Mobile-first approaches, breakpoint strategies
- **Browser Compatibility**: Cross-browser testing requirements
- **SEO Considerations**: Meta tags, semantic HTML, structured data

## Exploration Output Generation

### Step 1: Create Planning Directory
```bash
mkdir -p .planning/frontend
```

### Step 2: Generate Frontend Exploration Document
Save comprehensive exploration as: `.planning/frontend/EXPLORE_{SUFFIX}.md`

### Frontend Exploration Document Structure:
```markdown
# Frontend Feature Exploration: {Feature Name}

## Source Information
- **Input**: {file_path or issue_number}
- **Branch**: frontend/{SUFFIX}  
- **Generated**: {timestamp}
- **Frontend Tech Stack**: React 19, TypeScript, Vite, TailwindCSS

## User Journey Analysis
{Detailed breakdown of each scenario step with technical implications}

## Component Architecture Requirements
{All React components needed, their relationships, and responsibilities}

## State Management Strategy
{How data flows through components, what state is needed where}

## Testing Strategy
{Testing approach for each layer: Unit -> Integration -> E2E}

## UI/UX Implementation Details
{Design system usage, responsive considerations, accessibility requirements}

## API Integration Requirements
{Backend endpoints needed, data structures, error handling}

## Performance Considerations
{Code splitting, lazy loading, optimization strategies}

## Accessibility Requirements
{ARIA patterns, keyboard navigation, WCAG compliance}

## Technology Research Findings
{React patterns, testing best practices, tooling configuration}

## Implementation Knowledge Base
{Code examples, documentation links, proven patterns}

## Frontend-Specific Constraints
{Browser support, bundle size, performance budgets}

## Success Criteria
{Measurable completion criteria specific to frontend development}

## High-Level Frontend Approach
{Component-first development strategy with testing integration}

## Quality Gates
{Frontend-specific validation commands and quality checks}
```

## Frontend-Specific Research Areas

### React Component Research
- **Component Patterns**: Functional components, custom hooks, composition
- **Props Interface Design**: TypeScript interfaces for component props
- **Event Handling**: User interactions, form submissions, modal management
- **Lifecycle Management**: useEffect patterns, cleanup strategies
- **Performance Optimization**: useMemo, useCallback, React.memo usage

### Styling & Design System Research  
- **TailwindCSS Utilities**: Component-specific utility classes
- **Responsive Design**: Mobile-first breakpoint strategies
- **Component Variants**: Button styles, form states, loading indicators
- **Animation Patterns**: Transitions, micro-interactions, loading states
- **Dark Mode Support**: Theme switching, color scheme management

### Testing Pattern Research
- **Unit Testing**: Component rendering, prop validation, event handling
- **Integration Testing**: Component interactions, API integration with mocks
- **E2E Testing**: User workflow automation, form submissions, navigation
- **Visual Testing**: Screenshot comparisons, responsive testing
- **Accessibility Testing**: Automated a11y checks, keyboard navigation tests

## Quality Assurance for Frontend

### Exploration Completeness Checklist
- [ ] All user journeys mapped to specific React components
- [ ] Component props and state requirements identified
- [ ] Testing strategy covers unit, integration, and E2E levels
- [ ] API integration points and data flow documented
- [ ] Accessibility requirements specified with ARIA patterns
- [ ] Performance considerations addressed (bundle size, loading)
- [ ] Responsive design breakpoints and mobile considerations
- [ ] Error handling strategies for UI and API interactions

### Frontend Knowledge Transfer Validation
- [ ] Clear component architecture with responsibility boundaries
- [ ] Testable component design with clear interfaces
- [ ] Accessible UI patterns with keyboard navigation
- [ ] Performance-optimized implementation approach
- [ ] Cross-browser compatibility considerations documented

## Confidence Assessment
Rate the frontend exploration completeness on a scale of 1-10 for supporting:
- **Component Development**: Clear component responsibilities and interfaces
- **Test Implementation**: Comprehensive testing strategy across all levels
- **User Experience**: Intuitive and accessible user interactions
- **Technical Quality**: Performance, maintainability, and scalability

**Remember:** Frontend exploration focuses on user-centric component design with comprehensive testing strategy, ensuring both technical quality and exceptional user experience.
