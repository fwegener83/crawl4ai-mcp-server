import React from 'react';
import {
  Button,
  Box,
  Typography,
  LinearProgress
} from '@mui/material';
import {
  Sync as SyncIcon
} from '@mui/icons-material';
import type { VectorSyncStatus } from '../../types/api';

interface CollectionSyncButtonProps {
  collectionId: string;
  syncStatus?: VectorSyncStatus;
  onSync: () => Promise<void>;
  disabled?: boolean;
  size?: 'small' | 'medium' | 'large';
  'data-testid'?: string;
}

export const CollectionSyncButton: React.FC<CollectionSyncButtonProps> = ({
  syncStatus,
  onSync,
  disabled = false,
  size = 'medium',
  'data-testid': dataTestId
}) => {
  const isSyncing = syncStatus?.status === 'syncing';
  const canSync = !isSyncing && !disabled;

  const handleSync = async () => {
    if (canSync) {
      await onSync();
    }
  };

  const getSyncButtonText = () => {
    if (isSyncing) {
      return 'Syncing...';  // No fake progress % - backend doesn't provide it
    }
    
    // Remove fake "changed files" feature - backend doesn't provide this
    if (syncStatus?.status === 'never_synced') {
      return 'Initial Sync';
    }
    
    return 'Sync Collection';
  };

  const getSyncButtonColor = () => {
    // Remove fake "hasChanges" logic - backend doesn't provide changed_files_count
    if (syncStatus?.status === 'never_synced') return 'primary';
    return 'inherit';
  };

  const renderProgressInfo = () => {
    if (!isSyncing || !syncStatus) return null;

    // Backend doesn't provide real progress - show indeterminate progress bar
    return (
      <Box sx={{ mt: 1, minWidth: 200 }}>
        <LinearProgress 
          variant="indeterminate"
          sx={{ height: 4, borderRadius: 2 }}
        />
        <Typography variant="caption" color="textSecondary" sx={{ mt: 0.5, display: 'block', textAlign: 'center' }}>
          Synchronizing...
        </Typography>
      </Box>
    );
  };

  return (
    <Box>
      {/* Simplified Sync Button */}
      <Button
        data-testid={dataTestId}
        variant="outlined"
        color={getSyncButtonColor() as 'inherit' | 'primary' | 'secondary' | 'success' | 'error' | 'info' | 'warning'}
        size={size}
        disabled={!canSync}
        onClick={handleSync}
        startIcon={<SyncIcon className={isSyncing ? "animate-spin" : ""} />}
        sx={{ minWidth: 140 }}
      >
        {getSyncButtonText()}
      </Button>

      {/* Simplified Progress Display - only when really syncing */}
      {isSyncing && renderProgressInfo()}
    </Box>
  );
};

export default CollectionSyncButton;