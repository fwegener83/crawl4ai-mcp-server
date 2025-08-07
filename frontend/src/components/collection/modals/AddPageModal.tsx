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
  Typography,
  Alert,
  CircularProgress
} from '../../ui';
import { LoadingButton } from '../../ui/LoadingButton';
import WebIcon from '@mui/icons-material/Web';
import RefreshIcon from '@mui/icons-material/Refresh';

export function AddPageModal() {
  const { state, addPageToCollection, closeModal } = useCollectionOperations();
  const [url, setUrl] = useState('');
  const [folder, setFolder] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!state.ui.modals.addPage) {
    return null;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim() || !state.selectedCollection) return;

    setIsSubmitting(true);
    try {
      await addPageToCollection(
        state.selectedCollection,
        url.trim(),
        folder.trim() || undefined
      );
      setUrl('');
      setFolder('');
    } catch (error) {
      // Error is handled in the hook
      console.error('Failed to add page:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      closeModal('addPage');
      setUrl('');
      setFolder('');
    }
  };

  const isValidUrl = (urlString: string) => {
    try {
      new URL(urlString);
      return true;
    } catch {
      return false;
    }
  };

  const isFormValid = url.trim() && isValidUrl(url.trim());

  return (
    <Dialog
      open={state.ui.modals.addPage}
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
    >
      <form onSubmit={handleSubmit}>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <WebIcon color="success" fontSize="large" />
          Add Page from URL
        </DialogTitle>
        
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, pt: 1 }}>
            <TextField
              label={
                <span>
                  URL <Typography component="span" color="error">*</Typography>
                </span>
              }
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/article"
              required
              disabled={isSubmitting}
              autoFocus
              fullWidth
              error={url.trim() !== '' && !isValidUrl(url.trim())}
              helperText={url.trim() && !isValidUrl(url.trim()) ? 'Please enter a valid URL' : ''}
              inputProps={{ 'data-testid': 'add-page-url-input' }}
            />
            
            <TextField
              label="Folder (optional)"
              value={folder}
              onChange={(e) => setFolder(e.target.value)}
              placeholder="e.g., articles/tech"
              disabled={isSubmitting}
              fullWidth
              helperText="Leave empty to save in root directory. Use / to separate nested folders."
            />

            {state.ui.loading.crawling && (
              <Alert 
                severity="info" 
                icon={<CircularProgress size={20} />}
              >
                Crawling page content...
              </Alert>
            )}
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
            data-testid="add-page-submit"
            type="submit"
            loading={isSubmitting}
            disabled={!isFormValid}
            variant="contained"
            color="success"
            startIcon={isSubmitting ? <RefreshIcon /> : undefined}
          >
            {isSubmitting ? 'Crawling...' : 'Add Page'}
          </LoadingButton>
        </DialogActions>
      </form>
    </Dialog>
  );
}

export default AddPageModal;