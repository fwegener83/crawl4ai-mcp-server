import { useCallback } from 'react';
import { useCollection } from '../contexts/CollectionContext';
import { APIService } from '../services/api';
import type { 
  VectorSyncStatus, 
  SyncCollectionRequest
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
  
  // Actions
  getSyncStatus: (collectionId: string) => VectorSyncStatus | undefined;
  loadSyncStatuses: () => Promise<void>;
  refreshSyncStatus: (collectionId: string) => Promise<void>;
  syncCollection: (collectionId: string, request?: SyncCollectionRequest) => Promise<void>;
  
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
  const { vectorSync } = state;

  // Get sync status for a collection
  const getSyncStatus = useCallback((collectionId: string): VectorSyncStatus | undefined => {
    return vectorSync.statuses[collectionId];
  }, [vectorSync.statuses]);

  // Load sync statuses for all collections (called when collection is clicked)
  const loadSyncStatuses = useCallback(async () => {
    try {
      console.log('🔄 Loading sync statuses for all collections...');
      dispatch({ type: 'SET_LOADING', payload: { key: 'vectorSync', value: true } });
      
      const statuses = await APIService.listCollectionSyncStatuses();
      console.log('📊 Received statuses:', statuses);
      
      dispatch({ type: 'SET_VECTOR_SYNC_STATUSES', payload: statuses });
    } catch (error) {
      console.error('❌ Failed to load sync statuses:', error);
      dispatch({ 
        type: 'SET_ERROR', 
        payload: getErrorMessage(error) 
      });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: { key: 'vectorSync', value: false } });
    }
  }, [dispatch]);

  // Refresh sync status for a specific collection (manual refresh)
  const refreshSyncStatus = useCallback(async (collectionId: string) => {
    try {
      console.log('🔄 Refreshing sync status for collection:', collectionId);
      dispatch({ type: 'SET_LOADING', payload: { key: 'vectorSync', value: true } });
      
      const status = await APIService.getCollectionSyncStatus(collectionId);
      dispatch({ 
        type: 'SET_VECTOR_SYNC_STATUS', 
        payload: { collectionName: collectionId, status } 
      });
    } catch (error) {
      console.error('❌ Failed to refresh sync status:', error);
      dispatch({ 
        type: 'SET_ERROR', 
        payload: getErrorMessage(error) 
      });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: { key: 'vectorSync', value: false } });
    }
  }, [dispatch]);

  // Sync a collection with simplified strategy
  const syncCollection = useCallback(async (
    collectionId: string, 
    request?: SyncCollectionRequest
  ) => {
    try {
      console.log('🚀 Starting sync for collection:', collectionId);
      dispatch({ type: 'SET_LOADING', payload: { key: 'vectorSync', value: true } });
      
      // Set syncing status immediately for UI feedback
      const currentStatus = getSyncStatus(collectionId);
      if (currentStatus) {
        dispatch({
          type: 'SET_VECTOR_SYNC_STATUS',
          payload: {
            collectionName: collectionId,
            status: { ...currentStatus, status: 'syncing' }
          }
        });
      }

      // Use provided request or default to markdown_intelligent strategy
      const syncRequest = request || {
        chunking_strategy: 'markdown_intelligent',
        force_reprocess: false
      };

      await APIService.syncCollection(collectionId, syncRequest);
      
      // Refresh status after sync completes
      await refreshSyncStatus(collectionId);
      
    } catch (error) {
      console.error('❌ Sync failed:', error);
      dispatch({ 
        type: 'SET_ERROR', 
        payload: getErrorMessage(error) 
      });
      
      // Reset status on error
      await refreshSyncStatus(collectionId);
    } finally {
      dispatch({ type: 'SET_LOADING', payload: { key: 'vectorSync', value: false } });
    }
  }, [dispatch, getSyncStatus, refreshSyncStatus]);

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

  return {
    // State
    syncStatuses: vectorSync.statuses,
    
    // Actions
    getSyncStatus,
    loadSyncStatuses,
    refreshSyncStatus,
    syncCollection,
    
    // Utilities
    canSync,
    needsSync,
    isSyncing,
  };
};

export default useVectorSync;