import { useState, useEffect } from 'react';
import { Alert, IconButton, Box } from './ui';
import { AlertTitle, Slide } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

export interface ToastProps {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
  onClose: (id: string) => void;
}

export function Toast({ 
  id, 
  type, 
  title, 
  message, 
  duration = 5000, 
  onClose 
}: ToastProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [isLeaving, setIsLeaving] = useState(false);

  useEffect(() => {
    // Trigger entrance animation
    const timer = setTimeout(() => setIsVisible(true), 50);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        handleClose();
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [duration]);

  const handleClose = () => {
    setIsLeaving(true);
    setTimeout(() => {
      onClose(id);
    }, 300);
  };

  const getSeverity = () => {
    switch (type) {
      case 'success':
        return 'success' as const;
      case 'error':
        return 'error' as const;
      case 'warning':
        return 'warning' as const;
      case 'info':
        return 'info' as const;
      default:
        return 'info' as const;
    }
  };

  return (
    <Slide 
      direction="left" 
      in={isVisible && !isLeaving} 
      timeout={300}
      unmountOnExit
    >
      <Box sx={{ maxWidth: 400, width: '100%' }}>
        <Alert 
          severity={getSeverity()}
          variant="filled"
          action={
            <IconButton
              aria-label="close"
              color="inherit"
              size="small"
              onClick={handleClose}
            >
              <CloseIcon fontSize="inherit" />
            </IconButton>
          }
          sx={{ 
            boxShadow: 3,
            pointerEvents: 'auto'
          }}
        >
          <AlertTitle>{title}</AlertTitle>
          {message}
        </Alert>
      </Box>
    </Slide>
  );
}

export default Toast;