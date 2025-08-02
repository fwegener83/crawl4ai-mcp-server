import React from 'react';
import { Box, Typography } from '../ui';
import { FormControl, FormHelperText } from '@mui/material';

export interface FormFieldProps {
  label?: string;
  required?: boolean;
  error?: boolean;
  helperText?: string;
  description?: string;
  children: React.ReactNode;
  fullWidth?: boolean;
}

export const FormField: React.FC<FormFieldProps> = ({
  label,
  required = false,
  error = false,
  helperText,
  description,
  children,
  fullWidth = true,
}) => {
  return (
    <FormControl fullWidth={fullWidth} error={error} sx={{ mb: 2 }}>
      {label && (
        <Typography 
          component="label" 
          variant="body2" 
          sx={{ 
            fontWeight: 'medium',
            mb: 0.5,
            display: 'block',
            color: error ? 'error.main' : 'text.primary'
          }}
        >
          {label}
          {required && (
            <Typography 
              component="span" 
              color="error.main" 
              sx={{ ml: 0.5 }}
            >
              *
            </Typography>
          )}
        </Typography>
      )}
      {description && (
        <Typography 
          variant="body2" 
          color="text.secondary" 
          sx={{ mb: 1 }}
        >
          {description}
        </Typography>
      )}
      <Box>
        {children}
      </Box>
      {helperText && (
        <FormHelperText>{helperText}</FormHelperText>
      )}
    </FormControl>
  );
};

export default FormField;