import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { LabeledInput } from '../LabeledInput';
import { renderWithTheme } from '../../../test/mui-test-utils';

describe('LabeledInput', () => {
  it('renders label text', () => {
    renderWithTheme(<LabeledInput label="Test Label" />);
    
    expect(screen.getByText('Test Label')).toBeInTheDocument();
  });

  it('shows required asterisk when required is true', () => {
    renderWithTheme(<LabeledInput label="Test Label" required />);
    
    expect(screen.getByText('*')).toBeInTheDocument();
  });

  it('does not show required asterisk when required is false', () => {
    renderWithTheme(<LabeledInput label="Test Label" required={false} />);
    
    expect(screen.queryByText('*')).not.toBeInTheDocument();
  });

  it('renders description text when provided', () => {
    renderWithTheme(
      <LabeledInput 
        label="Test Label" 
        description="This is a description" 
      />
    );
    
    expect(screen.getByText('This is a description')).toBeInTheDocument();
  });

  it('renders helper text when provided', () => {
    renderWithTheme(
      <LabeledInput 
        label="Test Label" 
        helperText="This is helper text" 
      />
    );
    
    expect(screen.getByText('This is helper text')).toBeInTheDocument();
  });

  it('shows error state on label when error is true', () => {
    renderWithTheme(
      <LabeledInput 
        label="Test Label" 
        error 
        helperText="Error message" 
      />
    );
    
    const label = screen.getByText('Test Label');
    expect(label).toHaveStyle({ color: 'rgb(244, 67, 54)' }); // MUI error color
  });

  it('passes through TextField props', () => {
    renderWithTheme(
      <LabeledInput 
        label="Test Label" 
        placeholder="Enter text here"
        disabled
      />
    );
    
    const input = screen.getByRole('textbox');
    expect(input).toHaveAttribute('placeholder', 'Enter text here');
    expect(input).toBeDisabled();
  });

  it('renders input with proper spacing', () => {
    renderWithTheme(<LabeledInput label="Test Label" />);
    
    const container = screen.getByText('Test Label').closest('div');
    expect(container).toHaveStyle({ marginBottom: '16px' }); // 2 * 8px (theme spacing)
  });
});