import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Select } from '../Select';
import { renderWithTheme } from '../../../test/mui-test-utils';

describe('Select', () => {
  const mockOptions = [
    { value: 'option1', label: 'Option 1' },
    { value: 'option2', label: 'Option 2' },
    { value: 'option3', label: 'Option 3', disabled: true },
  ];

  it('renders select with label', () => {
    renderWithTheme(
      <Select label="Test Select" options={mockOptions} />
    );
    
    expect(screen.getByLabelText(/test select/i)).toBeInTheDocument();
  });

  it('renders all options', async () => {
    const user = userEvent.setup();
    
    renderWithTheme(
      <Select label="Test Select" options={mockOptions} />
    );
    
    const select = screen.getByLabelText(/test select/i);
    await user.click(select);
    
    expect(screen.getByText('Option 1')).toBeInTheDocument();
    expect(screen.getByText('Option 2')).toBeInTheDocument();
    expect(screen.getByText('Option 3')).toBeInTheDocument();
  });

  it('shows helper text when provided', () => {
    renderWithTheme(
      <Select 
        label="Test Select" 
        options={mockOptions}
        helperText="This is helper text"
      />
    );
    
    expect(screen.getByText('This is helper text')).toBeInTheDocument();
  });

  it('shows error state', () => {
    renderWithTheme(
      <Select 
        label="Test Select" 
        options={mockOptions}
        error
        helperText="Error message"
      />
    );
    
    const helperText = screen.getByText('Error message');
    expect(helperText).toHaveClass('Mui-error');
  });

  it('calls onChange when option is selected', async () => {
    const user = userEvent.setup();
    const handleChange = vi.fn();
    
    renderWithTheme(
      <Select 
        label="Test Select" 
        options={mockOptions}
        onChange={handleChange}
      />
    );
    
    const select = screen.getByLabelText(/test select/i);
    await user.click(select);
    
    const option1 = screen.getByText('Option 1');
    await user.click(option1);
    
    expect(handleChange).toHaveBeenCalled();
  });

  it('disables specified options', async () => {
    const user = userEvent.setup();
    
    renderWithTheme(
      <Select label="Test Select" options={mockOptions} />
    );
    
    const select = screen.getByLabelText(/test select/i);
    await user.click(select);
    
    const disabledOption = screen.getByText('Option 3');
    expect(disabledOption.closest('li')).toHaveAttribute('aria-disabled', 'true');
  });
});