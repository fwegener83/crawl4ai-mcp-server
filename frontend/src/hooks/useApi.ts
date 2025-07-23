import { useState, useCallback } from 'react';
import type { APIResponse } from '../types/api';

/**
 * Generic hook for API calls with loading states and error handling
 */
export function useApi<T>() {
  const [state, setState] = useState<APIResponse<T>>({
    data: undefined,
    error: undefined,
    loading: false,
  });

  const execute = useCallback(async (apiCall: () => Promise<T>) => {
    setState({ loading: true, error: undefined, data: undefined });
    
    try {
      const result = await apiCall();
      setState({ loading: false, data: result, error: undefined });
      return result;
    } catch (error: any) {
      const errorMessage = error.message || 'An unexpected error occurred';
      setState({ loading: false, error: errorMessage, data: undefined });
      throw error;
    }
  }, []);

  const reset = useCallback(() => {
    setState({ loading: false, error: undefined, data: undefined });
  }, []);

  return {
    ...state,
    execute,
    reset,
  };
}

/**
 * Hook specifically for crawling operations with progress tracking
 */
export function useCrawling() {
  const [progress, setProgress] = useState<{
    current: number;
    total: number;
    status: string;
  }>({ current: 0, total: 0, status: 'idle' });

  const api = useApi<any>();

  const startCrawl = useCallback(async (apiCall: () => Promise<any>) => {
    setProgress({ current: 0, total: 1, status: 'starting' });
    
    try {
      const result = await api.execute(apiCall);
      setProgress({ current: 1, total: 1, status: 'completed' });
      return result;
    } catch (error) {
      setProgress({ current: 0, total: 1, status: 'failed' });
      throw error;
    }
  }, [api]);

  const resetCrawl = useCallback(() => {
    setProgress({ current: 0, total: 0, status: 'idle' });
    api.reset();
  }, [api]);

  return {
    ...api,
    progress,
    startCrawl,
    resetCrawl,
  };
}

/**
 * Hook for managing collections with CRUD operations
 */
export function useCollections() {
  const [collections, setCollections] = useState<any[]>([]);
  const [selectedCollection, setSelectedCollection] = useState<string>('default');
  
  const listApi = useApi<any[]>();
  const deleteApi = useApi<any>();
  const storeApi = useApi<any>();
  const searchApi = useApi<any[]>();

  const refreshCollections = useCallback(async () => {
    try {
      const result = await listApi.execute(() => 
        import('../services/api').then(({ APIService }) => APIService.listCollections())
      );
      setCollections(result || []);
      return result;
    } catch (error) {
      console.error('Failed to refresh collections:', error);
      throw error;
    }
  }, [listApi]);

  const deleteCollection = useCallback(async (name: string) => {
    await deleteApi.execute(() =>
      import('../services/api').then(({ APIService }) => APIService.deleteCollection(name))
    );
    await refreshCollections();
  }, [deleteApi, refreshCollections]);

  const storeContent = useCallback(async (content: string, collectionName?: string) => {
    const targetCollection = collectionName || selectedCollection;
    const result = await storeApi.execute(() =>
      import('../services/api').then(({ APIService }) => 
        APIService.storeInCollection(content, targetCollection)
      )
    );
    await refreshCollections();
    return result;
  }, [storeApi, selectedCollection, refreshCollections]);

  const searchInCollection = useCallback(async (
    query: string,
    collectionName?: string,
    nResults?: number
  ) => {
    const targetCollection = collectionName || selectedCollection;
    return await searchApi.execute(() =>
      import('../services/api').then(({ APIService }) =>
        APIService.searchCollections(query, targetCollection, nResults)
      )
    );
  }, [searchApi, selectedCollection]);

  return {
    collections,
    selectedCollection,
    setSelectedCollection,
    
    // API states
    listLoading: listApi.loading,
    deleteLoading: deleteApi.loading,
    storeLoading: storeApi.loading,
    searchLoading: searchApi.loading,
    
    // Errors
    listError: listApi.error,
    deleteError: deleteApi.error,
    storeError: storeApi.error,
    searchError: searchApi.error,
    
    // Actions
    refreshCollections,
    deleteCollection,
    storeContent,
    searchInCollection,
    
    // Search results
    searchResults: searchApi.data,
  };
}

export default useApi;