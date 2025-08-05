import React from 'react';
import { render, screen } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { VectorSyncIndicator } from '../VectorSyncIndicator';
import type { VectorSyncStatus } from '../../../types/api';

const theme = createTheme();

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('VectorSyncIndicator', () => {
  const mockCollectionName = 'test-collection';

  const createMockStatus = (overrides: Partial<VectorSyncStatus> = {}): VectorSyncStatus => ({
    collection_name: mockCollectionName,
    sync_enabled: true,
    status: 'in_sync',
    total_files: 10,
    synced_files: 10,
    changed_files_count: 0,
    chunk_count: 25,
    total_chunks: 25,
    last_sync: '2025-08-04T10:00:00Z',
    last_sync_attempt: '2025-08-04T10:00:00Z',
    last_sync_duration: 2.5,
    sync_progress: null,
    sync_health_score: 0.95,
    errors: [],
    warnings: [],
    ...overrides,
  });

  it('renders without crashing', () => {
    renderWithTheme(
      <VectorSyncIndicator 
        collectionName={mockCollectionName}
        syncStatus={createMockStatus()}
      />
    );
    
    // VectorSyncIndicator renders a Tooltip with Badge, not a button
    expect(document.querySelector('.MuiBadge-root')).toBeInTheDocument();
  });

  it('shows unknown status when no sync status provided', () => {
    renderWithTheme(
      <VectorSyncIndicator 
        collectionName={mockCollectionName}
      />
    );
    
    // Check that indicator renders with unknown status
    expect(document.querySelector('.MuiBadge-root')).toBeInTheDocument();
    expect(document.querySelector('[data-testid="ScheduleIcon"]')).toBeInTheDocument();
  });

  it('displays in sync status correctly', () => {
    const status = createMockStatus({ status: 'in_sync', sync_health_score: 0.9 });
    
    renderWithTheme(
      <VectorSyncIndicator 
        collectionName={mockCollectionName}
        syncStatus={status}
        showText={true}
      />
    );
    
    expect(screen.getByText('In sync')).toBeInTheDocument();
  });

  it('shows out of sync status with file count', () => {
    const status = createMockStatus({ 
      status: 'out_of_sync', 
      changed_files_count: 3 
    });
    
    renderWithTheme(
      <VectorSyncIndicator 
        collectionName={mockCollectionName}
        syncStatus={status}
        showText={true}
      />
    );
    
    expect(screen.getByText('3 files changed')).toBeInTheDocument();
  });

  it('shows syncing status with progress', () => {
    const status = createMockStatus({ 
      status: 'syncing', 
      sync_progress: 0.6 
    });
    
    renderWithTheme(
      <VectorSyncIndicator 
        collectionName={mockCollectionName}
        syncStatus={status}
        showText={true}
      />
    );
    
    expect(screen.getByText('Syncing... 60%')).toBeInTheDocument();
  });

  it('shows error status with error count', () => {
    const status = createMockStatus({ 
      status: 'sync_error', 
      errors: ['Error 1', 'Error 2'] 
    });
    
    renderWithTheme(
      <VectorSyncIndicator 
        collectionName={mockCollectionName}
        syncStatus={status}
        showText={true}
      />
    );
    
    expect(screen.getByText('Error (2)')).toBeInTheDocument();
  });

  it('shows never synced status', () => {
    const status = createMockStatus({ status: 'never_synced' });
    
    renderWithTheme(
      <VectorSyncIndicator 
        collectionName={mockCollectionName}
        syncStatus={status}
        showText={true}
      />
    );
    
    expect(screen.getByText('Never synced')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const customClass = 'custom-indicator';
    
    renderWithTheme(
      <VectorSyncIndicator 
        collectionName={mockCollectionName}
        syncStatus={createMockStatus()}
        className={customClass}
      />
    );
    
    expect(document.querySelector(`.${customClass}`)).toBeInTheDocument();
  });

  it('renders with different sizes', () => {
    const { rerender } = renderWithTheme(
      <VectorSyncIndicator 
        collectionName={mockCollectionName}
        syncStatus={createMockStatus()}
        size="small"
      />
    );
    
    expect(document.querySelector('.MuiBadge-root')).toBeInTheDocument();
    
    rerender(
      <ThemeProvider theme={theme}>
        <VectorSyncIndicator 
          collectionName={mockCollectionName}
          syncStatus={createMockStatus()}
          size="large"
        />
      </ThemeProvider>
    );
    
    expect(document.querySelector('.MuiBadge-root')).toBeInTheDocument();
  });
});