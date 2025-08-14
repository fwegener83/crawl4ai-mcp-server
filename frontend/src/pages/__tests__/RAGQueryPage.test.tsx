import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithTheme } from '../../test/mui-test-utils';
import { AppThemeProvider } from '../../contexts/ThemeContext';
import RAGQueryPage from '../RAGQueryPage';
import { ragQueryService } from '../../services/ragQueryService';
import { RAGQueryResponse } from '../../types/api';

// Mock the RAG query service
vi.mock('../../services/ragQueryService', () => ({
  ragQueryService: {
    query: vi.fn(),
    healthCheck: vi.fn()
  }
}));

// Wrapper component to provide theme context
const ThemeWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AppThemeProvider>{children}</AppThemeProvider>
);

const renderWithAllProviders = (component: React.ReactElement) => {
  return renderWithTheme(component, {
    wrapper: ({ children }) => <ThemeWrapper>{children}</ThemeWrapper>
  });
};

describe('RAGQueryPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the page title', () => {
    renderWithAllProviders(<RAGQueryPage />);
    expect(screen.getByText('RAG Query')).toBeInTheDocument();
  });

  it('renders the page description', () => {
    renderWithAllProviders(<RAGQueryPage />);
    expect(screen.getByText(/search your collections using AI-powered semantic search/i)).toBeInTheDocument();
  });

  it('renders the query input field', () => {
    renderWithAllProviders(<RAGQueryPage />);
    expect(screen.getByLabelText(/enter your question/i)).toBeInTheDocument();
  });

  it('renders the search button', () => {
    renderWithAllProviders(<RAGQueryPage />);
    expect(screen.getByRole('button', { name: /search/i })).toBeInTheDocument();
  });

  it('renders collection selection dropdown', () => {
    renderWithAllProviders(<RAGQueryPage />);
    expect(screen.getByText(/all collections/i)).toBeInTheDocument();
  });

  it('renders advanced settings section', () => {
    renderWithAllProviders(<RAGQueryPage />);
    expect(screen.getByText(/advanced settings/i)).toBeInTheDocument();
  });

  it('shows max chunks setting', () => {
    renderWithAllProviders(<RAGQueryPage />);
    expect(screen.getByText(/max chunks/i)).toBeInTheDocument();
  });

  it('shows similarity threshold setting', () => {
    renderWithAllProviders(<RAGQueryPage />);
    expect(screen.getByText(/similarity threshold/i)).toBeInTheDocument();
  });

  it('allows typing in the query input', async () => {
    const user = userEvent.setup();
    renderWithAllProviders(<RAGQueryPage />);
    
    const queryInput = screen.getByLabelText(/enter your question/i);
    await user.type(queryInput, 'What is machine learning?');
    
    expect(queryInput).toHaveValue('What is machine learning?');
  });

  it('shows results section when query is performed', async () => {
    // Mock the API response
    const mockResponse: RAGQueryResponse = {
      success: true,
      answer: 'This is a mock answer that would come from the LLM based on the retrieved context.',
      sources: [
        {
          content: 'Machine learning is a subset of artificial intelligence.',
          similarity_score: 0.95,
          metadata: {
            source: 'ml-guide.md',
            created_at: '2024-01-15T10:30:00Z'
          },
          collection_name: 'ai-docs',
          file_path: '/ai-docs/ml-guide.md'
        }
      ],
      metadata: {
        chunks_used: 1,
        collection_searched: null,
        llm_provider: 'openai',
        response_time_ms: 1245,
        token_usage: {
          total: 150,
          prompt: 100,
          completion: 50
        }
      }
    };

    // Mock a delayed response to test loading state
    const mockQuery = vi.mocked(ragQueryService.query);
    mockQuery.mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve(mockResponse), 100))
    );

    const user = userEvent.setup();
    renderWithAllProviders(<RAGQueryPage />);
    
    const queryInput = screen.getByLabelText(/enter your question/i);
    const searchButton = screen.getByRole('button', { name: /search/i });
    
    await user.type(queryInput, 'test query');
    await user.click(searchButton);
    
    // Initially should show searching state
    expect(screen.getByText('Searching...')).toBeInTheDocument();
    
    // Wait for search to complete and results to appear
    await screen.findByTestId('rag-results-section');
    expect(screen.getByTestId('rag-results-section')).toBeInTheDocument();
    
    // Should show the mock answer
    expect(screen.getByText(/This is a mock answer/)).toBeInTheDocument();
  });

  it('disables search button when query is empty', () => {
    renderWithAllProviders(<RAGQueryPage />);
    const searchButton = screen.getByRole('button', { name: /search/i });
    expect(searchButton).toBeDisabled();
  });

  it('enables search button when query has content', async () => {
    const user = userEvent.setup();
    renderWithAllProviders(<RAGQueryPage />);
    
    const queryInput = screen.getByLabelText(/enter your question/i);
    const searchButton = screen.getByRole('button', { name: /search/i });
    
    await user.type(queryInput, 'test');
    expect(searchButton).toBeEnabled();
  });
});