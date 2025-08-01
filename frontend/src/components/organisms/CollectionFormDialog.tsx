import React from 'react';
import { useForm, FormProvider } from 'react-hook-form';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  Box
} from '../ui';
import {
  TextFieldElement,
  SubmitButton,
  ActionButton
} from '../forms';
import { useNotification } from '../ui/NotificationProvider';
import StorageIcon from '@mui/icons-material/Storage';

export interface CollectionFormData {
  name: string;
  description?: string;
}

export interface CollectionFormDialogProps {
  open: boolean;
  title: string;
  initialData?: Partial<CollectionFormData>;
  submitText?: string;
  loading?: boolean;
  onSubmit: (data: CollectionFormData) => void | Promise<void>;
  onCancel: () => void;
}

export const CollectionFormDialog: React.FC<CollectionFormDialogProps> = ({
  open,
  title,
  initialData,
  submitText = 'Create Collection',
  loading = false,
  onSubmit,
  onCancel,
}) => {
  const { showError } = useNotification();
  
  const form = useForm<CollectionFormData>({
    defaultValues: {
      name: initialData?.name || '',
      description: initialData?.description || '',
    },
  });

  const handleSubmit = async (data: CollectionFormData) => {
    try {
      // Validate collection name
      if (!data.name.trim()) {
        showError('Collection name is required');
        return;
      }

      // Basic name validation
      const validNamePattern = /^[a-zA-Z0-9_-]+$/;
      if (!validNamePattern.test(data.name.trim())) {
        showError('Collection name can only contain letters, numbers, hyphens, and underscores');
        return;
      }

      await onSubmit({
        name: data.name.trim(),
        description: data.description?.trim() || undefined,
      });
    } catch (error) {
      console.error('Form submission error:', error);
      showError('Failed to process collection form');
    }
  };

  const handleClose = () => {
    form.reset();
    onCancel();
  };

  // Reset form when dialog opens with new data
  React.useEffect(() => {
    if (open && initialData) {
      form.reset({
        name: initialData.name || '',
        description: initialData.description || '',
      });
    }
  }, [open, initialData, form]);

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      aria-labelledby="collection-form-dialog-title"
    >
      <DialogTitle id="collection-form-dialog-title">
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <StorageIcon color="primary" />
          <Typography variant="h6" component="span">
            {title}
          </Typography>
        </Box>
      </DialogTitle>
      
      <FormProvider {...form}>
        <form onSubmit={form.handleSubmit(handleSubmit)}>
          <DialogContent sx={{ pt: 2 }}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              <TextFieldElement
                name="name"
                label="Collection Name"
                helperText="A unique name for your collection (letters, numbers, hyphens, and underscores only)"
                fullWidth
                required
                rules={{
                  required: 'Collection name is required',
                  pattern: {
                    value: /^[a-zA-Z0-9_-]+$/,
                    message: 'Only letters, numbers, hyphens, and underscores are allowed'
                  },
                  minLength: {
                    value: 1,
                    message: 'Collection name must not be empty'
                  },
                  maxLength: {
                    value: 50,
                    message: 'Collection name must be 50 characters or less'
                  }
                }}
                autoFocus
              />
              
              <TextFieldElement
                name="description"
                label="Description"
                helperText="Optional description of what this collection contains"
                fullWidth
                multiline
                rows={3}
                rules={{
                  maxLength: {
                    value: 500,
                    message: 'Description must be 500 characters or less'
                  }
                }}
              />
            </Box>
          </DialogContent>
          
          <DialogActions sx={{ p: 3, gap: 1 }}>
            <ActionButton
              variant="outlined"
              onClick={handleClose}
              disabled={loading}
              type="button"
            >
              Cancel
            </ActionButton>
            <SubmitButton
              loading={loading}
            >
              {loading ? 'Processing...' : submitText}
            </SubmitButton>
          </DialogActions>
        </form>
      </FormProvider>
    </Dialog>
  );
};

export default CollectionFormDialog;