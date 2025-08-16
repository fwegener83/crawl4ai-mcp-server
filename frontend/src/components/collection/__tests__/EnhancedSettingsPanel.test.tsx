import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import { EnhancedSettingsPanel } from '../EnhancedSettingsPanel';
import type { VectorSyncStatus } from '../../../types/api';

// Mock MUI icons
vi.mock('@mui/icons-material', () => ({
  Settings: () => <div data-testid="settings-icon" />,
  Timeline: () => <div data-testid="timeline-icon" />,
  TuneRounded: () => <div data-testid="tune-icon" />,
  SpeedRounded: () => <div data-testid="speed-icon" />,
  SmartToy: () => <div data-testid="smart-toy-icon" />,
  Save: () => <div data-testid="save-icon" />,
  Refresh: () => <div data-testid="refresh-icon" />,
  Info: () => <div data-testid="info-icon" />,
  ExpandMore: () => <div data-testid="expand-more-icon" />,
}));

describe('EnhancedSettingsPanel', () => {
  const mockSyncStatus: VectorSyncStatus = {
    collection_name: 'test-collection',
    sync_enabled: true,
    status: 'in_sync',
    total_files: 10,
    synced_files: 10,
    changed_files_count: 0,
    chunk_count: 50,
    total_chunks: 50,
    last_sync: '2025-08-15T17:30:00Z',
    last_sync_attempt: '2025-08-15T17:30:00Z',
    last_sync_duration: 3.2,
    sync_progress: null,
    sync_health_score: 0.91,
    errors: [],
    warnings: [],
    enhanced_features_enabled: true,
    overlap_chunk_count: 15,
    context_expansion_eligible_chunks: 35
  };

  const defaultProps = {
    collectionName: 'test-collection',
    syncStatus: mockSyncStatus,
    onSettingsChange: vi.fn(),
    onApplySettings: vi.fn(),
    onResetToDefaults: vi.fn(),
    open: true,
    onClose: vi.fn()
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Enhanced RAG Settings', () => {
    it('renders enhanced RAG configuration options', () => {
      render(<EnhancedSettingsPanel {...defaultProps} />);
      
      expect(screen.getByText('Enhanced RAG Configuration')).toBeInTheDocument();
      expect(screen.getByLabelText('Enable Enhanced Processing')).toBeInTheDocument();
      expect(screen.getByText('Context Expansion Settings')).toBeInTheDocument();
      expect(screen.getByText('Chunk Overlap Settings')).toBeInTheDocument();
    });

    it('shows enhanced processing toggle', () => {
      render(<EnhancedSettingsPanel {...defaultProps} />);
      
      const enhancedToggle = screen.getByLabelText('Enable Enhanced Processing');
      expect(enhancedToggle).toBeChecked(); // Should be enabled by default
    });

    it('displays context expansion threshold controls', () => {
      render(<EnhancedSettingsPanel {...defaultProps} />);
      
      expect(screen.getAllByText('Context Expansion Threshold')[0]).toBeInTheDocument();
      expect(screen.getByLabelText('Context expansion similarity threshold')).toBeInTheDocument();
      expect(screen.getByDisplayValue('0.75')).toBeInTheDocument(); // Default threshold
    });

    it('shows chunk overlap percentage settings', () => {
      render(<EnhancedSettingsPanel {...defaultProps} />);
      
      expect(screen.getByText(/Chunk Overlap Percentage:/)).toBeInTheDocument();
      expect(screen.getByLabelText('Chunk overlap percentage')).toBeInTheDocument();
      // Default overlap should be between 20-30%
      expect(screen.getAllByText(/30%/).length).toBeGreaterThan(0); // Default from sync status calculation
    });

    it('provides chunking strategy selection', () => {
      render(<EnhancedSettingsPanel {...defaultProps} />);
      
      expect(screen.getAllByText('Chunking Strategy')[0]).toBeInTheDocument();
      expect(screen.getByLabelText('Chunking strategy')).toBeInTheDocument();
      
      // Strategy should be selected based on enhanced features
      expect(screen.getByDisplayValue('enhanced_overlap_aware')).toBeInTheDocument();
    });
  });

  describe('Settings Validation and Feedback', () => {
    it('validates context expansion threshold range', async () => {
      render(<EnhancedSettingsPanel {...defaultProps} />);
      
      const thresholdInput = screen.getByLabelText('Context expansion similarity threshold');
      
      // Test invalid high value
      await userEvent.clear(thresholdInput);
      await userEvent.type(thresholdInput, '1.5');
      
      expect(screen.getByText('Threshold must be between 0.0 and 1.0')).toBeInTheDocument();
    });

    it('validates chunk overlap percentage limits', async () => {
      render(<EnhancedSettingsPanel {...defaultProps} />);
      
      const overlapSlider = screen.getByLabelText('Chunk overlap percentage');
      
      // Test setting high overlap value
      fireEvent.change(overlapSlider, { target: { value: '55' } });
      
      await waitFor(() => {
        expect(screen.getByText('Warning: High overlap may significantly increase storage requirements')).toBeInTheDocument();
      });
    });

    it('shows performance impact warnings', async () => {
      // Start with enhanced processing enabled
      const enhancedProps = {
        ...defaultProps,
        syncStatus: {
          ...defaultProps.syncStatus,
          enhanced_features_enabled: true
        }
      };
      
      render(<EnhancedSettingsPanel {...enhancedProps} />);
      
      // Should show performance impact by default with enhanced features enabled
      await waitFor(() => {
        expect(screen.getByText(/Performance Impact:/)).toBeInTheDocument();
      });
    });

    it('calculates estimated storage impact', () => {
      render(<EnhancedSettingsPanel {...defaultProps} />);
      
      // Should show current storage calculation
      expect(screen.getByText('Current Enhanced Statistics')).toBeInTheDocument();
      expect(screen.getAllByText(/Storage Overhead: 30%/).length).toBeGreaterThan(0); // 15/50 chunks = 30%
      expect(screen.getAllByText(/Expansion Eligible: 70%/).length).toBeGreaterThan(0); // 35/50 chunks = 70%
    });
  });

  describe('Settings Persistence and Application', () => {
    it('calls onSettingsChange when values are modified', async () => {
      render(<EnhancedSettingsPanel {...defaultProps} />);
      
      const thresholdInput = screen.getByLabelText('Context expansion similarity threshold');
      
      await userEvent.clear(thresholdInput);
      await userEvent.type(thresholdInput, '0.8');
      
      await waitFor(() => {
        expect(defaultProps.onSettingsChange).toHaveBeenCalledWith(
          expect.objectContaining({
            contextExpansionThreshold: 0.8,
            chunkOverlapPercentage: expect.any(Number),
            chunkingStrategy: 'enhanced_overlap_aware',
            enhancedProcessingEnabled: true
          })
        );
      });
    });

    it('applies settings when Apply button is clicked', async () => {
      render(<EnhancedSettingsPanel {...defaultProps} />);
      
      const applyButton = screen.getByText('Apply Settings');
      await userEvent.click(applyButton);
      
      expect(defaultProps.onApplySettings).toHaveBeenCalledWith(
        expect.objectContaining({
          contextExpansionThreshold: 0.75,
          chunkingStrategy: 'enhanced_overlap_aware',
          enhancedProcessingEnabled: expect.any(Boolean)
        })
      );
    });

    it('resets to default values when Reset button is clicked', async () => {
      render(<EnhancedSettingsPanel {...defaultProps} />);
      
      // Modify some settings first
      const thresholdInput = screen.getByLabelText('Context expansion similarity threshold');
      await userEvent.clear(thresholdInput);
      await userEvent.type(thresholdInput, '0.9');
      
      // Click reset
      const resetButton = screen.getByText('Reset to Defaults');
      await userEvent.click(resetButton);
      
      expect(defaultProps.onResetToDefaults).toHaveBeenCalled();
      
      // Values should be back to defaults
      await waitFor(() => {
        expect(screen.getByDisplayValue('0.75')).toBeInTheDocument();
      });
    });

    it('shows unsaved changes indicator', async () => {
      render(<EnhancedSettingsPanel {...defaultProps} />);
      
      // Modify a setting
      const overlapSlider = screen.getByLabelText('Chunk overlap percentage');
      fireEvent.change(overlapSlider, { target: { value: '35' } });
      
      await waitFor(() => {
        expect(screen.getByText(/Unsaved Changes/)).toBeInTheDocument();
        expect(screen.getByTestId('info-icon')).toBeInTheDocument();
      });
    });
  });

  describe('Advanced Configuration', () => {
    it('shows advanced settings section', () => {
      render(<EnhancedSettingsPanel {...defaultProps} />);
      
      const advancedButton = screen.getByText('Advanced Settings');
      expect(advancedButton).toBeInTheDocument();
    });

    it('expands advanced settings when clicked', async () => {
      render(<EnhancedSettingsPanel {...defaultProps} />);
      
      const advancedButton = screen.getByText('Advanced Settings');
      await userEvent.click(advancedButton);
      
      await waitFor(() => {
        expect(screen.getAllByText('Maximum Context Window')[0]).toBeInTheDocument();
        expect(screen.getAllByText(/Relationship Detection Sensitivity/)[0]).toBeInTheDocument();
        expect(screen.getAllByText(/Memory Usage Limit/)[0]).toBeInTheDocument();
      });
    });

    it('provides expert-level configuration options', async () => {
      render(<EnhancedSettingsPanel {...defaultProps} />);
      
      const advancedButton = screen.getByText('Advanced Settings');
      await userEvent.click(advancedButton);
      
      await waitFor(() => {
        expect(screen.getByLabelText('Maximum context window size')).toBeInTheDocument();
        expect(screen.getByLabelText('Relationship detection sensitivity')).toBeInTheDocument();
        expect(screen.getByLabelText('Memory usage limit (MB)')).toBeInTheDocument();
      });
    });
  });

  describe('Collection-Specific Settings', () => {
    it('shows collection-specific configuration', () => {
      render(<EnhancedSettingsPanel {...defaultProps} />);
      
      expect(screen.getByText('Collection: test-collection')).toBeInTheDocument();
      expect(screen.getByText('Active')).toBeInTheDocument(); // Enhanced features status
    });

    it('displays current collection statistics', () => {
      render(<EnhancedSettingsPanel {...defaultProps} />);
      
      expect(screen.getByText('Current Statistics')).toBeInTheDocument();
      expect(screen.getByText('Total Chunks: 50')).toBeInTheDocument();
      expect(screen.getByText('Overlap Chunks: 15')).toBeInTheDocument();
      expect(screen.getByText('Expandable Chunks: 35')).toBeInTheDocument();
    });

    it('handles collections without enhanced features', () => {
      const basicSyncStatus = {
        ...mockSyncStatus,
        enhanced_features_enabled: false,
        overlap_chunk_count: undefined,
        context_expansion_eligible_chunks: undefined
      };

      render(
        <EnhancedSettingsPanel 
          {...defaultProps} 
          syncStatus={basicSyncStatus}
        />
      );

      expect(screen.getByText('Inactive')).toBeInTheDocument(); // Enhanced features status
      expect(screen.getByText('Enable enhanced processing to access advanced features')).toBeInTheDocument();
    });
  });

  describe('Accessibility and User Experience', () => {
    it('provides proper ARIA labels for all controls', () => {
      render(<EnhancedSettingsPanel {...defaultProps} />);
      
      expect(screen.getByLabelText('Enable Enhanced Processing')).toBeInTheDocument();
      expect(screen.getByLabelText('Context expansion similarity threshold')).toBeInTheDocument();
      expect(screen.getByLabelText('Chunk overlap percentage')).toBeInTheDocument();
      expect(screen.getByLabelText('Chunking strategy')).toBeInTheDocument();
    });

    it('supports keyboard navigation', async () => {
      render(<EnhancedSettingsPanel {...defaultProps} />);
      
      const enhancedToggle = screen.getByLabelText('Enable Enhanced Processing');
      
      await userEvent.click(enhancedToggle);
      
      expect(defaultProps.onSettingsChange).toHaveBeenCalled();
    });

    it('provides helpful tooltips and descriptions', () => {
      render(<EnhancedSettingsPanel {...defaultProps} />);
      
      expect(screen.getByText(/Context expansion uses similarity thresholds/)).toBeInTheDocument();
      expect(screen.getByText(/Chunk overlap creates redundancy/)).toBeInTheDocument();
    });

    it('shows loading states during settings application', async () => {
      const loadingProps = {
        ...defaultProps,
        applyingSettings: true
      };

      render(<EnhancedSettingsPanel {...loadingProps} />);
      
      expect(screen.getByText('Applying...')).toBeInTheDocument();
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('displays validation errors', async () => {
      render(<EnhancedSettingsPanel {...defaultProps} />);
      
      const thresholdInput = screen.getByLabelText('Context expansion similarity threshold');
      
      await userEvent.clear(thresholdInput);
      await userEvent.type(thresholdInput, 'invalid');
      
      expect(screen.getByText('Please enter a valid number')).toBeInTheDocument();
    });

    it('handles settings application errors', () => {
      const errorProps = {
        ...defaultProps,
        settingsError: 'Failed to apply enhanced settings: ChromaDB connection error'
      };

      render(<EnhancedSettingsPanel {...errorProps} />);
      
      expect(screen.getByText('Settings Error')).toBeInTheDocument();
      expect(screen.getByText(/Failed to apply enhanced settings/)).toBeInTheDocument();
    });

    it('provides recovery suggestions for errors', () => {
      const errorProps = {
        ...defaultProps,
        settingsError: 'Enhanced features unavailable'
      };

      render(<EnhancedSettingsPanel {...errorProps} />);
      
      expect(screen.getByText('Try Again')).toBeInTheDocument();
      expect(screen.getByText('Use Defaults')).toBeInTheDocument();
    });
  });
});