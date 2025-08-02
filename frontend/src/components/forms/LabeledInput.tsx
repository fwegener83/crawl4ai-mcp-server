import React from 'react';
import { Box, TextField, Typography } from '../ui';
import { TextField as MuiTextField } from '@mui/material';

export interface LabeledInputProps extends Omit<React.ComponentProps<typeof MuiTextField>, 'label'> {
  label: string;
  required?: boolean;
  description?: string;
}

export const LabeledInput: React.FC<LabeledInputProps> = ({
  label,
  required = false,
  description,
  error,
  helperText,
  ...textFieldProps
}) => {
  return (
    <Box sx={{ mb: 2 }}>
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
      {description && (
        <Typography 
          variant="body2" 
          color="text.secondary" 
          sx={{ mb: 1 }}
        >
          {description}
        </Typography>
      )}
      <TextField
        error={error}
        helperText={helperText}
        required={required}
        {...textFieldProps}
      />
    </Box>
  );
};

export default LabeledInput;