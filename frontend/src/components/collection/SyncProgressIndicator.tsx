import React from 'react';
import {
  Box,
  Typography,
  LinearProgress,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Collapse,
  Alert,
  IconButton
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Sync as SyncIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  InsertDriveFile as FileIcon,
  Schedule as ScheduleIcon
} from '@mui/icons-material';
import type { VectorSyncStatus, SyncResult } from '../../types/api';

interface SyncProgressIndicatorProps {
  syncStatus: VectorSyncStatus;
  syncResult?: SyncResult;
  showDetails?: boolean;
  onToggleDetails?: () => void;
  compact?: boolean;
}

export const SyncProgressIndicator: React.FC<SyncProgressIndicatorProps> = ({
  syncStatus,
  syncResult,
  showDetails = false,
  onToggleDetails,
  compact = false
}) => {
  const {
    status,
    sync_progress,
    changed_files_count,
    total_files,
    chunk_count,
    errors,
    warnings,
    last_sync_duration,
    sync_health_score
  } = syncStatus;

  const isSyncing = status === 'syncing';
  const hasErrors = errors.length > 0;
  const hasWarnings = warnings.length > 0;

  // Calculate progress information
  const progressPercent = sync_progress ? sync_progress * 100 : 0;
  const filesProcessed = sync_progress && changed_files_count 
    ? Math.floor(sync_progress * changed_files_count)
    : 0;
  const totalToProcess = changed_files_count || total_files;

  const getStatusIcon = () => {
    switch (status) {
      case 'syncing':
        return <SyncIcon className="animate-spin" color="primary" />;
      case 'in_sync':
        return <CheckCircleIcon color="success" />;
      case 'sync_error':
        return <ErrorIcon color="error" />;
      case 'partial_sync':
        return <WarningIcon color="warning" />;
      case 'out_of_sync':
        return <ScheduleIcon color="warning" />;
      default:
        return <ScheduleIcon color="disabled" />;
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'syncing':
        return `Syncing... ${progressPercent.toFixed(1)}%`;
      case 'in_sync':
        return 'Vector sync complete';
      case 'sync_error':
        return `Sync failed (${errors.length} errors)`;
      case 'partial_sync':
        return `Partial sync (${warnings.length} warnings)`;
      case 'out_of_sync':
        return changed_files_count > 0 ? `${changed_files_count} files changed` : 'Files changed';
      case 'never_synced':
        return 'Never synced to vector store';
      default:
        return 'Unknown sync status';
    }
  };

  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${seconds.toFixed(1)}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds.toFixed(0)}s`;
  };

  const renderCompactView = () => (
    <Box display="flex" alignItems="center" gap={1}>
      {getStatusIcon()}
      <Typography variant="body2" sx={{ flex: 1 }}>
        {getStatusText()}
      </Typography>
      {isSyncing && (
        <Typography variant="caption" color="textSecondary">
          {filesProcessed}/{totalToProcess}
        </Typography>
      )}
      {hasErrors && (
        <Chip size="small" label={errors.length} color="error" />
      )}
      {hasWarnings && (
        <Chip size="small" label={warnings.length} color="warning" />
      )}
    </Box>
  );

  const renderFullView = () => (
    <Paper elevation={1} sx={{ p: 2 }}>
      {/* Header */}
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
        <Box display="flex" alignItems="center" gap={1}>
          {getStatusIcon()}
          <Typography variant="h6" component="h3">
            Vector Sync Status
          </Typography>
        </Box>
        {onToggleDetails && (
          <IconButton onClick={onToggleDetails} size="small">
            {showDetails ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
        )}
      </Box>

      {/* Progress Bar (when syncing) */}
      {isSyncing && (
        <Box mb={2}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
            <Typography variant="body2" color="textSecondary">
              Processing files...
            </Typography>
            <Typography variant="body2" color="textSecondary">
              {filesProcessed}/{totalToProcess}
            </Typography>
          </Box>
          <LinearProgress 
            variant="determinate" 
            value={progressPercent} 
            sx={{ height: 8, borderRadius: 4 }}
          />
          <Typography variant="caption" color="textSecondary" sx={{ mt: 0.5, display: 'block' }}>
            {progressPercent.toFixed(1)}% complete
          </Typography>
        </Box>
      )}

      {/* Status Summary */}
      <Box display="flex" gap={1} flexWrap="wrap" mb={showDetails ? 2 : 0}>
        <Chip
          size="small"
          label={getStatusText()}
          color={
            status === 'in_sync' ? 'success' :
            status === 'sync_error' ? 'error' :
            status === 'syncing' ? 'primary' : 'default'
          }
        />
        <Chip size="small" label={`${total_files} files`} variant="outlined" />
        <Chip size="small" label={`${chunk_count} chunks`} variant="outlined" />
        {sync_health_score !== undefined && (
          <Chip
            size="small"
            label={`Health: ${Math.round(sync_health_score * 100)}%`}
            color={sync_health_score > 0.8 ? 'success' : 'warning'}
            variant="outlined"
          />
        )}
        {last_sync_duration && (
          <Chip
            size="small"
            label={`${formatDuration(last_sync_duration)}`}
            variant="outlined"
          />
        )}
      </Box>

      {/* Detailed Information */}
      <Collapse in={showDetails}>
        <Box>
          {/* Sync Result Information */}
          {syncResult && (
            <Box mb={2}>
              <Typography variant="subtitle2" gutterBottom>
                Last Sync Result
              </Typography>
              <Box display="flex" gap={1} flexWrap="wrap">
                {syncResult.files_processed > 0 && (
                  <Chip size="small" label={`${syncResult.files_processed} files processed`} />
                )}
                {syncResult.chunks_created > 0 && (
                  <Chip size="small" label={`${syncResult.chunks_created} chunks created`} color="success" />
                )}
                {syncResult.chunks_updated > 0 && (
                  <Chip size="small" label={`${syncResult.chunks_updated} chunks updated`} color="info" />
                )}
                {syncResult.chunks_deleted > 0 && (
                  <Chip size="small" label={`${syncResult.chunks_deleted} chunks deleted`} color="warning" />
                )}
              </Box>
            </Box>
          )}

          {/* Errors */}
          {hasErrors && (
            <Box mb={2}>
              <Alert severity="error" sx={{ mb: 1 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Sync Errors ({errors.length})
                </Typography>
              </Alert>
              <List dense>
                {errors.map((error, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <ErrorIcon color="error" fontSize="small" />
                    </ListItemIcon>
                    <ListItemText 
                      primary={error}
                      primaryTypographyProps={{ variant: 'body2' }}
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}

          {/* Warnings */}
          {hasWarnings && (
            <Box mb={2}>
              <Alert severity="warning" sx={{ mb: 1 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Sync Warnings ({warnings.length})
                </Typography>
              </Alert>
              <List dense>
                {warnings.map((warning, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <WarningIcon color="warning" fontSize="small" />
                    </ListItemIcon>
                    <ListItemText 
                      primary={warning}
                      primaryTypographyProps={{ variant: 'body2' }}
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}

          {/* Additional Metadata */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Sync Statistics
            </Typography>
            <List dense>
              <ListItem>
                <ListItemIcon>
                  <FileIcon fontSize="small" />
                </ListItemIcon>
                <ListItemText 
                  primary={
                    changed_files_count > 0 
                      ? `${total_files} total files, ${changed_files_count} changed`
                      : `${total_files} total files${total_files > 0 ? ', some changed' : ''}`
                  }
                  primaryTypographyProps={{ variant: 'body2' }}
                />
              </ListItem>
              {syncStatus.last_sync && (
                <ListItem>
                  <ListItemIcon>
                    <ScheduleIcon fontSize="small" />
                  </ListItemIcon>
                  <ListItemText 
                    primary={`Last synced: ${new Date(syncStatus.last_sync).toLocaleString()}`}
                    primaryTypographyProps={{ variant: 'body2' }}
                  />
                </ListItem>
              )}
            </List>
          </Box>
        </Box>
      </Collapse>
    </Paper>
  );

  return compact ? renderCompactView() : renderFullView();
};

export default SyncProgressIndicator;