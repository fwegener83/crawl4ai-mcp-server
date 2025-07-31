import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { CollectionSidebar } from '../CollectionSidebar';
import { CollectionProvider } from '../../../contexts/CollectionContext';
import type { FileCollection } from '../../../types/api';

// Mock the useCollectionOperations hook
const mockUseCollectionOperations = vi.fn();
vi.mock('../../../hooks/useCollectionOperations', () => ({
  useCollectionOperations: () => mockUseCollectionOperations()
}));

// Mock LoadingSpinner component
vi.mock('../../LoadingSpinner', () => ({
  default: ({ size }: { size: string }) => <div data-testid="loading-spinner" data-size={size}>Loading...</div>
}));

const mockCollections: FileCollection[] = [
  {
    name: 'collection-1',
    description: 'First test collection',
    created_at: '2024-01-01T00:00:00Z',
    file_count: 5,
    folders: ['folder1', 'folder2'],
    metadata: {
      total_size: 2048,
      file_types: ['md', 'txt'],
      last_modified: '2024-01-01T12:00:00Z'
    }
  },
  {
    name: 'collection-2',
    description: 'Second test collection',
    created_at: '2024-01-02T00:00:00Z',
    file_count: 3,
    folders: [],
    metadata: {
      total_size: 1024,
      file_types: ['md'],
      last_modified: '2024-01-02T12:00:00Z'
    }
  }
];

const defaultMockState = {
  collections: [],
  selectedCollection: null,
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
  loadCollections: vi.fn(),
  selectCollection: vi.fn(),
  openModal: vi.fn(),
  openDeleteConfirmation: vi.fn(),
  clearError: vi.fn(),
};

describe('CollectionSidebar', () => {
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
            collections: true,
          },
        },
      },
      ...defaultMockOperations,
    });

    render(
      <CollectionProvider>
        <CollectionSidebar />
      </CollectionProvider>
    );

    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    expect(screen.getByText('Loading collections...')).toBeInTheDocument();
  });

  it('should render empty state when no collections', () => {
    render(
      <CollectionProvider>
        <CollectionSidebar />
      </CollectionProvider>
    );

    expect(screen.getByText('Collections')).toBeInTheDocument();
    expect(screen.getByText('No collections yet')).toBeInTheDocument();
    expect(screen.getByText('Create your first collection')).toBeInTheDocument();
  });

  it('should render collections list', () => {
    mockUseCollectionOperations.mockReturnValue({
      state: {
        ...defaultMockState,
        collections: mockCollections,
      },
      ...defaultMockOperations,
    });

    render(
      <CollectionProvider>
        <CollectionSidebar />
      </CollectionProvider>
    );

    expect(screen.getByText('collection-1')).toBeInTheDocument();
    expect(screen.getByText('collection-2')).toBeInTheDocument();
    expect(screen.getByText('First test collection')).toBeInTheDocument();
    expect(screen.getByText('Second test collection')).toBeInTheDocument();
  });

  it('should display collection stats', () => {
    mockUseCollectionOperations.mockReturnValue({
      state: {
        ...defaultMockState,
        collections: mockCollections,
      },
      ...defaultMockOperations,
    });

    render(
      <CollectionProvider>
        <CollectionSidebar />
      </CollectionProvider>
    );

    // Should show total collections and files
    expect(screen.getByText(/2 collections/)).toBeInTheDocument();
    expect(screen.getByText(/8 total files/)).toBeInTheDocument();
  });

  it('should display file counts for each collection', () => {
    mockUseCollectionOperations.mockReturnValue({
      state: {
        ...defaultMockState,
        collections: mockCollections,
      },
      ...defaultMockOperations,
    });

    render(
      <CollectionProvider>
        <CollectionSidebar />
      </CollectionProvider>
    );

    expect(screen.getByText('5 files')).toBeInTheDocument();
    expect(screen.getByText('3 files')).toBeInTheDocument();
  });

  it('should display folder counts when folders exist', () => {
    mockUseCollectionOperations.mockReturnValue({
      state: {
        ...defaultMockState,
        collections: mockCollections,
      },
      ...defaultMockOperations,
    });

    render(
      <CollectionProvider>
        <CollectionSidebar />
      </CollectionProvider>
    );

    expect(screen.getByText('2 folders')).toBeInTheDocument();
  });

  it('should highlight selected collection', () => {
    mockUseCollectionOperations.mockReturnValue({
      state: {
        ...defaultMockState,
        collections: mockCollections,
        selectedCollection: 'collection-1',
      },
      ...defaultMockOperations,
    });

    render(
      <CollectionProvider>
        <CollectionSidebar />
      </CollectionProvider>
    );

    const selectedCollection = screen.getByText('collection-1').closest('.group');
    expect(selectedCollection).toHaveClass('bg-blue-50');
  });

  it('should call selectCollection when clicking on collection', async () => {
    const mockSelectCollection = vi.fn();
    
    mockUseCollectionOperations.mockReturnValue({
      state: {
        ...defaultMockState,
        collections: mockCollections,
      },
      ...defaultMockOperations,
      selectCollection: mockSelectCollection,
    });

    render(
      <CollectionProvider>
        <CollectionSidebar />
      </CollectionProvider>
    );

    fireEvent.click(screen.getByText('collection-1'));
    expect(mockSelectCollection).toHaveBeenCalledWith('collection-1');
  });

  it('should call openModal when clicking New button', async () => {
    const mockOpenModal = vi.fn();
    
    mockUseCollectionOperations.mockReturnValue({
      state: defaultMockState,
      ...defaultMockOperations,
      openModal: mockOpenModal,
    });

    render(
      <CollectionProvider>
        <CollectionSidebar />
      </CollectionProvider>
    );

    fireEvent.click(screen.getByText('New'));
    expect(mockOpenModal).toHaveBeenCalledWith('newCollection');
  });

  it('should display error message when error exists', () => {
    mockUseCollectionOperations.mockReturnValue({
      state: {
        ...defaultMockState,
        ui: {
          ...defaultMockState.ui,
          error: 'Failed to load collections',
        },
      },
      ...defaultMockOperations,
    });

    render(
      <CollectionProvider>
        <CollectionSidebar />
      </CollectionProvider>
    );

    expect(screen.getByText('Failed to load collections')).toBeInTheDocument();
  });

  it('should call clearError when clicking dismiss error button', async () => {
    const mockClearError = vi.fn();
    
    mockUseCollectionOperations.mockReturnValue({
      state: {
        ...defaultMockState,
        ui: {
          ...defaultMockState.ui,
          error: 'Test error message',
        },
      },
      ...defaultMockOperations,
      clearError: mockClearError,
    });

    render(
      <CollectionProvider>
        <CollectionSidebar />
      </CollectionProvider>
    );

    const dismissButton = screen.getByRole('button', { name: /dismiss/i });
    fireEvent.click(dismissButton);
    
    expect(mockClearError).toHaveBeenCalled();
  });

  it('should apply custom className', () => {
    const { container } = render(
      <CollectionProvider>
        <CollectionSidebar className="custom-class" />
      </CollectionProvider>
    );

    expect(container.firstChild).toHaveClass('custom-class');
  });

  it('should load collections on mount', () => {
    const mockLoadCollections = vi.fn();
    
    mockUseCollectionOperations.mockReturnValue({
      state: defaultMockState,
      ...defaultMockOperations,
      loadCollections: mockLoadCollections,
    });

    render(
      <CollectionProvider>
        <CollectionSidebar />
      </CollectionProvider>
    );

    expect(mockLoadCollections).toHaveBeenCalled();
  });
});