import axios, { type AxiosResponse } from 'axios';
import type {
  CrawlResult,
  DeepCrawlConfig,
  LinkPreview,
  StoreResult,
  SearchResult,
  Collection,
  DeleteResult,
  APIError,
  FileCollection,
  FileMetadata,
  CreateCollectionRequest,
  SaveFileRequest,
  UpdateFileRequest,
  CrawlToCollectionRequest,
  FileCollectionResponse,
  CrawlToCollectionResponse,
  FileCollectionListResponse,
  FileContentResponse,
  // Vector Sync types
  VectorSyncStatus,
  VectorSearchRequest,
  VectorSearchResponse,
  SyncCollectionRequest,
  SyncCollectionResponse,
} from '../types/api';

// Configure axios instance with base URL for backend API
const api = axios.create({
  baseURL: '/api', // Vite will proxy this to backend
  timeout: 120000, // 2 minute timeout for crawling operations
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const apiError: APIError = {
      error: error.response?.status || 'NetworkError',
      message: error.response?.data?.message || error.message || 'An unexpected error occurred',
      details: error.response?.data?.details,
    };
    return Promise.reject(apiError);
  }
);

/**
 * API Service for Extended MCP Tools Integration
 * 3 Basic Crawling Tools + 4 RAG Knowledge Base Tools + File Collection Management
 */
export class APIService {
  // ===== BASIC CRAWLING TOOLS =====
  
  /**
   * Extract content from a single webpage
   */
  static async extractWebContent(url: string): Promise<string> {
    const response: AxiosResponse<{ content: string }> = await api.post('/extract', {
      url,
    });
    return response.data.content;
  }

  /**
   * Perform deep domain crawling with advanced configuration
   */
  static async deepCrawlDomain(config: DeepCrawlConfig): Promise<CrawlResult[]> {
    const response: AxiosResponse<{ results: { success: boolean; pages: CrawlResult[]; crawl_summary: unknown; streaming: boolean; error?: string } }> = await api.post('/deep-crawl', config);
    
    // Check if the backend returned an error
    if (!response.data.results.success) {
      const errorMsg = response.data.results.error || 'Deep crawl failed';
      console.error('Backend deep crawl error:', errorMsg);
      throw new Error(`Deep crawl failed: ${errorMsg}`);
    }
    
    return response.data.results.pages || [];
  }

  /**
   * Get quick preview of links available on a domain
   */
  static async previewDomainLinks(
    domain_url: string,
    include_external: boolean = false
  ): Promise<LinkPreview> {
    const response: AxiosResponse<LinkPreview> = await api.post('/link-preview', {
      domain_url,
      include_external,
    });
    return response.data;
  }

  // ===== RAG KNOWLEDGE BASE TOOLS =====

  /**
   * Store crawled content in RAG knowledge base
   */
  static async storeInCollection(
    content: string,
    collection_name: string = 'default'
  ): Promise<StoreResult> {
    const response: AxiosResponse<StoreResult> = await api.post('/collections', {
      crawl_result: content,
      collection_name,
    });
    return response.data;
  }

  /**
   * Search across collections with semantic search
   */
  static async searchCollections(
    query: string,
    collection_name: string = 'default',
    n_results: number = 5,
    similarity_threshold?: number
  ): Promise<SearchResult[]> {
    const params: Record<string, unknown> = {
      query,
      collection_name,
      n_results,
    };
    
    if (similarity_threshold !== undefined) {
      params.similarity_threshold = similarity_threshold;
    }

    const response: AxiosResponse<{ results: SearchResult[] }> = await api.get('/search', {
      params,
    });
    return response.data.results;
  }

  /**
   * List all available collections with statistics
   */
  static async listCollections(): Promise<Collection[]> {
    const response: AxiosResponse<{ collections: Collection[] }> = await api.get('/collections');
    return response.data.collections;
  }

  /**
   * Delete a collection from knowledge base
   */
  static async deleteCollection(collection_name: string): Promise<DeleteResult> {
    const response: AxiosResponse<DeleteResult> = await api.delete(`/collections/${collection_name}`);
    return response.data;
  }

  // ===== UTILITY METHODS =====

  /**
   * Health check for backend connectivity
   */
  static async healthCheck(): Promise<boolean> {
    try {
      await api.get('/health');
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get backend status and available tools
   */
  static async getStatus(): Promise<{
    status: string;
    tools_available: number;
    rag_enabled: boolean;
  }> {
    const response = await api.get('/status');
    return response.data;
  }

  // ===== FILE COLLECTION MANAGEMENT =====

  /**
   * Create a new file collection
   */
  static async createFileCollection(request: CreateCollectionRequest): Promise<FileCollection> {
    const response: AxiosResponse<FileCollectionResponse<FileCollection>> = await api.post('/file-collections', request);
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to create collection');
    }
    
    return response.data.data!;
  }

  /**
   * List all file collections
   */
  static async listFileCollections(): Promise<FileCollection[]> {
    const response: AxiosResponse<FileCollectionResponse<FileCollectionListResponse>> = await api.get('/file-collections');
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to list collections');
    }
    
    return response.data.data?.collections || [];
  }

  /**
   * Get detailed information about a specific file collection
   */
  static async getFileCollection(collectionId: string): Promise<FileCollection> {
    const response: AxiosResponse<FileCollectionResponse<FileCollection>> = await api.get(`/file-collections/${collectionId}`);
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to get collection info');
    }
    
