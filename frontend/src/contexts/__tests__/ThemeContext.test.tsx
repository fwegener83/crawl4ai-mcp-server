import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { AppThemeProvider, useTheme } from '../ThemeContext';

// Mock localStorage
const mockLocalStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
});

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Test component that uses the theme context
const ThemeTestComponent = () => {
  const { mode, toggleTheme, setTheme } = useTheme();
  
  return (
    <div>
      <div data-testid="current-mode">{mode}</div>
      <button data-testid="toggle-theme" onClick={toggleTheme}>
        Toggle Theme
      </button>
      <button data-testid="set-dark" onClick={() => setTheme('dark')}>
        Set Dark
      </button>
      <button data-testid="set-light" onClick={() => setTheme('light')}>
        Set Light
      </button>
    </div>
  );
};

describe('ThemeContext', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockLocalStorage.getItem.mockReturnValue(null);
  });

  it('should provide light theme as default', () => {
    render(
      <AppThemeProvider>
        <ThemeTestComponent />
      </AppThemeProvider>
    );

    expect(screen.getByTestId('current-mode')).toHaveTextContent('light');
  });

  it('should toggle theme mode', () => {
    render(
      <AppThemeProvider>
        <ThemeTestComponent />
      </AppThemeProvider>
    );

    const toggleButton = screen.getByTestId('toggle-theme');
    const modeDisplay = screen.getByTestId('current-mode');

    expect(modeDisplay).toHaveTextContent('light');

    fireEvent.click(toggleButton);
    expect(modeDisplay).toHaveTextContent('dark');

    fireEvent.click(toggleButton);
    expect(modeDisplay).toHaveTextContent('light');
  });

  it('should set specific theme mode', () => {
    render(
      <AppThemeProvider>
        <ThemeTestComponent />
      </AppThemeProvider>
    );

    const setDarkButton = screen.getByTestId('set-dark');
    const setLightButton = screen.getByTestId('set-light');
    const modeDisplay = screen.getByTestId('current-mode');

    fireEvent.click(setDarkButton);
    expect(modeDisplay).toHaveTextContent('dark');

    fireEvent.click(setLightButton);
    expect(modeDisplay).toHaveTextContent('light');
  });

  it('should save theme preference to localStorage', () => {
    render(
      <AppThemeProvider>
        <ThemeTestComponent />
      </AppThemeProvider>
    );

    const toggleButton = screen.getByTestId('toggle-theme');
    fireEvent.click(toggleButton);

    expect(mockLocalStorage.setItem).toHaveBeenCalledWith('theme-mode', 'dark');
  });

  it('should load saved theme preference from localStorage', () => {
    mockLocalStorage.getItem.mockReturnValue('dark');

    render(
      <AppThemeProvider>
        <ThemeTestComponent />
      </AppThemeProvider>
    );

    expect(screen.getByTestId('current-mode')).toHaveTextContent('dark');
  });

  it('should throw error when useTheme is used outside provider', () => {
    // Suppress console.error for this test
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    
    expect(() => render(<ThemeTestComponent />)).toThrow(
      'useTheme must be used within a ThemeProvider'
    );
    
    consoleSpy.mockRestore();
  });
});