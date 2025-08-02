import React from 'react';
import { RadioButtonGroup as RHFRadioButtonGroup } from 'react-hook-form-mui';
import type { RadioButtonGroupProps } from 'react-hook-form-mui';

export interface CustomRadioButtonGroupProps extends RadioButtonGroupProps {
  // Additional custom props can be added here
}

export const RadioButtonGroup: React.FC<CustomRadioButtonGroupProps> = (props) => {
  return <RHFRadioButtonGroup {...props} />;
};

export default RadioButtonGroup;