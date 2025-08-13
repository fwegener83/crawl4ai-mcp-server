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
  const pollingSafeguards = useRef<Map<string, { startTime: number; attempts: number }>>(new Map());

  // UNIFIED RECOVERY FUNCTION - prevent multiple recovery functions per collection
  const createRecoveryPollingFunction = useCallback((collectionId: string) => {
    return async () => {
      try {
        console.log(`🔄 Recovery polling check for ${collectionId}`);
        const currentStatus = await APIService.getCollectionSyncStatus(collectionId);
        
        dispatch({ 
          type: 'SET_VECTOR_SYNC_STATUS', 
          payload: { collectionName: collectionId, status: currentStatus } 
        });
        
        // Stop recovery polling if sync is complete or failed
        if (currentStatus.status !== 'syncing') {
          console.log(`✅ Recovery complete for ${collectionId}, final status: ${currentStatus.status}`);
          stopPolling(collectionId);
          return;
        }

        // Check safeguards for recovery polling
        const safeguard = pollingSafeguards.current.get(collectionId);
        if (safeguard) {
          const elapsed = Date.now() - safeguard.startTime;
          const maxTime = 5 * 60 * 1000; // 5 minutes for recovery
          const maxAttempts = 30; // 30 attempts = 5 minutes at 10s intervals
          
          if (elapsed > maxTime || safeguard.attempts > maxAttempts) {
            console.warn(`⏰ Recovery timeout for ${collectionId}: ${elapsed}ms elapsed, ${safeguard.attempts} attempts`);
            console.log(`🔧 Forcing status reset for stuck collection ${collectionId}`);
            
            // Force status reset for permanently stuck collections
            dispatch({
              type: 'SET_VECTOR_SYNC_STATUS',
              payload: {
                collectionName: collectionId,
                status: { ...currentStatus, status: 'sync_error' }
              }
            });
            
            stopPolling(collectionId);
            return;
          }
        }
        
      } catch (error) {
        console.error(`❌ Recovery polling failed for ${collectionId}:`, error);
        stopPolling(collectionId);
      }
    };
  }, [dispatch]);

  // Utility functions for polling management
  const startPolling = useCallback((collectionId: string, pollFunction: () => void, interval: number = 10000) => {
    console.log('🟢 Starting polling for', collectionId, 'every', interval, 'ms');
    
    // Clear any existing polling first
    const existingInterval = pollingIntervals.current.get(collectionId);
    if (existingInterval) {
      console.log('🔄 Clearing existing polling for', collectionId);
      clearInterval(existingInterval);
      pollingIntervals.current.delete(collectionId);
    }
    
    const intervalId = setInterval(pollFunction, interval);
    pollingIntervals.current.set(collectionId, intervalId);
    console.log('✅ Polling started for', collectionId, 'with interval ID:', intervalId);
  }, []);

  const stopPolling = useCallback((collectionId: string) => {
    const intervalId = pollingIntervals.current.get(collectionId);
    if (intervalId) {
      console.log('🛑 Stopping polling for', collectionId, 'interval ID:', intervalId);
      clearInterval(intervalId);
      pollingIntervals.current.delete(collectionId);
    } else {
      console.log('⚠️ No active polling found for', collectionId);
    }
    // Clear safeguards too
    pollingSafeguards.current.delete(collectionId);
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
      console.log('🔄 Refreshing all sync statuses...');
      dispatch({ type: 'SET_LOADING', payload: { key: 'vectorSync', value: true } });
      
      const statuses = await APIService.listCollectionSyncStatuses();
      console.log('📊 Received statuses:', statuses);
      
      // COMPREHENSIVE RECOVERY: Check ALL collections for orphaned "syncing" status - NOT just first one
      const orphanedCollections = Object.entries(statuses).filter(([collectionId, status]) => {
        if (status.status === 'syncing') {
          const hasActivePolling = pollingIntervals.current.has(collectionId);
          console.log(`🔍 Collection ${collectionId} is syncing, active polling: ${hasActivePolling}`);
          
          if (!hasActivePolling) {
            console.warn(`⚠️ ORPHANED: Collection ${collectionId} shows "syncing" but has no active polling!`);
            return true; // Mark as orphaned
          }
        }
        return false;
      });

      // Start recovery polling for ALL orphaned collections
      if (orphanedCollections.length > 0) {
        console.log(`🚀 COMPREHENSIVE RECOVERY: Starting polling for ${orphanedCollections.length} orphaned collections:`, 
                   orphanedCollections.map(([id]) => id));
        
        orphanedCollections.forEach(([collectionId]) => {          
          // Initialize safeguards for recovery polling
          pollingSafeguards.current.set(collectionId, { 
            startTime: Date.now(), 
            attempts: 0 
          });
          
          // Use UNIFIED recovery function to prevent conflicts
          const recoveryFunction = createRecoveryPollingFunction(collectionId);
          
          // Start recovery polling immediately, then every 10s
          recoveryFunction();
          startPolling(collectionId, recoveryFunction, 10000);
        });
      }
      
      dispatch({ type: 'SET_VECTOR_SYNC_STATUSES', payload: statuses });
    } catch (error) {
      console.error('❌ Failed to refresh sync statuses:', error);
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
      
      // Start intelligent polling with safeguards
      const pollSyncProgress = async () => {
        try {
          // Get or initialize safeguard data - with proper initialization
          let safeguard = pollingSafeguards.current.get(collectionId);
          if (!safeguard) {
            safeguard = { startTime: Date.now(), attempts: 0 };
            pollingSafeguards.current.set(collectionId, safeguard);
          }
          safeguard.attempts += 1;
          
          // Safety checks: Stop polling after 2 minutes or 12 attempts
          const elapsed = Date.now() - safeguard.startTime;
          const maxTime = 2 * 60 * 1000; // 2 minutes
          const maxAttempts = 12; // 12 attempts = 2 minutes at 10s intervals
          
          if (elapsed > maxTime || safeguard.attempts > maxAttempts) {
            console.warn(`Stopping polling for ${collectionId}: timeout or max attempts reached`);
            stopPolling(collectionId);
            return;
          }
          
          const status = await APIService.getCollectionSyncStatus(collectionId);
          dispatch({ 
            type: 'SET_VECTOR_SYNC_STATUS', 
            payload: { collectionName: collectionId, status } 
          });
          
          // Stop polling if sync is complete or failed
          if (status.status !== 'syncing') {
            console.log(`Sync completed for ${collectionId}, status: ${status.status}`);
            stopPolling(collectionId);
          }
        } catch (error) {
          console.error('Error polling sync progress:', error);
          stopPolling(collectionId);
        }
      };

      // Initialize safeguards and start polling
      pollingSafeguards.current.set(collectionId, { 
        startTime: Date.now(), 
        attempts: 0 
      });
      startPolling(collectionId, pollSyncProgress, 10000);
      
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
      console.log('🔄 Loading sync statuses for', state.collections.length, 'collections');
      refreshAllSyncStatuses();
    }
  }, [state.collections.length, refreshAllSyncStatuses]);

  // Debug: Log active polling intervals + Continuous orphaned detection
  useEffect(() => {
    const interval = setInterval(async () => {
      const activePolling = Array.from(pollingIntervals.current.keys());
      const activeSafeguards = Array.from(pollingSafeguards.current.entries());
      
      if (activePolling.length > 0) {
        console.log('🟡 Active polling:', activePolling);
        console.log('🛡️ Safeguards:', activeSafeguards);
      }
      
      // CONTINUOUS ORPHANED DETECTION: Check every 30s for new orphaned collections
      try {
        const currentStatuses = await APIService.listCollectionSyncStatuses();
        const newOrphanedCollections = Object.entries(currentStatuses).filter(([collectionId, status]) => {
          if (status.status === 'syncing') {
            const hasActivePolling = pollingIntervals.current.has(collectionId);
            if (!hasActivePolling) {
              console.warn(`🆘 CONTINUOUS DETECTION: Found new orphaned collection ${collectionId}`);
              return true;
            }
          }
          return false;
        });
        
        // Start polling for newly discovered orphaned collections
        if (newOrphanedCollections.length > 0) {
          console.log(`🔄 CONTINUOUS RECOVERY: Starting polling for ${newOrphanedCollections.length} newly discovered orphaned collections`);
          
          newOrphanedCollections.forEach(([collectionId]) => {
            // Initialize safeguards for continuous recovery  
            pollingSafeguards.current.set(collectionId, { 
              startTime: Date.now(), 
              attempts: 0 
            });
            
            // Use UNIFIED recovery function to prevent conflicts with initial recovery
            const recoveryFunction = createRecoveryPollingFunction(collectionId);
            
            recoveryFunction();
            startPolling(collectionId, recoveryFunction, 10000);
          });
        }
        
      } catch (error) {
        console.error('❌ Continuous orphaned detection failed:', error);
      }
    }, 30000); // Check every 30 seconds
    
    return () => clearInterval(interval);
  }, [dispatch, startPolling, stopPolling, createRecoveryPollingFunction]);

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