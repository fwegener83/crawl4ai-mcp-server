import React, { useState } from 'react';
import {
  Box,
  Button,
  ButtonGroup,
  IconButton,
  Menu,
  MenuItem,
  Tooltip,
  Typography,
  Chip,
  Alert,
  Divider,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import {
  Sync as SyncIcon,
  Refresh as RefreshIcon,
  MoreVert as MoreVertIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import type { VectorSyncStatus } from '../../types/api';
import { APIService } from '../../services/api';

interface ModelInfo {
  vector_service_available: boolean;
  model_name?: string;
  device?: string;
  model_dimension?: number;
  model_properties?: {
    max_sequence_length?: number;
  };
  error_message?: string;
}

interface EnhancedSyncControlsProps {
  collectionId: string;
  collectionName: string;
  syncStatus?: VectorSyncStatus;
  onSyncStarted?: () => void;
  onSyncCompleted?: () => void;
  onRefresh?: () => void;
  disabled?: boolean;
  size?: 'small' | 'medium' | 'large';
}

export const EnhancedSyncControls: React.FC<EnhancedSyncControlsProps> = ({
  collectionId,
  collectionName,
  syncStatus,
  onSyncStarted,
  onSyncCompleted,
  onRefresh,
  disabled = false,
  size = 'medium'
}) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [modelInfo, setModelInfo] = useState<ModelInfo | null>(null);
  const [showModelInfo, setShowModelInfo] = useState(false);

  const isSyncing = syncStatus?.status === 'syncing';
  const canSync = !isSyncing && !disabled;

  // Handle regular sync
  const handleRegularSync = async () => {
    if (!canSync) return;
    
    setIsLoading(true);
    onSyncStarted?.();
    
    try {
      await APIService.syncCollection(collectionId);
      onSyncCompleted?.();
    } catch (error) {
      console.error('Regular sync failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle force resync (uses same endpoint with force flags)
  const handleForceResync = async () => {
    if (!canSync) return;
    
    setIsLoading(true);
    onSyncStarted?.();
    setAnchorEl(null);
    
    try {
      await APIService.forceResyncCollection(collectionId);
      onSyncCompleted?.();
    } catch (error) {
      console.error('Force resync failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Load model info from sync status endpoint
  const loadModelInfo = async () => {
    try {
      const response = await APIService.getCollectionSyncStatusWithModel(collectionId);
      setModelInfo(response.modelInfo);
      setShowModelInfo(true);
    } catch (error) {
      console.error('Failed to load model info:', error);
      setModelInfo({
        vector_service_available: false,
        error_message: 'Failed to load model information'
      });
      setShowModelInfo(true);
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  // Manual refresh handler
  const handleRefresh = () => {
    onRefresh?.();
  };

  const getSyncButtonText = () => {
    if (isSyncing || isLoading) {
      return 'Syncing...';
    }
    
    if (syncStatus?.status === 'never_synced') {
      return 'Initial Sync';
    }
    
    return 'Sync';
  };

  const getSyncStatusColor = () => {
    if (!syncStatus) return 'default';
    
    switch (syncStatus.status) {
      case 'in_sync':
        return 'success';
      case 'syncing':
        return 'info';
      case 'sync_error':
        return 'error';
      case 'out_of_sync':
        return 'warning';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      {/* Main Sync Controls */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        {/* Primary Sync Button */}
        <Button
          variant="contained"
          startIcon={<SyncIcon />}
          onClick={handleRegularSync}
          disabled={!canSync}
          size={size}
          sx={{ minWidth: 120 }}
        >
          {getSyncButtonText()}
        </Button>

        {/* Manual Refresh Button */}
        <Tooltip title="Refresh Status">
          <IconButton
            onClick={handleRefresh}
            disabled={disabled}
            size={size}
            color="primary"
          >
            <RefreshIcon />
          </IconButton>
        </Tooltip>

        {/* Enhanced Controls Menu */}
        <Tooltip title="More Options">
          <span>
            <IconButton
              onClick={handleMenuOpen}
              disabled={disabled}
              size={size}
            >
              <MoreVertIcon />
            </IconButton>
          </span>
        </Tooltip>

        {/* Sync Status Indicator */}
        {syncStatus && (
          <Chip
            label={syncStatus.status.replace('_', ' ')}
            color={getSyncStatusColor() as any}
            size="small"
            variant="outlined"
          />
        )}
      </Box>

      {/* Enhanced Options Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <MenuItem onClick={handleForceResync} disabled={!canSync}>
          <ListItemIcon>
            <RefreshIcon />
          </ListItemIcon>
          <ListItemText 
            primary="Force Resync"
            secondary="Delete all vectors and resync"
          />
        </MenuItem>
        
        <Divider />
        
        <MenuItem onClick={loadModelInfo}>
          <ListItemIcon>
            <InfoIcon />
          </ListItemIcon>
          <ListItemText 
            primary="Model Info"
            secondary="View embedding model details"
          />
        </MenuItem>
      </Menu>

      {/* Model Info Display */}
      {showModelInfo && modelInfo && (
        <Alert 
          severity={modelInfo.vector_service_available ? "info" : "warning"}
          onClose={() => setShowModelInfo(false)}
          sx={{ mt: 2 }}
        >
          <Typography variant="subtitle2" gutterBottom>
            Vector Model Information
          </Typography>
          
          {modelInfo.vector_service_available ? (
            <Box>
              <Typography variant="body2">
                <strong>Model:</strong> {modelInfo.model_name}
              </Typography>
              <Typography variant="body2">
                <strong>Device:</strong> {modelInfo.device}
              </Typography>
              <Typography variant="body2">
                <strong>Dimension:</strong> {modelInfo.model_dimension}
              </Typography>
              {modelInfo.model_properties?.max_sequence_length && (
                <Typography variant="body2">
                  <strong>Max Sequence Length:</strong> {modelInfo.model_properties.max_sequence_length}
                </Typography>
              )}
            </Box>
          ) : (
            <Typography variant="body2" color="error">
              {modelInfo.error_message || 'Vector service not available'}
            </Typography>
          )}
        </Alert>
      )}

      {/* Simplified Sync Statistics */}
      {syncStatus && syncStatus.status !== 'never_synced' && (
        <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Chip
            label={`${syncStatus.chunk_count || 0} vectors`}
            size="small"
            variant="outlined"
          />
          <Chip
            label={`${syncStatus.total_files || 0} files`}
            size="small"
            variant="outlined"
          />
          {syncStatus.last_sync && (
            <Chip
              label={`Last: ${new Date(syncStatus.last_sync).toLocaleDateString()}`}
              size="small"
              variant="outlined"
            />
          )}
        </Box>
      )}
    </Box>
  );
};