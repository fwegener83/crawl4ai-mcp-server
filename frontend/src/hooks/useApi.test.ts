import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useApi, useCrawling, useCollections } from './useApi';

// Mock the API service
vi.mock('../services/api', () => ({
  APIService: {
    listCollections: vi.fn(),
    deleteCollection: vi.fn(),
    storeInCollection: vi.fn(),
    searchCollections: vi.fn(),
  }
}));

describe('useApi', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should initialize with default state', () => {
    const { result } = renderHook(() => useApi<string>());
    
    expect(result.current.data).toBeUndefined();
    expect(result.current.error).toBeUndefined();
    expect(result.current.loading).toBe(false);
  });

  it('should handle successful API call', async () => {
    const { result } = renderHook(() => useApi<string>());
    
    const mockApiCall = vi.fn().mockResolvedValue('success data');
    
    await act(async () => {
      const data = await result.current.execute(mockApiCall);
      expect(data).toBe('success data');
    });
    
    expect(result.current.data).toBe('success data');
    expect(result.current.error).toBeUndefined();
    expect(result.current.loading).toBe(false);
    expect(mockApiCall).toHaveBeenCalledOnce();
  });

  it('should handle API call error', async () => {
    const { result } = renderHook(() => useApi<string>());
    
    const mockError = new Error('API Error');
    const mockApiCall = vi.fn().mockRejectedValue(mockError);
    
    await act(async () => {
      try {
        await result.current.execute(mockApiCall);
      } catch (error) {
        expect(error).toBe(mockError);
      }
    });
    
    expect(result.current.data).toBeUndefined();
    expect(result.current.error).toBe('API Error');
    expect(result.current.loading).toBe(false);
  });

  it('should set loading state during API call', async () => {
    const { result } = renderHook(() => useApi<string>());
    
    let resolvePromise: (value: string) => void;
    const mockApiCall = vi.fn().mockImplementation(() => 
      new Promise<string>((resolve) => {
        resolvePromise = resolve;
      })
    );
    
    act(() => {
      result.current.execute(mockApiCall);
    });
    
    expect(result.current.loading).toBe(true);
    expect(result.current.data).toBeUndefined();
    expect(result.current.error).toBeUndefined();
    
    await act(async () => {
      resolvePromise!('data');
    });
    
    expect(result.current.loading).toBe(false);
    expect(result.current.data).toBe('data');
  });

  it('should reset state', () => {
    const { result } = renderHook(() => useApi<string>());
    
    // Manually set some state to test reset
    act(() => {
      result.current.execute(() => Promise.resolve('test data'));
    });
    
    act(() => {
      result.current.reset();
    });
    
    expect(result.current.data).toBeUndefined();
    expect(result.current.error).toBeUndefined();
    expect(result.current.loading).toBe(false);
  });
});

describe('useCrawling', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should initialize with idle progress', () => {
    const { result } = renderHook(() => useCrawling());
    
    expect(result.current.progress).toEqual({
      current: 0,
      total: 0,
      status: 'idle'
    });
  });

  it('should track progress during successful crawl', async () => {
    const { result } = renderHook(() => useCrawling());
    
    const mockApiCall = vi.fn().mockResolvedValue('crawl data');
    
    await act(async () => {
      await result.current.startCrawl(mockApiCall);
    });
    
    expect(result.current.progress).toEqual({
      current: 1,
      total: 1,
      status: 'completed'
    });
    expect(result.current.data).toBe('crawl data');
  });

  it('should track progress during failed crawl', async () => {
    const { result } = renderHook(() => useCrawling());
    
    const mockError = new Error('Crawl failed');
    const mockApiCall = vi.fn().mockRejectedValue(mockError);
    
    await act(async () => {
      try {
        await result.current.startCrawl(mockApiCall);
      } catch (error) {
        expect(error).toBe(mockError);
      }
    });
    
    expect(result.current.progress).toEqual({
      current: 0,
      total: 1,
      status: 'failed'
    });
  });

  it('should reset crawl state', () => {
    const { result } = renderHook(() => useCrawling());
    
    act(() => {
      result.current.resetCrawl();
    });
    
    expect(result.current.progress).toEqual({
      current: 0,
      total: 0,
      status: 'idle'
    });
    expect(result.current.data).toBeUndefined();
    expect(result.current.error).toBeUndefined();
    expect(result.current.loading).toBe(false);
  });
});

