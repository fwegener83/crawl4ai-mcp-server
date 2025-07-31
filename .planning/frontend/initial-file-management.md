# Frontend Feature: Collection-Centric File Management (Phase 1)

## Overview
Replace existing frontend with collection-centric document management system. Focus on core file management workflows with simple page crawling integration. Reuse existing components where suitable while implementing new collection-focused architecture.

## Backend Prerequisites

### New HTTP API Endpoints (Required)
Create REST API layer for existing MCP tools:

```
POST   /api/collections                     # create_collection
POST   /api/collections/{id}/files          # save_to_collection  
GET    /api/collections                     # list_file_collections
GET    /api/collections/{id}                # get_collection_info
GET    /api/collections/{id}/files/{file}   # read_from_collection
DELETE /api/collections/{id}                # delete_file_collection
DELETE /api/collections/{id}/files/{file}   # delete file from collection
PUT    /api/collections/{id}/files/{file}   # update file in collection

# Simple crawl integration
POST   /api/crawl/single                    # single page crawl → save to collection
```

### Deprecation Plan
- Mark existing RAG tools as `@deprecated` 
- Add deprecation warnings to RAG MCP tools
- Document migration path from RAG to file collections

## User Scenarios (Phase 1)

### Scenario 1: Collection Lifecycle Management
**Goal**: User can create, select, and manage collections

**Pre-conditions**: Clean application state

**User Journey**:
1. User opens application → sees empty collections sidebar
2. User clicks "New Collection" → modal opens with form
3. User enters name "Python Documentation" and description
4. User submits → collection appears in sidebar as active
5. User can select different collections → content area updates
6. User can delete collection → confirmation dialog → collection removed

**Success Criteria**:
- Collection CRUD operations work via HTTP API
- UI state management handles collection selection
- Proper loading states and error handling
- Confirmation dialogs for destructive actions

**Components to Reuse**:
- Modal components (adapt for collection forms)
- Form validation logic
- Loading indicators

**New Components**:
- CollectionSidebar
- CollectionCard
- NewCollectionModal
- DeleteConfirmationModal

### Scenario 2: Simple Page Crawling to Collection  
**Goal**: User can crawl single pages into selected collection

**Pre-conditions**: At least one collection exists

**User Journey**:
1. User selects collection from sidebar → collection becomes active
2. User clicks "Add Page" → crawl modal opens
3. User enters URL "https://docs.python.org/3/tutorial/introduction.html"
4. User optionally enters folder name "Tutorial"
5. User clicks "Crawl Page" → loading state shown
6. System crawls page → saves as markdown file in collection
7. File appears in collection file explorer → auto-selected
8. Content loads in editor area

**Success Criteria**:
- Single page crawl integrated with collection system
- Files organized in folders within collections
- Real-time feedback during crawl process
- Proper error handling for failed crawls

**Components to Reuse**:
- Existing crawl form components (adapt for collection context)
- Loading indicators
- Error message displays

**New Components**:
- AddPageModal
- CrawlProgressIndicator

### Scenario 3: File Editor Integration
**Goal**: User can edit markdown files within collections

**Pre-conditions**: Collection with at least one file exists

**User Journey**:
1. User selects collection → file explorer shows files/folders
2. User clicks on markdown file → file loads in editor
3. User edits content in markdown editor
4. User clicks "Save" → file updates via API
5. File status indicator shows "saved" → auto-sync feedback
6. User can switch between files → unsaved changes prompt

**Success Criteria**:
- Seamless file editing experience
- Auto-save or explicit save functionality
- Unsaved changes detection and warnings
- File status indicators (saved/modified/error)

**Components to Reuse**:
- **Existing MarkdownEditor** (primary reuse candidate)
- Existing toolbar components
- Save/loading state indicators

**New Components**:
- FileExplorer
- FileTree
- FileStatusIndicator

### Scenario 4: Manual File Management
**Goal**: User can create, delete, and organize files manually

**Pre-conditions**: Collection exists

**User Journey**:
1. User right-clicks in file explorer → context menu appears
2. User selects "New File" → file creation modal opens
3. User enters filename "notes.md" and optional folder
4. User creates file → empty file appears in explorer and opens in editor
5. User can create folders → folder structure updates
6. User can delete files → confirmation → file removed
7. User can rename files/folders → inline editing

**Success Criteria**:
- Complete file/folder CRUD operations
- Intuitive context menus and interactions
- Proper validation (filename restrictions, duplicates)
- Folder hierarchy management

**Components to Reuse**:
- Modal components for file operations
- Form inputs and validation
- Confirmation dialogs

