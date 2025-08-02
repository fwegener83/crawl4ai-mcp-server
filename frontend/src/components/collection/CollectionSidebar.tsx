import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Button,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Alert,
  CircularProgress,
  Chip,
  Tooltip,
  Divider
} from '../ui';
import { useCollectionOperations } from '../../hooks/useCollectionOperations';
import RefreshIcon from '@mui/icons-material/Refresh';
import AddIcon from '@mui/icons-material/Add';
import FolderIcon from '@mui/icons-material/Folder';
import DeleteIcon from '@mui/icons-material/Delete';
import DescriptionIcon from '@mui/icons-material/Description';
import CloseIcon from '@mui/icons-material/Close';
import CreateNewFolderIcon from '@mui/icons-material/CreateNewFolder';
import WebIcon from '@mui/icons-material/Web';

interface CollectionSidebarProps {
  className?: string;
}

export function CollectionSidebar({ className = '' }: CollectionSidebarProps) {
  const {
    state,
    loadCollections,
    selectCollection,
    openModal,
    openDeleteConfirmation,
    clearError,
  } = useCollectionOperations();

  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    loadCollections();
  }, [loadCollections, refreshKey]);

  // Auto-refresh collections every 30 seconds to keep data fresh
  useEffect(() => {
    const interval = setInterval(() => {
      if (!state.ui.loading.collections) {
        loadCollections();
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [loadCollections, state.ui.loading.collections]);

  const handleSelectCollection = (collectionId: string) => {
    if (state.selectedCollection !== collectionId) {
      selectCollection(collectionId);
    }
  };

  const handleDeleteCollection = (collectionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    openDeleteConfirmation('collection', collectionId);
  };

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return 'Unknown';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  if (state.ui.loading.collections) {
    return (
      <Box 
        sx={{ 
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          bgcolor: 'background.paper'
        }} 
        className={className}
      >
        <Box sx={{ p: 3, display: 'flex', alignItems: 'center', justifyContent: 'center', flex: 1 }}>
          <CircularProgress size={20} />
          <Typography variant="body2" color="text.secondary" sx={{ ml: 2 }}>
            Loading collections...
          </Typography>
        </Box>
      </Box>
    );
  }

  return (
    <Box 
      sx={{ 
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'background.paper'
      }} 
      className={className}
    >
      {/* Sidebar Header */}
      <Box sx={{ p: 2.5 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <WebIcon sx={{ color: 'primary.main', mr: 1.5 }} />
          <Typography variant="h6" fontWeight="bold" color="primary.main">
            Collections
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Button
            onClick={() => openModal('newCollection')}
            size="medium"
            variant="contained"
            startIcon={<AddIcon />}
            fullWidth
            sx={{ mr: 1 }}
          >
            New Collection
          </Button>
          <Tooltip title="Refresh collections">
            <IconButton
              onClick={handleRefresh}
              disabled={state.ui.loading.collections}
              size="medium"
              color="primary"
            >
              <RefreshIcon 
                fontSize="medium"
                sx={{
                  animation: state.ui.loading.collections ? 'spin 1s linear infinite' : 'none',
                  '@keyframes spin': {
                    '0%': { transform: 'rotate(0deg)' },
                    '100%': { transform: 'rotate(360deg)' }
                  }
                }}
              />
            </IconButton>
          </Tooltip>
        </Box>
        
        {/* Collection Stats */}
        {state.collections.length > 0 && (
          <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
            <Typography variant="body2" fontWeight="medium" sx={{ mb: 0.5 }}>
              Collection Summary
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
              {state.collections.length} collection{state.collections.length !== 1 ? 's' : ''}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {state.collections.reduce((sum, c) => sum + c.file_count, 0)} total files
            </Typography>
          </Box>
        )}
      </Box>

      <Divider />

      {/* Error Display */}
      {state.ui.error && (
        <Box sx={{ p: 2 }}>
          <Alert 
            severity="error" 
            action={
              <IconButton 
                aria-label="close" 
                color="inherit" 
                size="small" 
                onClick={clearError}
              >
                <CloseIcon fontSize="inherit" />
              </IconButton>
            }
          >
            {state.ui.error}
          </Alert>
        </Box>
      )}

      {/* Collections List */}
      <Box sx={{ flex: 1, overflow: 'auto', px: 1, pb: 1 }}>
        {state.collections.length === 0 ? (
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <CreateNewFolderIcon 
              sx={{ 
                fontSize: 64, 
                color: 'text.secondary',
                mb: 2,
                display: 'block',
                mx: 'auto'
              }} 
            />
            <Typography variant="h6" fontWeight="medium" sx={{ mb: 1 }}>
              No Collections Yet
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Create your first collection to start organizing your web content
            </Typography>
            <Button
              onClick={() => openModal('newCollection')}
              variant="contained"
              startIcon={<AddIcon />}
              size="large"
            >
              Create Collection
            </Button>
          </Box>
        ) : (
          <List sx={{ p: 0 }}>
            {state.collections.map((collection) => (
              <ListItem
                key={collection.name}
                onClick={() => handleSelectCollection(collection.name)}
                sx={{
                  cursor: 'pointer',
                  borderRadius: 2,
                  mb: 1,
                  p: 2,
                  position: 'relative',
                  border: 1,
                  borderColor: 'transparent',
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': {
                    bgcolor: 'action.hover',
                    borderColor: 'primary.200',
                    transform: 'translateX(4px)',
                  },
                  '&:hover .delete-button': {
                    opacity: 1
                  },
                  ...(state.selectedCollection === collection.name && {
                    bgcolor: 'primary.50',
                    borderColor: 'primary.main',
                    '& .MuiListItemIcon-root': {
                      color: 'primary.main'
                    }
                  })
                }}
              >
                <ListItemIcon sx={{ minWidth: 40 }}>
                  <FolderIcon />
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Typography 
                      variant="body1" 
                      fontWeight="semibold"
                      color={state.selectedCollection === collection.name ? 'primary.main' : 'text.primary'}
                      noWrap
                      sx={{ mb: 0.5 }}
                    >
                      {collection.name}
                    </Typography>
                  }
                  secondary={
                    <Box>
                      {collection.description && (
                        <Typography variant="body2" color="text.secondary" noWrap sx={{ mb: 1 }}>
                          {collection.description}
                        </Typography>
                      )}
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <Chip 
                          icon={<DescriptionIcon />} 
                          label={`${collection.file_count} files`}
                          size="small"
                          variant="outlined"
                          color={state.selectedCollection === collection.name ? 'primary' : 'default'}
                        />
                        {collection.folders.length > 0 && (
                          <Chip 
                            icon={<FolderIcon />} 
                            label={`${collection.folders.length} folders`}
                            size="small"
                            variant="outlined"
                            color={state.selectedCollection === collection.name ? 'primary' : 'default'}
                          />
                        )}
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <Typography variant="caption" color="text.disabled">
                          Created {formatDate(collection.created_at)}
                        </Typography>
                        {collection.metadata.total_size > 0 && (
                          <Typography variant="caption" color="text.disabled">
                            {formatFileSize(collection.metadata.total_size)}
                          </Typography>
                        )}
                      </Box>
                    </Box>
                  }
                />
                <Box
                  className="delete-button"
                  sx={{
                    position: 'absolute',
                    right: 12,
                    top: 12,
                    opacity: 0,
                    transition: 'opacity 0.2s ease-in-out',
                  }}
                >
                  <Tooltip title="Delete collection">
                    <IconButton
                      onClick={(e) => handleDeleteCollection(collection.name, e)}
                      size="small"
                      color="error"
                      sx={{
                        bgcolor: 'error.50',
                        '&:hover': {
                          bgcolor: 'error.100'
                        }
                      }}
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
              </ListItem>
            ))}
          </List>
        )}
      </Box>
    </Box>
  );
}

export default CollectionSidebar;