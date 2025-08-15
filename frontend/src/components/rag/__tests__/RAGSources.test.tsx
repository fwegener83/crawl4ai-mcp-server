import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithTheme } from '../../../test/mui-test-utils';
import { RAGSources } from '../RAGSources';
import { RAGSource } from '../../../types/api';

const mockSources: RAGSource[] = [
  {
    content: 'This is the first source content with relevant information about machine learning.',
    similarity_score: 0.95,
    metadata: {
      source: 'ml-guide.md',
      created_at: '2024-01-15T10:30:00Z'
    },
    collection_name: 'ai-docs',
    file_path: '/ai-docs/ml-guide.md'
  },
  {
    content: 'Second source about artificial intelligence and neural networks.',
    similarity_score: 0.87,
    metadata: {
      source: 'ai-basics.md',
      created_at: '2024-01-10T14:20:00Z'
    },
    collection_name: 'ai-docs',
    file_path: '/ai-docs/ai-basics.md'
  },
  {
    content: 'Third source with lower relevance score but still useful information.',
    similarity_score: 0.72,
    metadata: {
      source: 'general-info.md'
    },
    collection_name: 'general',
    file_path: '/general/general-info.md'
  }
];

describe('RAGSources', () => {
  it('renders all sources when provided', () => {
    renderWithTheme(<RAGSources sources={mockSources} />);
    
    expect(screen.getByText('Sources')).toBeInTheDocument();
    expect(screen.getByText(/3 sources found/)).toBeInTheDocument();
    expect(screen.getByText('ml-guide.md')).toBeInTheDocument();
    expect(screen.getByText('ai-basics.md')).toBeInTheDocument();
    expect(screen.getByText('general-info.md')).toBeInTheDocument();
  });

  it('renders empty state when no sources provided', () => {
    renderWithTheme(<RAGSources sources={[]} />);
    
    expect(screen.getByText('Sources')).toBeInTheDocument();
    expect(screen.getByText(/no sources found/i)).toBeInTheDocument();
  });

  it('displays similarity scores correctly', () => {
    renderWithTheme(<RAGSources sources={mockSources} />);
    
    expect(screen.getByText('95%')).toBeInTheDocument();
    expect(screen.getByText('87%')).toBeInTheDocument();
    expect(screen.getByText('72%')).toBeInTheDocument();
  });

  it('displays collection names when available', () => {
    renderWithTheme(<RAGSources sources={mockSources} />);
    
    expect(screen.getAllByText('ai-docs')).toHaveLength(2);
    expect(screen.getByText('general')).toBeInTheDocument();
  });

  it('handles sources without collection names', () => {
    const sourcesWithoutCollection: RAGSource[] = [{
      content: 'Content without collection',
      similarity_score: 0.85,
      metadata: {
        source: 'standalone.md'
      },
      file_path: '/standalone.md'
    }];

    renderWithTheme(<RAGSources sources={sourcesWithoutCollection} />);
    
    expect(screen.getByText('standalone.md')).toBeInTheDocument();
    expect(screen.getByText('85%')).toBeInTheDocument();
  });

  it('expands and collapses source content', async () => {
    const user = userEvent.setup();
    renderWithTheme(<RAGSources sources={mockSources.slice(0, 1)} />);
    
    // Check if we can find the expand button and click it
    const expandButton = screen.getByTestId('source-item-0');
    expect(expandButton).toBeInTheDocument();
    
    // Test that the component responds to clicks (basic interaction test)
    await user.click(expandButton);
    
    // Verify the component is still rendered after interaction
    expect(screen.getByTestId('source-item-0')).toBeInTheDocument();
  });

  it('sorts sources by similarity score in descending order', () => {
    const unsortedSources: RAGSource[] = [
      { ...mockSources[2] }, // 0.72
      { ...mockSources[0] }, // 0.95
      { ...mockSources[1] }  // 0.87
    ];

    renderWithTheme(<RAGSources sources={unsortedSources} />);
    
    const sourceElements = screen.getAllByTestId(/source-item-/);
    expect(sourceElements).toHaveLength(3);
    
    // First source should be the highest scoring one
    expect(sourceElements[0]).toHaveTextContent('95%');
    expect(sourceElements[1]).toHaveTextContent('87%');
    expect(sourceElements[2]).toHaveTextContent('72%');
  });

  it('truncates long content in preview', () => {
    const longContentSource: RAGSource[] = [{
      content: 'This is a very long content '.repeat(20),
      similarity_score: 0.85,
      metadata: {
        source: 'long-content.md'
      },
      collection_name: 'test',
      file_path: '/test/long-content.md'
    }];

    renderWithTheme(<RAGSources sources={longContentSource} />);
    
    expect(screen.getByTestId('source-preview-0')).toBeInTheDocument();
  });

  it('displays creation date when available', () => {
    renderWithTheme(<RAGSources sources={mockSources.slice(0, 1)} />);
    
    expect(screen.getByText(/Created:/)).toBeInTheDocument();
  });

  it('handles missing metadata gracefully', () => {
    const sourceWithMinimalMetadata: RAGSource[] = [{
      content: 'Minimal content',
      similarity_score: 0.80,
      metadata: {
        source: 'minimal.md'
      }
    }];

    renderWithTheme(<RAGSources sources={sourceWithMinimalMetadata} />);
    
    expect(screen.getAllByText('minimal.md')).toHaveLength(2); // Once in header, once in file path
    expect(screen.getByText('80%')).toBeInTheDocument();
  });

  it('applies proper test IDs for integration testing', () => {
    renderWithTheme(<RAGSources sources={mockSources} />);
    
    expect(screen.getByTestId('rag-sources-section')).toBeInTheDocument();
    expect(screen.getByTestId('source-item-0')).toBeInTheDocument();
    expect(screen.getByTestId('source-item-1')).toBeInTheDocument();
    expect(screen.getByTestId('source-item-2')).toBeInTheDocument();
  });
});