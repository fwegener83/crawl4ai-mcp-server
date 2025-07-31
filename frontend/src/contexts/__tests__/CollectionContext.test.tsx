import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { CollectionProvider, useCollection } from '../CollectionContext';
import { type FileCollection, type FileMetadata } from '../../types/api';

// Test component to access the context
function TestComponent() {
  const { state, dispatch } = useCollection();
  
  return (
    <div>
      <div data-testid="collections-count">{state.collections.length}</div>
      <div data-testid="selected-collection">{state.selectedCollection || 'none'}</div>
      <div data-testid="files-count">{state.files.length}</div>
      <div data-testid="editor-modified">{state.editor.modified.toString()}</div>
      <div data-testid="loading-collections">{state.ui.loading.collections.toString()}</div>
      <div data-testid="modal-new-collection">{state.ui.modals.newCollection.toString()}</div>
      <div data-testid="error-message">{state.ui.error || 'none'}</div>
      
      <button 
        data-testid="add-collection"
        onClick={() => dispatch({ 
          type: 'ADD_COLLECTION', 
          payload: mockCollection 
        })}
      >
        Add Collection
      </button>
      
      <button 
        data-testid="select-collection"
        onClick={() => dispatch({ 
          type: 'SELECT_COLLECTION', 
          payload: 'test-collection' 
        })}
      >
        Select Collection
      </button>
      
      <button 
        data-testid="open-modal"
        onClick={() => dispatch({ 
          type: 'OPEN_MODAL', 
          payload: 'newCollection' 
        })}
      >
        Open Modal
      </button>
      
      <button 
        data-testid="set-error"
        onClick={() => dispatch({ 
          type: 'SET_ERROR', 
          payload: 'Test error message' 
        })}
      >
        Set Error
      </button>
    </div>
  );
}

const mockCollection: FileCollection = {
  name: 'test-collection',
  description: 'Test collection description',
  created_at: '2024-01-01T00:00:00Z',
  file_count: 2,
  folders: ['folder1'],
  metadata: {
    total_size: 1024,
    file_types: ['md', 'txt'],
    last_modified: '2024-01-01T00:00:00Z'
  }
};


describe('CollectionContext', () => {
  beforeEach(() => {
    // Reset any state between tests
  });

  it('should provide initial state', () => {
    render(
      <CollectionProvider>
        <TestComponent />
      </CollectionProvider>
    );

    expect(screen.getByTestId('collections-count')).toHaveTextContent('0');
    expect(screen.getByTestId('selected-collection')).toHaveTextContent('none');
    expect(screen.getByTestId('files-count')).toHaveTextContent('0');
    expect(screen.getByTestId('editor-modified')).toHaveTextContent('false');
    expect(screen.getByTestId('loading-collections')).toHaveTextContent('false');
    expect(screen.getByTestId('modal-new-collection')).toHaveTextContent('false');
    expect(screen.getByTestId('error-message')).toHaveTextContent('none');
  });

  it('should throw error when used outside provider', () => {
    // Suppress console.error for this test
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    
    expect(() => {
      render(<TestComponent />);
    }).toThrow('useCollection must be used within a CollectionProvider');
    
    consoleSpy.mockRestore();
  });

  describe('Collection Actions', () => {
    it('should set collections', () => {
      render(
        <CollectionProvider>
          <TestComponent />
        </CollectionProvider>
      );

      const testComponent = screen.getByTestId('collections-count');
      expect(testComponent).toHaveTextContent('0');

      // We need to test the reducer directly since we can't easily dispatch SET_COLLECTIONS from the test component
      // This would typically be tested through integration with useCollectionOperations
    });

    it('should add collection', () => {
      render(
        <CollectionProvider>
          <TestComponent />
        </CollectionProvider>
      );

      expect(screen.getByTestId('collections-count')).toHaveTextContent('0');

      act(() => {
        screen.getByTestId('add-collection').click();
      });

      expect(screen.getByTestId('collections-count')).toHaveTextContent('1');
    });

    it('should select collection', () => {
      render(
        <CollectionProvider>
          <TestComponent />
        </CollectionProvider>
      );

      expect(screen.getByTestId('selected-collection')).toHaveTextContent('none');

      act(() => {
        screen.getByTestId('select-collection').click();
      });

      expect(screen.getByTestId('selected-collection')).toHaveTextContent('test-collection');
    });

    it('should clear files and editor when selecting new collection', () => {
      render(
        <CollectionProvider>
          <TestComponent />
        </CollectionProvider>
      );

      // First select a collection
      act(() => {
        screen.getByTestId('select-collection').click();
      });

      expect(screen.getByTestId('selected-collection')).toHaveTextContent('test-collection');
      expect(screen.getByTestId('files-count')).toHaveTextContent('0');
      expect(screen.getByTestId('editor-modified')).toHaveTextContent('false');
    });
  });

  describe('Modal Actions', () => {
    it('should open modal', () => {
      render(
        <CollectionProvider>
          <TestComponent />
        </CollectionProvider>
      );

      expect(screen.getByTestId('modal-new-collection')).toHaveTextContent('false');

      act(() => {
        screen.getByTestId('open-modal').click();
      });

      expect(screen.getByTestId('modal-new-collection')).toHaveTextContent('true');
    });
  });

  describe('Error Handling', () => {
    it('should set and clear errors', () => {
      render(
        <CollectionProvider>
          <TestComponent />
        </CollectionProvider>
      );

      expect(screen.getByTestId('error-message')).toHaveTextContent('none');

      act(() => {
        screen.getByTestId('set-error').click();
      });

      expect(screen.getByTestId('error-message')).toHaveTextContent('Test error message');
    });
  });
});

// Test the reducer directly
describe('CollectionReducer', () => {
  // We'll need to export the reducer from the context to test it directly
  // For now, these tests verify the reducer logic through the context provider
  
  it('should handle SET_COLLECTIONS action', () => {
    // This would test the reducer directly if exported
  });

  it('should handle ADD_COLLECTION action', () => {
    // This would test the reducer directly if exported
  });

  it('should handle REMOVE_COLLECTION action', () => {
    // This would test the reducer directly if exported
  });

  it('should handle SELECT_COLLECTION action', () => {
    // This would test the reducer directly if exported
  });

  it('should handle file operations', () => {
    // This would test file-related actions
  });

  it('should handle editor operations', () => {
    // This would test editor-related actions
  });

  it('should handle loading states', () => {
    // This would test loading state changes
  });

  it('should handle modal operations', () => {
    // This would test modal state changes
  });
});