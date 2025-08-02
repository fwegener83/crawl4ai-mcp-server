import React, { createContext, useContext, useState, useCallback } from 'react';
import { Snackbar, Alert } from '@mui/material';
import type { AlertColor } from '@mui/material';

export interface NotificationOptions {
  message: string;
  severity?: AlertColor;
  duration?: number;
  action?: React.ReactNode;
}

interface NotificationContextType {
  showNotification: (options: NotificationOptions) => void;
  showSuccess: (message: string, duration?: number) => void;
  showError: (message: string, duration?: number) => void;
  showWarning: (message: string, duration?: number) => void;
  showInfo: (message: string, duration?: number) => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const useNotification = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotification must be used within a NotificationProvider');
  }
  return context;
};

interface NotificationState {
  open: boolean;
  message: string;
  severity: AlertColor;
  duration: number;
  action?: React.ReactNode;
}

export interface NotificationProviderProps {
  children: React.ReactNode;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children }) => {
  const [notification, setNotification] = useState<NotificationState>({
    open: false,
    message: '',
    severity: 'info',
    duration: 6000,
  });

  const showNotification = useCallback((options: NotificationOptions) => {
    setNotification({
      open: true,
      message: options.message,
      severity: options.severity || 'info',
      duration: options.duration || 6000,
      action: options.action,
    });
  }, []);

  const showSuccess = useCallback((message: string, duration = 4000) => {
    showNotification({ message, severity: 'success', duration });
  }, [showNotification]);

  const showError = useCallback((message: string, duration = 6000) => {
    showNotification({ message, severity: 'error', duration });
  }, [showNotification]);

  const showWarning = useCallback((message: string, duration = 6000) => {
    showNotification({ message, severity: 'warning', duration });
  }, [showNotification]);

  const showInfo = useCallback((message: string, duration = 4000) => {
    showNotification({ message, severity: 'info', duration });
  }, [showNotification]);

  const handleClose = (_event?: React.SyntheticEvent | Event, reason?: string) => {
    if (reason === 'clickaway') {
      return;
    }
    setNotification(prev => ({ ...prev, open: false }));
  };

  const contextValue: NotificationContextType = {
    showNotification,
    showSuccess,
    showError,
    showWarning,
    showInfo,
  };

  return (
    <NotificationContext.Provider value={contextValue}>
      {children}
      <Snackbar
        open={notification.open}
        autoHideDuration={notification.duration}
        onClose={handleClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={handleClose}
          severity={notification.severity}
          variant="filled"
          action={notification.action}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </NotificationContext.Provider>
  );
};

export default NotificationProvider;