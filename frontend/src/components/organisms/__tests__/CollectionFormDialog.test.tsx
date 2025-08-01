import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import { ThemeProvider } from '../../../contexts/ThemeContext';
import { NotificationProvider } from '../../ui/NotificationProvider';
import { CollectionFormDialog } from '../CollectionFormDialog';
import type { CollectionFormDialogProps } from '../CollectionFormDialog';

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider>
    <NotificationProvider>
      {children}
    </NotificationProvider>
  </ThemeProvider>
);

const defaultProps: CollectionFormDialogProps = {
  open: true,
  title: 'Create New Collection',
  onSubmit: vi.fn(),
  onCancel: vi.fn(),
};

describe('CollectionFormDialog', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders with basic props', () => {
    render(
      <TestWrapper>
        <CollectionFormDialog {...defaultProps} />
      </TestWrapper>
    );

    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText('Create New Collection')).toBeInTheDocument();
    expect(screen.getByLabelText(/collection name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create collection/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    render(
      <TestWrapper>
        <CollectionFormDialog {...defaultProps} open={false} />
      </TestWrapper>
    );

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('displays initial data', () => {
    const initialData = {
      name: 'test-collection',
      description: 'Test description',
    };

    render(
      <TestWrapper>
        <CollectionFormDialog {...defaultProps} initialData={initialData} />
      </TestWrapper>
    );

    expect(screen.getByDisplayValue('test-collection')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Test description')).toBeInTheDocument();
  });

  it('displays custom submit text', () => {
    render(
      <TestWrapper>
        <CollectionFormDialog
          {...defaultProps}
          submitText="Update Collection"
        />
      </TestWrapper>
    );

    expect(screen.getByRole('button', { name: /update collection/i })).toBeInTheDocument();
  });

  it('calls onCancel when cancel button is clicked', () => {
    const onCancel = vi.fn();
    render(
      <TestWrapper>
        <CollectionFormDialog {...defaultProps} onCancel={onCancel} />
      </TestWrapper>
    );

    fireEvent.click(screen.getByRole('button', { name: /cancel/i }));
    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it('submits form with valid data', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    
    render(
      <TestWrapper>
        <CollectionFormDialog {...defaultProps} onSubmit={onSubmit} />
      </TestWrapper>
    );

    await user.type(screen.getByLabelText(/collection name/i), 'my-collection');
    await user.type(screen.getByLabelText(/description/i), 'My test collection');
    
    fireEvent.click(screen.getByRole('button', { name: /create collection/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        name: 'my-collection',
        description: 'My test collection',
      });
    });
  });

  it('trims whitespace from input values', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    
    render(
      <TestWrapper>
        <CollectionFormDialog {...defaultProps} onSubmit={onSubmit} />
      </TestWrapper>
    );

    await user.type(screen.getByLabelText(/collection name/i), '  test-collection  ');
    await user.type(screen.getByLabelText(/description/i), '  Test description  ');
    
    fireEvent.click(screen.getByRole('button', { name: /create collection/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        name: 'test-collection',
        description: 'Test description',
      });
    });
  });

  it('omits empty description', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    
    render(
      <TestWrapper>
        <CollectionFormDialog {...defaultProps} onSubmit={onSubmit} />
      </TestWrapper>
    );

    await user.type(screen.getByLabelText(/collection name/i), 'test-collection');
    
    fireEvent.click(screen.getByRole('button', { name: /create collection/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        name: 'test-collection',
        description: undefined,
      });
    });
  });

  it('validates required name field', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    
    render(
      <TestWrapper>
        <CollectionFormDialog {...defaultProps} onSubmit={onSubmit} />
      </TestWrapper>
    );

    // Try to submit without entering a name
    fireEvent.click(screen.getByRole('button', { name: /create collection/i }));

    await waitFor(() => {
      expect(screen.getByText(/collection name is required/i)).toBeInTheDocument();
    });

    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('validates name pattern', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    
    render(
      <TestWrapper>
        <CollectionFormDialog {...defaultProps} onSubmit={onSubmit} />
      </TestWrapper>
    );

    await user.type(screen.getByLabelText(/collection name/i), 'invalid name!');
    fireEvent.click(screen.getByRole('button', { name: /create collection/i }));

    await waitFor(() => {
      expect(screen.getByText(/only letters, numbers, hyphens, and underscores are allowed/i)).toBeInTheDocument();
    });

    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('validates name length', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    
    render(
      <TestWrapper>
        <CollectionFormDialog {...defaultProps} onSubmit={onSubmit} />
      </TestWrapper>
    );

    const longName = 'a'.repeat(51);
    await user.type(screen.getByLabelText(/collection name/i), longName);
    fireEvent.click(screen.getByRole('button', { name: /create collection/i }));

    await waitFor(() => {
      expect(screen.getByText(/collection name must be 50 characters or less/i)).toBeInTheDocument();
    });

    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('validates description length', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    
    render(
      <TestWrapper>
        <CollectionFormDialog {...defaultProps} onSubmit={onSubmit} />
      </TestWrapper>
    );

    await user.type(screen.getByLabelText(/collection name/i), 'test-collection');
    
    const longDescription = 'a'.repeat(501);
    await user.type(screen.getByLabelText(/description/i), longDescription);
    fireEvent.click(screen.getByRole('button', { name: /create collection/i }));

    await waitFor(() => {
      expect(screen.getByText(/description must be 500 characters or less/i)).toBeInTheDocument();
    });

    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('disables buttons when loading', () => {
    render(
      <TestWrapper>
        <CollectionFormDialog {...defaultProps} loading={true} />
      </TestWrapper>
    );

    expect(screen.getByRole('button', { name: /cancel/i })).toBeDisabled();
    expect(screen.getByRole('button', { name: /processing/i })).toBeInTheDocument();
  });

  it('resets form on cancel', async () => {
    const user = userEvent.setup();
    const onCancel = vi.fn();
    
    render(
      <TestWrapper>
        <CollectionFormDialog {...defaultProps} onCancel={onCancel} />
      </TestWrapper>
    );

    await user.type(screen.getByLabelText(/collection name/i), 'test-name');
    fireEvent.click(screen.getByRole('button', { name: /cancel/i }));

    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it('handles form submission errors gracefully', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn().mockRejectedValue(new Error('Test error'));
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    
    render(
      <TestWrapper>
        <CollectionFormDialog {...defaultProps} onSubmit={onSubmit} />
      </TestWrapper>
    );

    await user.type(screen.getByLabelText(/collection name/i), 'test-collection');
    fireEvent.click(screen.getByRole('button', { name: /create collection/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledTimes(1);
      expect(consoleSpy).toHaveBeenCalledWith('Form submission error:', expect.any(Error));
    });

    consoleSpy.mockRestore();
  });

  it('focuses name field when dialog opens', () => {
    render(
      <TestWrapper>
        <CollectionFormDialog {...defaultProps} />
      </TestWrapper>
    );

    expect(screen.getByLabelText(/collection name/i)).toHaveFocus();
  });

  it('has proper accessibility attributes', () => {
    render(
      <TestWrapper>
        <CollectionFormDialog {...defaultProps} />
      </TestWrapper>
    );

    const dialog = screen.getByRole('dialog');
    expect(dialog).toHaveAttribute('aria-labelledby', 'collection-form-dialog-title');
    
    expect(screen.getByRole('heading')).toHaveAttribute('id', 'collection-form-dialog-title');
  });
});