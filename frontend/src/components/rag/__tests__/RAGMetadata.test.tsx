import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import { renderWithTheme } from '../../../test/mui-test-utils';
import { RAGMetadata } from '../RAGMetadata';
import { RAGQueryMetadata } from '../../../types/api';

const mockMetadata: RAGQueryMetadata = {
  chunks_used: 5,
  collection_searched: 'ai-docs',
  llm_provider: 'openai',
  response_time_ms: 1245,
  token_usage: {
    total: 150,
    prompt: 100,
    completion: 50
  }
};

const mockMetadataMinimal: RAGQueryMetadata = {
  chunks_used: 3,
  collection_searched: null,
  llm_provider: null,
  response_time_ms: 892
};

describe('RAGMetadata', () => {
  it('renders all metadata when provided', () => {
    renderWithTheme(<RAGMetadata metadata={mockMetadata} />);
    
    expect(screen.getByText('Query Metadata')).toBeInTheDocument();
    expect(screen.getByText('5 chunks')).toBeInTheDocument(); // chunks_used
    expect(screen.getByText('ai-docs')).toBeInTheDocument(); // collection_searched
    expect(screen.getByText('openai')).toBeInTheDocument(); // llm_provider
    expect(screen.getByText('1.25s')).toBeInTheDocument(); // response_time_ms
    expect(screen.getByText('150')).toBeInTheDocument(); // total tokens
  });

  it('renders minimal metadata gracefully', () => {
    renderWithTheme(<RAGMetadata metadata={mockMetadataMinimal} />);
    
    expect(screen.getByText('Query Metadata')).toBeInTheDocument();
    expect(screen.getByText('3 chunks')).toBeInTheDocument(); // chunks_used
    expect(screen.getByText('All Collections')).toBeInTheDocument(); // null collection
    expect(screen.getByText('Vector Search Only')).toBeInTheDocument(); // null provider
    expect(screen.getByText('0.89s')).toBeInTheDocument(); // response_time_ms
  });

  it('formats response time correctly', () => {
    const metadata1: RAGQueryMetadata = {
      chunks_used: 1,
      collection_searched: null,
      llm_provider: null,
      response_time_ms: 500
    };

    const metadata2: RAGQueryMetadata = {
      chunks_used: 1,
      collection_searched: null,
      llm_provider: null,
      response_time_ms: 2500
    };

    renderWithTheme(<RAGMetadata metadata={metadata1} />);
    expect(screen.getByText('0.50s')).toBeInTheDocument();

    renderWithTheme(<RAGMetadata metadata={metadata2} />);
    expect(screen.getByText('2.50s')).toBeInTheDocument();
  });

  it('displays token usage when available', () => {
    renderWithTheme(<RAGMetadata metadata={mockMetadata} />);
    
    expect(screen.getByText(/Tokens Used/)).toBeInTheDocument();
    expect(screen.getByText('150')).toBeInTheDocument(); // total
    expect(screen.getByText('100')).toBeInTheDocument(); // prompt
    expect(screen.getByText('50')).toBeInTheDocument(); // completion
  });

  it('hides token usage when not available', () => {
    renderWithTheme(<RAGMetadata metadata={mockMetadataMinimal} />);
    
    expect(screen.queryByText(/Tokens Used/)).not.toBeInTheDocument();
  });

  it('displays chunks used with proper pluralization', () => {
    const singleChunk: RAGQueryMetadata = {
      chunks_used: 1,
      collection_searched: null,
      llm_provider: null,
      response_time_ms: 500
    };

    const multipleChunks: RAGQueryMetadata = {
      chunks_used: 5,
      collection_searched: null,
      llm_provider: null,
      response_time_ms: 500
    };

    renderWithTheme(<RAGMetadata metadata={singleChunk} />);
    expect(screen.getByText(/1 chunk/)).toBeInTheDocument();

    renderWithTheme(<RAGMetadata metadata={multipleChunks} />);
    expect(screen.getByText(/5 chunks/)).toBeInTheDocument();
  });

  it('handles zero chunks gracefully', () => {
    const zeroChunks: RAGQueryMetadata = {
      chunks_used: 0,
      collection_searched: null,
      llm_provider: null,
      response_time_ms: 200
    };

    renderWithTheme(<RAGMetadata metadata={zeroChunks} />);
    expect(screen.getByText(/0 chunks/)).toBeInTheDocument();
  });

  it('applies proper test IDs for integration testing', () => {
    renderWithTheme(<RAGMetadata metadata={mockMetadata} />);
    
    expect(screen.getByTestId('rag-metadata-section')).toBeInTheDocument();
    expect(screen.getByTestId('chunks-used')).toBeInTheDocument();
    expect(screen.getByTestId('collection-searched')).toBeInTheDocument();
    expect(screen.getByTestId('llm-provider')).toBeInTheDocument();
    expect(screen.getByTestId('response-time')).toBeInTheDocument();
  });

  it('shows different LLM provider names correctly', () => {
    const ollamaMetadata: RAGQueryMetadata = {
      chunks_used: 2,
      collection_searched: 'test',
      llm_provider: 'ollama',
      response_time_ms: 3000
    };

    renderWithTheme(<RAGMetadata metadata={ollamaMetadata} />);
    expect(screen.getByText('ollama')).toBeInTheDocument();
  });

  it('handles missing token usage gracefully', () => {
    const noTokens: RAGQueryMetadata = {
      chunks_used: 3,
      collection_searched: 'test',
      llm_provider: 'openai',
      response_time_ms: 1000,
      token_usage: undefined
    };

    renderWithTheme(<RAGMetadata metadata={noTokens} />);
    expect(screen.queryByText(/Tokens Used/)).not.toBeInTheDocument();
  });
});