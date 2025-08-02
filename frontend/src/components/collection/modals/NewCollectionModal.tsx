import { useState } from 'react';
import type React from 'react';
import { useCollectionOperations } from '../../../hooks/useCollectionOperations';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
  Typography
} from '../../ui';
import { LoadingButton } from '../../ui/LoadingButton';

export function NewCollectionModal() {
  const { state, createCollection, closeModal } = useCollectionOperations();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!state.ui.modals.newCollection) {
    return null;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setIsSubmitting(true);
    try {
      await createCollection({ name: name.trim(), description: description.trim() });
      setName('');
      setDescription('');
    } catch (error) {
      // Error is handled in the hook
      console.error('Failed to create collection:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      closeModal('newCollection');
      setName('');
      setDescription('');
    }
  };

  return (
    <Dialog
      open={state.ui.modals.newCollection}
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
    >
      <form onSubmit={handleSubmit}>
        <DialogTitle>
          Create New Collection
        </DialogTitle>
        
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, pt: 1 }}>
            <TextField
              label={
                <span>
                  Name <Typography component="span" color="error">*</Typography>
                </span>
              }
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter collection name"
              required
              disabled={isSubmitting}
              autoFocus
              fullWidth
            />
            
            <TextField
              label="Description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Optional description"
              multiline
              rows={3}
              disabled={isSubmitting}
              fullWidth
            />
          </Box>
        </DialogContent>
        
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button
            onClick={handleClose}
            disabled={isSubmitting}
            variant="outlined"
          >
            Cancel
          </Button>
          <LoadingButton
            type="submit"
            loading={isSubmitting}
            disabled={!name.trim()}
            variant="contained"
          >
            Create Collection
          </LoadingButton>
        </DialogActions>
      </form>
    </Dialog>
  );
}

export default NewCollectionModal;