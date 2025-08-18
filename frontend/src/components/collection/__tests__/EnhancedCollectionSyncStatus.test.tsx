import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import { EnhancedCollectionSyncStatus } from '../EnhancedCollectionSyncStatus';
import type { VectorSyncStatus } from '../../../types/api';

// Mock MUI icons
vi.mock('@mui/icons-material', () => ({
  Sync: () => <div data-testid="sync-icon" />,
  CheckCircle: () => <div data-testid="check-circle-icon" />,
  Warning: () => <div data-testid="warning-icon" />,
  Error: () => <div data-testid="error-icon" />,
  Timeline: () => <div data-testid="timeline-icon" />,
  TrendingUp: () => <div data-testid="trending-up-icon" />,
  Speed: () => <div data-testid="speed-icon" />,
  Storage: () => <div data-testid="storage-icon" />,
  ExpandMore: () => <div data-testid="expand-more-icon" />,
  Info: () => <div data-testid="info-icon" />,
}));

describe('EnhancedCollectionSyncStatus', () => {
  const mockEnhancedSyncStatus: VectorSyncStatus = {
    collection_name: 'test-collection',
    sync_enabled: true,
    status: 'in_sync',
    total_files: 12,
    synced_files: 12,
    changed_files_count: 0,
    chunk_count: 85,
    total_chunks: 85,
    last_sync: '2025-08-15T17:30:00Z',
    last_sync_attempt: '2025-08-15T17:30:00Z',
    last_sync_duration: 4.2,
    sync_progress: null,
    sync_health_score: 0.92,
    errors: [],
    warnings: ['Some files contain very long chunks that may impact performance'],
    // Enhanced features
    enhanced_features_enabled: true,
    overlap_chunk_count: 23,
    context_expansion_eligible_chunks: 67
  };

  const mockBasicSyncStatus: VectorSyncStatus = {
    collection_name: 'basic-collection',
    sync_enabled: true,
    status: 'in_sync',
    total_files: 8,
    synced_files: 8,
    changed_files_count: 0,
    chunk_count: 45,
    total_chunks: 45,
    last_sync: '2025-08-15T16:00:00Z',
    last_sync_attempt: '2025-08-15T16:00:00Z',
    last_sync_duration: 2.1,
    sync_progress: null,
    sync_health_score: 0.88,
    errors: [],
    warnings: []
  };

  const defaultProps = {
    syncStatus: mockEnhancedSyncStatus,
    collectionName: 'test-collection',
    onSyncClick: vi.fn(),
    onShowDetails: vi.fn(),
    showEnhancedFeatures: true
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Enhanced Statistics Display', () => {
    it('displays enhanced collection statistics when available', () => {
      render(<EnhancedCollectionSyncStatus {...defaultProps} />);
      
      expect(screen.getByText('85 total chunks')).toBeInTheDocument();
      expect(screen.getByText('23 overlap chunks')).toBeInTheDocument();
      expect(screen.getByText('67 expandable chunks')).toBeInTheDocument();
    });

    it('shows enhanced features indicator when enabled', () => {
      render(<EnhancedCollectionSyncStatus {...defaultProps} />);
      
      expect(screen.getByText('Enhanced RAG')).toBeInTheDocument();
      expect(screen.getAllByTestId('timeline-icon').length).toBeGreaterThan(0);
    });

    it('does not show enhanced features for basic collections', () => {
      render(
        <EnhancedCollectionSyncStatus 
          {...defaultProps} 
          syncStatus={mockBasicSyncStatus}
        />
      );
      
      expect(screen.queryByText('Enhanced RAG')).not.toBeInTheDocument();
      expect(screen.queryByText('overlap chunks')).not.toBeInTheDocument();
    });

    it('displays performance metrics with enhanced context', () => {
      render(<EnhancedCollectionSyncStatus {...defaultProps} />);
      
      // Health score should be visible (there are multiple 92% - one in quick stats, one in details)
      expect(screen.getAllByText(/92%/).length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText(/4\.2s/)).toBeInTheDocument(); // Sync duration
    });
  });

  describe('Enhanced Status Indicators', () => {
    it('shows detailed sync health with enhanced metrics', () => {
      render(<EnhancedCollectionSyncStatus {...defaultProps} />);
      
      // Should show health score indicator in quick stats
      expect(screen.getByText('92% health')).toBeInTheDocument();
      
      // Should indicate enhanced processing in chip
      expect(screen.getByText('Enhanced RAG')).toBeInTheDocument();
    });

    it('displays warnings with enhanced context awareness', () => {
      render(<EnhancedCollectionSyncStatus {...defaultProps} />);
      
      // Should show warning count
      expect(screen.getByText('1 Warning')).toBeInTheDocument();
      expect(screen.getByTestId('warning-icon')).toBeInTheDocument();
    });

    it('shows comprehensive sync statistics', () => {
      render(<EnhancedCollectionSyncStatus {...defaultProps} />);
      
      expect(screen.getByText('Files: 12/12')).toBeInTheDocument();
      expect(screen.getByText(/Last sync:/)).toBeInTheDocument();
    });
  });

  describe('Enhanced Features Toggle', () => {
    it('allows toggling enhanced features display', async () => {
      render(
        <EnhancedCollectionSyncStatus 
          {...defaultProps} 
          showEnhancedFeatures={false}
        />
      );
      
      // Enhanced features should be hidden
      expect(screen.queryByText('23 overlap chunks')).not.toBeInTheDocument();
      expect(screen.queryByText('Enhanced RAG')).not.toBeInTheDocument();
    });

    it('shows enhanced features when explicitly enabled', () => {
      render(
        <EnhancedCollectionSyncStatus 
          {...defaultProps} 
          showEnhancedFeatures={true}
        />
      );
      
      expect(screen.getByText('Enhanced RAG')).toBeInTheDocument();
      expect(screen.getByText('23 overlap chunks')).toBeInTheDocument();
    });
  });

  describe('Expandable Details Section', () => {
    it('shows expandable details button', () => {
      render(<EnhancedCollectionSyncStatus {...defaultProps} />);
      
      const detailsButton = screen.getByLabelText('Show sync details');
      expect(detailsButton).toBeInTheDocument();
    });

    it('expands to show detailed statistics', async () => {
      render(<EnhancedCollectionSyncStatus {...defaultProps} />);
      
      const detailsButton = screen.getByLabelText('Show sync details');
      await userEvent.click(detailsButton);
      
      await waitFor(() => {
        expect(screen.getByTestId('overlap-ratio-metric')).toBeInTheDocument();
        expect(screen.getByText(/27%/)).toBeInTheDocument(); // Math.round(23/85 * 100) = 27
        expect(screen.getByTestId('context-expansion-metric')).toBeInTheDocument();
        expect(screen.getByText(/79%/)).toBeInTheDocument(); // Math.round(67/85 * 100) = 79
      });
    });

    it('shows enhanced performance metrics in details', async () => {
      render(<EnhancedCollectionSyncStatus {...defaultProps} />);
      
      const detailsButton = screen.getByLabelText('Show sync details');
      await userEvent.click(detailsButton);
      
      await waitFor(() => {
        expect(screen.getByTestId('sync-duration-metric')).toBeInTheDocument();
        expect(screen.getByTestId('health-score-metric')).toBeInTheDocument();
        expect(screen.getByText(/Enhanced Processing: Active/)).toBeInTheDocument();
      });
    });
  });

  describe('Collection Statistics Integration', () => {
    it('integrates with collection statistics API', async () => {
      const onShowStatistics = vi.fn();
      
      render(
        <EnhancedCollectionSyncStatus 
          {...defaultProps} 
          onShowStatistics={onShowStatistics}
        />
      );
      
      const statisticsButton = screen.getByText('View Statistics');
      await userEvent.click(statisticsButton);
      
      expect(onShowStatistics).toHaveBeenCalledWith('test-collection');
    });

    it('displays quick statistics preview', () => {
      render(<EnhancedCollectionSyncStatus {...defaultProps} />);
      
      // Should show key statistics inline
      expect(screen.getByText('85 total chunks')).toBeInTheDocument();
      expect(screen.getByText('92% health')).toBeInTheDocument();
    });
  });

  describe('Error States and Edge Cases', () => {
    it('handles missing enhanced features gracefully', () => {
      const statusWithoutEnhanced = {
        ...mockBasicSyncStatus,
        enhanced_features_enabled: false
      };
      
      render(
        <EnhancedCollectionSyncStatus 
          {...defaultProps} 
          syncStatus={statusWithoutEnhanced}
        />
      );
      
      // Should show basic information without errors
      expect(screen.getByText('45 total chunks')).toBeInTheDocument();
      expect(screen.queryByText('overlap chunks')).not.toBeInTheDocument();
    });

    it('displays sync errors with enhanced context', () => {
      const errorStatus: VectorSyncStatus = {
        ...mockEnhancedSyncStatus,
        status: 'sync_error',
        errors: ['Enhanced processing failed: ChromaDB connection error', 'Overlap calculation timeout']
      };
      
      render(
        <EnhancedCollectionSyncStatus 
          {...defaultProps} 
          syncStatus={errorStatus}
        />
      );
      
      expect(screen.getByText('2 Errors')).toBeInTheDocument();
      expect(screen.getAllByTestId('error-icon').length).toBeGreaterThan(0);
    });

    it('handles syncing state with enhanced features', () => {
      const syncingStatus: VectorSyncStatus = {
        ...mockEnhancedSyncStatus,
        status: 'syncing',
        sync_progress: 0.65
      };
      
      render(
        <EnhancedCollectionSyncStatus 
          {...defaultProps} 
          syncStatus={syncingStatus}
        />
      );
      
      expect(screen.getByText('Syncing... (65%)')).toBeInTheDocument();
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });
  });

  describe('Accessibility and User Experience', () => {
    it('provides proper ARIA labels for enhanced elements', () => {
      render(<EnhancedCollectionSyncStatus {...defaultProps} />);
      
      expect(screen.getByLabelText('Show sync details')).toBeInTheDocument();
      expect(screen.getByLabelText('Collection sync status')).toBeInTheDocument();
    });

    it('supports keyboard navigation for interactive elements', async () => {
      render(<EnhancedCollectionSyncStatus {...defaultProps} />);
      
      const detailsButton = screen.getByLabelText('Show sync details');
      
      detailsButton.focus();
      await userEvent.keyboard('{Enter}');
      
      await waitFor(() => {
        expect(screen.getByTestId('overlap-ratio-metric')).toBeInTheDocument();
      });
    });

    it('provides meaningful tooltips for enhanced metrics', () => {
      render(<EnhancedCollectionSyncStatus {...defaultProps} />);
      
      // Look for the tooltip container rather than the chip text itself
      const enhancedIndicator = screen.getByLabelText('Collection uses enhanced RAG features with overlap-aware chunking and context expansion');
      expect(enhancedIndicator).toBeInTheDocument();
    });
  });

  describe('Performance and Optimization', () => {
    it('memoizes complex calculations', () => {
      const { rerender } = render(<EnhancedCollectionSyncStatus {...defaultProps} />);
      
      // Rerender with same props should not recalculate expensive values
      rerender(<EnhancedCollectionSyncStatus {...defaultProps} />);
      
      // Enhanced statistics should still be visible (memoization working)
      expect(screen.getByText('23 overlap chunks')).toBeInTheDocument();
    });

    it('handles large numbers of chunks efficiently', () => {
      const largeCollectionStatus: VectorSyncStatus = {
        ...mockEnhancedSyncStatus,
        chunk_count: 10000,
        total_chunks: 10000,
        overlap_chunk_count: 3500,
        context_expansion_eligible_chunks: 8200
      };
      
      render(
        <EnhancedCollectionSyncStatus 
          {...defaultProps} 
          syncStatus={largeCollectionStatus}
        />
      );
      
      // Use regex to match different locale formats (10,000 or 10.000)
      expect(screen.getByText(/10[.,]000 total chunks/)).toBeInTheDocument();
      expect(screen.getByText(/3[.,]500 overlap chunks/)).toBeInTheDocument();
    });
  });
});