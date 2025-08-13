import { describe, it, expect, vi, beforeEach } from 'vitest';
import type { 
  FileCollection, 
  CreateCollectionRequest, 
  SaveFileRequest,
  UpdateFileRequest,
  CrawlToCollectionRequest
} from '../../types/api';

// Mock the entire axios module
const mockApi = {
  post: vi.fn(),
  get: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
  interceptors: {
    response: {
      use: vi.fn()
    }
  }
};

vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => mockApi)
  }
}));

// Import after mocking
const { APIService } = await import('../api');

describe('APIService - File Collection Management', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('createFileCollection', () => {
    it('should create a file collection successfully', async () => {
      const request: CreateCollectionRequest = {
        name: 'test-collection',
        description: 'A test collection'
      };

      const mockResponse = {
        data: {
          success: true,
          collection: {
            id: 'test-collection',
            name: 'test-collection',
            description: 'A test collection',
            created_at: '2025-01-01T00:00:00Z',
            file_count: 0,
            folders: [],
            metadata: {
              created_at: '2025-01-01T00:00:00Z',
              description: 'A test collection',
              last_modified: '2025-01-01T00:00:00Z',
              file_count: 0,
              total_size: 0
            }
          }
        }
      };

      mockApi.post.mockResolvedValue(mockResponse);

      const result = await APIService.createFileCollection(request);

      expect(mockApi.post).toHaveBeenCalledWith('/file-collections', request);
      expect(result).toEqual({
        id: 'test-collection',
        name: 'test-collection',
        description: 'A test collection',
        created_at: '2025-01-01T00:00:00Z',
        file_count: 0,
        folders: [],
        metadata: {
          created_at: '2025-01-01T00:00:00Z',
          description: 'A test collection',
          last_modified: '2025-01-01T00:00:00Z',
          file_count: 0,
          total_size: 0
        }
      });
    });

    it('should throw error when creation fails', async () => {
      const request: CreateCollectionRequest = {
        name: 'test-collection'
      };

      const mockResponse = {
        data: {
          success: false,
          error: 'Collection already exists'
        }
      };

      mockApi.post.mockResolvedValue(mockResponse);

      await expect(APIService.createFileCollection(request)).rejects.toThrow('Collection already exists');
    });
  });

  describe('listFileCollections', () => {
    it('should list file collections successfully', async () => {
      const mockCollections: FileCollection[] = [
        {
          id: 'collection1',
          name: 'collection1',
          description: 'First collection',
          created_at: '2025-01-01T00:00:00Z',
          file_count: 5,
          folders: ['docs', 'images'],
          metadata: {
            created_at: '2025-01-01T00:00:00Z',
            description: 'First collection',
            last_modified: '2025-01-01T00:00:00Z',
            file_count: 5,
            total_size: 1024
          }
        }
      ];

      const mockResponse = {
        data: {
          success: true,
          collections: mockCollections
        }
      };

      mockApi.get.mockResolvedValue(mockResponse);

      const result = await APIService.listFileCollections();

      expect(mockApi.get).toHaveBeenCalledWith('/file-collections');
      expect(result).toEqual(mockCollections);
    });
  });

  describe('saveFileToCollection', () => {
    it('should save file to collection successfully', async () => {
      const collectionId = 'test-collection';
      const request: SaveFileRequest = {
        filename: 'test.md',
        content: '# Test Document',
        folder: 'docs'
      };

      const mockResponse = {
        data: {
          success: true,
          data: {
            filename: 'test.md',
            folder_path: 'docs',
            created_at: '2025-01-01T00:00:00Z',
            size: 15
          }
        }
      };

      mockApi.post.mockResolvedValue(mockResponse);

      const result = await APIService.saveFileToCollection(collectionId, request);

      expect(mockApi.post).toHaveBeenCalledWith(`/file-collections/${collectionId}/files`, request);
      expect(result).toEqual(mockResponse.data.data);
    });
  });

  describe('readFileFromCollection', () => {
    it('should read file from collection successfully', async () => {
      const collectionId = 'test-collection';
      const filename = 'test.md';
      const folder = 'docs';

      const mockResponse = {
        data: {
          success: true,
          data: {
            content: '# Test Document\n\nContent here.'
          }
        }
      };

      mockApi.get.mockResolvedValue(mockResponse);

      const result = await APIService.readFileFromCollection(collectionId, filename, folder);

      expect(mockApi.get).toHaveBeenCalledWith(`/file-collections/${collectionId}/files/${encodeURIComponent(filename)}`, {
        params: { folder }
      });
      expect(result).toBe('# Test Document\n\nContent here.');
    });
  });

  describe('updateFileInCollection', () => {
    it('should update file in collection successfully', async () => {
      const collectionId = 'test-collection';
      const filename = 'test.md';
      const request: UpdateFileRequest = {
        content: '# Updated Document'
      };

      const mockResponse = {
        data: {
          success: true,
          data: {
            filename: 'test.md',
            folder_path: '',
            created_at: '2025-01-01T00:00:00Z',
            size: 18
          }
        }
      };

      mockApi.put.mockResolvedValue(mockResponse);

      const result = await APIService.updateFileInCollection(collectionId, filename, request);

      expect(mockApi.put).toHaveBeenCalledWith(
        `/file-collections/${collectionId}/files/${encodeURIComponent(filename)}`,
        request,
        { params: {} }
      );
      expect(result).toEqual(mockResponse.data.data);
    });
  });

  describe('deleteFileFromCollection', () => {
    it('should delete file from collection successfully', async () => {
      const collectionId = 'test-collection';
      const filename = 'test.md';

      const mockResponse = {
        data: {
          success: true,
          message: 'File deleted successfully'
        }
      };

      mockApi.delete.mockResolvedValue(mockResponse);

      await APIService.deleteFileFromCollection(collectionId, filename);

      expect(mockApi.delete).toHaveBeenCalledWith(
        `/file-collections/${collectionId}/files/${encodeURIComponent(filename)}`,
        { params: {} }
      );
    });
  });

  describe('crawlPageToCollection', () => {
    it('should crawl page to collection successfully', async () => {
      const collectionId = 'test-collection';
      const request: CrawlToCollectionRequest = {
        url: 'https://example.com',
        folder: 'crawled'
      };

      const mockResponse = {
        data: {
          success: true,
          url: 'https://example.com',
          content_length: 1024,
          filename: 'example.com_index.md',
          collection_name: 'test-collection',
          folder: 'crawled',
          message: 'Page crawled and saved successfully'
        }
      };

      mockApi.post.mockResolvedValue(mockResponse);

      const result = await APIService.crawlPageToCollection(collectionId, request);

      expect(mockApi.post).toHaveBeenCalledWith(`/crawl/single/${collectionId}`, request);
      expect(result).toEqual(mockResponse.data);
    });
  });
});