import React, { createContext, useContext, useReducer } from 'react';
import type { ReactNode } from 'react';
import type { FileCollection, FileMetadata, VectorSyncStatus } from '../types/api';

// State Types
export interface FileNode {
  name: string;
  path: string;
  type: 'file';
  metadata: FileMetadata;
}

export interface FolderNode {
  name: string;
  path: string;
  type: 'folder';
  children: (FileNode | FolderNode)[];
}

export interface EditorState {
  filePath: string | null;
  content: string;
  originalContent: string;
  modified: boolean;
  saving: boolean;
}

export interface CollectionState {
  // Collections data
  collections: FileCollection[];
  selectedCollection: string | null;
  
  // File tree data
  files: FileNode[];
  folders: FolderNode[];
  
  // Editor state
  editor: EditorState;
  
  // Vector sync state
  vectorSync: {
    statuses: Record<string, VectorSyncStatus>; // collectionName -> status
  };
  
  // UI state
  ui: {
    loading: {
      collections: boolean;
      files: boolean;
      saving: boolean;
      crawling: boolean;
      vectorSync: boolean;
    };
    modals: {
      newCollection: boolean;
      addPage: boolean;
      addMultiplePages: boolean;
      newFile: boolean;
      deleteConfirmation: { open: boolean; type: 'collection' | 'file'; target: string | null };
      vectorSearch: boolean;
    };
    error: string | null;
  };
}

// Initial State
const initialState: CollectionState = {
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
  vectorSync: {
    statuses: {},
  },
  ui: {
    loading: {
      collections: false,
      files: false,
      saving: false,
      crawling: false,
      vectorSync: false,
    },
    modals: {
      newCollection: false,
      addPage: false,
      addMultiplePages: false,
      newFile: false,
      deleteConfirmation: { open: false, type: 'collection', target: null },
      vectorSearch: false,
    },
    error: null,
  },
};

// Action Types
export type CollectionAction =
  // Collection actions
  | { type: 'SET_COLLECTIONS'; payload: FileCollection[] }
  | { type: 'ADD_COLLECTION'; payload: FileCollection }
  | { type: 'REMOVE_COLLECTION'; payload: string }
  | { type: 'SELECT_COLLECTION'; payload: string | null }
  
  // File actions
  | { type: 'SET_FILES'; payload: { files: FileNode[]; folders: FolderNode[] } }
  | { type: 'ADD_FILE'; payload: FileNode }
  | { type: 'REMOVE_FILE'; payload: string }
  | { type: 'UPDATE_FILE'; payload: { path: string; metadata: FileMetadata } }
  
  // Editor actions
  | { type: 'OPEN_FILE'; payload: { path: string; content: string } }
  | { type: 'CLOSE_FILE' }
  | { type: 'UPDATE_CONTENT'; payload: string }
  | { type: 'SET_SAVING'; payload: boolean }
  | { type: 'SAVE_SUCCESS'; payload: string }
  
  // Loading actions
  | { type: 'SET_LOADING'; payload: { key: keyof CollectionState['ui']['loading']; value: boolean } }
  
  // Modal actions
  | { type: 'OPEN_MODAL'; payload: keyof CollectionState['ui']['modals'] }
  | { type: 'CLOSE_MODAL'; payload: keyof CollectionState['ui']['modals'] }
  | { type: 'OPEN_DELETE_CONFIRMATION'; payload: { type: 'collection' | 'file'; target: string } }
  | { type: 'CLOSE_DELETE_CONFIRMATION' }
  
  // Error actions
  | { type: 'SET_ERROR'; payload: string | null }
  
  // Vector sync actions
  | { type: 'SET_VECTOR_SYNC_STATUS'; payload: { collectionName: string; status: VectorSyncStatus } }
  | { type: 'SET_VECTOR_SYNC_STATUSES'; payload: Record<string, VectorSyncStatus> }
  | { type: 'UPDATE_SYNC_PROGRESS'; payload: { collectionName: string; progress: number; message?: string } };

