import { useCallback, useEffect, useRef } from 'react';
import { useCollection } from '../contexts/CollectionContext';
import { APIService } from '../services/api';
import type { 
  VectorSyncStatus, 
  VectorSearchRequest, 
  SyncCollectionRequest,
  VectorSearchResult 
} from '../types/api';
import {
  CollectionNotFoundError,
  ServiceUnavailableError,
  SyncFailedError,
  InvalidFileExtensionError,
} from '../types/api';

interface UseVectorSyncReturn {
  // State
  syncStatuses: Record<string, VectorSyncStatus>;
  searchResults: VectorSearchResult[];
  searchQuery: string;
  searchLoading: boolean;
  
  // Actions
  getSyncStatus: (collectionId: string) => VectorSyncStatus | undefined;
  refreshSyncStatus: (collectionId: string) => Promise<void>;
  refreshAllSyncStatuses: () => Promise<void>;
  syncCollection: (collectionId: string, request?: SyncCollectionRequest) => Promise<void>;
  deleteVectors: (collectionId: string) => Promise<void>;
  searchVectors: (query: string, collectionId?: string) => Promise<void>;
  clearSearch: () => void;
  
  // Utilities
  canSync: (collectionId: string) => boolean;
  needsSync: (collectionId: string) => boolean;
  isSyncing: (collectionId: string) => boolean;
}

// Helper function to create user-friendly error messages
const getErrorMessage = (error: unknown): string => {
  if (error instanceof CollectionNotFoundError) {
    return 'Collection not found - it may have been deleted';
  } else if (error instanceof ServiceUnavailableError) {
    return 'Vector search is not available. Please install RAG dependencies.';
  } else if (error instanceof SyncFailedError) {
    return `Sync failed: ${error.message}`;
  } else if (error instanceof InvalidFileExtensionError) {
    return `File upload failed: ${error.message}`;
  } else if (error instanceof Error) {
    return error.message;
  } else {
    return 'An unexpected error occurred';
  }
};

