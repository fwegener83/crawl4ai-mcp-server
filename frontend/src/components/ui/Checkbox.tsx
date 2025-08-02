import React from 'react';
import { Checkbox as MuiCheckbox } from '@mui/material';
import type { CheckboxProps as MuiCheckboxProps } from '@mui/material';

export interface CheckboxProps extends MuiCheckboxProps {
  // Additional custom props can be added here
}

export const Checkbox: React.FC<CheckboxProps> = (props) => {
  return <MuiCheckbox {...props} />;
};

export default Checkbox;