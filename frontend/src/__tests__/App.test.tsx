import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithTheme } from '../test/mui-test-utils';
import App from '../App';

// Mock the heavy components to speed up tests
vi.mock('../pages/FileCollectionsPage', () => ({
  default: () => <div data-testid="file-collections-page">File Collections Page</div>
}));

vi.mock('../pages/RAGQueryPage', () => ({
  default: () => <div data-testid="rag-query-page">RAG Query Page</div>
}));

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders file collections page by default', () => {
    renderWithTheme(<App />);
    expect(screen.getByTestId('file-collections-page')).toBeInTheDocument();
    expect(screen.queryByTestId('rag-query-page')).not.toBeInTheDocument();
  });

  it('navigates to RAG Query page when tab is clicked', async () => {
    const user = userEvent.setup();
    renderWithTheme(<App />);
    
    // Click on the RAG Query tab
    await user.click(screen.getByTestId('rag-query-tab'));
    
    // Should now show RAG Query page
    expect(screen.getByTestId('rag-query-page')).toBeInTheDocument();
    expect(screen.queryByTestId('file-collections-page')).not.toBeInTheDocument();
  });

  it('navigates back to File Collections page', async () => {
    const user = userEvent.setup();
    renderWithTheme(<App />);
    
    // Go to RAG Query first
    await user.click(screen.getByTestId('rag-query-tab'));
    expect(screen.getByTestId('rag-query-page')).toBeInTheDocument();
    
    // Navigate back to File Collections
    await user.click(screen.getByTestId('file-collections-tab'));
    
    // Should now show File Collections page again
    expect(screen.getByTestId('file-collections-page')).toBeInTheDocument();
    expect(screen.queryByTestId('rag-query-page')).not.toBeInTheDocument();
  });

  it('shows correct tab as active based on current page', async () => {
    const user = userEvent.setup();
    renderWithTheme(<App />);
    
    // Initially File Collections should be active
    expect(screen.getByTestId('file-collections-tab')).toHaveClass('Mui-selected');
    expect(screen.getByTestId('rag-query-tab')).not.toHaveClass('Mui-selected');
    
    // Navigate to RAG Query
    await user.click(screen.getByTestId('rag-query-tab'));
    
    // Now RAG Query should be active
    expect(screen.getByTestId('rag-query-tab')).toHaveClass('Mui-selected');
    expect(screen.getByTestId('file-collections-tab')).not.toHaveClass('Mui-selected');
  });

  it('renders navigation and settings properly', () => {
    renderWithTheme(<App />);
    
    expect(screen.getByText('Crawl4AI File Manager')).toBeInTheDocument();
    expect(screen.getByLabelText('Settings')).toBeInTheDocument();
    expect(screen.getByText('Beta')).toBeInTheDocument();
  });
});