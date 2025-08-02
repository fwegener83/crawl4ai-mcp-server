import React from 'react';
import { 
  Select as MuiSelect, 
  MenuItem,
  FormControl,
  InputLabel,
  FormHelperText
} from '@mui/material';
import type { 
  SelectProps as MuiSelectProps,
  MenuItemProps
} from '@mui/material';

export interface SelectOption {
  value: string | number;
  label: string;
  disabled?: boolean;
}

export interface SelectProps extends Omit<MuiSelectProps, 'label'> {
  options?: SelectOption[];
  label?: string;
  helperText?: string;
  error?: boolean;
}

export const Select: React.FC<SelectProps> = ({ 
  options = [],
  label,
  helperText,
  error,
  children,
  ...props 
}) => {
  const labelId = `select-label-${Math.random().toString(36).substr(2, 9)}`;

  return (
    <FormControl fullWidth error={error}>
      {label && <InputLabel id={labelId}>{label}</InputLabel>}
      <MuiSelect
        labelId={label ? labelId : undefined}
        label={label}
        {...props}
      >
        {options.map((option) => (
          <MenuItem 
            key={option.value} 
            value={option.value}
            disabled={option.disabled}
          >
            {option.label}
          </MenuItem>
        ))}
        {children}
      </MuiSelect>
      {helperText && <FormHelperText>{helperText}</FormHelperText>}
    </FormControl>
  );
};

export interface SelectItemProps extends MenuItemProps {
  // Additional custom props can be added here
}

export const SelectItem: React.FC<SelectItemProps> = (props) => {
  return <MenuItem {...props} />;
};

export default Select;