describe('useCollections', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should initialize with default state', () => {
    const { result } = renderHook(() => useCollections());
    
    expect(result.current.collections).toEqual([]);
    expect(result.current.selectedCollection).toBe('default');
    expect(result.current.listLoading).toBe(false);
    expect(result.current.deleteLoading).toBe(false);
    expect(result.current.storeLoading).toBe(false);
    expect(result.current.searchLoading).toBe(false);
  });

  it('should allow setting selected collection', () => {
    const { result } = renderHook(() => useCollections());
    
    act(() => {
      result.current.setSelectedCollection('custom');
    });
    
    expect(result.current.selectedCollection).toBe('custom');
  });

  it('should refresh collections', async () => {
    const mockCollections = [
      { name: 'default', document_count: 5 },
      { name: 'custom', document_count: 3 }
    ];
    
    const { APIService } = await import('../services/api');
    vi.mocked(APIService.listCollections).mockResolvedValue(mockCollections);
    
    const { result } = renderHook(() => useCollections());
    
    await act(async () => {
      await result.current.refreshCollections();
    });
    
    expect(result.current.collections).toEqual(mockCollections);
    expect(APIService.listCollections).toHaveBeenCalledOnce();
  });

  it('should handle refresh collections error', async () => {
    const mockError = new Error('Failed to fetch');
    
    const { APIService } = await import('../services/api');
    vi.mocked(APIService.listCollections).mockRejectedValue(mockError);
    
    const { result } = renderHook(() => useCollections());
    
    await act(async () => {
      try {
        await result.current.refreshCollections();
      } catch (error) {
        expect(error).toBe(mockError);
      }
    });
    
    expect(result.current.listError).toBe('Failed to fetch');
  });

  it('should delete collection and refresh', async () => {
    const { APIService } = await import('../services/api');
    vi.mocked(APIService.deleteCollection).mockResolvedValue({ success: true, collection_name: 'test', message: 'Deleted' });
    vi.mocked(APIService.listCollections).mockResolvedValue([]);
    
    const { result } = renderHook(() => useCollections());
    
    await act(async () => {
      await result.current.deleteCollection('test');
    });
    
    expect(APIService.deleteCollection).toHaveBeenCalledWith('test');
    expect(APIService.listCollections).toHaveBeenCalled();
  });

  it('should store content in selected collection', async () => {
    const mockStoreResult = {
      success: true,
      collection_name: 'default',
      documents_added: 1,
      message: 'Stored'
    };
    
    const { APIService } = await import('../services/api');
    vi.mocked(APIService.storeInCollection).mockResolvedValue(mockStoreResult);
    vi.mocked(APIService.listCollections).mockResolvedValue([]);
    
    const { result } = renderHook(() => useCollections());
    
    await act(async () => {
      const result_data = await result.current.storeContent('test content');
      expect(result_data).toEqual(mockStoreResult);
    });
    
    expect(APIService.storeInCollection).toHaveBeenCalledWith('test content', 'default');
    expect(APIService.listCollections).toHaveBeenCalled();
  });

  it('should store content in custom collection', async () => {
    const mockStoreResult = {
      success: true,
      collection_name: 'custom',
      documents_added: 1,
      message: 'Stored'
    };
    
    const { APIService } = await import('../services/api');
    vi.mocked(APIService.storeInCollection).mockResolvedValue(mockStoreResult);
    vi.mocked(APIService.listCollections).mockResolvedValue([]);
    
    const { result } = renderHook(() => useCollections());
    
    await act(async () => {
      await result.current.storeContent('test content', 'custom');
    });
    
    expect(APIService.storeInCollection).toHaveBeenCalledWith('test content', 'custom');
  });

  it('should search in collection', async () => {
    const mockSearchResults = [
      { id: '1', content: 'result 1', metadata: {}, score: 0.9 }
    ];
    
    const { APIService } = await import('../services/api');
    vi.mocked(APIService.searchCollections).mockResolvedValue(mockSearchResults);
    
    const { result } = renderHook(() => useCollections());
    
    await act(async () => {
      const results = await result.current.searchInCollection('test query');
      expect(results).toEqual(mockSearchResults);
    });
    
    expect(APIService.searchCollections).toHaveBeenCalledWith('test query', 'default', undefined, undefined);
    expect(result.current.searchResults).toEqual(mockSearchResults);
  });

  it('should search with custom parameters', async () => {
    const { APIService } = await import('../services/api');
    vi.mocked(APIService.searchCollections).mockResolvedValue([]);
    
    const { result } = renderHook(() => useCollections());
    
    await act(async () => {
      await result.current.searchInCollection('query', 'custom', 10, 0.8);
    });
    
    expect(APIService.searchCollections).toHaveBeenCalledWith('query', 'custom', 10, 0.8);
  });
});