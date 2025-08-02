import React from 'react';
import { SelectElement as RHFSelectElement } from 'react-hook-form-mui';
import type { SelectElementProps } from 'react-hook-form-mui';

export interface CustomSelectElementProps extends SelectElementProps {
  // Additional custom props can be added here
}

export const SelectElement: React.FC<CustomSelectElementProps> = (props) => {
  return (
    <RHFSelectElement
      variant="outlined"
      fullWidth
      {...props}
    />
  );
};

export default SelectElement;