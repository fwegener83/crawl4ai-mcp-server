import axios, { type AxiosResponse } from 'axios';
import type {
  CrawlResult,
  DeepCrawlConfig,
  LinkPreview,
  APIError,
  FileCollection,
  FileMetadata,
  CreateCollectionRequest,
  SaveFileRequest,
  UpdateFileRequest,
  CrawlToCollectionRequest,
  FileCollectionResponse,
  CrawlToCollectionResponse,
  FileContentResponse,
  // Vector Sync types (for File Collections)
  VectorSyncStatus,
  VectorSearchRequest,
  VectorSearchResponse,
  SyncCollectionRequest,
  SyncCollectionResponse,
} from '../types/api';

// Import Error Classes as values, not types
import {
  CollectionNotFoundError,
  ServiceUnavailableError,
  SyncFailedError,
  InvalidFileExtensionError,
} from '../types/api';

// Configure axios instance with base URL for backend API
const api = axios.create({
  baseURL: '/api', // Vite will proxy this to backend
  timeout: 120000, // 2 minute timeout for crawling operations
  headers: {
    'Content-Type': 'application/json',
  },
});

// Backend-to-Frontend Vector Sync Status field mapping
interface BackendVectorSyncStatus {
  collection_name: string;
  is_enabled: boolean;
  sync_status: string;
  file_count: number;
  vector_count: number;
  last_sync: string | null;
  error_message: string | null;
}

// Response interceptor for error handling with RESTful status codes
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    let errorMessage = 'An unexpected error occurred';
    
    if (error.response?.data?.detail?.error) {
      // New structured error format: { detail: { error: { code, message, details } } }
      const errorData = error.response.data.detail.error;
      errorMessage = errorData.message || errorMessage;
      
      // Throw specific error classes based on error codes and status
      switch (status) {
        case 404:
          if (errorData.code === 'COLLECTION_NOT_FOUND') {
            return Promise.reject(new CollectionNotFoundError(errorMessage));
          }
          break;
        case 503:
          if (errorData.code === 'SERVICE_UNAVAILABLE') {
            return Promise.reject(new ServiceUnavailableError(errorMessage));
          }
          break;
        case 500:
          if (errorData.code === 'SYNC_FAILED') {
            return Promise.reject(new SyncFailedError(errorMessage));
          }
          if (errorMessage.includes('extension not allowed') || errorMessage.includes('Invalid file extension')) {
            return Promise.reject(new InvalidFileExtensionError(errorMessage));
          }
          break;
      }
    } else {
      // Fallback to legacy format or basic error
      errorMessage = error.response?.data?.message || error.message || errorMessage;
    }
    
    // Generic APIError for other cases
    const apiError: APIError = {
      error: error.response?.data?.detail?.error?.code || status?.toString() || 'NetworkError',
      message: errorMessage,
      details: error.response?.data?.detail?.error?.details || error.response?.data?.details,
    };
    
    return Promise.reject(apiError);
  }
);

/**
 * API Service for Unified Server Integration
 * 3 Basic Crawling Tools + File Collection Management + Vector Sync for File Collections
 */
export class APIService {
  
  /**
   * Transform backend VectorSyncStatus format to frontend format
   */
  private static transformVectorSyncStatus(backendStatus: BackendVectorSyncStatus): VectorSyncStatus {
    return {
      collection_name: backendStatus.collection_name,
      sync_enabled: backendStatus.is_enabled,
      status: backendStatus.sync_status as VectorSyncStatus['status'], // Map sync_status → status
      total_files: backendStatus.file_count,     // Map file_count → total_files
      synced_files: backendStatus.file_count,    // Assume all files are synced for now
      changed_files_count: 0,                    // Backend doesn't provide this - always 0
      chunk_count: backendStatus.vector_count,   // Map vector_count → chunk_count
      total_chunks: backendStatus.vector_count,  // Assume total = current for now
      last_sync: backendStatus.last_sync,
      last_sync_attempt: backendStatus.last_sync,
      last_sync_duration: null,                  // Backend doesn't provide this
      sync_progress: null,                       // Backend doesn't provide progress - always null
      sync_health_score: 1.0,                   // Assume healthy if no errors
      errors: backendStatus.error_message ? [backendStatus.error_message] : [],
      warnings: []                               // Backend doesn't provide warnings yet
    };
  }
  
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
    const response: AxiosResponse<{ success: boolean; pages: CrawlResult[]; error?: string }> = await api.post('/deep-crawl', config);
    
