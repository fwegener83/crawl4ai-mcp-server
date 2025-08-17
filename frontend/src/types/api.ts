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

// Specific Error Classes for HTTP Status Code Handling
export class CollectionNotFoundError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'CollectionNotFoundError';
  }
}

export class ServiceUnavailableError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ServiceUnavailableError';
  }
}

export class SyncFailedError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'SyncFailedError';
  }
}

export class InvalidFileExtensionError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'InvalidFileExtensionError';
  }
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
  id: string;          // Unique ID (same as name for uniqueness) 
  name: string;        // Collection name
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
  // Enhanced RAG features
  enhanced_features_enabled?: boolean;
  overlap_chunk_count?: number;
  context_expansion_eligible_chunks?: number;
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

// Enhanced Vector Search Request with relationship parameters
export interface EnhancedVectorSearchRequest extends VectorSearchRequest {
  enable_context_expansion?: boolean;
  relationship_filter?: Record<string, any>;
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

// Enhanced Vector Search Result with relationship data
export interface EnhancedVectorSearchResult extends VectorSearchResult {
  metadata: VectorSearchResult['metadata'] & {
    overlap_sources?: string[];
    context_expansion_eligible?: boolean;
    overlap_percentage?: number;
  };
  relationship_data?: {
    previous_chunk_id?: string;
    next_chunk_id?: string;
    overlap_percentage?: number;
  };
  expansion_source?: string;
  expansion_type?: string;
  chunk_id?: string;
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

// RAG Query Types
export interface RAGQueryRequest {
  query: string;
  collection_name?: string;
  max_chunks?: number;
  similarity_threshold?: number;
  // Enhanced RAG features
  enable_context_expansion?: boolean;
  enable_relationship_search?: boolean;
}

export interface RAGSource {
  content: string;
  similarity_score: number;
  metadata: {
    source: string;
    created_at?: string;
    [key: string]: any;
  };
  collection_name?: string;
  file_path?: string;
}

export interface RAGQueryMetadata {
  chunks_used: number;
  collection_searched: string | null;
  llm_provider: string | null;
  response_time_ms: number;
  token_usage?: {
    total: number;
    prompt: number;
    completion: number;
  };
}

export interface RAGQueryResponse {
  success: boolean;
  answer: string | null;
  sources: RAGSource[];
  metadata: RAGQueryMetadata;
  error?: string;
}

export interface RAGError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

// Note: Types are already exported above as individual interface declarations