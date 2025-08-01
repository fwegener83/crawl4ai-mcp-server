import React from 'react';
import { 
  Radio as MuiRadio, 
  RadioGroup as MuiRadioGroup,
  FormControlLabel
} from '@mui/material';
import type { 
  RadioProps as MuiRadioProps,
  RadioGroupProps as MuiRadioGroupProps,
  FormControlLabelProps
} from '@mui/material';

export interface RadioProps extends MuiRadioProps {
  // Additional custom props can be added here
}

export const Radio: React.FC<RadioProps> = (props) => {
  return <MuiRadio {...props} />;
};

export interface RadioGroupProps extends MuiRadioGroupProps {
  // Additional custom props can be added here
}

export const RadioGroup: React.FC<RadioGroupProps> = (props) => {
  return <MuiRadioGroup {...props} />;
};

export interface RadioOptionProps extends Omit<FormControlLabelProps, 'control'> {
  radioProps?: RadioProps;
}

export const RadioOption: React.FC<RadioOptionProps> = ({ radioProps, ...props }) => {
  return <FormControlLabel control={<Radio {...radioProps} />} {...props} />;
};

export default Radio;