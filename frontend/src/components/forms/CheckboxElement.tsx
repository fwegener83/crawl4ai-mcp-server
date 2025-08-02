import React from 'react';
import { CheckboxElement as RHFCheckboxElement } from 'react-hook-form-mui';
import type { CheckboxElementProps } from 'react-hook-form-mui';

export interface CustomCheckboxElementProps extends CheckboxElementProps {
  // Additional custom props can be added here
}

export const CheckboxElement: React.FC<CustomCheckboxElementProps> = (props) => {
  return <RHFCheckboxElement {...props as any} />;
};

export default CheckboxElement;