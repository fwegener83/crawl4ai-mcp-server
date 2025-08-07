import React, { useState } from 'react';
import {
  Button,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Box,
  Typography,
  LinearProgress,
  Chip,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  FormControlLabel,
  Checkbox,
  Alert
} from '@mui/material';
import {
  Sync as SyncIcon,
  Settings as SettingsIcon,
  Refresh as RefreshIcon,
  DeleteSweep as DeleteSweepIcon,
  ExpandMore as ExpandMoreIcon,
  Close as CloseIcon
} from '@mui/icons-material';
import type { VectorSyncStatus, SyncCollectionRequest } from '../../types/api';

interface CollectionSyncButtonProps {
  collectionName: string;
  syncStatus?: VectorSyncStatus;
  onSync: (request: SyncCollectionRequest) => Promise<void>;
  onDeleteVectors?: () => Promise<void>;
  disabled?: boolean;
  size?: 'small' | 'medium' | 'large';
  'data-testid'?: string;
}

export const CollectionSyncButton: React.FC<CollectionSyncButtonProps> = ({
  collectionName,
  syncStatus,
  onSync,
  onDeleteVectors,
  disabled = false,
  size = 'medium',
  'data-testid': dataTestId
}) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [configOpen, setConfigOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [syncConfig, setSyncConfig] = useState<SyncCollectionRequest>({
    force_reprocess: false,
    chunking_strategy: 'auto'
  });

  const isMenuOpen = Boolean(anchorEl);
  const isSyncing = syncStatus?.status === 'syncing';
  const hasChanges = syncStatus?.status === 'out_of_sync' && (syncStatus?.changed_files_count || 0) > 0;
  const canSync = !isSyncing && !disabled;

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleQuickSync = async () => {
    handleMenuClose();
    await onSync({ chunking_strategy: 'auto' });
  };

  const handleConfiguredSync = async () => {
    setConfigOpen(false);
    await onSync(syncConfig);
  };

  const handleDeleteVectors = async () => {
    setDeleteDialogOpen(false);
    if (onDeleteVectors) {
      await onDeleteVectors();
    }
  };

  const getSyncButtonText = () => {
    if (isSyncing) {
      const progress = syncStatus?.sync_progress ? Math.round(syncStatus.sync_progress * 100) : 0;
      return `Syncing... ${progress}%`;
    }
    
    if (hasChanges) {
      return `Sync (${syncStatus?.changed_files_count} changed)`;
    }
    
    if (syncStatus?.status === 'never_synced') {
      return 'Initial Sync';
    }
    
    return 'Sync Collection';
  };

  const getSyncButtonColor = () => {
    if (hasChanges) return 'warning';
    if (syncStatus?.status === 'never_synced') return 'primary';
    return 'inherit';
  };

  const renderProgressInfo = () => {
    if (!isSyncing || !syncStatus) return null;

    const { sync_progress, changed_files_count, total_files } = syncStatus;
    const progressPercent = sync_progress ? sync_progress * 100 : 0;
    const filesProcessed = sync_progress ? Math.floor(sync_progress * (changed_files_count || total_files)) : 0;
    const totalToProcess = changed_files_count || total_files;

    return (
      <Box sx={{ mt: 1, minWidth: 200 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
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
          sx={{ mt: 0.5, height: 6, borderRadius: 3 }}
        />
        <Typography variant="caption" color="textSecondary" sx={{ mt: 0.5, display: 'block' }}>
          {progressPercent.toFixed(1)}% complete
        </Typography>
      </Box>
    );
  };

  return (
    <>
      {/* Main Sync Button */}
      <Box display="flex" alignItems="center">
        <Button
          data-testid={dataTestId}
          variant={hasChanges ? "contained" : "outlined"}
          color={getSyncButtonColor() as 'inherit' | 'primary' | 'secondary' | 'success' | 'error' | 'info' | 'warning'}
          size={size}
          disabled={!canSync}
          onClick={canSync ? handleQuickSync : undefined}
          startIcon={<SyncIcon className={isSyncing ? "animate-spin" : ""} />}
          sx={{ minWidth: 140 }}
        >
          {getSyncButtonText()}
        </Button>
        
        <Button
          size={size}
          disabled={disabled}
          onClick={handleMenuOpen}
          sx={{ minWidth: 'auto', px: 1, ml: 0.5 }}
        >
          <ExpandMoreIcon />
        </Button>
      </Box>

      {/* Progress Display */}
      {isSyncing && renderProgressInfo()}

      {/* Sync Options Menu */}
      <Menu
        anchorEl={anchorEl}
        open={isMenuOpen}
        onClose={handleMenuClose}
        transformOrigin={{ horizontal: 'left', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'left', vertical: 'bottom' }}
      >
        <MenuItem onClick={handleQuickSync} disabled={!canSync}>
          <ListItemIcon>
            <SyncIcon />
          </ListItemIcon>
          <ListItemText 
            primary="Quick Sync" 
            secondary={hasChanges ? `${syncStatus?.changed_files_count} files` : "Auto strategy"}
          />
        </MenuItem>
        
        <MenuItem onClick={() => { handleMenuClose(); setConfigOpen(true); }} disabled={!canSync}>
          <ListItemIcon>
            <SettingsIcon />
          </ListItemIcon>
          <ListItemText 
            primary="Configure Sync" 
            secondary="Choose strategy & options"
          />
        </MenuItem>
        
        <MenuItem 
          onClick={async () => { 
            handleMenuClose(); 
            await onSync({ ...syncConfig, force_reprocess: true }); 
          }} 
          disabled={!canSync}
        >
          <ListItemIcon>
            <RefreshIcon />
          </ListItemIcon>
          <ListItemText 
            primary="Force Reprocess" 
            secondary="Reprocess all files"
          />
        </MenuItem>
        
        {onDeleteVectors && (
          <>
            <Divider />
            <MenuItem 
              onClick={() => { handleMenuClose(); setDeleteDialogOpen(true); }}
              sx={{ color: 'error.main' }}
            >
              <ListItemIcon>
                <DeleteSweepIcon color="error" />
              </ListItemIcon>
              <ListItemText 
                primary="Delete Vectors" 
                secondary="Remove from vector store"
              />
            </MenuItem>
          </>
        )}
      </Menu>

      {/* Sync Configuration Dialog */}
      <Dialog open={configOpen} onClose={() => setConfigOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            Vector Sync Configuration
            <Button onClick={() => setConfigOpen(false)} size="small">
              <CloseIcon />
            </Button>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <FormControl fullWidth margin="normal">
              <InputLabel>Chunking Strategy</InputLabel>
              <Select
                value={syncConfig.chunking_strategy || 'auto'}
                label="Chunking Strategy"
                onChange={(e) => setSyncConfig({
                  ...syncConfig,
                  chunking_strategy: e.target.value as 'baseline' | 'markdown_intelligent' | 'auto'
                })}
              >
                <MenuItem value="auto">
                  <Box>
                    <Typography variant="body2">Auto</Typography>
                    <Typography variant="caption" color="textSecondary">
                      Intelligent strategy selection based on content
                    </Typography>
                  </Box>
                </MenuItem>
                <MenuItem value="markdown_intelligent">
                  <Box>
                    <Typography variant="body2">Markdown Intelligent</Typography>
                    <Typography variant="caption" color="textSecondary">
                      Header-aware chunking with code preservation
                    </Typography>
                  </Box>
                </MenuItem>
                <MenuItem value="baseline">
                  <Box>
                    <Typography variant="body2">Baseline</Typography>
                    <Typography variant="caption" color="textSecondary">
                      Simple recursive text splitting
                    </Typography>
                  </Box>
                </MenuItem>
              </Select>
            </FormControl>

            <FormControlLabel
              control={
                <Checkbox
                  checked={syncConfig.force_reprocess || false}
                  onChange={(e) => setSyncConfig({
                    ...syncConfig,
                    force_reprocess: e.target.checked
                  })}
                />
              }
              label={
                <Box>
                  <Typography variant="body2">Force Reprocess</Typography>
                  <Typography variant="caption" color="textSecondary">
                    Reprocess all files regardless of changes
                  </Typography>
                </Box>
              }
              sx={{ mt: 2, alignItems: 'flex-start' }}
            />

            {syncStatus && (
              <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Collection Status
                </Typography>
                <Box display="flex" gap={1} flexWrap="wrap">
                  <Chip size="small" label={`${syncStatus.total_files} files`} />
                  <Chip size="small" label={`${syncStatus.chunk_count} chunks`} />
                  {syncStatus.changed_files_count > 0 && (
                    <Chip 
                      size="small" 
                      label={`${syncStatus.changed_files_count} changed`} 
                      color="warning"
                    />
                  )}
                  <Chip 
                    size="small" 
                    label={`Health: ${Math.round(syncStatus.sync_health_score * 100)}%`}
                    color={syncStatus.sync_health_score > 0.8 ? 'success' : 'warning'}
                  />
                </Box>
              </Box>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfigOpen(false)}>Cancel</Button>
          <Button onClick={handleConfiguredSync} variant="contained" disabled={!canSync}>
            Start Sync
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Vector Data</DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            This will permanently delete all vector embeddings for collection "{collectionName}".
          </Alert>
          <Typography>
            Are you sure you want to delete all vector data for this collection? 
            This action cannot be undone.
          </Typography>
          {syncStatus && syncStatus.chunk_count > 0 && (
            <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
              This will delete {syncStatus.chunk_count} chunks from the vector store.
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleDeleteVectors} color="error" variant="contained">
            Delete Vectors
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default CollectionSyncButton;