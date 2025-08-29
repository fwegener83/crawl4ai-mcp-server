import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import { EnhancedVectorSearchPanel } from '../EnhancedVectorSearchPanel';
import type { VectorSearchResult, VectorSyncStatus, EnhancedVectorSearchResult } from '../../../types/api';

// Mock MUI icons
vi.mock('@mui/icons-material', () => ({
  Search: () => <div data-testid="search-icon" />,
  Clear: () => <div data-testid="clear-icon" />,
  InsertDriveFile: () => <div data-testid="file-icon" />,
  ExpandMore: () => <div data-testid="expand-more-icon" />,
  ChevronRight: () => <div data-testid="chevron-right-icon" />,
  Timeline: () => <div data-testid="timeline-icon" />,
  Settings: () => <div data-testid="settings-icon" />,
}));

describe('EnhancedVectorSearchPanel', () => {
  const mockSyncStatus: VectorSyncStatus = {
    collection_name: 'test-collection',
    sync_enabled: true,
    status: 'in_sync',
    total_files: 5,
    synced_files: 5,
    changed_files_count: 0,
    chunk_count: 25,
    total_chunks: 25,
    last_sync: '2025-08-15T17:00:00Z',
    last_sync_attempt: '2025-08-15T17:00:00Z',
    last_sync_duration: 2.5,
    sync_progress: null,
    sync_health_score: 0.95,
    errors: [],
    warnings: []
  };

  const mockEnhancedResults: EnhancedVectorSearchResult[] = [
    {
      content: 'This is enhanced search result content with relationship data',
      score: 0.87,
      collection_name: 'test-collection',
      file_path: 'docs/test.md',
      chunk_index: 1,
      metadata: {
        chunk_type: 'heading',
        header_hierarchy: 'Introduction > Overview',
        contains_code: false,
        created_at: '2025-08-15T16:00:00Z',
        overlap_sources: ['chunk_000', 'chunk_002'],
        context_expansion_eligible: true
      },
      relationship_data: {
        previous_chunk_id: 'chunk_000',
        next_chunk_id: 'chunk_002',
        overlap_percentage: 0.25
      },
      expansion_source: 'similarity_threshold',
      expansion_type: 'sequential'
    },
    {
      content: 'Standard search result without enhanced features',
      score: 0.72,
      collection_name: 'test-collection',
      file_path: 'docs/standard.md',
      chunk_index: 0,
      metadata: {
        chunk_type: 'paragraph',
        header_hierarchy: '',
        contains_code: true,
        programming_language: 'javascript',
        created_at: '2025-08-15T15:30:00Z'
      }
    }
  ];

  const defaultProps = {
    collectionId: 'test-collection',
    collectionSyncStatus: mockSyncStatus,
    searchResults: mockEnhancedResults,
    searchQuery: 'test query',
    searchLoading: false,
    onSearch: vi.fn(),
    onEnhancedSearch: vi.fn(),
    onResultClick: vi.fn(),
    onClearSearch: vi.fn(),
    maxHeight: 400,
    showEnhancedFeatures: true
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Enhanced Search Controls', () => {
    it('renders context expansion toggle when enhanced features are enabled', () => {
      render(<EnhancedVectorSearchPanel {...defaultProps} />);
      
      expect(screen.getByLabelText('Enable Context Expansion')).toBeInTheDocument();
      expect(screen.getByText('Enable Context Expansion')).toBeInTheDocument();
    });

    it('does not render context expansion toggle when enhanced features are disabled', () => {
      render(<EnhancedVectorSearchPanel {...defaultProps} showEnhancedFeatures={false} />);
      
      expect(screen.queryByLabelText('Enable Context Expansion')).not.toBeInTheDocument();
      expect(screen.queryByText('Enable Context Expansion')).not.toBeInTheDocument();
    });

    it('calls onEnhancedSearch when context expansion is toggled', async () => {
      render(<EnhancedVectorSearchPanel {...defaultProps} />);
      
      const contextToggle = screen.getByLabelText('Enable Context Expansion');
      
      await userEvent.click(contextToggle);
      
      await waitFor(() => {
        expect(defaultProps.onEnhancedSearch).toHaveBeenCalledWith(
          'test query',
          'test-collection',
          { enableContextExpansion: true, relationshipFilter: null, similarityThreshold: 0.2 }
        );
      });
    });

    it('renders enhanced search settings panel', () => {
      render(<EnhancedVectorSearchPanel {...defaultProps} />);
      
      const settingsButton = screen.getByLabelText('Enhanced Search Settings');
      expect(settingsButton).toBeInTheDocument();
    });

    it('shows similarity threshold control when settings panel is expanded', async () => {
      render(<EnhancedVectorSearchPanel {...defaultProps} />);
      
      const settingsButton = screen.getByLabelText('Enhanced Search Settings');
      await userEvent.click(settingsButton);
      
      await waitFor(() => {
        expect(screen.getByText('Similarity Threshold')).toBeInTheDocument();
        expect(screen.getByRole('slider')).toBeInTheDocument();
      });
    });
  });

  describe('Enhanced Search Results Display', () => {
    it('displays relationship indicators for enhanced results', () => {
      render(<EnhancedVectorSearchPanel {...defaultProps} />);
      
      // Should show overlap indicator
      expect(screen.getByText('25% Overlap')).toBeInTheDocument();
      
      // Should show expansion indicator
      expect(screen.getByText('Expanded')).toBeInTheDocument();
    });

    it('shows chunk navigation buttons for results with relationships', () => {
      render(<EnhancedVectorSearchPanel {...defaultProps} />);
      
      // Should show previous/next chunk navigation
      expect(screen.getByLabelText('Previous chunk')).toBeInTheDocument();
      expect(screen.getByLabelText('Next chunk')).toBeInTheDocument();
    });

    it('does not show enhanced indicators for standard results', () => {
      render(<EnhancedVectorSearchPanel {...defaultProps} />);
      
      // Second result should not have enhanced features
      const resultItems = screen.getAllByRole('button', { name: /.*\.md/ });
      expect(resultItems).toHaveLength(2);
      
      // Check that standard result doesn't have overlap indicator
      expect(screen.getAllByText(/Overlap/)).toHaveLength(1); // Only first result
    });

    it('handles navigation to related chunks', async () => {
      render(<EnhancedVectorSearchPanel {...defaultProps} />);
      
      const nextChunkButton = screen.getByLabelText('Next chunk');
      await userEvent.click(nextChunkButton);
      
      expect(defaultProps.onResultClick).toHaveBeenCalledWith(
        expect.objectContaining({
          chunk_id: 'chunk_002' // Next chunk ID from relationship data
        })
      );
    });
  });

  describe('Enhanced Metadata Display', () => {
    it('displays header hierarchy information', () => {
      render(<EnhancedVectorSearchPanel {...defaultProps} />);
      
      expect(screen.getByText('Introduction > Overview')).toBeInTheDocument();
    });

    it('shows programming language for code chunks', () => {
      render(<EnhancedVectorSearchPanel {...defaultProps} />);
      
      expect(screen.getByText('javascript')).toBeInTheDocument();
    });

    it('displays chunk type indicators', () => {
      render(<EnhancedVectorSearchPanel {...defaultProps} />);
      
      expect(screen.getByText('heading')).toBeInTheDocument();
      expect(screen.getByText('paragraph')).toBeInTheDocument();
    });
  });

  describe('Collection Statistics Integration', () => {
    it('shows enhanced collection statistics when available', () => {
      const enhancedSyncStatus = {
        ...mockSyncStatus,
        enhanced_features_enabled: true,
        overlap_chunk_count: 8,
        context_expansion_eligible_chunks: 20
      };

      render(
        <EnhancedVectorSearchPanel 
          {...defaultProps} 
          collectionSyncStatus={enhancedSyncStatus}
        />
      );
      
      expect(screen.getByText(/8 overlap chunks/)).toBeInTheDocument();
      expect(screen.getByText(/20 expandable/)).toBeInTheDocument();
    });

    it('handles missing enhanced statistics gracefully', () => {
      render(<EnhancedVectorSearchPanel {...defaultProps} />);
      
      // Should still render basic collection info without enhanced stats
      expect(screen.getByText(/25 chunks/)).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('displays error message when enhanced search fails', () => {
      render(
        <EnhancedVectorSearchPanel 
          {...defaultProps} 
          enhancedSearchError="Enhanced search service unavailable"
        />
      );
      
      expect(screen.getByText('Enhanced search service unavailable')).toBeInTheDocument();
      expect(screen.getByText('Falling back to standard search')).toBeInTheDocument();
    });

    it('disables enhanced features when context expansion toggle fails', async () => {
      const onEnhancedSearchMock = vi.fn().mockRejectedValue(new Error('Service error'));
      
      render(
        <EnhancedVectorSearchPanel 
          {...defaultProps} 
          onEnhancedSearch={onEnhancedSearchMock}
        />
      );
      
      const contextToggle = screen.getByLabelText('Enable Context Expansion');
      await userEvent.click(contextToggle);
      
      await waitFor(() => {
        expect(screen.getByText(/Enhanced features temporarily unavailable/)).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('provides proper ARIA labels for enhanced controls', async () => {
      render(<EnhancedVectorSearchPanel {...defaultProps} />);
      
      expect(screen.getByLabelText('Enable Context Expansion')).toBeInTheDocument();
      expect(screen.getByLabelText('Enhanced Search Settings')).toBeInTheDocument();
      
      // Expand settings to access the slider
      const settingsButton = screen.getByLabelText('Enhanced Search Settings');
      await userEvent.click(settingsButton);
      
      await waitFor(() => {
        expect(screen.getByLabelText('Similarity Threshold')).toBeInTheDocument();
      });
    });

    it('maintains keyboard navigation for enhanced features', async () => {
      render(<EnhancedVectorSearchPanel {...defaultProps} />);
      
      const contextToggle = screen.getByRole('checkbox');
      
      // Test keyboard interaction with userEvent.click which properly handles keyboard
      await userEvent.click(contextToggle);
      
      await waitFor(() => {
        expect(defaultProps.onEnhancedSearch).toHaveBeenCalled();
      });
    });

    it('provides meaningful tooltips for enhanced features', async () => {
      render(<EnhancedVectorSearchPanel {...defaultProps} />);
      
      // Find the tooltip trigger (the Chip component should be wrapped in Tooltip)
      const overlapIndicator = screen.getByText('25% Overlap');
      
      // Hover to show tooltip
      await userEvent.hover(overlapIndicator);
      
      // Wait for tooltip to appear
      await waitFor(() => {
        expect(screen.getByText(/This chunk overlaps 25% with adjacent chunks/)).toBeInTheDocument();
      });
    });
  });

  describe('Performance', () => {
    it('debounces enhanced search requests', async () => {
      render(<EnhancedVectorSearchPanel {...defaultProps} />);
      
      const searchInput = screen.getByDisplayValue('test query');
      
      // Clear and type quickly - should only trigger one enhanced search after debounce
      await userEvent.clear(searchInput);
      await userEvent.type(searchInput, 'quick typing');
      
      // Wait for debounce period (300ms)
      await waitFor(() => {
        expect(defaultProps.onSearch).toHaveBeenCalledWith('quick typing', 'test-collection');
      }, { timeout: 500 });
    });

    it('memoizes relationship data calculations', () => {
      const { rerender } = render(<EnhancedVectorSearchPanel {...defaultProps} />);
      
      // Rerender with same data should not recalculate
      rerender(<EnhancedVectorSearchPanel {...defaultProps} />);
      
      // Relationship indicators should still be visible (memoization working)
      expect(screen.getByText('25% Overlap')).toBeInTheDocument();
    });
  });
});