import React from 'react';
import { TextFieldElement as RHFTextFieldElement } from 'react-hook-form-mui';
import type { TextFieldElementProps } from 'react-hook-form-mui';

export interface CustomTextFieldElementProps extends TextFieldElementProps {
  // Additional custom props can be added here
}

export const TextFieldElement: React.FC<CustomTextFieldElementProps> = (props) => {
  return (
    <RHFTextFieldElement
      variant="outlined"
      fullWidth
      {...props}
    />
  );
};

export default TextFieldElement;