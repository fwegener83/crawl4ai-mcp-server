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
import DescriptionIcon from '@mui/icons-material/Description';
import RefreshIcon from '@mui/icons-material/Refresh';

export function NewFileModal() {
  const { state, createNewFile, closeModal } = useCollectionOperations();
  const [filename, setFilename] = useState('');
  const [folder, setFolder] = useState('');
  const [content, setContent] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!state.ui.modals.newFile) {
    return null;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!filename.trim() || !state.selectedCollection) return;

    setIsSubmitting(true);
    try {
      await createNewFile(
        state.selectedCollection,
        processedFilename,
        content.trim(),
        folder.trim() || undefined
      );
      setFilename('');
      setFolder('');
      setContent('');
    } catch (error) {
      // Error is handled in the hook
      console.error('Failed to create file:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      closeModal('newFile');
      setFilename('');
      setFolder('');
      setContent('');
    }
  };

  const isValidFilename = (name: string) => {
    // Check for valid filename (no invalid characters)
    const invalidChars = /[<>:"/\\|?*]/;
    return name.trim() && !invalidChars.test(name) && name !== '.' && name !== '..';
  };

  const addMarkdownExtension = (name: string) => {
    if (!name.includes('.')) {
      return name + '.md';
    }
    return name;
  };

  const processedFilename = filename.trim() ? addMarkdownExtension(filename.trim()) : '';
  const isFormValid = filename.trim() && isValidFilename(filename.trim());

  return (
    <Dialog
      open={state.ui.modals.newFile}
      onClose={handleClose}
      maxWidth="md"
      fullWidth
    >
      <form onSubmit={handleSubmit}>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <DescriptionIcon color="primary" fontSize="large" />
          Create New File
        </DialogTitle>
        
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, pt: 1 }}>
            <TextField
              label={
                <span>
                  Filename <Typography component="span" color="error">*</Typography>
                </span>
              }
              value={filename}
              onChange={(e) => setFilename(e.target.value)}
              placeholder="my-document"
              required
              disabled={isSubmitting}
              autoFocus
              fullWidth
              error={filename.trim() !== '' && !isValidFilename(filename.trim())}
              helperText={
                filename.trim() ? (
                  !isValidFilename(filename.trim()) ? (
                    'Invalid filename. Avoid special characters: < > : " / \\ | ? *'
                  ) : (
                    <>Will be saved as: <Typography component="span" fontFamily="monospace">{processedFilename}</Typography></>
                  )
                ) : ''
              }
            />
            
            <TextField
              label="Folder (optional)"
              value={folder}
              onChange={(e) => setFolder(e.target.value)}
              placeholder="e.g., drafts/ideas"
              disabled={isSubmitting}
              fullWidth
              helperText="Leave empty to save in root directory. Use / to separate nested folders."
            />

            <TextField
              label="Initial Content (optional)"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder={`# My New Document

Start writing your content here...`}
              multiline
              rows={6}
              disabled={isSubmitting}
              fullWidth
              helperText="Markdown formatting supported"
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
            disabled={!isFormValid}
            variant="contained"
            startIcon={isSubmitting ? <RefreshIcon /> : undefined}
          >
            {isSubmitting ? 'Creating...' : 'Create File'}
          </LoadingButton>
        </DialogActions>
      </form>
    </Dialog>
  );
}

export default NewFileModal;