// Reducer
function collectionReducer(state: CollectionState, action: CollectionAction): CollectionState {
  switch (action.type) {
    case 'SET_COLLECTIONS':
      return {
        ...state,
        collections: action.payload,
      };
      
    case 'ADD_COLLECTION':
      return {
        ...state,
        collections: [...state.collections, action.payload],
      };
      
    case 'REMOVE_COLLECTION':
      return {
        ...state,
        collections: state.collections.filter(c => c.id !== action.payload),
        selectedCollection: state.selectedCollection === action.payload ? null : state.selectedCollection,
      };
      
    case 'SELECT_COLLECTION':
      return {
        ...state,
        selectedCollection: action.payload,
        // Clear files when switching collections
        files: [],
        folders: [],
        // Close editor when switching collections
        editor: {
          ...initialState.editor,
        },
      };
      
    case 'SET_FILES':
      return {
        ...state,
        files: action.payload.files,
        folders: action.payload.folders,
      };
      
    case 'ADD_FILE':
      return {
        ...state,
        files: [...state.files, action.payload],
      };
      
    case 'REMOVE_FILE':
      return {
        ...state,
        files: state.files.filter(f => f.path !== action.payload),
        // Close editor if the deleted file was open
        editor: state.editor.filePath === action.payload ? initialState.editor : state.editor,
      };
      
    case 'UPDATE_FILE':
      return {
        ...state,
        files: state.files.map(f => 
          f.path === action.payload.path 
            ? { ...f, metadata: action.payload.metadata }
            : f
        ),
      };
      
    case 'OPEN_FILE':
      return {
        ...state,
        editor: {
          filePath: action.payload.path,
          content: action.payload.content,
          originalContent: action.payload.content,
          modified: false,
          saving: false,
        },
      };
      
    case 'CLOSE_FILE':
      return {
        ...state,
        editor: initialState.editor,
      };
      
    case 'UPDATE_CONTENT':
      return {
        ...state,
        editor: {
          ...state.editor,
          content: action.payload,
          modified: action.payload !== state.editor.originalContent,
        },
      };
      
    case 'SET_SAVING':
      return {
        ...state,
        editor: {
          ...state.editor,
          saving: action.payload,
        },
      };
      
    case 'SAVE_SUCCESS':
      return {
        ...state,
        editor: {
          ...state.editor,
          originalContent: action.payload,
          modified: false,
          saving: false,
        },
      };
      
    case 'SET_LOADING':
      return {
        ...state,
        ui: {
          ...state.ui,
          loading: {
            ...state.ui.loading,
            [action.payload.key]: action.payload.value,
          },
        },
      };
      
    case 'OPEN_MODAL':
      return {
        ...state,
        ui: {
          ...state.ui,
          modals: {
            ...state.ui.modals,
            [action.payload]: true,
          },
        },
      };
      
    case 'CLOSE_MODAL':
      return {
        ...state,
        ui: {
          ...state.ui,
          modals: {
            ...state.ui.modals,
            [action.payload]: false,
          },
        },
      };
      
    case 'OPEN_DELETE_CONFIRMATION':
      return {
        ...state,
        ui: {
          ...state.ui,
          modals: {
            ...state.ui.modals,
            deleteConfirmation: {
              open: true,
              type: action.payload.type,
              target: action.payload.target,
            },
          },
        },
      };
      
    case 'CLOSE_DELETE_CONFIRMATION':
      return {
        ...state,
        ui: {
          ...state.ui,
          modals: {
            ...state.ui.modals,
            deleteConfirmation: {
              open: false,
              type: 'collection',
              target: null,
            },
          },
        },
      };
      
    case 'SET_ERROR':
      return {
        ...state,
        ui: {
          ...state.ui,
          error: action.payload,
        },
      };

    // Vector sync cases
    case 'SET_VECTOR_SYNC_STATUS':
      return {
        ...state,
        vectorSync: {
          ...state.vectorSync,
          statuses: {
            ...state.vectorSync.statuses,
            [action.payload.collectionName]: action.payload.status,
          },
        },
      };

    case 'SET_VECTOR_SYNC_STATUSES':
      return {
        ...state,
        vectorSync: {
          ...state.vectorSync,
          statuses: action.payload,
        },
      };

    case 'UPDATE_SYNC_PROGRESS': {
      const currentStatus = state.vectorSync.statuses[action.payload.collectionName];
      if (currentStatus) {
        return {
          ...state,
          vectorSync: {
            ...state.vectorSync,
            statuses: {
              ...state.vectorSync.statuses,
              [action.payload.collectionName]: {
                ...currentStatus,
                sync_progress: action.payload.progress,
                status: action.payload.progress < 1.0 ? 'syncing' : 'in_sync',
              },
            },
          },
        };
      }
      return state;
    }
      
    default:
      return state;
  }
}

// Context
interface CollectionContextType {
  state: CollectionState;
  dispatch: React.Dispatch<CollectionAction>;
}

const CollectionContext = createContext<CollectionContextType | undefined>(undefined);

// Provider
interface CollectionProviderProps {
  children: ReactNode;
}

export function CollectionProvider({ children }: CollectionProviderProps) {
  const [state, dispatch] = useReducer(collectionReducer, initialState);

  return (
    <CollectionContext.Provider value={{ state, dispatch }}>
      {children}
    </CollectionContext.Provider>
  );
}

// Hook
export function useCollection() {
  const context = useContext(CollectionContext);
  if (context === undefined) {
    throw new Error('useCollection must be used within a CollectionProvider');
  }
  return context;
}

export default CollectionContext;