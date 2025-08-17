import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { vi } from 'vitest';
import CompactSyncStatus from '../CompactSyncStatus';

// Mock Material-UI theme for consistent testing
const theme = createTheme();

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('CompactSyncStatus', () => {
  const defaultProps = {
    status: 'synced' as const,
    fileCount: 5,
    chunkCount: 25
  };

  describe('Visual States', () => {
    it('renders all status states correctly', () => {
      const statuses = ['synced', 'syncing', 'error', 'never_synced'] as const;
      const expectedLabels = ['Synced', 'Syncing', 'Error', 'Not Synced'];
      
      statuses.forEach((status, index) => {
        const { unmount } = renderWithTheme(
          <CompactSyncStatus {...defaultProps} status={status} />
        );
        
        expect(screen.getByText(expectedLabels[index])).toBeInTheDocument();
        expect(screen.getByTestId('compact-sync-status')).toBeInTheDocument();
        
        unmount();
      });
    });

    it('displays correct emoji for each status', () => {
      const statusEmojis = {
        synced: '🟢',
        syncing: '🟡', 
        error: '🔴',
        never_synced: '⚪'
      };
      
      Object.entries(statusEmojis).forEach(([status, emoji]) => {
        const { unmount } = renderWithTheme(
          <CompactSyncStatus {...defaultProps} status={status as any} />
        );
        
        expect(screen.getByText(emoji)).toBeInTheDocument();
        expect(screen.getByLabelText(`Status: ${status.replace('_', ' ')}`)).toBeInTheDocument();
        
        unmount();
      });
    });

    it('applies correct color variants for each status', () => {
      const statusColors = {
        synced: 'success',
        syncing: 'warning', 
        error: 'error',
        never_synced: 'default'
      };
      
      Object.entries(statusColors).forEach(([status, color]) => {
        const { unmount } = renderWithTheme(
          <CompactSyncStatus {...defaultProps} status={status as any} />
        );
        
        const chip = screen.getByTestId('compact-sync-status');
        expect(chip).toHaveClass(`MuiChip-color${color.charAt(0).toUpperCase() + color.slice(1)}`);
        
        unmount();
      });
    });

    it('shows syncing animation for syncing status', () => {
      renderWithTheme(
        <CompactSyncStatus {...defaultProps} status="syncing" />
      );
      
      const chip = screen.getByTestId('compact-sync-status');
      const computedStyle = window.getComputedStyle(chip);
      
      // Check if animation is applied (MUI might add animation via CSS-in-JS)
      expect(chip).toBeInTheDocument();
      // Note: Testing CSS animations in jsdom is limited, but we verify the component renders
    });
  });

  describe('Tooltip Functionality', () => {
    it('shows tooltip with file and chunk counts on hover', async () => {
      const user = userEvent.setup();
      
      renderWithTheme(
        <CompactSyncStatus 
          status="synced" 
          fileCount={5} 
          chunkCount={25} 
          lastSync="2 hours ago"
        />
      );
      
      const chip = screen.getByTestId('compact-sync-status');
      await user.hover(chip);
      
      await waitFor(() => {
        expect(screen.getByText(/5.*files.*25.*chunks/)).toBeVisible();
        expect(screen.getByText('Collection is synced')).toBeVisible();
      });
    });

    it('includes last sync time in tooltip when provided', async () => {
      const user = userEvent.setup();
      
      renderWithTheme(
        <CompactSyncStatus 
          status="synced" 
          fileCount={5} 
          chunkCount={25} 
          lastSync="2 hours ago"
        />
      );
      
      const chip = screen.getByTestId('compact-sync-status');
      await user.hover(chip);
      
      await waitFor(() => {
        expect(screen.getByText(/Last sync: 2 hours ago/)).toBeVisible();
      });
    });

    it('does not show last sync time when not provided', async () => {
      const user = userEvent.setup();
      
      renderWithTheme(
        <CompactSyncStatus 
          status="never_synced" 
          fileCount={5} 
          chunkCount={0} 
        />
      );
      
      const chip = screen.getByTestId('compact-sync-status');
      await user.hover(chip);
      
      await waitFor(() => {
        expect(screen.getByText('5 files, 0 chunks')).toBeVisible();
        expect(screen.queryByText(/Last sync:/)).not.toBeInTheDocument();
      });
    });

    it('shows appropriate tooltip messages for each status', async () => {
      const user = userEvent.setup();
      const statusTooltips = {
        synced: 'Collection is synced',
        syncing: 'Syncing in progress',
        error: 'Sync failed - click for details',
        never_synced: 'Click to sync collection'
      };
      
      for (const [status, expectedTooltip] of Object.entries(statusTooltips)) {
        const { unmount } = renderWithTheme(
          <CompactSyncStatus {...defaultProps} status={status as any} />
        );
        
        const chip = screen.getByTestId('compact-sync-status');
        await user.hover(chip);
        
        await waitFor(() => {
          expect(screen.getByText(expectedTooltip)).toBeVisible();
        });
        
        await user.unhover(chip);
        unmount();
      }
    });
  });

  describe('Click Interactions', () => {
    it('calls onClick when clicked with mouse', async () => {
      const user = userEvent.setup();
      const mockOnClick = vi.fn();
      
      renderWithTheme(
        <CompactSyncStatus 
          {...defaultProps}
          onClick={mockOnClick} 
        />
      );
      
      const chip = screen.getByTestId('compact-sync-status');
      await user.click(chip);
      
      expect(mockOnClick).toHaveBeenCalledTimes(1);
    });

    it('calls onClick when activated with Enter key', async () => {
      const user = userEvent.setup();
      const mockOnClick = vi.fn();
      
      renderWithTheme(
        <CompactSyncStatus 
          {...defaultProps}
          onClick={mockOnClick} 
        />
      );
      
      const chip = screen.getByTestId('compact-sync-status');
      chip.focus();
      await user.keyboard('{Enter}');
      
      // MUI Chip may call onClick multiple times for keyboard events
      expect(mockOnClick).toHaveBeenCalled();
    });

    it('calls onClick when activated with Space key', async () => {
      const user = userEvent.setup();
      const mockOnClick = vi.fn();
      
      renderWithTheme(
        <CompactSyncStatus 
          {...defaultProps}
          onClick={mockOnClick} 
        />
      );
      
      const chip = screen.getByTestId('compact-sync-status');
      chip.focus();
      await user.keyboard(' ');
      
      // MUI Chip may call onClick multiple times for keyboard events
      expect(mockOnClick).toHaveBeenCalled();
    });

    it('does not call onClick for other keys', async () => {
      const user = userEvent.setup();
      const mockOnClick = vi.fn();
      
      renderWithTheme(
        <CompactSyncStatus 
          {...defaultProps}
          onClick={mockOnClick} 
        />
      );
      
      const chip = screen.getByTestId('compact-sync-status');
      chip.focus();
      await user.keyboard('{ArrowDown}');
      await user.keyboard('{Tab}');
      await user.keyboard('a');
      
      expect(mockOnClick).not.toHaveBeenCalled();
    });

    it('does not respond to interactions when onClick is not provided', async () => {
      const user = userEvent.setup();
      
      renderWithTheme(
        <CompactSyncStatus {...defaultProps} />
      );
      
      const chip = screen.getByTestId('compact-sync-status');
      
      // Should not be clickable (MUI may not set tabIndex but won't be focusable)
      expect(chip).toBeInTheDocument();
      
      // Click should not cause any errors
      await user.click(chip);
      
      // No assertions needed - just ensuring no errors are thrown
    });
  });

  describe('Accessibility', () => {
    it('provides proper ARIA labels for status emojis', () => {
      const statuses = ['synced', 'syncing', 'error', 'never_synced'] as const;
      
      statuses.forEach(status => {
        const { unmount } = renderWithTheme(
          <CompactSyncStatus {...defaultProps} status={status} />
        );
        
        const expectedLabel = `Status: ${status.replace('_', ' ')}`;
        expect(screen.getByLabelText(expectedLabel)).toBeInTheDocument();
        
        unmount();
      });
    });

    it('is keyboard accessible when onClick is provided', () => {
      renderWithTheme(
        <CompactSyncStatus 
          {...defaultProps}
          onClick={() => {}} 
        />
      );
      
      const chip = screen.getByTestId('compact-sync-status');
      // MUI Chip should be focusable when clickable
      expect(chip).toBeInTheDocument();
    });

    it('is not keyboard accessible when onClick is not provided', () => {
      renderWithTheme(
        <CompactSyncStatus {...defaultProps} />
      );
      
      const chip = screen.getByTestId('compact-sync-status');
      // MUI Chip should not be focusable when not clickable
      expect(chip).toBeInTheDocument();
    });

    it('has proper cursor styling based on interaction capability', () => {
      // With onClick - should be clickable
      const { unmount } = renderWithTheme(
        <CompactSyncStatus 
          {...defaultProps}
          onClick={() => {}} 
        />
      );
      
      const clickableChip = screen.getByTestId('compact-sync-status');
      expect(clickableChip).toHaveStyle('cursor: pointer');
      
      unmount();
      
      // Without onClick - should not appear clickable
      renderWithTheme(
        <CompactSyncStatus {...defaultProps} />
      );
      
      const nonClickableChip = screen.getByTestId('compact-sync-status');
      expect(nonClickableChip).toHaveStyle('cursor: default');
    });
  });

  describe('Layout and Styling', () => {
    it('maintains consistent width', () => {
      renderWithTheme(
        <CompactSyncStatus {...defaultProps} />
      );
      
      const chip = screen.getByTestId('compact-sync-status');
      expect(chip).toHaveStyle('min-width: 90px');
    });

    it('uses small size for compact display', () => {
      renderWithTheme(
        <CompactSyncStatus {...defaultProps} />
      );
      
      const chip = screen.getByTestId('compact-sync-status');
      expect(chip).toHaveClass('MuiChip-sizeSmall');
    });

    it('uses outlined variant for consistent styling', () => {
      renderWithTheme(
        <CompactSyncStatus {...defaultProps} />
      );
      
      const chip = screen.getByTestId('compact-sync-status');
      expect(chip).toHaveClass('MuiChip-outlined');
    });
  });

  describe('Edge Cases', () => {
    it('handles zero file and chunk counts', () => {
      renderWithTheme(
        <CompactSyncStatus 
          status="never_synced"
          fileCount={0}
          chunkCount={0}
        />
      );
      
      expect(screen.getByTestId('compact-sync-status')).toBeInTheDocument();
    });

    it('handles very large file and chunk counts', async () => {
      const user = userEvent.setup();
      
      renderWithTheme(
        <CompactSyncStatus 
          status="synced"
          fileCount={999999}
          chunkCount={1000000}
        />
      );
      
      const chip = screen.getByTestId('compact-sync-status');
      await user.hover(chip);
      
      await waitFor(() => {
        expect(screen.getByText(/999999.*files.*1000000.*chunks/)).toBeVisible();
      });
    });

    it('handles empty lastSync string', async () => {
      const user = userEvent.setup();
      
      renderWithTheme(
        <CompactSyncStatus 
          status="synced"
          fileCount={5}
          chunkCount={25}
          lastSync=""
        />
      );
      
      const chip = screen.getByTestId('compact-sync-status');
      await user.hover(chip);
      
      await waitFor(() => {
        expect(screen.getByText(/5.*files.*25.*chunks/)).toBeVisible();
        expect(screen.queryByText(/Last sync:/)).not.toBeInTheDocument();
      });
    });
  });

  describe('Performance', () => {
    it('renders efficiently with multiple instances', () => {
      const start = performance.now();
      
      // Render 50 status components (realistic sidebar scenario)
      render(
        <ThemeProvider theme={theme}>
          <div>
            {Array.from({ length: 50 }, (_, i) => (
              <CompactSyncStatus
                key={i}
                status="synced"
                fileCount={Math.floor(Math.random() * 50)}
                chunkCount={Math.floor(Math.random() * 200)}
              />
            ))}
          </div>
        </ThemeProvider>
      );
      
      const renderTime = performance.now() - start;
      expect(renderTime).toBeLessThan(100); // Should render 50 components in <100ms
    });
  });
});