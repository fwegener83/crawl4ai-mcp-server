import React from 'react';
import { IconButton as MuiIconButton } from '@mui/material';
import type { IconButtonProps as MuiIconButtonProps } from '@mui/material';

export interface IconButtonProps extends MuiIconButtonProps {
  loading?: boolean;
}

export const IconButton: React.FC<IconButtonProps> = ({ 
  loading = false, 
  disabled,
  children,
  ...props 
}) => {
  return (
    <MuiIconButton 
      disabled={disabled || loading}
      {...props}
    >
      {children}
    </MuiIconButton>
  );
};

export default IconButton;