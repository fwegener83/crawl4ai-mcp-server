import { describe, it, expect, beforeEach, vi } from 'vitest';
import axios from 'axios';
import type { 
  DeepCrawlConfig, 
  CrawlResult, 
  LinkPreview, 
  StoreResult, 
  SearchResult, 
  Collection, 
  DeleteResult 
} from '../types/api';

// Mock axios
vi.mock('axios');
const mockedAxios = vi.mocked(axios);

// Create mock axios instance
const mockAxiosInstance = {
  post: vi.fn(),
  get: vi.fn(),
  delete: vi.fn(),
  interceptors: {
    response: {
      use: vi.fn()
    }
  }
};

beforeEach(() => {
  vi.clearAllMocks();
  mockedAxios.create = vi.fn().mockReturnValue(mockAxiosInstance);
  // Reset all mock implementations
  mockAxiosInstance.post.mockReset();
  mockAxiosInstance.get.mockReset();
  mockAxiosInstance.delete.mockReset();
  vi.resetModules();
});

describe('APIService', () => {
  describe('extractWebContent', () => {
    it('should extract content from a URL', async () => {
      const mockContent = 'Extracted webpage content';
      const mockResponse = { data: { content: mockContent } };
      
      mockAxiosInstance.post.mockResolvedValue(mockResponse);
      
      const { APIService } = await import('./api');
      const result = await APIService.extractWebContent('https://example.com');
      
      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/extract', {
        url: 'https://example.com'
      });
      expect(result).toBe(mockContent);
    });

    it('should handle API errors', async () => {
      const mockError = {
        response: {
          status: 404,
          data: { message: 'URL not found' }
        }
      };
      
      mockAxiosInstance.post.mockRejectedValue(mockError);
      
      const { APIService } = await import('./api');
      await expect(APIService.extractWebContent('https://invalid-url.com'))
        .rejects.toEqual(mockError);
    });
  });

  describe('deepCrawlDomain', () => {
    it('should perform deep crawl with configuration', async () => {
      const mockConfig: DeepCrawlConfig = {
        domain_url: 'https://example.com',
        max_depth: 2,
        max_pages: 10,
        crawl_strategy: 'bfs'
      };
      
      const mockResults: CrawlResult[] = [
        {
          url: 'https://example.com',
          title: 'Example Page',
          content: 'Page content',
          links: [],
          success: true,
          timestamp: '2024-01-01T00:00:00Z'
        }
      ];
      
      const mockResponse = { 
        data: { 
          results: { 
            success: true,
            pages: mockResults,
            crawl_summary: {},
            streaming: false
          } 
        } 
      };
      mockAxiosInstance.post.mockResolvedValueOnce(mockResponse);
      
      const { APIService } = await import('./api');
      const result = await APIService.deepCrawlDomain(mockConfig);
      
      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/deep-crawl', mockConfig);
      expect(result).toEqual(mockResults);
    });
  });

  describe('previewDomainLinks', () => {
    it('should get domain link preview', async () => {
      const mockPreview: LinkPreview = {
        domain: 'example.com',
        total_links: 15,
        internal_links: 12,
        external_links: 3,
        links: [
          { url: 'https://example.com/page1', title: 'Page 1', is_external: false },
          { url: 'https://example.com/page2', title: 'Page 2', is_external: false }
        ]
      };
      
      mockAxiosInstance.post.mockResolvedValue({ data: mockPreview });
      
      const { APIService } = await import('./api');
      const result = await APIService.previewDomainLinks('https://example.com', false);
      
      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/link-preview', {
        domain_url: 'https://example.com',
        include_external: false
      });
      expect(result).toEqual(mockPreview);
    });
  });

  describe('storeInCollection', () => {
    it('should store content in default collection', async () => {
      const mockStoreResult: StoreResult = {
        success: true,
        collection_name: 'default',
        documents_added: 1,
        message: 'Content stored successfully'
      };
      
      mockAxiosInstance.post.mockResolvedValue({ data: mockStoreResult });
      
      const { APIService } = await import('./api');
      const result = await APIService.storeInCollection('Sample content');
      
      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/collections', {
        crawl_result: 'Sample content',
        collection_name: 'default'
      });
      expect(result).toEqual(mockStoreResult);
    });
  });

  describe('searchCollections', () => {
    it('should search with default parameters', async () => {
      const mockResults: SearchResult[] = [
        {
          id: '1',
          content: 'Matching content',
          metadata: { source: 'https://example.com' },
          score: 0.95
        }
      ];
      
      mockAxiosInstance.get.mockResolvedValue({ data: { results: mockResults } });
      
      const { APIService } = await import('./api');
      const result = await APIService.searchCollections('test query');
      
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/search', {
        params: {
          query: 'test query',
          collection_name: 'default',
          n_results: 5
        }
      });
      expect(result).toEqual(mockResults);
    });
  });

  describe('listCollections', () => {
    it('should list all collections', async () => {
      const mockCollections: Collection[] = [
        {
          name: 'default',
          document_count: 10,
          created_at: '2024-01-01T00:00:00Z',
          last_updated: '2024-01-02T00:00:00Z'
        }
      ];
      
      mockAxiosInstance.get.mockResolvedValue({ data: { collections: mockCollections } });
      
      const { APIService } = await import('./api');
      const result = await APIService.listCollections();
      
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/collections');
      expect(result).toEqual(mockCollections);
    });
  });

  describe('deleteCollection', () => {
    it('should delete a collection', async () => {
      const mockDeleteResult: DeleteResult = {
        success: true,
        collection_name: 'test-collection',
        message: 'Collection deleted successfully'
      };
      
      mockAxiosInstance.delete.mockResolvedValue({ data: mockDeleteResult });
      
      const { APIService } = await import('./api');
      const result = await APIService.deleteCollection('test-collection');
      
      expect(mockAxiosInstance.delete).toHaveBeenCalledWith('/collections/test-collection');
      expect(result).toEqual(mockDeleteResult);
    });
  });

  describe('healthCheck', () => {
    it('should return true when backend is healthy', async () => {
      mockAxiosInstance.get.mockResolvedValue({ data: { status: 'ok' } });
      
      const { APIService } = await import('./api');
      const result = await APIService.healthCheck();
      
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/health');
      expect(result).toBe(true);
    });

    it('should return false when backend is unhealthy', async () => {
      mockAxiosInstance.get.mockRejectedValue(new Error('Network error'));
      
      const { APIService } = await import('./api');
      const result = await APIService.healthCheck();
      
      expect(result).toBe(false);
    });
  });

  describe('getStatus', () => {
    it('should get backend status', async () => {
      const mockStatus = {
        status: 'running',
        tools_available: 7,
        rag_enabled: true
      };
      
      mockAxiosInstance.get.mockResolvedValue({ data: mockStatus });
      
      const { APIService } = await import('./api');
      const result = await APIService.getStatus();
      
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/status');
      expect(result).toEqual(mockStatus);
    });
  });
});