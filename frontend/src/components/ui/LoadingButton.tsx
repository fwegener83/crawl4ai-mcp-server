import React from 'react';
import { Button as MuiButton, CircularProgress } from '@mui/material';
import type { ButtonProps as MuiButtonProps } from '@mui/material';

export interface LoadingButtonProps extends MuiButtonProps {
  loading?: boolean;
  loadingIndicator?: React.ReactNode;
}

export const LoadingButton: React.FC<LoadingButtonProps> = ({ 
  loading = false, 
  loadingIndicator,
  disabled,
  children,
  startIcon,
  ...props 
}) => {
  const indicator = loadingIndicator ?? <CircularProgress size={16} />;

  return (
    <MuiButton 
      disabled={disabled || loading}
      startIcon={loading ? indicator : startIcon}
      {...props}
    >
      {children}
    </MuiButton>
  );
};

export default LoadingButton;