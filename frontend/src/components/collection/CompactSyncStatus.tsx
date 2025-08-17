import React from 'react';
import {
  Chip,
  Tooltip,
  Box,
  Typography
} from '@mui/material';

interface CompactSyncStatusProps {
  status: 'synced' | 'syncing' | 'error' | 'never_synced';
  fileCount: number;
  chunkCount: number;
  lastSync?: string;
  onClick?: () => void;
}

const CompactSyncStatus: React.FC<CompactSyncStatusProps> = ({
  status,
  fileCount,
  chunkCount,
  lastSync,
  onClick
}) => {
  const statusConfig = {
    synced: { 
      icon: '🟢', 
      color: 'success' as const, 
      tooltip: 'Collection is synced',
      label: 'Synced'
    },
    syncing: { 
      icon: '🟡', 
      color: 'warning' as const, 
      tooltip: 'Syncing in progress',
      label: 'Syncing'
    },
    error: { 
      icon: '🔴', 
      color: 'error' as const, 
      tooltip: 'Sync failed - click for details',
      label: 'Error'
    },
    never_synced: { 
      icon: '⚪', 
      color: 'default' as const, 
      tooltip: 'Click to sync collection',
      label: 'Not Synced'
    }
  }[status];

  // Progressive disclosure: Basic info in tooltip
  const tooltipContent = (
    <Box>
      <Typography variant="body2" fontWeight="bold">
        {statusConfig.tooltip}
      </Typography>
      <Typography variant="caption">
        {fileCount} files, {chunkCount} chunks
        {lastSync && (
          <>
            <br />
            Last sync: {lastSync}
          </>
        )}
      </Typography>
    </Box>
  );

  return (
    <Tooltip title={tooltipContent} placement="bottom" arrow>
      <Chip
        icon={<span role="img" aria-label={`Status: ${status.replace('_', ' ')}`}>{statusConfig.icon}</span>}
        label={statusConfig.label}
        onClick={onClick}
        size="small"
        color={statusConfig.color}
        variant="outlined"
        sx={{
          cursor: onClick ? 'pointer' : 'default',
          minWidth: 90,  // Consistent width
          '&:hover': onClick ? { 
            bgcolor: 'action.hover',
            transform: 'scale(1.02)',
            transition: 'transform 0.1s ease-in-out'
          } : {},
          // Status-specific styling
          ...(status === 'syncing' && {
            animation: 'pulse 2s infinite'
          })
        }}
        data-testid="compact-sync-status"
      />
    </Tooltip>
  );
};

export default CompactSyncStatus;