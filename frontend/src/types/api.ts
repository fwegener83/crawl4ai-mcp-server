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

// Note: RAG Knowledge Base types removed - using File Collections with Vector Sync instead

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

// Vector Sync Types - matching backend schemas
export interface VectorSyncStatus {
  collection_name: string;
  sync_enabled: boolean;
  status: 'never_synced' | 'in_sync' | 'out_of_sync' | 'syncing' | 'sync_error' | 'partial_sync';
  total_files: number;
  synced_files: number;
  changed_files_count: number;
  chunk_count: number;
  total_chunks: number;
  last_sync: string | null;
  last_sync_attempt: string | null;
  last_sync_duration: number | null;
  sync_progress: number | null; // 0.0 to 1.0 when syncing
  sync_health_score: number;
  errors: string[];
  warnings: string[];
}

export interface SyncResult {
  job_id: string;
  collection_name: string;
  operation_type: 'create' | 'update' | 'delete';
  success: boolean;
  started_at: string;
  completed_at: string | null;
  total_duration: number | null;
  files_processed: number;
  chunks_created: number;
  chunks_updated: number;
  chunks_deleted: number;
  errors: string[];
  warnings: string[];
}

export interface VectorSearchRequest {
  query: string;
  collection_name?: string;
  limit?: number;
  similarity_threshold?: number;
}

export interface VectorSearchResult {
  content: string;
  score: number;
  collection_name: string;
  file_path: string;
  chunk_index: number;
  metadata: {
    chunk_type: string;
    header_hierarchy: string;
    contains_code: boolean;
    programming_language?: string;
    created_at: string;
  };
}

export interface VectorSearchResponse {
  success: boolean;
  results: VectorSearchResult[];
  query: string;
  total_found: number;
  search_time: number;
  error?: string;
}

export interface SyncCollectionRequest {
  force_reprocess?: boolean;
  chunking_strategy?: 'baseline' | 'markdown_intelligent' | 'auto';
}

export interface SyncCollectionResponse {
  success: boolean;
  job_id: string;
  message: string;
  sync_result?: SyncResult;
  error?: string;
}