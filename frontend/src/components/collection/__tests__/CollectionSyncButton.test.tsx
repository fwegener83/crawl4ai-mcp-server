import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider } from '@mui/material/styles';
import { vi } from 'vitest';
import { CollectionSyncButton } from '../CollectionSyncButton';
import { lightTheme } from '../../../theme';
import type { VectorSyncStatus } from '../../../types/api';

const theme = lightTheme;

const mockSyncStatus: VectorSyncStatus = {
  collection_name: 'test-collection',
  status: 'in_sync',
  sync_enabled: true,
  last_sync: '2024-01-01T00:00:00Z',
  total_files: 5,
  chunk_count: 50,
  changed_files_count: 0,
  sync_progress: 0,
  sync_health_score: 0.9,
  errors: []
};

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('CollectionSyncButton', () => {
  const mockOnSync = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders with default props', () => {
    renderWithTheme(
      <CollectionSyncButton
        collectionId="test-collection"
        onSync={mockOnSync}
      />
    );

    const button = screen.getByRole('button', { name: /sync collection/i });
    expect(button).toBeInTheDocument();
    expect(button).not.toHaveAttribute('data-testid');
  });

  it('renders with custom data-testid', () => {
    renderWithTheme(
      <CollectionSyncButton
        collectionId="test-collection"
        onSync={mockOnSync}
        data-testid="custom-sync-button"
      />
    );

    const button = screen.getByTestId('custom-sync-button');
    expect(button).toBeInTheDocument();
  });

  it('shows correct text for different sync states', () => {
    // Never synced
    const neverSyncedStatus = { ...mockSyncStatus, status: 'never_synced' as const };
    const { rerender } = renderWithTheme(
      <CollectionSyncButton
        collectionId="test-collection"
        onSync={mockOnSync}
        syncStatus={neverSyncedStatus}
      />
    );

    expect(screen.getByRole('button', { name: /initial sync/i })).toBeInTheDocument();

    // Regular sync status (removed "changed files" feature)
    const regularStatus = { 
      ...mockSyncStatus, 
      status: 'in_sync' as const
    };
    rerender(
      <ThemeProvider theme={theme}>
        <CollectionSyncButton
          collectionId="test-collection"
          onSync={mockOnSync}
          syncStatus={regularStatus}
        />
      </ThemeProvider>
    );

    expect(screen.getByRole('button', { name: /sync collection/i })).toBeInTheDocument();

    // Currently syncing (removed fake progress %)
    const syncingStatus = { 
      ...mockSyncStatus, 
      status: 'syncing' as const, 
      sync_progress: null // Backend doesn't provide real progress
    };
    rerender(
      <ThemeProvider theme={theme}>
        <CollectionSyncButton
          collectionId="test-collection"
          onSync={mockOnSync}
          syncStatus={syncingStatus}
        />
      </ThemeProvider>
    );

    expect(screen.getByRole('button', { name: /syncing\.\.\./i })).toBeInTheDocument();
  });

  it('shows different button colors based on status', () => {
    // Primary color for never synced
    const neverSyncedStatus = { ...mockSyncStatus, status: 'never_synced' as const };
    const { rerender } = renderWithTheme(
      <CollectionSyncButton
        collectionId="test-collection"
        onSync={mockOnSync}
        syncStatus={neverSyncedStatus}
      />
    );

    expect(screen.getByRole('button')).toHaveClass('MuiButton-outlinedPrimary');

    // Regular status (inherit color)
    const regularStatus = { ...mockSyncStatus, status: 'in_sync' as const };
    rerender(
      <ThemeProvider theme={theme}>
        <CollectionSyncButton
          collectionId="test-collection"
          onSync={mockOnSync}
          syncStatus={regularStatus}
        />
      </ThemeProvider>
    );

    expect(screen.getByRole('button')).toHaveClass('MuiButton-outlinedInherit');
  });

  it('calls onSync when button is clicked', async () => {
    renderWithTheme(
      <CollectionSyncButton
        collectionId="test-collection"
        onSync={mockOnSync}
        syncStatus={mockSyncStatus}
      />
    );

    const button = screen.getByRole('button');
    fireEvent.click(button);

    await waitFor(() => {
      expect(mockOnSync).toHaveBeenCalledTimes(1);
    });
  });

  it('disables button when disabled prop is true', () => {
    renderWithTheme(
      <CollectionSyncButton
        collectionId="test-collection"
        onSync={mockOnSync}
        disabled={true}
      />
    );

    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });

  it('disables button when syncing', () => {
    const syncingStatus = { 
      ...mockSyncStatus, 
      status: 'syncing' as const, 
      sync_progress: 0.5 
    };

    renderWithTheme(
      <CollectionSyncButton
        collectionId="test-collection"
        onSync={mockOnSync}
        syncStatus={syncingStatus}
      />
    );

    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });

  it('shows progress bar when syncing', () => {
    const syncingStatus = { 
      ...mockSyncStatus, 
      status: 'syncing' as const, 
      sync_progress: null // Backend doesn't provide real progress
    };

    renderWithTheme(
      <CollectionSyncButton
        collectionId="test-collection"
        onSync={mockOnSync}
        syncStatus={syncingStatus}
      />
    );

    expect(screen.getByRole('progressbar')).toBeInTheDocument();
    expect(screen.getByText('Synchronizing...')).toBeInTheDocument();
  });

  // Removed: "shows changed files chip" tests - Backend doesn't provide changed_files_count

  it('handles different button sizes', () => {
    const { rerender } = renderWithTheme(
      <CollectionSyncButton
        collectionId="test-collection"
        onSync={mockOnSync}
        size="small"
      />
    );

    const button = screen.getByRole('button');
    expect(button).toHaveClass('MuiButton-sizeSmall');

    rerender(
      <ThemeProvider theme={theme}>
        <CollectionSyncButton
          collectionId="test-collection"
          onSync={mockOnSync}
          size="large"
        />
      </ThemeProvider>
    );

    expect(screen.getByRole('button')).toHaveClass('MuiButton-sizeLarge');
  });

  it('does not call onSync when button is disabled', () => {
    renderWithTheme(
      <CollectionSyncButton
        collectionId="test-collection"
        onSync={mockOnSync}
        disabled={true}
      />
    );

    const button = screen.getByRole('button');
    fireEvent.click(button);

    expect(mockOnSync).not.toHaveBeenCalled();
  });

  it('has spinning animation on sync icon when syncing', () => {
    const syncingStatus = { 
      ...mockSyncStatus, 
      status: 'syncing' as const, 
      sync_progress: 0.25 
    };

    renderWithTheme(
      <CollectionSyncButton
        collectionId="test-collection"
        onSync={mockOnSync}
        syncStatus={syncingStatus}
      />
    );

    const syncIcon = screen.getByTestId('SyncIcon');
    expect(syncIcon).toHaveClass('animate-spin');
  });

  it('does not have spinning animation when not syncing', () => {
    renderWithTheme(
      <CollectionSyncButton
        collectionId="test-collection"
        onSync={mockOnSync}
        syncStatus={mockSyncStatus}
      />
    );

    const syncIcon = screen.getByTestId('SyncIcon');
    expect(syncIcon).not.toHaveClass('animate-spin');
  });

  it('handles async onSync function', async () => {
    const asyncMockOnSync = vi.fn().mockResolvedValue(undefined);

    renderWithTheme(
      <CollectionSyncButton
        collectionId="test-collection"
        onSync={asyncMockOnSync}
        syncStatus={mockSyncStatus}
      />
    );

    const button = screen.getByRole('button');
    fireEvent.click(button);

    await waitFor(() => {
      expect(asyncMockOnSync).toHaveBeenCalledTimes(1);
    });
  });
});