import React from 'react';
import { TextField as MuiTextField } from '@mui/material';
import type { TextFieldProps as MuiTextFieldProps } from '@mui/material';

export type TextFieldProps = MuiTextFieldProps;

export const TextField: React.FC<TextFieldProps> = (props) => {
  return (
    <MuiTextField
      variant="outlined"
      fullWidth
      {...props}
    />
  );
};

export default TextField;