**New Components**:
- FileContextMenu
- NewFileModal
- FolderTree
- RenameInlineEditor

## Technical Architecture

### Component Hierarchy
```
App
├── CollectionSidebar
│   ├── NewCollectionButton
│   ├── CollectionList
│   └── CollectionCard
├── MainContent
│   ├── CollectionHeader
│   │   ├── CollectionTitle
│   │   └── AddPageButton
│   └── ContentArea
│       ├── FileExplorer
│       │   ├── FolderTree
│       │   ├── FileList
│       │   └── FileContextMenu
│       └── EditorArea
│           ├── EditorHeader
│           ├── MarkdownEditor (REUSED)
│           └── EditorToolbar (REUSED)
└── Modals
    ├── NewCollectionModal
    ├── AddPageModal
    ├── NewFileModal
    └── DeleteConfirmationModal
```

### State Management
```javascript
// Global State Structure
{
  collections: {
    items: Collection[],
    selected: string | null,
    loading: boolean
  },
  files: {
    currentCollection: {
      files: File[],
      folders: Folder[],
      activeFile: string | null
    },
    editor: {
      content: string,
      modified: boolean,
      saving: boolean
    }
  },
  ui: {
    modals: {
      newCollection: boolean,
      addPage: boolean,
      newFile: boolean
    },
    loading: {
      crawling: boolean,
      saving: boolean
    }
  }
}
```

### API Integration
```javascript
// API Client Structure
class CollectionAPI {
  // Collection operations
  async createCollection(data)
  async listCollections()
  async getCollection(id)
  async deleteCollection(id)
  
  // File operations  
  async saveFile(collectionId, filename, content, folder?)
  async readFile(collectionId, filename, folder?)
  async deleteFile(collectionId, filename, folder?)
  async updateFile(collectionId, filename, content, folder?)
  
  // Crawl integration
  async crawlSinglePage(url, collectionId, folder?)
}
```

### Reusable Components Migration

**MarkdownEditor** (High Priority Reuse):
- Keep existing editor functionality
- Add collection-aware save handlers
- Integrate with new file state management
- Maintain syntax highlighting and preview

**Form Components** (Medium Priority Reuse):
- Adapt existing form validation
- Reuse input components and styling
- Extend for collection-specific forms

**Modal System** (Medium Priority Reuse):
- Keep modal base components
- Adapt content for collection operations
- Maintain accessibility features

**Loading/Error States** (High Priority Reuse):
- Reuse existing loading indicators
- Adapt error message components
- Keep consistent visual feedback

## Implementation Phases

### Phase 1A: Foundation (Week 1)
- Set up new component architecture
- Implement CollectionSidebar with basic CRUD
- Create HTTP API endpoints for collection operations
- Basic routing between collections

### Phase 1B: File Management (Week 2) 
- Implement FileExplorer with folder support
- Integrate MarkdownEditor with collection files
- File CRUD operations via API
- Manual file creation/deletion

### Phase 1C: Crawl Integration (Week 3)
- Simple page crawl → collection workflow
- Progress feedback and error handling
- File organization (folders) during crawl
- Integration testing

### Phase 1D: Polish & Testing (Week 4)
- UI/UX refinements
- Comprehensive error handling
- Loading states and transitions
- End-to-end testing of all scenarios

## Success Criteria

### Functional Requirements
- All 4 scenarios complete successfully
- Collection operations work reliably
- File editing maintains existing quality
- Simple crawl integration functional

### Technical Requirements  
- HTTP API layer complete and documented
- Component reuse maximized where appropriate
- State management handles complex interactions
- Proper error handling and loading states

### User Experience
- Intuitive collection-first navigation
- Smooth transitions between collections/files
- Clear visual feedback for all operations
- Responsive design maintained

## Migration Strategy

### From Current Frontend
1. **Preserve**: MarkdownEditor, form components, styling
2. **Replace**: Main layout, navigation, content organization
3. **Extend**: Add collection/file management capabilities
4. **Deprecate**: RAG-focused components and workflows

### Data Migration
- Existing crawl results can be imported to collections
- RAG database remains for backward compatibility
- Clear migration path for existing users

## Risk Mitigation

### Technical Risks
- **Component Integration**: Test reused components thoroughly in new context
- **State Complexity**: Use established patterns for state management
- **API Performance**: Implement proper caching and loading states

### User Experience Risks  
- **Learning Curve**: Maintain familiar patterns where possible
- **Data Loss**: Implement proper confirmation dialogs
- **Performance**: Optimize for large collections/files

This specification provides a clear roadmap for implementing collection-centric file management while maximizing reuse of existing components and maintaining development velocity.