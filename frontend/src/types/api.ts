// API Types for 7 MCP Tools Integration

export interface CrawlResult {
  url: string;
  depth: number;
  title: string;
  content: string;
  success: boolean;
  metadata: {
    crawl_time: string;
    score: number;
  };
}

export interface DeepCrawlConfig {
  domain_url: string;
  max_depth: number;
  crawl_strategy: 'bfs' | 'dfs' | 'best_first';
  max_pages: number;
  include_external: boolean;
  url_patterns?: string[];
  exclude_patterns?: string[];
  keywords?: string[];
  stream_results?: boolean;
}

export interface LinkPreview {
  domain_url: string;
  internal_links: string[];
  external_links: string[];
  total_internal: number;
  total_external: number;
}

// RAG Knowledge Base Types
export interface StoreResult {
  success: boolean;
  message: string;
  chunks_stored: number;
  collection_name: string;
}

export interface SearchResult {
  content: string;
  metadata: {
    source_url?: string;
    chunk_index: number;
    score: number;
  };
  distance: number;
}

export interface Collection {
  name: string;
  count: number;
  metadata: Record<string, any>;
}

export interface DeleteResult {
  success: boolean;
  message: string;
  collection_name: string;
}

// API Error Response
export interface APIError {
  error: string;
  message: string;
  details?: any;
}

// Loading States
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export interface APIResponse<T> {
  data?: T;
  error?: string;
  loading: boolean;
}