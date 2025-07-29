// API Types for 7 MCP Tools Integration + File Collection Management

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
  metadata: Record<string, unknown>;
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
  details?: unknown;
}

// Loading States
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export interface APIResponse<T> {
  data?: T;
  error?: string;
  loading: boolean;
}

// File Collection Management Types
export interface FileCollection {
  name: string;
  description: string;
  created_at: string;
  file_count: number;
  folders: string[];
  metadata: CollectionMetadata;
}

export interface CollectionMetadata {
  created_at: string;
  description: string;
  last_modified: string;
  file_count: number;
  total_size: number;
}

export interface FileMetadata {
  filename: string;
  folder_path: string;
  created_at: string;
  source_url?: string;
  content_hash?: string;
  size: number;
}

export interface CreateCollectionRequest {
  name: string;
  description?: string;
}

export interface SaveFileRequest {
  filename: string;
  content: string;
  folder?: string;
}

export interface UpdateFileRequest {
  content: string;
}

export interface CrawlToCollectionRequest {
  url: string;
  folder?: string;
}

export interface FileCollectionResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface CrawlToCollectionResponse extends FileCollectionResponse {
  url?: string;
  content_length?: number;
  filename?: string;
  collection_name?: string;
  folder?: string;
}

// Specific response types for type safety
export interface FileCollectionListResponse {
  collections: FileCollection[];
}

export interface FileContentResponse {
  content: string;
}