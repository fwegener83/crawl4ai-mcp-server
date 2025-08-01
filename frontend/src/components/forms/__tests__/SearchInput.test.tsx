import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SearchInput } from '../SearchInput';
import { renderWithTheme } from '../../../test/mui-test-utils';

describe('SearchInput', () => {
  it('renders with search icon by default', () => {
    renderWithTheme(<SearchInput />);
    
    const searchIcon = screen.getByTestId('SearchIcon');
    expect(searchIcon).toBeInTheDocument();
  });

  it('shows placeholder text', () => {
    renderWithTheme(<SearchInput placeholder="Search items..." />);
    
    expect(screen.getByPlaceholderText('Search items...')).toBeInTheDocument();
  });

  it('shows clear button when value is present and showClearButton is true', () => {
    renderWithTheme(<SearchInput value="test search" showClearButton onClear={() => {}} />);
    
    expect(screen.getByLabelText('clear search')).toBeInTheDocument();
  });

  it('does not show clear button when value is empty', () => {
    renderWithTheme(<SearchInput value="" showClearButton />);
    
    expect(screen.queryByLabelText('clear search')).not.toBeInTheDocument();
  });

  it('does not show clear button when showClearButton is false', () => {
    renderWithTheme(<SearchInput value="test search" showClearButton={false} onClear={() => {}} />);
    
    expect(screen.queryByLabelText('clear search')).not.toBeInTheDocument();
  });

  it('calls onClear when clear button is clicked', async () => {
    const user = userEvent.setup();
    const handleClear = vi.fn();
    
    renderWithTheme(
      <SearchInput 
        value="test search" 
        onClear={handleClear}
        showClearButton 
      />
    );
    
    const clearButton = screen.getByLabelText('clear search');
    await user.click(clearButton);
    
    expect(handleClear).toHaveBeenCalledTimes(1);
  });

  it('positions search icon at end when specified', () => {
    renderWithTheme(<SearchInput searchIconPosition="end" />);
    
    const searchIcon = screen.getByTestId('SearchIcon');
    expect(searchIcon.closest('[class*="MuiInputAdornment-positionEnd"]')).toBeInTheDocument();
  });

  it('calls onChange when text is entered', async () => {
    const user = userEvent.setup();
    const handleChange = vi.fn();
    
    renderWithTheme(<SearchInput onChange={handleChange} />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, 'search text');
    
    expect(handleChange).toHaveBeenCalled();
  });

  it('passes through other TextField props', () => {
    renderWithTheme(
      <SearchInput 
        disabled 
        helperText="Search helper text" 
      />
    );
    
    expect(screen.getByRole('textbox')).toBeDisabled();
    expect(screen.getByText('Search helper text')).toBeInTheDocument();
  });
});