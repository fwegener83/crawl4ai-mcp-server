import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TopNavigation } from '../TopNavigation';
import { renderWithTheme } from '../../../test/mui-test-utils';
import { AppThemeProvider } from '../../../contexts/ThemeContext';

// Wrapper component to provide theme context
const ThemeWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AppThemeProvider>{children}</AppThemeProvider>
);

const renderWithAllProviders = (component: React.ReactElement) => {
  return renderWithTheme(component, {
    wrapper: ({ children }) => <ThemeWrapper>{children}</ThemeWrapper>
  });
};

describe('TopNavigation', () => {
  const defaultProps = {
    onNavigate: vi.fn(),
    onSettingsClick: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the application title', () => {
    renderWithAllProviders(<TopNavigation {...defaultProps} />);
    expect(screen.getByText('Crawl4AI File Manager')).toBeInTheDocument();
  });

  it('renders File Collections tab', () => {
    renderWithAllProviders(<TopNavigation {...defaultProps} />);
    expect(screen.getByTestId('file-collections-tab')).toBeInTheDocument();
    expect(screen.getByText('File Collections')).toBeInTheDocument();
  });

  it('renders RAG Query tab', () => {
    renderWithAllProviders(<TopNavigation {...defaultProps} />);
    expect(screen.getByTestId('rag-query-tab')).toBeInTheDocument();
    expect(screen.getByText('RAG Query')).toBeInTheDocument();
  });

  it('highlights the active tab', () => {
    renderWithAllProviders(<TopNavigation {...defaultProps} currentPage="rag-query" />);
    const ragQueryTab = screen.getByTestId('rag-query-tab');
    expect(ragQueryTab).toHaveClass('Mui-selected');
  });

  it('calls onNavigate when clicking a tab', async () => {
    const user = userEvent.setup();
    const mockNavigate = vi.fn();
    
    renderWithAllProviders(
      <TopNavigation {...defaultProps} onNavigate={mockNavigate} currentPage="file-collections" />
    );
    
    await user.click(screen.getByTestId('rag-query-tab'));
    expect(mockNavigate).toHaveBeenCalledWith('rag-query');
  });

  it('renders theme toggle button', () => {
    renderWithAllProviders(<TopNavigation {...defaultProps} />);
    expect(screen.getByLabelText(/switch to (dark|light) mode/i)).toBeInTheDocument();
  });

  it('renders settings button', () => {
    renderWithAllProviders(<TopNavigation {...defaultProps} />);
    expect(screen.getByLabelText('Settings')).toBeInTheDocument();
  });

  it('calls onSettingsClick when settings button is clicked', async () => {
    const user = userEvent.setup();
    const mockSettingsClick = vi.fn();
    
    renderWithAllProviders(
      <TopNavigation {...defaultProps} onSettingsClick={mockSettingsClick} />
    );
    
    await user.click(screen.getByLabelText('Settings'));
    await user.click(screen.getByText('Settings'));
    expect(mockSettingsClick).toHaveBeenCalled();
  });

  it('shows beta label', () => {
    renderWithAllProviders(<TopNavigation {...defaultProps} />);
    expect(screen.getByText('Beta')).toBeInTheDocument();
  });
});