import type { RAGQueryRequest, RAGQueryResponse } from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export class RAGQueryService {
  private async fetchWithTimeout(
    url: string,
    options: RequestInit = {},
    timeoutMs: number = 120000
  ): Promise<Response> {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), timeoutMs);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });
      clearTimeout(timeout);
      return response;
    } catch (error) {
      clearTimeout(timeout);
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error('Request timed out');
      }
      throw error;
    }
  }

  async query(request: RAGQueryRequest): Promise<RAGQueryResponse> {
    try {
      const response = await this.fetchWithTimeout(
        `${API_BASE_URL}/api/query`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query: request.query,
            collection_name: request.collection_name === 'all' ? undefined : request.collection_name,
            max_chunks: request.max_chunks,
            similarity_threshold: request.similarity_threshold,
            // Enhanced RAG features
            enable_context_expansion: request.enable_context_expansion,
            enable_relationship_search: request.enable_relationship_search,
          }),
        }
      );

      if (!response.ok) {
        let errorMessage = `HTTP error! status: ${response.status}`;
        
        try {
          const errorData = await response.json();
          if (errorData.detail?.error?.message) {
            errorMessage = errorData.detail.error.message;
          } else if (errorData.detail) {
            errorMessage = errorData.detail;
          }
        } catch {
          // If we can't parse error JSON, use the status text
          errorMessage = response.statusText || errorMessage;
        }
        
        throw new Error(errorMessage);
      }

      const data = await response.json();
      
      // The backend returns the response directly, not wrapped in a data field
      return {
        success: data.success,
        answer: data.answer,
        sources: data.sources || [],
        metadata: data.metadata,
        error: data.error,
      };
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Failed to execute RAG query');
    }
  }

  // Health check method to test API connectivity
  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.fetchWithTimeout(
        `${API_BASE_URL}/api/health`,
        { method: 'GET' },
        5000 // 5 second timeout for health check
      );
      return response.ok;
    } catch {
      return false;
    }
  }
}

// Export a singleton instance
export const ragQueryService = new RAGQueryService();