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
 * API Service for 7 MCP Tools Integration
 * 3 Basic Crawling Tools + 4 RAG Knowledge Base Tools
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
    const response: AxiosResponse<{ results: { success: boolean; pages: CrawlResult[]; crawl_summary: any; streaming: boolean } }> = await api.post('/deep-crawl', config);
    return response.data.results.pages;
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
    const params: any = {
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
}

export default APIService;