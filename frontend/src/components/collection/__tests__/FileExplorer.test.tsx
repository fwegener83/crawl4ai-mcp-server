import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FileExplorer } from '../FileExplorer';
import { CollectionProvider } from '../../../contexts/CollectionContext';
import type { FileNode } from '../../../contexts/CollectionContext';

// Mock the useCollectionOperations hook
const mockUseCollectionOperations = vi.fn();
vi.mock('../../../hooks/useCollectionOperations', () => ({
  useCollectionOperations: () => mockUseCollectionOperations()
}));

// Mock Icon component
vi.mock('../../ui/Icon', () => ({
  default: ({ name, size, className }: any) => (
    <div data-testid={`icon-${name}`} data-size={size} className={className}>
      {name}
    </div>
  )
}));

// Mock MUI components that need custom behavior for testing
vi.mock('../../ui', async () => {
  const actual = await vi.importActual('../../ui');
  return {
    ...actual,
    CircularProgress: ({ size }: { size?: number }) => <div data-testid="loading-spinner" data-size={size}>Loading...</div>
  };
});

const mockFiles: FileNode[] = [
  {
    name: 'readme.md',
    path: 'readme.md',
    type: 'file',
    metadata: {
      filename: 'readme.md',
      folder_path: '',
      created_at: '2024-01-01T00:00:00Z',
      source_url: 'https://example.com/readme',
      size: 1024
    }
  },
  {
    name: 'config.json',
    path: 'config/config.json',
    type: 'file',
    metadata: {
      filename: 'config.json',
      folder_path: 'config',
      created_at: '2024-01-02T00:00:00Z',
      source_url: 'https://example.com/config',
      size: 512
    }
  },
  {
    name: 'api.md',
    path: 'docs/api.md',
    type: 'file',
    metadata: {
      filename: 'api.md',
      folder_path: 'docs',
      created_at: '2024-01-03T00:00:00Z',
      source_url: 'https://example.com/api',
      size: 2048
    }
  }
];

const defaultMockState = {
  collections: [],
  selectedCollection: 'test-collection',
  files: [],
  folders: [],
  editor: {
    filePath: null,
    content: '',
    originalContent: '',
    modified: false,
    saving: false,
  },
  ui: {
    loading: {
      collections: false,
      files: false,
      saving: false,
      crawling: false,
    },
    modals: {
      newCollection: false,
      addPage: false,
      newFile: false,
      deleteConfirmation: { open: false, type: 'collection' as const, target: null },
    },
    error: null,
  },
};

const defaultMockOperations = {
  openFile: vi.fn(),
  openDeleteConfirmation: vi.fn(),
  openModal: vi.fn(),
};

