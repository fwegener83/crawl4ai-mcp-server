import { useCallback, useEffect, useRef } from 'react';
import { useCollection } from '../contexts/CollectionContext';
import { APIService } from '../services/api';
import type { 
  VectorSyncStatus, 
  VectorSearchRequest, 
  SyncCollectionRequest,
  VectorSearchResult 
} from '../types/api';

interface UseVectorSyncReturn {
  // State
  syncStatuses: Record<string, VectorSyncStatus>;
  searchResults: VectorSearchResult[];
  searchQuery: string;
  searchLoading: boolean;
  
  // Actions
  getSyncStatus: (collectionName: string) => VectorSyncStatus | undefined;
  refreshSyncStatus: (collectionName: string) => Promise<void>;
  refreshAllSyncStatuses: () => Promise<void>;
  syncCollection: (collectionName: string, request?: SyncCollectionRequest) => Promise<void>;
  enableSync: (collectionName: string) => Promise<void>;
  disableSync: (collectionName: string) => Promise<void>;
  deleteVectors: (collectionName: string) => Promise<void>;
  searchVectors: (query: string, collectionName?: string) => Promise<void>;
  clearSearch: () => void;
  
  // Utilities
  canSync: (collectionName: string) => boolean;
  needsSync: (collectionName: string) => boolean;
  isSyncing: (collectionName: string) => boolean;
}