    return response.data.data!;
  }

  /**
   * Delete a file collection and all its files
   */
  static async deleteFileCollection(collectionId: string): Promise<void> {
    const response: AxiosResponse<FileCollectionResponse<void>> = await api.delete(`/file-collections/${collectionId}`);
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to delete collection');
    }
  }

  /**
   * Save a file to a collection
   */
  static async saveFileToCollection(
    collectionId: string, 
    request: SaveFileRequest
  ): Promise<FileMetadata> {
    const response: AxiosResponse<FileCollectionResponse<FileMetadata>> = await api.post(
      `/file-collections/${collectionId}/files`, 
      request
    );
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to save file');
    }
    
    return response.data.data!;
  }

  /**
   * Read a file from a collection
   */
  static async readFileFromCollection(
    collectionId: string,
    filename: string,
    folder?: string
  ): Promise<string> {
    const params = folder ? { folder } : {};
    const response: AxiosResponse<FileCollectionResponse<FileContentResponse>> = await api.get(
      `/file-collections/${collectionId}/files/${encodeURIComponent(filename)}`,
      { params }
    );
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to read file');
    }
    
    return response.data.data?.content || '';
  }

  /**
   * Update a file in a collection
   */
  static async updateFileInCollection(
    collectionId: string,
    filename: string,
    request: UpdateFileRequest,
    folder?: string
  ): Promise<FileMetadata> {
    const params = folder ? { folder } : {};
    const response: AxiosResponse<FileCollectionResponse<FileMetadata>> = await api.put(
      `/file-collections/${collectionId}/files/${encodeURIComponent(filename)}`,
      request,
      { params }
    );
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to update file');
    }
    
    return response.data.data!;
  }

  /**
   * Delete a file from a collection
   */
  static async deleteFileFromCollection(
    collectionId: string,
    filename: string,
    folder?: string
  ): Promise<void> {
    const params = folder ? { folder } : {};
    const response: AxiosResponse<FileCollectionResponse<void>> = await api.delete(
      `/file-collections/${collectionId}/files/${encodeURIComponent(filename)}`,
      { params }
    );
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to delete file');
    }
  }

  /**
   * List files and folders in a collection
   */
  static async listFilesInCollection(collectionId: string): Promise<{files: any[], folders: any[], total_files: number, total_folders: number}> {
    const response: AxiosResponse<FileCollectionResponse<{files: any[], folders: any[], total_files: number, total_folders: number}>> = await api.get(
      `/file-collections/${collectionId}/files`
    );
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to list files in collection');
    }
    
    return response.data.data!;
  }

  /**
   * Crawl a single page and save to collection
   */
  static async crawlPageToCollection(
    collectionId: string,
    request: CrawlToCollectionRequest
  ): Promise<CrawlToCollectionResponse> {
    const response: AxiosResponse<CrawlToCollectionResponse> = await api.post(
      `/crawl/single/${collectionId}`,
      request
    );
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to crawl page to collection');
    }
    
    return response.data;
  }

  // ===== VECTOR SYNC TOOLS =====
  // Note: These will be integrated with MCP server tools in the backend

  /**
   * Get vector sync status for a specific collection
   */
  static async getCollectionSyncStatus(collectionName: string): Promise<VectorSyncStatus> {
    const response: AxiosResponse<{ success: boolean; status: VectorSyncStatus; error?: string }> = 
      await api.get(`/vector-sync/collections/${collectionName}/status`);
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to get sync status');
    }
    
    return response.data.status;
  }

  /**
   * Get vector sync status for all collections
   */
  static async listCollectionSyncStatuses(): Promise<Record<string, VectorSyncStatus>> {
    const response: AxiosResponse<{ success: boolean; statuses: Record<string, VectorSyncStatus>; error?: string }> = 
      await api.get('/vector-sync/collections/statuses');
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to list sync statuses');
    }
    
    return response.data.statuses;
  }

  /**
   * Sync a collection to vector store
   */
  static async syncCollection(
    collectionName: string, 
    request: SyncCollectionRequest = {}
  ): Promise<SyncCollectionResponse> {
    const response: AxiosResponse<SyncCollectionResponse> = await api.post(
      `/vector-sync/collections/${collectionName}/sync`,
      request
    );
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to sync collection');
    }
    
    return response.data;
  }

  /**
   * Enable vector sync for a collection
   */
  static async enableCollectionSync(collectionName: string): Promise<void> {
    const response: AxiosResponse<{ success: boolean; error?: string }> = await api.post(
      `/vector-sync/collections/${collectionName}/enable`
    );
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to enable sync');
    }
  }

  /**
   * Disable vector sync for a collection
   */
  static async disableCollectionSync(collectionName: string): Promise<void> {
    const response: AxiosResponse<{ success: boolean; error?: string }> = await api.post(
      `/vector-sync/collections/${collectionName}/disable`
    );
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to disable sync');
    }
  }

  /**
   * Delete all vectors for a collection
   */
  static async deleteCollectionVectors(collectionName: string): Promise<void> {
    const response: AxiosResponse<{ success: boolean; error?: string }> = await api.delete(
      `/vector-sync/collections/${collectionName}/vectors`
    );
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to delete vectors');
    }
  }

  /**
   * Search vectors across collections
   */
  static async searchVectors(request: VectorSearchRequest): Promise<VectorSearchResponse> {
    const response: AxiosResponse<VectorSearchResponse> = await api.post('/vector-sync/search', request);
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to search vectors');
    }
    
    return response.data;
  }
}

export default APIService;