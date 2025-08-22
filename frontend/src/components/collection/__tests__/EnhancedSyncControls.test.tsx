import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { EnhancedSyncControls } from '../EnhancedSyncControls';
import APIService from '../../../services/api';
import type { VectorSyncStatus } from '../../../types/api';

// Mock API Service
vi.mock('../../../services/api');
const mockAPIService = vi.mocked(APIService);

// Mock props
const mockProps = {
  collectionId: 'test-collection',
  collectionName: 'Test Collection',
  onSyncStarted: vi.fn(),
  onSyncCompleted: vi.fn(),
};

const mockSyncStatus: VectorSyncStatus = {
  collection_name: 'test-collection',
  sync_enabled: true,
  status: 'in_sync',
  total_files: 5,
  synced_files: 5,
  changed_files_count: 0,
  chunk_count: 50,
  total_chunks: 50,
  last_sync: new Date().toISOString(),
  last_sync_attempt: new Date().toISOString(),
  last_sync_duration: null,
  sync_progress: null,
  sync_health_score: 1.0,
  errors: [],
  warnings: []
};

describe('EnhancedSyncControls', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders basic sync button', () => {
    render(<EnhancedSyncControls {...mockProps} />);
    
    // Use more specific selectors
    expect(screen.getByRole('button', { name: /sync/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/more options/i)).toBeInTheDocument();
  });

  it('shows sync status when provided', () => {
    render(<EnhancedSyncControls {...mockProps} syncStatus={mockSyncStatus} />);
    
    expect(screen.getByText('in sync')).toBeInTheDocument();
    expect(screen.getByText('50 vectors')).toBeInTheDocument();
    expect(screen.getByText('5 files')).toBeInTheDocument();
  });

  it('calls syncCollection when sync button clicked', async () => {
    mockAPIService.syncCollection.mockResolvedValueOnce({
      success: true,
      job_id: 'test-job',
      message: 'Sync started',
    });

    render(<EnhancedSyncControls {...mockProps} />);
    
    const syncButton = screen.getByRole('button', { name: /^sync$/i });
    fireEvent.click(syncButton);

    await waitFor(() => {
      expect(mockAPIService.syncCollection).toHaveBeenCalledWith('test-collection');
      expect(mockProps.onSyncStarted).toHaveBeenCalled();
    });
  });

  it('shows force resync option in menu', async () => {
    render(<EnhancedSyncControls {...mockProps} />);
    
    // Find the icon button by its MoreVertIcon testid
    const menuButton = screen.getByTestId('MoreVertIcon').closest('button')!;
    fireEvent.click(menuButton);

    await waitFor(() => {
      expect(screen.getByText('Force Resync')).toBeInTheDocument();
      expect(screen.getByText('Delete all vectors and resync')).toBeInTheDocument();
    });
  });

  it('calls forceResyncCollection when force resync clicked', async () => {
    mockAPIService.forceResyncCollection.mockResolvedValueOnce({
      success: true,
      job_id: 'test-job',
      message: 'Force resync started',
    });

    render(<EnhancedSyncControls {...mockProps} />);
    
    // Find the icon button by its MoreVertIcon testid
    const menuButton = screen.getByTestId('MoreVertIcon').closest('button')!;
    fireEvent.click(menuButton);

    await waitFor(() => {
      const forceResyncItem = screen.getByText('Force Resync');
      fireEvent.click(forceResyncItem);
    });

    await waitFor(() => {
      expect(mockAPIService.forceResyncCollection).toHaveBeenCalledWith('test-collection');
      expect(mockProps.onSyncStarted).toHaveBeenCalled();
    });
  });

  it('shows model info when requested', async () => {
    const mockModelInfo = {
      status: mockSyncStatus,
      modelInfo: {
        vector_service_available: true,
        model_name: 'distiluse-base-multilingual-cased-v1',
        device: 'cpu',
        model_dimension: 512,
        model_properties: {
          max_sequence_length: 128
        }
      }
    };

    mockAPIService.getCollectionSyncStatusWithModel.mockResolvedValueOnce(mockModelInfo);

    render(<EnhancedSyncControls {...mockProps} />);
    
    // Find the icon button by its MoreVertIcon testid
    const menuButton = screen.getByTestId('MoreVertIcon').closest('button')!;
    fireEvent.click(menuButton);

    await waitFor(() => {
      const modelInfoItem = screen.getByText('Model Info');
      fireEvent.click(modelInfoItem);
    });

    await waitFor(() => {
      expect(screen.getByText('Vector Model Information')).toBeInTheDocument();
      expect(screen.getByText('distiluse-base-multilingual-cased-v1')).toBeInTheDocument();
      expect(screen.getByText('cpu')).toBeInTheDocument();
      expect(screen.getByText('512')).toBeInTheDocument();
    });
  });

  it('handles model info error gracefully', async () => {
    mockAPIService.getCollectionSyncStatusWithModel.mockRejectedValueOnce(new Error('API Error'));

    render(<EnhancedSyncControls {...mockProps} />);
    
    // Find the icon button by its MoreVertIcon testid
    const menuButton = screen.getByTestId('MoreVertIcon').closest('button')!;
    fireEvent.click(menuButton);

    await waitFor(() => {
      const modelInfoItem = screen.getByText('Model Info');
      fireEvent.click(modelInfoItem);
    });

    await waitFor(() => {
      expect(screen.getByText('Failed to load model information')).toBeInTheDocument();
    });
  });

  it('disables buttons when syncing', () => {
    const syncingStatus: VectorSyncStatus = {
      ...mockSyncStatus,
      status: 'syncing'
    };

    render(<EnhancedSyncControls {...mockProps} syncStatus={syncingStatus} />);
    
    const syncButton = screen.getByRole('button', { name: /syncing.../i });
    expect(syncButton).toBeDisabled();
  });

  it('shows initial sync text for never synced collections', () => {
    const neverSyncedStatus: VectorSyncStatus = {
      ...mockSyncStatus,
      status: 'never_synced'
    };

    render(<EnhancedSyncControls {...mockProps} syncStatus={neverSyncedStatus} />);
    
    expect(screen.getByRole('button', { name: /initial sync/i })).toBeInTheDocument();
  });

  it('respects disabled prop', () => {
    render(<EnhancedSyncControls {...mockProps} disabled={true} />);
    
    const syncButton = screen.getByRole('button', { name: /^sync$/i });
    expect(syncButton).toBeDisabled();
    
    const menuButton = screen.getByTestId('MoreVertIcon').closest('button')!;
    expect(menuButton).toBeDisabled();
  });
});