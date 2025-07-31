import { describe, it, expect } from 'vitest';
import { lightTheme, darkTheme, getTheme } from '..';

describe('Theme Configuration', () => {
  it('should create light theme with correct palette', () => {
    expect(lightTheme.palette.mode).toBe('light');
    expect(lightTheme.palette.primary.main).toBe('#2196f3');
    expect(lightTheme.palette.background.default).toBe('#ffffff');
  });

  it('should create dark theme with correct palette', () => {
    expect(darkTheme.palette.mode).toBe('dark');
    expect(darkTheme.palette.primary.main).toBe('#2196f3');
    expect(darkTheme.palette.background.default).toBe('#121212');
  });

  it('should return correct theme based on mode', () => {
    const light = getTheme('light');
    const dark = getTheme('dark');
    
    expect(light.palette.mode).toBe('light');
    expect(dark.palette.mode).toBe('dark');
  });

  it('should have consistent typography across themes', () => {
    expect(lightTheme.typography.h1.fontSize).toBe(darkTheme.typography.h1.fontSize);
    expect(lightTheme.typography.body1.fontSize).toBe(darkTheme.typography.body1.fontSize);
  });

  it('should have custom component overrides', () => {
    expect(lightTheme.components?.MuiButton?.styleOverrides?.root).toBeDefined();
    expect(lightTheme.components?.MuiCard?.styleOverrides?.root).toBeDefined();
  });

  it('should have correct border radius', () => {
    expect(lightTheme.shape.borderRadius).toBe(8);
    expect(darkTheme.shape.borderRadius).toBe(8);
  });
});