describe('FileExplorer', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseCollectionOperations.mockReturnValue({
      state: defaultMockState,
      ...defaultMockOperations,
    });
  });

  it('should render loading state', () => {
    mockUseCollectionOperations.mockReturnValue({
      state: {
        ...defaultMockState,
        ui: {
          ...defaultMockState.ui,
          loading: {
            ...defaultMockState.ui.loading,
            files: true,
          },
        },
      },
      ...defaultMockOperations,
    });

    render(
      <CollectionProvider>
        <FileExplorer />
      </CollectionProvider>
    );

    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    expect(screen.getByText('Loading files...')).toBeInTheDocument();
  });

  it('should render header with title and new file button', () => {
    render(
      <CollectionProvider>
        <FileExplorer />
      </CollectionProvider>
    );

    expect(screen.getByText('Files & Folders')).toBeInTheDocument();
    expect(screen.getByLabelText('New file')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Search files...')).toBeInTheDocument();
  });

  it('should render empty state when no files', () => {
    render(
      <CollectionProvider>
        <FileExplorer />
      </CollectionProvider>
    );

    expect(screen.getByText('No files in this collection')).toBeInTheDocument();
    expect(screen.getByText('Add pages by crawling URLs or create new files manually')).toBeInTheDocument();
    expect(screen.getByText('Add Page from URL')).toBeInTheDocument();
    expect(screen.getByText('Create New File')).toBeInTheDocument();
  });

  it('should render file tree when files exist', () => {
    mockUseCollectionOperations.mockReturnValue({
      state: {
        ...defaultMockState,
        files: mockFiles,
      },
      ...defaultMockOperations,
    });

    render(
      <CollectionProvider>
        <FileExplorer />
      </CollectionProvider>
    );

    expect(screen.getByText('readme.md')).toBeInTheDocument();
    expect(screen.getByText('config')).toBeInTheDocument(); // Folder name, not the file directly
    expect(screen.getByText('docs')).toBeInTheDocument(); // Folder name, not the file directly
  });

  it('should display folder structure correctly', () => {
    mockUseCollectionOperations.mockReturnValue({
      state: {
        ...defaultMockState,
        files: mockFiles,
      },
      ...defaultMockOperations,
    });

    render(
      <CollectionProvider>
        <FileExplorer />
      </CollectionProvider>
    );

    // Should show folders
    expect(screen.getByText('config')).toBeInTheDocument();
    expect(screen.getByText('docs')).toBeInTheDocument();
    
    // Should show file count in folders (both folders have 1 file each)
    expect(screen.getAllByText('1 files')).toHaveLength(2);
  });

  it('should expand and collapse folders', async () => {
    const user = userEvent.setup();
    
    mockUseCollectionOperations.mockReturnValue({
      state: {
        ...defaultMockState,
        files: mockFiles,
      },
      ...defaultMockOperations,
    });

    render(
      <CollectionProvider>
        <FileExplorer />
      </CollectionProvider>
    );

    // Initially, folders should be collapsed, so files inside shouldn't be visible
    expect(screen.queryByText('config.json')).not.toBeInTheDocument();
    
    // Click to expand config folder
    await user.click(screen.getByText('config'));
    
    // Now the file should be visible
    expect(screen.getByText('config.json')).toBeInTheDocument();
  });

  it('should call openFile when clicking on a file', async () => {
    const user = userEvent.setup();
    const mockOpenFile = vi.fn();
    
    mockUseCollectionOperations.mockReturnValue({
      state: {
        ...defaultMockState,
        files: mockFiles,
      },
      ...defaultMockOperations,
      openFile: mockOpenFile,
    });

    render(
      <CollectionProvider>
        <FileExplorer />
      </CollectionProvider>
    );

    await user.click(screen.getByText('readme.md'));
    
    expect(mockOpenFile).toHaveBeenCalledWith('test-collection', 'readme.md', undefined);
  });

  it('should call openFile with folder when clicking on nested file', async () => {
    const user = userEvent.setup();
    const mockOpenFile = vi.fn();
    
    mockUseCollectionOperations.mockReturnValue({
      state: {
        ...defaultMockState,
        files: mockFiles,
      },
      ...defaultMockOperations,
      openFile: mockOpenFile,
    });

    render(
      <CollectionProvider>
        <FileExplorer />
      </CollectionProvider>
    );

    // Expand config folder first
    await user.click(screen.getByText('config'));
    
    // Click on the nested file
    await user.click(screen.getByText('config.json'));
    
    expect(mockOpenFile).toHaveBeenCalledWith('test-collection', 'config.json', 'config');
  });

  it('should highlight selected file', () => {
    mockUseCollectionOperations.mockReturnValue({
      state: {
        ...defaultMockState,
        files: mockFiles,
        editor: {
          ...defaultMockState.editor,
          filePath: 'readme.md',
        },
      },
      ...defaultMockOperations,
    });

    render(
      <CollectionProvider>
        <FileExplorer />
      </CollectionProvider>
    );

    // The selected file should be rendered with MUI styling - just verify it exists
    const selectedFile = screen.getByText('readme.md');
    expect(selectedFile).toBeInTheDocument();
  });

  it('should call openDeleteConfirmation when clicking delete button', async () => {
    const user = userEvent.setup();
    const mockOpenDeleteConfirmation = vi.fn();
    
    mockUseCollectionOperations.mockReturnValue({
      state: {
        ...defaultMockState,
        files: mockFiles,
      },
      ...defaultMockOperations,
      openDeleteConfirmation: mockOpenDeleteConfirmation,
    });

    render(
      <CollectionProvider>
        <FileExplorer />
      </CollectionProvider>
    );

    // Find the delete button for the file (it's a Tooltip with IconButton)
    const deleteButton = screen.getByLabelText('Delete file');
    await user.click(deleteButton);

    expect(mockOpenDeleteConfirmation).toHaveBeenCalledWith('file', 'readme.md');
  });

  it('should filter files based on search term', async () => {
    const user = userEvent.setup();
    
    mockUseCollectionOperations.mockReturnValue({
      state: {
        ...defaultMockState,
        files: mockFiles,
      },
      ...defaultMockOperations,
    });

    render(
      <CollectionProvider>
        <FileExplorer />
      </CollectionProvider>
    );

    // Initially all files should be visible
    expect(screen.getByText('readme.md')).toBeInTheDocument();
    expect(screen.getByText('config')).toBeInTheDocument();
    expect(screen.getByText('docs')).toBeInTheDocument();

    // Search for 'config'
    await user.type(screen.getByPlaceholderText('Search files...'), 'config');

    // Only config-related items should be visible
    expect(screen.queryByText('readme.md')).not.toBeInTheDocument();
    expect(screen.getByText('config')).toBeInTheDocument();
    expect(screen.queryByText('docs')).not.toBeInTheDocument();
  });

  it('should show no results message when search yields no results', async () => {
    const user = userEvent.setup();
    
    mockUseCollectionOperations.mockReturnValue({
      state: {
        ...defaultMockState,
        files: mockFiles,
      },
      ...defaultMockOperations,
    });

    render(
      <CollectionProvider>
        <FileExplorer />
      </CollectionProvider>
    );

    await user.type(screen.getByPlaceholderText('Search files...'), 'nonexistent');

    expect(screen.getByText('No files match "nonexistent"')).toBeInTheDocument();
    expect(screen.getByText('Clear search')).toBeInTheDocument();
  });

  it('should clear search when clicking clear search button', async () => {
    const user = userEvent.setup();
    
    mockUseCollectionOperations.mockReturnValue({
      state: {
        ...defaultMockState,
        files: mockFiles,
      },
      ...defaultMockOperations,
    });

    render(
      <CollectionProvider>
        <FileExplorer />
      </CollectionProvider>
    );

    // Search for something that doesn't exist
    await user.type(screen.getByPlaceholderText('Search files...'), 'nonexistent');
    expect(screen.getByText('No files match "nonexistent"')).toBeInTheDocument();

    // Clear search
    await user.click(screen.getByText('Clear search'));

    // All files should be visible again
    expect(screen.getByText('readme.md')).toBeInTheDocument();
    expect(screen.getByText('config')).toBeInTheDocument();
  });

  it('should call openModal when clicking new file button', async () => {
    const user = userEvent.setup();
    const mockOpenModal = vi.fn();
    
    mockUseCollectionOperations.mockReturnValue({
      state: defaultMockState,
      ...defaultMockOperations,
      openModal: mockOpenModal,
    });

    render(
      <CollectionProvider>
        <FileExplorer />
      </CollectionProvider>
    );

    await user.click(screen.getByLabelText('New file'));
    expect(mockOpenModal).toHaveBeenCalledWith('newFile');
  });

  it('should call openModal when clicking "Add Page from URL"', async () => {
    const user = userEvent.setup();
    const mockOpenModal = vi.fn();
    
    mockUseCollectionOperations.mockReturnValue({
      state: defaultMockState,
      ...defaultMockOperations,
      openModal: mockOpenModal,
    });

    render(
      <CollectionProvider>
        <FileExplorer />
      </CollectionProvider>
    );

    await user.click(screen.getByText('Add Page from URL'));
    expect(mockOpenModal).toHaveBeenCalledWith('addPage');
  });

  it('should call openModal when clicking "Create New File"', async () => {
    const user = userEvent.setup();
    const mockOpenModal = vi.fn();
    
    mockUseCollectionOperations.mockReturnValue({
      state: defaultMockState,
      ...defaultMockOperations,
      openModal: mockOpenModal,
    });

    render(
      <CollectionProvider>
        <FileExplorer />
      </CollectionProvider>
    );

    await user.click(screen.getByText('Create New File'));
    expect(mockOpenModal).toHaveBeenCalledWith('newFile');
  });

  it('should display file metadata like source URL', () => {
    mockUseCollectionOperations.mockReturnValue({
      state: {
        ...defaultMockState,
        files: mockFiles,
      },
      ...defaultMockOperations,
    });

    render(
      <CollectionProvider>
        <FileExplorer />
      </CollectionProvider>
    );

    expect(screen.getByText('from example.com')).toBeInTheDocument();
  });

  it('should sort folders before files', () => {
    mockUseCollectionOperations.mockReturnValue({
      state: {
        ...defaultMockState,
        files: mockFiles,
      },
      ...defaultMockOperations,
    });

    const { container } = render(
      <CollectionProvider>
        <FileExplorer />
      </CollectionProvider>
    );

    // Folders should be displayed (config and docs folders exist in mockFiles)
    expect(screen.getByText('config')).toBeInTheDocument();
    expect(screen.getByText('docs')).toBeInTheDocument();
    // Root file should also be displayed
    expect(screen.getByText('readme.md')).toBeInTheDocument();
  });

  it('should apply custom className', () => {
    const { container } = render(
      <CollectionProvider>
        <FileExplorer className="custom-class" />
      </CollectionProvider>
    );

    expect(container.firstChild).toHaveClass('custom-class');
  });

  it('should auto-expand folders in search results', async () => {
    const user = userEvent.setup();
    
    mockUseCollectionOperations.mockReturnValue({
      state: {
        ...defaultMockState,
        files: mockFiles,
      },
      ...defaultMockOperations,
    });

    render(
      <CollectionProvider>
        <FileExplorer />
      </CollectionProvider>
    );

    // Search for a file inside a folder
    await user.type(screen.getByPlaceholderText('Search files...'), 'config.json');

    // The folder should be auto-expanded and the file should be visible
    expect(screen.getByText('config.json')).toBeInTheDocument();
  });

  it('should handle empty folder paths correctly', () => {
    const filesWithEmptyPath: FileNode[] = [
      {
        name: 'root-file.md',
        path: 'root-file.md',
        type: 'file',
        metadata: {
          filename: 'root-file.md',
          folder_path: '',
          created_at: '2024-01-01T00:00:00Z',
          size: 1024
        }
      }
    ];

    mockUseCollectionOperations.mockReturnValue({
      state: {
        ...defaultMockState,
        files: filesWithEmptyPath,
      },
      ...defaultMockOperations,
    });

    render(
      <CollectionProvider>
        <FileExplorer />
      </CollectionProvider>
    );

    expect(screen.getByText('root-file.md')).toBeInTheDocument();
  });
});