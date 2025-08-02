import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FormContainer } from '../FormContainer';
import { TextFieldElement, SubmitButton } from '../';
import { renderWithTheme } from '../../../test/mui-test-utils';

describe('FormContainer', () => {
  it('renders form with children', () => {
    renderWithTheme(
      <FormContainer>
        <TextFieldElement name="test" label="Test Field" />
        <SubmitButton>Submit</SubmitButton>
      </FormContainer>
    );
    
    expect(screen.getByLabelText('Test Field')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /submit/i })).toBeInTheDocument();
  });

  it('handles form submission', async () => {
    const user = userEvent.setup();
    const handleSubmit = vi.fn();
    
    renderWithTheme(
      <FormContainer onSuccess={handleSubmit}>
        <TextFieldElement name="name" label="Name" />
        <SubmitButton>Submit</SubmitButton>
      </FormContainer>
    );
    
    const input = screen.getByLabelText('Name');
    const submitButton = screen.getByRole('button', { name: /submit/i });
    
    await user.type(input, 'Test Name');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(handleSubmit).toHaveBeenCalledWith(
        { name: 'Test Name' },
        expect.any(Object) // The form event
      );
    });
  });

  it('displays validation errors', async () => {
    const user = userEvent.setup();
    
    renderWithTheme(
      <FormContainer
        defaultValues={{ email: '' }}
      >
        <TextFieldElement 
          name="email" 
          label="Email" 
          rules={{ 
            required: 'Email is required',
            pattern: {
              value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
              message: 'Invalid email format'
            }
          }}
        />
        <SubmitButton>Submit</SubmitButton>
      </FormContainer>
    );
    
    const submitButton = screen.getByRole('button', { name: /submit/i });
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Email is required')).toBeInTheDocument();
    });
    
    const input = screen.getByLabelText('Email');
    await user.type(input, 'invalid-email');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Invalid email format')).toBeInTheDocument();
    });
  });

  it('applies custom spacing', () => {
    renderWithTheme(
      <FormContainer spacing={5}>
        <TextFieldElement name="field1" label="Field 1" />
        <TextFieldElement name="field2" label="Field 2" />
      </FormContainer>
    );
    
    // Find the box container that should have the gap styling
    const boxContainer = screen.getByLabelText('Field 1').closest('form')?.querySelector('[class*="MuiBox-root"]');
    expect(boxContainer).toBeInTheDocument();
  });
});