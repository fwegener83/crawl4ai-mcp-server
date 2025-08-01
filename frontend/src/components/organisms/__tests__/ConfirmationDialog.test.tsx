import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import { ThemeProvider } from '../../../contexts/ThemeContext';
import { NotificationProvider } from '../../ui/NotificationProvider';
import { ConfirmationDialog } from '../ConfirmationDialog';
import type { ConfirmationDialogProps } from '../ConfirmationDialog';

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider>
    <NotificationProvider>
      {children}
    </NotificationProvider>
  </ThemeProvider>
);

const defaultProps: ConfirmationDialogProps = {
  open: true,
  title: 'Test Confirmation',
  message: 'Are you sure you want to proceed?',
  onConfirm: vi.fn(),
  onCancel: vi.fn(),
};

describe('ConfirmationDialog', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders with basic props', () => {
    render(
      <TestWrapper>
        <ConfirmationDialog {...defaultProps} />
      </TestWrapper>
    );

    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText('Test Confirmation')).toBeInTheDocument();
    expect(screen.getByText('Are you sure you want to proceed?')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /confirm/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    render(
      <TestWrapper>
        <ConfirmationDialog {...defaultProps} open={false} />
      </TestWrapper>
    );

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('displays custom button texts', () => {
    render(
      <TestWrapper>
        <ConfirmationDialog
          {...defaultProps}
          confirmText="Delete"
          cancelText="Keep"
        />
      </TestWrapper>
    );

    expect(screen.getByRole('button', { name: /delete/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /keep/i })).toBeInTheDocument();
  });

  it('calls onCancel when cancel button is clicked', () => {
    const onCancel = vi.fn();
    render(
      <TestWrapper>
        <ConfirmationDialog {...defaultProps} onCancel={onCancel} />
      </TestWrapper>
    );

    fireEvent.click(screen.getByRole('button', { name: /cancel/i }));
    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it('calls onConfirm when confirm button is clicked', async () => {
    const onConfirm = vi.fn();
    render(
      <TestWrapper>
        <ConfirmationDialog {...defaultProps} onConfirm={onConfirm} />
      </TestWrapper>
    );

    fireEvent.click(screen.getByRole('button', { name: /confirm/i }));
    await waitFor(() => {
      expect(onConfirm).toHaveBeenCalledTimes(1);
    });
  });

  it('handles async onConfirm', async () => {
    const onConfirm = vi.fn().mockResolvedValue(undefined);
    render(
      <TestWrapper>
        <ConfirmationDialog {...defaultProps} onConfirm={onConfirm} />
      </TestWrapper>
    );

    fireEvent.click(screen.getByRole('button', { name: /confirm/i }));
    await waitFor(() => {
      expect(onConfirm).toHaveBeenCalledTimes(1);
    });
  });

  it('disables buttons when loading', () => {
    render(
      <TestWrapper>
        <ConfirmationDialog {...defaultProps} loading={true} />
      </TestWrapper>
    );

    expect(screen.getByRole('button', { name: /cancel/i })).toBeDisabled();
    expect(screen.getByRole('button', { name: /processing/i })).toBeInTheDocument();
  });

  it('displays warning variant correctly', () => {
    render(
      <TestWrapper>
        <ConfirmationDialog {...defaultProps} variant="warning" />
      </TestWrapper>
    );

    // Warning icon should be present
    expect(screen.getByTestId('WarningIcon')).toBeInTheDocument();
  });

  it('displays error variant correctly', () => {
    render(
      <TestWrapper>
        <ConfirmationDialog {...defaultProps} variant="error" />
      </TestWrapper>
    );

    // Error icon should be present
    expect(screen.getByTestId('ErrorIcon')).toBeInTheDocument();
  });

  it('displays info variant correctly', () => {
    render(
      <TestWrapper>
        <ConfirmationDialog {...defaultProps} variant="info" />
      </TestWrapper>
    );

    // Info icon should be present
    expect(screen.getByTestId('InfoIcon')).toBeInTheDocument();
  });

  it('handles onConfirm errors gracefully', async () => {
    const onConfirm = vi.fn().mockRejectedValue(new Error('Test error'));
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    
    render(
      <TestWrapper>
        <ConfirmationDialog {...defaultProps} onConfirm={onConfirm} />
      </TestWrapper>
    );

    fireEvent.click(screen.getByRole('button', { name: /confirm/i }));
    
    await waitFor(() => {
      expect(onConfirm).toHaveBeenCalledTimes(1);
      expect(consoleSpy).toHaveBeenCalledWith('Confirmation action failed:', expect.any(Error));
    });

    consoleSpy.mockRestore();
  });

  it('has proper accessibility attributes', () => {
    render(
      <TestWrapper>
        <ConfirmationDialog {...defaultProps} />
      </TestWrapper>
    );

    const dialog = screen.getByRole('dialog');
    expect(dialog).toHaveAttribute('aria-labelledby', 'confirmation-dialog-title');
    expect(dialog).toHaveAttribute('aria-describedby', 'confirmation-dialog-description');
    
    expect(screen.getByRole('heading')).toHaveAttribute('id', 'confirmation-dialog-title');
    expect(screen.getByText('Are you sure you want to proceed?')).toHaveAttribute('id', 'confirmation-dialog-description');
  });
});