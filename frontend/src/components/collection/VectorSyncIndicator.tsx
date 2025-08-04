import React from 'react';
import { Badge, Tooltip, Typography, Box } from '@mui/material';
import { 
  Sync as SyncIcon,
  CheckCircle as CheckCircleIcon, 
  Error as ErrorIcon,
  Warning as WarningIcon,
  CloudUpload as CloudUploadIcon,
  Schedule as ScheduleIcon
} from '@mui/icons-material';
import type { VectorSyncStatus } from '../../types/api';

interface VectorSyncIndicatorProps {
  collectionName: string;
  syncStatus?: VectorSyncStatus;
  size?: 'small' | 'medium' | 'large';
  showText?: boolean;
  className?: string;
}

export const VectorSyncIndicator: React.FC<VectorSyncIndicatorProps> = ({
  collectionName,
  syncStatus,
  size = 'medium',
  showText = false,
  className = ''
}) => {
  // Get status display information
  const getStatusInfo = () => {
    if (!syncStatus) {
      return {
        icon: <ScheduleIcon />,
        color: 'default' as const,
        text: 'Unknown',
        tooltipTitle: 'Vector sync status unknown'
      };
    }

    const { status, sync_progress, changed_files_count, sync_health_score, errors } = syncStatus;

    switch (status) {
      case 'never_synced':
        return {
          icon: <CloudUploadIcon />,
          color: 'info' as const,
          text: 'Never synced',
          tooltipTitle: `Collection "${collectionName}" has never been synced to vector store`
        };

      case 'in_sync':
        return {
          icon: <CheckCircleIcon />,
          color: 'success' as const,
          text: 'In sync',
          tooltipTitle: `Collection "${collectionName}" is up to date (Health: ${Math.round(sync_health_score * 100)}%)`
        };

      case 'out_of_sync':
        return {
          icon: <SyncIcon />,
          color: 'warning' as const,
          text: `${changed_files_count} files changed`,
          tooltipTitle: `${changed_files_count} files have changed since last sync`
        };

      case 'syncing': {
        const progressPercent = sync_progress ? Math.round(sync_progress * 100) : 0;
        return {
          icon: <SyncIcon className="animate-spin" />,
          color: 'primary' as const,
          text: `Syncing... ${progressPercent}%`,
          tooltipTitle: `Syncing collection "${collectionName}" - ${progressPercent}% complete`
        };
      }

      case 'sync_error':
        return {
          icon: <ErrorIcon />,
          color: 'error' as const,
          text: `Error (${errors.length})`,
          tooltipTitle: `Sync failed: ${errors[0] || 'Unknown error'}`
        };

      case 'partial_sync':
        return {
          icon: <WarningIcon />,
          color: 'warning' as const,
          text: 'Partial sync',
          tooltipTitle: `Partial sync completed with ${errors.length} errors`
        };

      default:
        return {
          icon: <ScheduleIcon />,
          color: 'default' as const,
          text: 'Unknown',
          tooltipTitle: 'Unknown sync status'
        };
    }
  };

  const statusInfo = getStatusInfo();

  // Icon size mapping
  const iconSizes = {
    small: { fontSize: 16 },
    medium: { fontSize: 20 },
    large: { fontSize: 24 }
  };

  const renderContent = () => {
    if (showText) {
      return (
        <Box display="flex" alignItems="center" gap={1} className={className}>
          <Badge
            color={statusInfo.color}
            variant="dot"
            overlap="circular"
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
          >
            {React.cloneElement(statusInfo.icon, { style: iconSizes[size] })}
          </Badge>
          <Typography variant="body2" color="textSecondary">
            {statusInfo.text}
          </Typography>
        </Box>
      );
    }

    return (
      <Badge
        color={statusInfo.color}
        variant="dot"
        overlap="circular"
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        className={className}
      >
        {React.cloneElement(statusInfo.icon, { style: iconSizes[size] })}
      </Badge>
    );
  };

  return (
    <Tooltip title={statusInfo.tooltipTitle} arrow>
      {renderContent()}
    </Tooltip>
  );
};

export default VectorSyncIndicator;