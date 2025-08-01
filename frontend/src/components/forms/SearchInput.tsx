import React from 'react';
import { TextField, IconButton } from '../ui';
import { InputAdornment, TextField as MuiTextField } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import ClearIcon from '@mui/icons-material/Clear';

export interface SearchInputProps extends React.ComponentProps<typeof MuiTextField> {
  onClear?: () => void;
  showClearButton?: boolean;
  searchIconPosition?: 'start' | 'end';
}

export const SearchInput: React.FC<SearchInputProps> = ({
  onClear,
  showClearButton = true,
  searchIconPosition = 'start',
  value,
  placeholder = 'Search...',
  ...textFieldProps
}) => {
  const hasValue = Boolean(value && String(value).length > 0);
  
  const startAdornment = searchIconPosition === 'start' ? (
    <InputAdornment position="start">
      <SearchIcon color="action" />
    </InputAdornment>
  ) : undefined;

  const endAdornment = (
    <InputAdornment position="end">
      {searchIconPosition === 'end' && <SearchIcon color="action" />}
      {showClearButton && hasValue && onClear && (
        <IconButton
          size="small"
          onClick={onClear}
          edge="end"
          aria-label="clear search"
        >
          <ClearIcon />
        </IconButton>
      )}
    </InputAdornment>
  );

  return (
    <TextField
      value={value}
      placeholder={placeholder}
      {...textFieldProps}
      InputProps={{
        startAdornment,
        endAdornment: (searchIconPosition === 'end' || (showClearButton && hasValue)) ? endAdornment : undefined,
        ...textFieldProps.InputProps,
      }}
    />
  );
};

export default SearchInput;