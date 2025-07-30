# Icon Sizing Standards

## Consistent Icon Sizes for UI

To maintain a clean and consistent UI layout, follow these icon sizing standards:

### Standard Sizes

- **`h-3 w-3` (12px)**: Tiny icons in metadata, badges, inline text
- **`h-4 w-4` (16px)**: Small icons in buttons, form elements, navigation
- **`h-5 w-5` (20px)**: Medium icons in list items, cards
- **`h-6 w-6` (24px)**: Large icons in modals, headers, important actions
- **`h-8 w-8` (32px)**: Empty state icons, placeholder graphics

### Usage Guidelines

1. **Button Icons**: Use `h-4 w-4` for inline button icons
2. **List Items**: Use `h-5 w-5` for list item icons (folders, files)  
3. **Modal Headers**: Use `h-6 w-6` for modal header icons
4. **Empty States**: Use `h-8 w-8` for empty state placeholder icons
5. **Metadata**: Use `h-3 w-3` for small metadata icons (dates, counts)

### Examples Fixed

- MainContent "Select Collection": Changed from `h-16 w-16` to `h-8 w-8`
- FileExplorer "No files": Changed from `h-12 w-12` to `h-8 w-8`  
- EditorArea "No file selected": Changed from `h-16 w-16` to `h-8 w-8`
- CollectionSidebar "No collections": Changed from `h-12 w-12` to `h-8 w-8`

### Avoid

- Icons larger than `h-8 w-8` except for special cases (hero sections)
- Inconsistent sizes within the same component type
- Mixing different size patterns in related UI elements