export const useVectorSync = (): UseVectorSyncReturn => {
  const { state, dispatch } = useCollection();
  const { vectorSync, ui } = state;
  
  // Track active polling intervals for sync operations
  const pollingIntervals = useRef<Map<string, NodeJS.Timeout>>(new Map());

  // Utility functions for polling management
  const startPolling = useCallback((collectionName: string, pollFunction: () => void, interval: number = 3000) => {
    // Clear any existing polling first
    const existingInterval = pollingIntervals.current.get(collectionName);
    if (existingInterval) {
      clearInterval(existingInterval);
      pollingIntervals.current.delete(collectionName);
    }
    
    const intervalId = setInterval(pollFunction, interval);
    pollingIntervals.current.set(collectionName, intervalId);
  }, []);

  const stopPolling = useCallback((collectionName: string) => {
    const intervalId = pollingIntervals.current.get(collectionName);
    if (intervalId) {
      clearInterval(intervalId);
      pollingIntervals.current.delete(collectionName);
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
  const getSyncStatus = useCallback((collectionName: string): VectorSyncStatus | undefined => {
    return vectorSync.statuses[collectionName];
  }, [vectorSync.statuses]);

  // Refresh sync status for a specific collection
  const refreshSyncStatus = useCallback(async (collectionName: string) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: { key: 'vectorSync', value: true } });
      
      const status = await APIService.getCollectionSyncStatus(collectionName);
      dispatch({ 
        type: 'SET_VECTOR_SYNC_STATUS', 
        payload: { collectionName, status } 
      });
    } catch (error) {
      dispatch({ 
        type: 'SET_ERROR', 
        payload: error instanceof Error ? error.message : 'Failed to refresh sync status' 
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
        payload: error instanceof Error ? error.message : 'Failed to refresh sync statuses' 
      });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: { key: 'vectorSync', value: false } });
    }
  }, [dispatch]);

  // Sync a collection
  const syncCollection = useCallback(async (
    collectionName: string, 
    request: SyncCollectionRequest = {}
  ) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: { key: 'vectorSync', value: true } });
      
      // Set syncing status immediately
      const currentStatus = getSyncStatus(collectionName);
      if (currentStatus) {
        dispatch({
          type: 'SET_VECTOR_SYNC_STATUS',
          payload: {
            collectionName,
            status: { ...currentStatus, status: 'syncing', sync_progress: 0 }
          }
        });
      }

      // Start sync operation
      await APIService.syncCollection(collectionName, request);
      
      // Start real-time polling for progress updates
      const pollSyncProgress = async () => {
        try {
          const status = await APIService.getCollectionSyncStatus(collectionName);
          dispatch({ 
            type: 'SET_VECTOR_SYNC_STATUS', 
            payload: { collectionName, status } 
          });
          
          // Stop polling if sync is complete or failed
          if (status.status !== 'syncing') {
            stopPolling(collectionName);
          }
        } catch (error) {
          console.error('Error polling sync progress:', error);
          stopPolling(collectionName);
        }
      };

      // Start polling every 2 seconds for real-time updates
      startPolling(collectionName, pollSyncProgress, 2000);
      
    } catch (error) {
      dispatch({ 
        type: 'SET_ERROR', 
        payload: error instanceof Error ? error.message : 'Failed to sync collection' 
      });
      
      // Reset status on error
      await refreshSyncStatus(collectionName);
    } finally {
      dispatch({ type: 'SET_LOADING', payload: { key: 'vectorSync', value: false } });
    }
  }, [dispatch, getSyncStatus, refreshSyncStatus, startPolling, stopPolling]);

  // Enable sync for a collection
  const enableSync = useCallback(async (collectionName: string) => {
    try {
      await APIService.enableCollectionSync(collectionName);
      await refreshSyncStatus(collectionName);
    } catch (error) {
      dispatch({ 
        type: 'SET_ERROR', 
        payload: error instanceof Error ? error.message : 'Failed to enable sync' 
      });
    }
  }, [dispatch, refreshSyncStatus]);

  // Disable sync for a collection
  const disableSync = useCallback(async (collectionName: string) => {
    try {
      await APIService.disableCollectionSync(collectionName);
      await refreshSyncStatus(collectionName);
    } catch (error) {
      dispatch({ 
        type: 'SET_ERROR', 
        payload: error instanceof Error ? error.message : 'Failed to disable sync' 
      });
    }
  }, [dispatch, refreshSyncStatus]);

  // Delete vectors for a collection
  const deleteVectors = useCallback(async (collectionName: string) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: { key: 'vectorSync', value: true } });
      
      // Stop any active polling for this collection
      stopPolling(collectionName);
      
      await APIService.deleteCollectionVectors(collectionName);
      await refreshSyncStatus(collectionName);
    } catch (error) {
      dispatch({ 
        type: 'SET_ERROR', 
        payload: error instanceof Error ? error.message : 'Failed to delete vectors' 
      });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: { key: 'vectorSync', value: false } });
    }
  }, [dispatch, refreshSyncStatus, stopPolling]);

  // Search vectors
  const searchVectors = useCallback(async (query: string, collectionName?: string) => {
    if (!query.trim()) {
      dispatch({ type: 'CLEAR_VECTOR_SEARCH' });
      return;
    }

    try {
      dispatch({ type: 'SET_LOADING', payload: { key: 'vectorSearch', value: true } });
      dispatch({ type: 'SET_VECTOR_SEARCH_QUERY', payload: query });
      
      const request: VectorSearchRequest = {
        query: query.trim(),
        collection_name: collectionName,
        limit: 20
      };
      
      const response = await APIService.searchVectors(request);
      dispatch({ type: 'SET_VECTOR_SEARCH_RESULTS', payload: response.results });
    } catch (error) {
      dispatch({ 
        type: 'SET_ERROR', 
        payload: error instanceof Error ? error.message : 'Failed to search vectors' 
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
  const canSync = useCallback((collectionName: string): boolean => {
    const status = getSyncStatus(collectionName);
    if (!status) return false;
    return status.sync_enabled && status.status !== 'syncing';
  }, [getSyncStatus]);

  const needsSync = useCallback((collectionName: string): boolean => {
    const status = getSyncStatus(collectionName);
    if (!status) return false;
    return status.status === 'out_of_sync' || status.status === 'never_synced';
  }, [getSyncStatus]);

  const isSyncing = useCallback((collectionName: string): boolean => {
    const status = getSyncStatus(collectionName);
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
    enableSync,
    disableSync,
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