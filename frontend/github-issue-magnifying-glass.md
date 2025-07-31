# Bug Report: Oversized Magnifying Glass SVG in File Manager

## Problem Description
The File Manager's "Files & Folders" section contains multiple inline SVG magnifying glass icons that are inconsistent with the centralized Icon component system. These icons may appear oversized or inconsistent with the established design standards.

## Investigation Results

### Evidence Gathered
- **Component**: FileExplorer.tsx (`/src/components/collection/FileExplorer.tsx`)
- **Issue Type**: Frontend Bug - Inconsistent Icon Usage
- **Affected Lines**: 284-286, 297-299, 312-314

### Problematic Code Locations

#### 1. Search Input Field (Lines 284-286)
```jsx
<svg className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
</svg>
```

#### 2. Empty Search Results State (Lines 297-299)
```jsx
<svg className="mx-auto h-8 w-8 text-gray-400 flex-shrink-0" width="32" height="32" fill="none" stroke="currentColor" viewBox="0 0 24 24">
  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
</svg>
```

#### 3. Empty Collection State (Lines 312-314)  
```jsx
<svg className="mx-auto h-8 w-8 text-gray-400 flex-shrink-0" width="32" height="32" fill="none" stroke="currentColor" viewBox="0 0 24 24">
  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
</svg>
```

### Additional Inline SVG Issues Found
The FileExplorer component has multiple other inline SVG icons that should be replaced:
- **Folder icons** (Lines 156-165, 166-168)
- **File icons** (Lines 207-209)  
- **Delete icons** (Lines 237-239)
- **Plus icons** (Lines 269-271)
- **Chevron icons** (Lines 156-165)

## Root Cause Analysis
- **Issue Type**: Frontend Bug - Inconsistent Icon System
- **Affected Component**: `FileExplorer.tsx`
- **Likely Cause**: Component was created before centralized Icon system or wasn't updated during icon standardization

## Centralized Icon System Available
The project has a centralized Icon component at `/src/components/ui/Icon.tsx` with:
- Standardized sizes: `xs`, `sm`, `md`, `lg`, `xl`
- Consistent color mapping
- Built-in `search` icon available
- Proper sizing standards documented in `ICON_SIZING_STANDARDS.md`

## Reproduction Steps
1. Navigate to File Manager tab
2. Click on any existing collection (e.g., "Test")
3. Window opens titled "Files & Folders"
4. **Expected**: All icons should use consistent sizing from centralized Icon component
5. **Actual**: Multiple inline SVG icons with potentially inconsistent sizing

## Suggested Fix
Replace all inline SVG icons in FileExplorer.tsx with the centralized Icon component:

### Search Icons
```jsx
// Replace inline search SVGs with:
<Icon name="search" size="sm" />  // For input field
<Icon name="search" size="xl" />  // For empty states
```

### Other Icons
```jsx
// Folder icons
<Icon name="folder" size="sm" color="blue" />

// File icons  
<Icon name="document" size="sm" />

// Delete icons
<Icon name="trash" size="xs" color="red" />

// Plus icons
<Icon name="plus" size="sm" />

// Chevron icons
<Icon name="chevronRight" size="sm" />
```

## Additional Context
- **Severity**: Medium - Visual inconsistency affecting user experience
- **User Impact**: File Manager interface may have oversized or inconsistent icons
- **Related**: Part of broader icon standardization effort
- **Standards**: Follow `ICON_SIZING_STANDARDS.md` guidelines

## Files Affected
- `/src/components/collection/FileExplorer.tsx` (Primary)
- Potentially other components in collection folder

---
*Issue created automatically by frontend-issue-detective agent*