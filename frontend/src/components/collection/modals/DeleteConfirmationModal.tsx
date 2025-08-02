import { useCollectionOperations } from '../../../hooks/useCollectionOperations';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Alert,
  Typography
} from '../../ui';
import FolderIcon from '@mui/icons-material/Folder';
import DescriptionIcon from '@mui/icons-material/Description';
import WarningIcon from '@mui/icons-material/Warning';

export function DeleteConfirmationModal() {
  const { state, deleteCollection, deleteFile, closeDeleteConfirmation } = useCollectionOperations();

  if (!state.ui.modals.deleteConfirmation.open) {
    return null;
  }

  const { type, target } = state.ui.modals.deleteConfirmation;

  const handleConfirm = async () => {
    if (!target) return;

    try {
      if (type === 'collection') {
        await deleteCollection(target);
      } else if (type === 'file' && state.selectedCollection) {
        // Parse file path to get filename and folder
        const pathParts = target.split('/');
        const filename = pathParts.pop()!;
        const folder = pathParts.length > 0 ? pathParts.join('/') : undefined;
        await deleteFile(state.selectedCollection, filename, folder);
      }
    } catch (error) {
      // Error is handled in the hook
      console.error(`Failed to delete ${type}:`, error);
    }
  };

  const getTitle = () => {
    if (type === 'collection') {
      return 'Delete Collection';
    }
    return 'Delete File';
  };

  const getMessage = () => {
    if (type === 'collection') {
      return `Are you sure you want to delete the collection "${target}"? This will permanently delete all files and folders within this collection. This action cannot be undone.`;
    }
    return `Are you sure you want to delete the file "${target}"? This action cannot be undone.`;
  };

  const getIcon = () => {
    if (type === 'collection') {
      return <FolderIcon color="error" fontSize="large" />;
    }
    return <DescriptionIcon color="error" fontSize="large" />;
  };

  return (
    <Dialog
      open={state.ui.modals.deleteConfirmation.open}
      onClose={closeDeleteConfirmation}
      maxWidth="sm"
      fullWidth
    >
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        {getIcon()}
        {getTitle()}
      </DialogTitle>
      
      <DialogContent>
        <Alert 
          severity="warning" 
          icon={<WarningIcon />}
          sx={{ mb: 2 }}
        >
          <Typography variant="body2">
            {getMessage()}
          </Typography>
        </Alert>
      </DialogContent>
      
      <DialogActions sx={{ px: 3, pb: 3 }}>
        <Button
          onClick={closeDeleteConfirmation}
          variant="outlined"
        >
          Cancel
        </Button>
        <Button
          onClick={handleConfirm}
          variant="contained"
          color="error"
        >
          Delete {type === 'collection' ? 'Collection' : 'File'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default DeleteConfirmationModal;