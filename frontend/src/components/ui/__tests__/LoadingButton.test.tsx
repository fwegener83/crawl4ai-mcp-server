import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoadingButton } from '../LoadingButton';
import { renderWithTheme } from '../../../test/mui-test-utils';

describe('LoadingButton', () => {
  it('renders button with children', () => {
    renderWithTheme(<LoadingButton>Click me</LoadingButton>);
    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
  });

  it('shows loading indicator when loading is true', () => {
    renderWithTheme(<LoadingButton loading>Click me</LoadingButton>);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('is disabled when loading is true', () => {
    renderWithTheme(<LoadingButton loading>Click me</LoadingButton>);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('is disabled when disabled prop is true', () => {
    renderWithTheme(<LoadingButton disabled>Click me</LoadingButton>);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('calls onClick when clicked and not loading', async () => {
    const user = userEvent.setup();
    const handleClick = vi.fn();
    
    renderWithTheme(
      <LoadingButton onClick={handleClick}>Click me</LoadingButton>
    );
    
    await user.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('does not call onClick when loading', async () => {
    const handleClick = vi.fn();
    
    renderWithTheme(
      <LoadingButton onClick={handleClick} loading>Click me</LoadingButton>
    );
    
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
    expect(handleClick).not.toHaveBeenCalled();
  });

  it('shows custom loading indicator', () => {
    const customIndicator = <div data-testid="custom-loader">Loading...</div>;
    
    renderWithTheme(
      <LoadingButton loading loadingIndicator={customIndicator}>
        Click me
      </LoadingButton>
    );
    
    expect(screen.getByTestId('custom-loader')).toBeInTheDocument();
  });

  it('preserves startIcon when not loading', () => {
    const startIcon = <div data-testid="start-icon">Icon</div>;
    
    renderWithTheme(
      <LoadingButton startIcon={startIcon}>Click me</LoadingButton>
    );
    
    expect(screen.getByTestId('start-icon')).toBeInTheDocument();
  });
});