    // Check if the backend returned an error
    if (!response.data.success) {
      const errorMsg = response.data.error || 'Deep crawl failed';
      console.error('Backend deep crawl error:', errorMsg);
      throw new Error(`Deep crawl failed: ${errorMsg}`);
    }
    
    return response.data.pages || [];
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

  // Note: RAG Knowledge Base tools removed - replaced by File Collections with Vector Sync

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
    const response: AxiosResponse<any> = await api.post('/file-collections', request);
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to create collection');
    }
    
    // Backend returns collection directly in response.data.collection, not nested in data.data
    const collection = response.data.collection || response.data.data;
    
    // Ensure collection has an id field (same as name for uniqueness)
    return {
      ...collection,
      id: collection.id || collection.name, // Use existing id or fallback to name
    };
  }

  /**
   * List all file collections
   */
  static async listFileCollections(): Promise<FileCollection[]> {
    const response: AxiosResponse<any> = await api.get('/file-collections');
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to list collections');
    }
    
    // Backend returns collections directly in response.data.collections, not nested in data.data
    const collections = response.data.collections || [];
    
    // Ensure each collection has an id field (same as name for uniqueness)
    return collections.map((collection: any) => ({
      ...collection,
      id: collection.id || collection.name, // Use existing id or fallback to name
    }));
  }

  /**
   * Get detailed information about a specific file collection
   */
  static async getFileCollection(collectionId: string): Promise<FileCollection> {
    const response: AxiosResponse<FileCollectionResponse<FileCollection>> = await api.get(`/file-collections/${collectionId}`);
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to get collection info');
    }
    
    const collection = response.data.data!;
    
    // Ensure collection has an id field (same as name for uniqueness)
    return {
      ...collection,
      id: collection.id || collection.name, // Use existing id or fallback to name
    };
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
  static async getCollectionSyncStatus(collectionId: string): Promise<VectorSyncStatus> {
    const response: AxiosResponse<{ success: boolean; status: any; error?: string }> = 
      await api.get(`/vector-sync/collections/${collectionId}/status`);
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to get sync status');
    }
    
    // Transform backend response format to frontend format
    return APIService.transformVectorSyncStatus(response.data.status);
  }

  /**
   * Get vector sync status for all collections
   */
  static async listCollectionSyncStatuses(): Promise<Record<string, VectorSyncStatus>> {
    const response: AxiosResponse<{ success: boolean; statuses: Record<string, any>; error?: string }> = 
      await api.get('/vector-sync/collections/statuses');
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to list sync statuses');
    }
    
    // Transform backend response format to frontend format
    const transformedStatuses: Record<string, VectorSyncStatus> = {};
    
    for (const [collectionName, backendStatus] of Object.entries(response.data.statuses)) {
      transformedStatuses[collectionName] = APIService.transformVectorSyncStatus(backendStatus);
    }
    
    return transformedStatuses;
  }

  /**
   * Sync a collection to vector store
   */
  static async syncCollection(
    collectionId: string, 
    request: SyncCollectionRequest = {}
  ): Promise<SyncCollectionResponse> {
    const response: AxiosResponse<SyncCollectionResponse> = await api.post(
      `/vector-sync/collections/${collectionId}/sync`,
      request
    );
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to sync collection');
    }
    
    return response.data;
  }


  /**
   * Delete all vectors for a collection
   */
  static async deleteCollectionVectors(collectionId: string): Promise<void> {
    const response: AxiosResponse<{ success: boolean; error?: string }> = await api.delete(
      `/vector-sync/collections/${collectionId}/vectors`
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