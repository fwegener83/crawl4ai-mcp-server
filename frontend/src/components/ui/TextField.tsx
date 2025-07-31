import React from 'react';
import { TextField as MuiTextField, TextFieldProps as MuiTextFieldProps } from '@mui/material';

export interface TextFieldProps extends MuiTextFieldProps {
  // Additional custom props can be added here
}

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