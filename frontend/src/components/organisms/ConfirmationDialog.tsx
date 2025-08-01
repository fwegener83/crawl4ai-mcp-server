import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  Box
} from '../ui';
import { ActionButton } from '../forms';
import WarningIcon from '@mui/icons-material/Warning';
import ErrorIcon from '@mui/icons-material/Error';
import InfoIcon from '@mui/icons-material/Info';

export type ConfirmationDialogVariant = 'warning' | 'error' | 'info';

export interface ConfirmationDialogProps {
  open: boolean;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  variant?: ConfirmationDialogVariant;
  loading?: boolean;
  onConfirm: () => void | Promise<void>;
  onCancel: () => void;
}

export const ConfirmationDialog: React.FC<ConfirmationDialogProps> = ({
  open,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  variant = 'warning',
  loading = false,
  onConfirm,
  onCancel,
}) => {
  const getVariantConfig = () => {
    const configs = {
      warning: {
        icon: <WarningIcon sx={{ fontSize: 48, color: 'warning.main' }} />,
        confirmColor: 'warning' as const,
      },
      error: {
        icon: <ErrorIcon sx={{ fontSize: 48, color: 'error.main' }} />,
        confirmColor: 'error' as const,
      },
      info: {
        icon: <InfoIcon sx={{ fontSize: 48, color: 'info.main' }} />,
        confirmColor: 'primary' as const,
      },
    };
    return configs[variant];
  };

  const config = getVariantConfig();

  const handleConfirm = async () => {
    try {
      await onConfirm();
    } catch (error) {
      console.error('Confirmation action failed:', error);
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onCancel}
      maxWidth="sm"
      fullWidth
      aria-labelledby="confirmation-dialog-title"
      aria-describedby="confirmation-dialog-description"
    >
      <DialogTitle id="confirmation-dialog-title">
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {config.icon}
          <Typography variant="h6" component="span">
            {title}
          </Typography>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Typography
          id="confirmation-dialog-description"
          variant="body1"
          color="text.secondary"
          sx={{ mt: 1 }}
        >
          {message}
        </Typography>
      </DialogContent>
      
      <DialogActions sx={{ p: 3, gap: 1 }}>
        <ActionButton
          variant="outlined"
          onClick={onCancel}
          disabled={loading}
        >
          {cancelText}
        </ActionButton>
        <ActionButton
          variant="contained"
          color={config.confirmColor}
          onClick={handleConfirm}
          loading={loading}
        >
          {loading ? 'Processing...' : confirmText}
        </ActionButton>
      </DialogActions>
    </Dialog>
  );
};

export default ConfirmationDialog;