export const useVectorSync = (): UseVectorSyncReturn => {
  const { state, dispatch } = useCollection();
  const { vectorSync, ui } = state;
  
  // Track active polling intervals for sync operations
  const pollingIntervals = useRef<Map<string, NodeJS.Timeout>>(new Map());

  // Utility functions for polling management
  const startPolling = useCallback((collectionId: string, pollFunction: () => void, interval: number = 3000) => {
    // Clear any existing polling first
    const existingInterval = pollingIntervals.current.get(collectionId);
    if (existingInterval) {
      clearInterval(existingInterval);
      pollingIntervals.current.delete(collectionId);
    }
    
    const intervalId = setInterval(pollFunction, interval);
    pollingIntervals.current.set(collectionId, intervalId);
  }, []);

  const stopPolling = useCallback((collectionId: string) => {
    const intervalId = pollingIntervals.current.get(collectionId);
    if (intervalId) {
      clearInterval(intervalId);
      pollingIntervals.current.delete(collectionId);
    }
  }, []);

  // Cleanup all polling on unmount
  useEffect(() => {
    const currentIntervals = pollingIntervals.current;
    return () => {
      currentIntervals.forEach((intervalId) => clearInterval(intervalId));
      currentIntervals.clear();
    };
  }, []);

  // Get sync status for a collection
  const getSyncStatus = useCallback((collectionId: string): VectorSyncStatus | undefined => {
    return vectorSync.statuses[collectionId];
  }, [vectorSync.statuses]);

  // Refresh sync status for a specific collection
  const refreshSyncStatus = useCallback(async (collectionId: string) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: { key: 'vectorSync', value: true } });
      
      const status = await APIService.getCollectionSyncStatus(collectionId);
      dispatch({ 
        type: 'SET_VECTOR_SYNC_STATUS', 
        payload: { collectionName: collectionId, status } 
      });
    } catch (error) {
      dispatch({ 
        type: 'SET_ERROR', 
        payload: getErrorMessage(error) 
      });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: { key: 'vectorSync', value: false } });
    }
  }, [dispatch]);

  // Refresh sync statuses for all collections
  const refreshAllSyncStatuses = useCallback(async () => {
    try {
      dispatch({ type: 'SET_LOADING', payload: { key: 'vectorSync', value: true } });
      
      const statuses = await APIService.listCollectionSyncStatuses();
      dispatch({ type: 'SET_VECTOR_SYNC_STATUSES', payload: statuses });
    } catch (error) {
      dispatch({ 
        type: 'SET_ERROR', 
        payload: getErrorMessage(error) 
      });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: { key: 'vectorSync', value: false } });
    }
  }, [dispatch]);

  // Sync a collection
  const syncCollection = useCallback(async (
    collectionId: string, 
    request: SyncCollectionRequest = {}
  ) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: { key: 'vectorSync', value: true } });
      
      // Set syncing status immediately
      const currentStatus = getSyncStatus(collectionId);
      if (currentStatus) {
        dispatch({
          type: 'SET_VECTOR_SYNC_STATUS',
          payload: {
            collectionName: collectionId,
            status: { ...currentStatus, status: 'syncing', sync_progress: 0 }
          }
        });
      }

      // Start sync operation
      await APIService.syncCollection(collectionId, request);
      
      // Start real-time polling for progress updates
      const pollSyncProgress = async () => {
        try {
          const status = await APIService.getCollectionSyncStatus(collectionId);
          dispatch({ 
            type: 'SET_VECTOR_SYNC_STATUS', 
            payload: { collectionName: collectionId, status } 
          });
          
          // Stop polling if sync is complete or failed
          if (status.status !== 'syncing') {
            stopPolling(collectionId);
          }
        } catch (error) {
          console.error('Error polling sync progress:', error);
          stopPolling(collectionId);
        }
      };

      // Start polling every 2 seconds for real-time updates
      startPolling(collectionId, pollSyncProgress, 2000);
      
    } catch (error) {
      dispatch({ 
        type: 'SET_ERROR', 
        payload: getErrorMessage(error) 
      });
      
      // Reset status on error
      await refreshSyncStatus(collectionId);
    } finally {
      dispatch({ type: 'SET_LOADING', payload: { key: 'vectorSync', value: false } });
    }
  }, [dispatch, getSyncStatus, refreshSyncStatus, startPolling, stopPolling]);

  // Note: Enable/disable sync functions removed - sync is now manual trigger only

  // Delete vectors for a collection
  const deleteVectors = useCallback(async (collectionId: string) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: { key: 'vectorSync', value: true } });
      
      // Stop any active polling for this collection
      stopPolling(collectionId);
      
      await APIService.deleteCollectionVectors(collectionId);
      await refreshSyncStatus(collectionId);
    } catch (error) {
      dispatch({ 
        type: 'SET_ERROR', 
        payload: getErrorMessage(error) 
      });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: { key: 'vectorSync', value: false } });
    }
  }, [dispatch, refreshSyncStatus, stopPolling]);

  // Search vectors
  const searchVectors = useCallback(async (query: string, collectionId?: string) => {
    if (!query.trim()) {
      dispatch({ type: 'CLEAR_VECTOR_SEARCH' });
      return;
    }

    try {
      dispatch({ type: 'SET_LOADING', payload: { key: 'vectorSearch', value: true } });
      dispatch({ type: 'SET_VECTOR_SEARCH_QUERY', payload: query });
      
      const request: VectorSearchRequest = {
        query: query.trim(),
        collection_name: collectionId,
        limit: 20
      };
      
      const response = await APIService.searchVectors(request);
      dispatch({ type: 'SET_VECTOR_SEARCH_RESULTS', payload: response.results });
    } catch (error) {
      dispatch({ 
        type: 'SET_ERROR', 
        payload: getErrorMessage(error) 
      });
      dispatch({ type: 'SET_VECTOR_SEARCH_RESULTS', payload: [] });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: { key: 'vectorSearch', value: false } });
    }
  }, [dispatch]);

  // Clear search
  const clearSearch = useCallback(() => {
    dispatch({ type: 'CLEAR_VECTOR_SEARCH' });
  }, [dispatch]);

  // Utility functions
  const canSync = useCallback((collectionId: string): boolean => {
    const status = getSyncStatus(collectionId);
    if (!status) return false;
    return status.sync_enabled && status.status !== 'syncing';
  }, [getSyncStatus]);

  const needsSync = useCallback((collectionId: string): boolean => {
    const status = getSyncStatus(collectionId);
    if (!status) return false;
    return status.status === 'out_of_sync' || status.status === 'never_synced';
  }, [getSyncStatus]);

  const isSyncing = useCallback((collectionId: string): boolean => {
    const status = getSyncStatus(collectionId);
    return status?.status === 'syncing' || false;
  }, [getSyncStatus]);

  // Load sync statuses on mount or when collections change
  useEffect(() => {
    if (state.collections.length > 0) {
      refreshAllSyncStatuses();
    }
  }, [state.collections.length, refreshAllSyncStatuses]);

  return {
    // State
    syncStatuses: vectorSync.statuses,
    searchResults: vectorSync.searchResults,
    searchQuery: vectorSync.searchQuery,
    searchLoading: ui.loading.vectorSearch,
    
    // Actions
    getSyncStatus,
    refreshSyncStatus,
    refreshAllSyncStatuses,
    syncCollection,
    deleteVectors,
    searchVectors,
    clearSearch,
    
    // Utilities
    canSync,
    needsSync,
    isSyncing,
  };
};

export default useVectorSync;