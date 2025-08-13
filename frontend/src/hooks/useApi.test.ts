import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useApi, useCrawling, useCollections } from './useApi';

// Mock the API service
vi.mock('../services/api', () => ({
  APIService: {
    listFileCollections: vi.fn(),
    deleteFileCollection: vi.fn(),
    saveFileToCollection: vi.fn(),
    createFileCollection: vi.fn(),
    searchVectors: vi.fn(),
    // File Collections API methods would be added here as needed
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
    vi.mocked(APIService.listFileCollections).mockResolvedValue(mockCollections);
    
    const { result } = renderHook(() => useCollections());
    
    await act(async () => {
      await result.current.refreshCollections();
    });
    
    expect(result.current.collections).toEqual(mockCollections);
    expect(APIService.listFileCollections).toHaveBeenCalledOnce();
  });

  it('should handle refresh collections error', async () => {
    const mockError = new Error('Failed to fetch');
    
    const { APIService } = await import('../services/api');
    vi.mocked(APIService.listFileCollections).mockRejectedValue(mockError);
    
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
    vi.mocked(APIService.deleteFileCollection).mockResolvedValue(undefined);
    vi.mocked(APIService.listFileCollections).mockResolvedValue([]);
    
    const { result } = renderHook(() => useCollections());
    
    await act(async () => {
      await result.current.deleteCollection('test-collection');
    });
    
    expect(APIService.deleteFileCollection).toHaveBeenCalledWith('test-collection');
    expect(APIService.listFileCollections).toHaveBeenCalled();
  });

  it('should store content in selected collection', async () => {
    const mockResult = { filename: 'test.md', content: 'test content' };
    
    const { APIService } = await import('../services/api');
    vi.mocked(APIService.saveFileToCollection).mockResolvedValue(mockResult);
    vi.mocked(APIService.listFileCollections).mockResolvedValue([]);
    
    const { result } = renderHook(() => useCollections());
    
    await act(async () => {
      const savedResult = await result.current.storeContent('test content');
      expect(savedResult).toBe(mockResult);
    });
    
    expect(APIService.saveFileToCollection).toHaveBeenCalled();
    expect(APIService.listFileCollections).toHaveBeenCalled();
  });

  it('should store content in custom collection', async () => {
    const mockResult = { filename: 'test.md', content: 'test content' };
    
    const { APIService } = await import('../services/api');
    vi.mocked(APIService.saveFileToCollection).mockResolvedValue(mockResult);
    vi.mocked(APIService.listFileCollections).mockResolvedValue([]);
    
    const { result } = renderHook(() => useCollections());
    
    await act(async () => {
      await result.current.storeContent('test content', 'custom-collection');
    });
    
    expect(APIService.saveFileToCollection).toHaveBeenCalledWith('custom-collection', expect.any(Object));
  });

  it('should search in collection', async () => {
    const mockSearchResults = [
      { id: '1', content: 'result 1', score: 0.9, metadata: {} }
    ];
    
    const { APIService } = await import('../services/api');
    vi.mocked(APIService.searchVectors).mockResolvedValue({ results: mockSearchResults });
    
    const { result } = renderHook(() => useCollections());
    
    await act(async () => {
      const results = await result.current.searchInCollection('test query');
      expect(results).toEqual({ results: mockSearchResults });
    });
  });

  it('should search with custom parameters', async () => {
    const mockSearchResults = [{ id: '1', content: 'result 1', score: 0.9, metadata: {} }];
    
    const { APIService } = await import('../services/api');
    vi.mocked(APIService.searchVectors).mockResolvedValue({ results: mockSearchResults });
    
    const { result } = renderHook(() => useCollections());
    
    await act(async () => {
      await result.current.searchInCollection('query', 'custom', 10, 0.8);
    });
    
    expect(APIService.searchVectors).toHaveBeenCalledWith({
      query: 'query',
      collection_name: 'custom',
      limit: 10,
      similarity_threshold: 0.8
    });
  });
});