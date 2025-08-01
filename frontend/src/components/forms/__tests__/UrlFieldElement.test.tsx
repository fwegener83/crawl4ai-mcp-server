import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FormContainer } from '../FormContainer';
import { UrlFieldElement } from '../UrlFieldElement';
import { SubmitButton } from '../SubmitButton';
import { renderWithTheme } from '../../../test/mui-test-utils';

describe('UrlFieldElement', () => {
  it('renders URL input field', () => {
    renderWithTheme(
      <FormContainer>
        <UrlFieldElement name="url" label="Website URL" />
      </FormContainer>
    );
    
    const input = screen.getByLabelText('Website URL');
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute('type', 'url');
  });

  it('shows default placeholder', () => {
    renderWithTheme(
      <FormContainer>
        <UrlFieldElement name="url" label="Website URL" />
      </FormContainer>
    );
    
    expect(screen.getByPlaceholderText('https://example.com')).toBeInTheDocument();
  });

  it('shows custom placeholder', () => {
    renderWithTheme(
      <FormContainer>
        <UrlFieldElement 
          name="url" 
          label="Website URL" 
          placeholder="Enter your URL here..."
        />
      </FormContainer>
    );
    
    expect(screen.getByPlaceholderText('Enter your URL here...')).toBeInTheDocument();
  });

  it('validates required URLs', async () => {
    const user = userEvent.setup();
    
    renderWithTheme(
      <FormContainer>
        <UrlFieldElement name="url" label="Website URL" required />
        <SubmitButton>Submit</SubmitButton>
      </FormContainer>
    );
    
    const submitButton = screen.getByRole('button', { name: /submit/i });
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('URL is required')).toBeInTheDocument();
    });
  });

  it('validates URL format', async () => {
    const user = userEvent.setup();
    
    renderWithTheme(
      <FormContainer>
        <UrlFieldElement name="url" label="Website URL" required />
        <SubmitButton>Submit</SubmitButton>
      </FormContainer>
    );
    
    const input = screen.getByLabelText('Website URL');
    const submitButton = screen.getByRole('button', { name: /submit/i });
    
    await user.type(input, 'invalid-url');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Please enter a valid URL starting with http:// or https://')).toBeInTheDocument();
    });
  });

  it('accepts valid URLs', async () => {
    const user = userEvent.setup();
    const handleSubmit = vi.fn();
    
    renderWithTheme(
      <FormContainer onSuccess={handleSubmit}>
        <UrlFieldElement name="url" label="Website URL" required />
        <SubmitButton>Submit</SubmitButton>
      </FormContainer>
    );
    
    const input = screen.getByLabelText('Website URL');
    const submitButton = screen.getByRole('button', { name: /submit/i });
    
    await user.type(input, 'https://example.com');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(handleSubmit).toHaveBeenCalledWith(
        { url: 'https://example.com' },
        expect.any(Object)
      );
    });
  });

  it('allows optional URLs', async () => {
    const user = userEvent.setup();
    const handleSubmit = vi.fn();
    
    renderWithTheme(
      <FormContainer 
        onSuccess={handleSubmit}
        defaultValues={{ url: '' }}
      >
        <UrlFieldElement name="url" label="Website URL" required={false} />
        <SubmitButton>Submit</SubmitButton>
      </FormContainer>
    );
    
    const submitButton = screen.getByRole('button', { name: /submit/i });
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(handleSubmit).toHaveBeenCalledWith(
        { url: '' },
        expect.any(Object)
      );
    });
  });
});