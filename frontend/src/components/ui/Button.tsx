import React from 'react';
import { Button as MuiButton } from '@mui/material';
import type { ButtonProps as MuiButtonProps } from '@mui/material';

export interface ButtonProps extends MuiButtonProps {
  loading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({ 
  loading = false, 
  disabled,
  children,
  ...props 
}) => {
  return (
    <MuiButton 
      disabled={disabled || loading}
      {...props}
    >
      {children}
    </MuiButton>
  );
};

export default Button;