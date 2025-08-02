import { useState } from 'react';
import type { Collection } from '../types/api';
import {
  Paper,
  Box,
  Typography,
  Chip,
  Button,
  IconButton,
  Alert,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  Divider
} from './ui';
import FolderIcon from '@mui/icons-material/Folder';
import StorageIcon from '@mui/icons-material/Storage';
import DeleteIcon from '@mui/icons-material/Delete';

interface CollectionsListProps {
  collections: Collection[];
  selectedCollection?: string;
  onSelectCollection?: (collection: string) => void;
  onDeleteCollection?: (collection: string) => void;
  isDeleting?: boolean;
  deleteError?: string;
}

export function CollectionsList({
  collections,
  selectedCollection,
  onSelectCollection,
  onDeleteCollection,
  isDeleting = false,
  deleteError
}: CollectionsListProps) {
  const [deletingCollection, setDeletingCollection] = useState<string | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<string | null>(null);

  const handleDeleteClick = (collectionName: string) => {
    setShowDeleteConfirm(collectionName);
  };

  const handleDeleteConfirm = async (collectionName: string) => {
    if (onDeleteCollection) {
      setDeletingCollection(collectionName);
      try {
        await onDeleteCollection(collectionName);
        setShowDeleteConfirm(null);
      } catch (error) {
        console.error('Delete failed:', error);
      } finally {
        setDeletingCollection(null);
      }
    }
  };

  const handleDeleteCancel = () => {
    setShowDeleteConfirm(null);
  };

  const getCollectionIcon = (collection: Collection) => {
    if (collection.name === 'default') {
      return <FolderIcon color="primary" />;
    }
    return <StorageIcon color="secondary" />;
  };

  if (collections.length === 0) {
    return (
      <Paper sx={{ p: 4 }}>
        <Box sx={{ textAlign: 'center' }}>
          <StorageIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            No collections found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Start crawling and saving content to create your first collection.
          </Typography>
        </Box>
      </Paper>
    );
  }

  return (
    <Paper>
      {/* Header */}
      <Box sx={{ p: 3, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h6">
          Collections ({collections.length})
        </Typography>
      </Box>

      {/* Error Display */}
      {deleteError && (
        <Alert severity="error" sx={{ m: 2, mb: 0 }}>
          {deleteError}
        </Alert>
      )}

      {/* Collections List */}
      <List disablePadding>
        {collections.map((collection, index) => (
          <Box key={collection.name}>
            <ListItem 
              sx={{ 
                '&:hover': { bgcolor: 'action.hover' }
              }}
            >
              <ListItemButton
                onClick={() => onSelectCollection?.(selectedCollection === collection.name ? '' : collection.name)}
                selected={selectedCollection === collection.name}
                sx={{ 
                  flex: 1,
                  borderRadius: 1,
                  mx: 1
                }}
              >
                <ListItemIcon>
                  {getCollectionIcon(collection)}
                </ListItemIcon>
                <Box sx={{ flex: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                    <Typography 
                      variant="body2" 
                      fontWeight="medium"
                      noWrap
                    >
                      {collection.name}
                    </Typography>
                    {collection.name === 'default' && (
                      <Chip 
                        label="Default" 
                        size="small" 
                        color="primary" 
                      />
                    )}
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      {collection.count} items
                    </Typography>
                    {collection.metadata?.created_at ? (
                      <Typography variant="caption" color="text.secondary">
                        Created: {new Date(String(collection.metadata.created_at)).toLocaleDateString()}
                      </Typography>
                    ) : null}
                  </Box>
                </Box>
              </ListItemButton>

              {/* Actions */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: 1 }}>
                {selectedCollection === collection.name && (
                  <Chip 
                    label="Selected" 
                    size="small" 
                    color="success" 
                  />
                )}
                
                {collection.name !== 'default' && (
                  <Box>
                    {showDeleteConfirm === collection.name ? (
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="caption" color="text.secondary">
                          Delete?
                        </Typography>
                        <Button
                          size="small"
                          color="error"
                          onClick={() => handleDeleteConfirm(collection.name)}
                          disabled={deletingCollection === collection.name}
                        >
                          {deletingCollection === collection.name ? 'Deleting...' : 'Yes'}
                        </Button>
                        <Button
                          size="small"
                          onClick={handleDeleteCancel}
                          disabled={deletingCollection === collection.name}
                        >
                          No
                        </Button>
                      </Box>
                    ) : (
                      <IconButton
                        size="small"
                        onClick={() => handleDeleteClick(collection.name)}
                        disabled={isDeleting || deletingCollection === collection.name}
                        title="Delete collection"
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    )}
                  </Box>
                )}
              </Box>
            </ListItem>
            {index < collections.length - 1 && <Divider />}
          </Box>
        ))}
      </List>

      {/* Summary Footer */}
      <Box sx={{ 
        p: 2, 
        bgcolor: 'action.selected', 
        borderTop: 1, 
        borderColor: 'divider' 
      }}>
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between' 
        }}>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Total Items: {collections.reduce((sum, c) => sum + c.count, 0)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Active: {collections.length}
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">
            Click to select • Delete to remove (except default)
          </Typography>
        </Box>
      </Box>
    </Paper>
  );
}

export default CollectionsList;