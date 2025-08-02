import { createTheme } from '@mui/material/styles';
import type { ThemeOptions } from '@mui/material/styles';
import { colors, backgrounds } from './colors';
import { typography } from './typography';
import { components } from './components';

// Base theme configuration
const baseTheme: ThemeOptions = {
  typography,
  components,
  shape: {
    borderRadius: 8,
  },
  spacing: 8,
};

// Light theme configuration
export const lightTheme = createTheme({
  ...baseTheme,
  palette: {
    mode: 'light',
    primary: {
      main: colors.primary[500],
      light: colors.primary[300],
      dark: colors.primary[700],
      contrastText: '#ffffff',
    },
    secondary: {
      main: colors.secondary[500],
      light: colors.secondary[300],
      dark: colors.secondary[700],
      contrastText: '#ffffff',
    },
    error: {
      main: colors.error[500],
      light: colors.error[300],
      dark: colors.error[700],
      contrastText: '#ffffff',
    },
    warning: {
      main: colors.warning[500],
      light: colors.warning[300],
      dark: colors.warning[700],
      contrastText: '#000000',
    },
    success: {
      main: colors.success[500],
      light: colors.success[300],
      dark: colors.success[700],
      contrastText: '#ffffff',
    },
    grey: colors.grey,
    background: backgrounds.light,
    text: {
      primary: colors.grey[900],
      secondary: colors.grey[700],
      disabled: colors.grey[500],
    },
    divider: colors.grey[200],
  },
});

// Dark theme configuration
export const darkTheme = createTheme({
  ...baseTheme,
  palette: {
    mode: 'dark',
    primary: {
      main: colors.primary[500],
      light: colors.primary[300],
      dark: colors.primary[700],
      contrastText: '#ffffff',
    },
    secondary: {
      main: colors.secondary[500],
      light: colors.secondary[300],
      dark: colors.secondary[700],
      contrastText: '#ffffff',
    },
    error: {
      main: colors.error[500],
      light: colors.error[300],
      dark: colors.error[700],
      contrastText: '#ffffff',
    },
    warning: {
      main: colors.warning[500],
      light: colors.warning[300],
      dark: colors.warning[700],
      contrastText: '#000000',
    },
    success: {
      main: colors.success[500],
      light: colors.success[300],
      dark: colors.success[700],
      contrastText: '#ffffff',
    },
    grey: colors.grey,
    background: backgrounds.dark,
    text: {
      primary: colors.grey[50],
      secondary: colors.grey[300],
      disabled: colors.grey[500],
    },
    divider: colors.grey[700],
  },
});

// Default theme (light)
export const theme = lightTheme;

// Theme type for TypeScript
export type AppTheme = typeof theme;

// Helper function to get theme by mode
export const getTheme = (mode: 'light' | 'dark') => {
  return mode === 'dark' ? darkTheme : lightTheme;
};