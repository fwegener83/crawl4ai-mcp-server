import { useState, useEffect } from 'react';
import { useCollections } from '../hooks/useApi';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Alert,
  Box,
  Typography,
  MenuItem,
  FormControl,
  InputLabel,
  Select
} from './ui';
import { LoadingButton } from './ui/LoadingButton';

interface SaveToCollectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  content: string;
  onSaveComplete?: (collectionName: string) => void;
}

export function SaveToCollectionModal({ 
  isOpen, 
  onClose, 
  content, 
  onSaveComplete 
}: SaveToCollectionModalProps) {
  const [collectionName, setCollectionName] = useState('default');
  const [isNewCollection, setIsNewCollection] = useState(false);
  const [newCollectionName, setNewCollectionName] = useState('');
  
  const {
    collections,
    refreshCollections,
    storeContent,
    storeLoading,
    storeError,
  } = useCollections();

  useEffect(() => {
    if (isOpen) {
      refreshCollections();
    }
  }, [isOpen]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleSave = async () => {
    if (!content.trim()) return;

    const targetCollection = isNewCollection ? newCollectionName.trim() : collectionName;
    
    if (!targetCollection) {
      return;
    }

    try {
      await storeContent(content, targetCollection);
      
      if (onSaveComplete) {
        onSaveComplete(targetCollection);
      }
      
      // Reset form
      setNewCollectionName('');
      setIsNewCollection(false);
      setCollectionName('default');
      
      onClose();
    } catch (error) {
      console.error('Failed to save to collection:', error);
    }
  };

  const handleCollectionChange = (value: string) => {
    if (value === '__new__') {
      setIsNewCollection(true);
      setCollectionName('');
    } else {
      setIsNewCollection(false);
      setCollectionName(value);
    }
  };

  return (
    <Dialog open={isOpen} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Save to Collection</DialogTitle>
      
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, pt: 1 }}>
          {/* Collection Selection */}
          <Box>
            {!isNewCollection ? (
              <FormControl fullWidth>
                <InputLabel>Select Collection</InputLabel>
                <Select
                  value={collectionName}
                  onChange={(e) => handleCollectionChange(e.target.value as string)}
                  label="Select Collection"
                  data-testid="collection-select"
                >
                  <MenuItem value="default">Default Collection</MenuItem>
                  {collections.map((collection) => (
                    <MenuItem key={collection.name} value={collection.name}>
                      {collection.name} ({collection.count} items)
                    </MenuItem>
                  ))}
                  <MenuItem value="__new__">+ Create New Collection</MenuItem>
                </Select>
              </FormControl>
            ) : (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <TextField
                  fullWidth
                  value={newCollectionName}
                  onChange={(e) => setNewCollectionName(e.target.value)}
                  label="Collection Name"
                  placeholder="Enter collection name"
                  data-testid="collection-name"
                  autoFocus
                />
                <Button
                  variant="text"
                  size="small"
                  onClick={() => setIsNewCollection(false)}
                  sx={{ alignSelf: 'flex-start' }}
                >
                  ← Back to existing collections
                </Button>
              </Box>
            )}
          </Box>

          {/* Content Preview */}
          <Box>
            <Typography variant="body2" fontWeight="medium" gutterBottom>
              Content to Save
            </Typography>
            <Box 
              sx={{ 
                bgcolor: 'action.selected', 
                border: 1, 
                borderColor: 'divider',
                borderRadius: 1, 
                p: 2, 
                maxHeight: 128, 
                overflow: 'auto' 
              }}
            >
              <Typography variant="body2" color="text.secondary">
                {content.length > 200 ? `${content.substring(0, 200)}...` : content}
              </Typography>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                {content.length} characters
              </Typography>
            </Box>
          </Box>

          {/* Error Display */}
          {storeError && (
            <Alert severity="error">
              {storeError}
            </Alert>
          )}
        </Box>
      </DialogContent>

      <DialogActions>
        <Button
          onClick={onClose}
          disabled={storeLoading}
        >
          Cancel
        </Button>
        <LoadingButton
          onClick={handleSave}
          disabled={
            !content.trim() ||
            (isNewCollection && !newCollectionName.trim()) ||
            (!isNewCollection && !collectionName)
          }
          loading={storeLoading}
          variant="contained"
          data-testid="save-confirm"
        >
          Save to Collection
        </LoadingButton>
      </DialogActions>
    </Dialog>
  );
}

export default SaveToCollectionModal;