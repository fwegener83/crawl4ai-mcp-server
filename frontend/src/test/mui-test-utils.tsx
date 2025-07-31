import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { vi } from 'vitest';
import { lightTheme } from '../theme';

// Custom render function that includes MUI theme provider
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  theme?: typeof lightTheme;
}

const AllTheProviders: React.FC<{ children: React.ReactNode; theme?: typeof lightTheme }> = ({ 
  children, 
  theme = lightTheme 
}) => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  );
};

const customRender = (
  ui: ReactElement,
  { theme, ...options }: CustomRenderOptions = {}
) => {
  const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <AllTheProviders theme={theme}>{children}</AllTheProviders>
  );

  return render(ui, { wrapper: Wrapper, ...options });
};

// Helper function to test theme accessibility
export const getThemeColor = (theme: typeof lightTheme, path: string) => {
  const pathArray = path.split('.');
  let result: any = theme.palette;
  
  for (const key of pathArray) {
    result = result[key];
  }
  
  return result;
};

// Helper to test responsive breakpoints
export const mockBreakpoint = (breakpoint: 'xs' | 'sm' | 'md' | 'lg' | 'xl') => {
  const breakpoints = {
    xs: '(max-width: 599px)',
    sm: '(min-width: 600px) and (max-width: 959px)',
    md: '(min-width: 960px) and (max-width: 1279px)',
    lg: '(min-width: 1280px) and (max-width: 1919px)',
    xl: '(min-width: 1920px)',
  };

  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation(query => ({
      matches: query === breakpoints[breakpoint],
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });
};

// Re-export everything from React Testing Library
export * from '@testing-library/react';

// Override render method
export { customRender as render };