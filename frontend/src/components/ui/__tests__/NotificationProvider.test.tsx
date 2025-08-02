import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { NotificationProvider, useNotification } from '../NotificationProvider';
import { Button } from '../Button';
import { renderWithTheme } from '../../../test/mui-test-utils';

// Test component that uses the notification context
const TestComponent = () => {
  const { showSuccess, showError, showWarning, showInfo } = useNotification();
  
  return (
    <div>
      <Button onClick={() => showSuccess('Success message')}>Show Success</Button>
      <Button onClick={() => showError('Error message')}>Show Error</Button>
      <Button onClick={() => showWarning('Warning message')}>Show Warning</Button>
      <Button onClick={() => showInfo('Info message')}>Show Info</Button>
    </div>
  );
};

describe('NotificationProvider', () => {
  it('provides notification context to children', () => {
    renderWithTheme(
      <NotificationProvider>
        <TestComponent />
      </NotificationProvider>
    );
    
    expect(screen.getByText('Show Success')).toBeInTheDocument();
    expect(screen.getByText('Show Error')).toBeInTheDocument();
    expect(screen.getByText('Show Warning')).toBeInTheDocument();
    expect(screen.getByText('Show Info')).toBeInTheDocument();
  });

  it('shows success notification', async () => {
    const user = userEvent.setup();
    
    renderWithTheme(
      <NotificationProvider>
        <TestComponent />
      </NotificationProvider>
    );
    
    const successButton = screen.getByText('Show Success');
    await user.click(successButton);
    
    await waitFor(() => {
      expect(screen.getByText('Success message')).toBeInTheDocument();
    });
  });

  it('shows error notification', async () => {
    const user = userEvent.setup();
    
    renderWithTheme(
      <NotificationProvider>
        <TestComponent />
      </NotificationProvider>
    );
    
    const errorButton = screen.getByText('Show Error');
    await user.click(errorButton);
    
    await waitFor(() => {
      expect(screen.getByText('Error message')).toBeInTheDocument();
    });
  });

  it('shows warning notification', async () => {
    const user = userEvent.setup();
    
    renderWithTheme(
      <NotificationProvider>
        <TestComponent />
      </NotificationProvider>
    );
    
    const warningButton = screen.getByText('Show Warning');
    await user.click(warningButton);
    
    await waitFor(() => {
      expect(screen.getByText('Warning message')).toBeInTheDocument();
    });
  });

  it('shows info notification', async () => {
    const user = userEvent.setup();
    
    renderWithTheme(
      <NotificationProvider>
        <TestComponent />
      </NotificationProvider>
    );
    
    const infoButton = screen.getByText('Show Info');
    await user.click(infoButton);
    
    await waitFor(() => {
      expect(screen.getByText('Info message')).toBeInTheDocument();
    });
  });

  it('throws error when used outside provider', () => {
    // Suppress console.error for this test
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    
    expect(() => {
      render(<TestComponent />);
    }).toThrow('useNotification must be used within a NotificationProvider');
    
    consoleSpy.mockRestore();
  });

  it('closes notification when close button is clicked', async () => {
    const user = userEvent.setup();
    
    renderWithTheme(
      <NotificationProvider>
        <TestComponent />
      </NotificationProvider>
    );
    
    const successButton = screen.getByText('Show Success');
    await user.click(successButton);
    
    await waitFor(() => {
      expect(screen.getByText('Success message')).toBeInTheDocument();
    });
    
    const closeButton = screen.getByLabelText('Close');
    await user.click(closeButton);
    
    await waitFor(() => {
      expect(screen.queryByText('Success message')).not.toBeInTheDocument();
    });
  });
});