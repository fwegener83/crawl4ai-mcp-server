import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { vi } from 'vitest';
import { ThemeProvider } from '../../../contexts/ThemeContext';
import { NotificationProvider } from '../../ui/NotificationProvider';
import { ContentViewerDialog } from '../ContentViewerDialog';
import type { ContentViewerDialogProps, ContentItem } from '../ContentViewerDialog';

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider>
    <NotificationProvider>
      {children}
    </NotificationProvider>
  </ThemeProvider>
);

const mockContent: ContentItem = {
  id: 'test-content-1',
  name: 'test-document.md',
  content: '# Test Document\n\nThis is a test markdown document with some content.',
  type: 'markdown',
  size: 1024,
  createdAt: new Date('2024-01-01'),
  modifiedAt: new Date('2024-01-15'),
  metadata: {
    sourceUrl: 'https://example.com/test',
    description: 'A test document for testing purposes',
    tags: ['test', 'markdown', 'example'],
  },
};

const defaultProps: ContentViewerDialogProps = {
  open: true,
  content: mockContent,
  onClose: vi.fn(),
};

describe('ContentViewerDialog', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders with content', () => {
    render(
      <TestWrapper>
        <ContentViewerDialog {...defaultProps} />
      </TestWrapper>
    );

    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText('test-document.md')).toBeInTheDocument();
    expect(screen.getByText('A test document for testing purposes')).toBeInTheDocument();
    expect(screen.getByText('Source: https://example.com/test')).toBeInTheDocument();
    expect(screen.getByText('1 KB')).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    render(
      <TestWrapper>
        <ContentViewerDialog {...defaultProps} open={false} />
      </TestWrapper>
    );

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('renders without content', () => {
    render(
      <TestWrapper>
        <ContentViewerDialog {...defaultProps} content={null} />
      </TestWrapper>
    );

    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText('Content Viewer')).toBeInTheDocument();
  });

  it('displays tags as chips', () => {
    render(
      <TestWrapper>
        <ContentViewerDialog {...defaultProps} />
      </TestWrapper>
    );

    expect(screen.getByText('test')).toBeInTheDocument();
    expect(screen.getByText('markdown')).toBeInTheDocument();
    expect(screen.getByText('example')).toBeInTheDocument();
  });

  it('formats file size correctly', () => {
    const largeContent = {
      ...mockContent,
      size: 2048576, // 2MB
    };

    render(
      <TestWrapper>
        <ContentViewerDialog {...defaultProps} content={largeContent} />
      </TestWrapper>
    );

    expect(screen.getByText('2 MB')).toBeInTheDocument();
  });

  it('calls onClose when close button is clicked', () => {
    const onClose = vi.fn();
    render(
      <TestWrapper>
        <ContentViewerDialog {...defaultProps} onClose={onClose} />
      </TestWrapper>
    );

    fireEvent.click(screen.getByRole('button', { name: /close/i }));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('calls onEdit when edit button is clicked', () => {
    const onEdit = vi.fn();
    render(
      <TestWrapper>
        <ContentViewerDialog {...defaultProps} onEdit={onEdit} />
      </TestWrapper>
    );

    fireEvent.click(screen.getByRole('button', { name: /edit/i }));
    expect(onEdit).toHaveBeenCalledWith('test-content-1');
  });

  it('calls onDownload when download button is clicked', () => {
    const onDownload = vi.fn();
    render(
      <TestWrapper>
        <ContentViewerDialog {...defaultProps} onDownload={onDownload} />
      </TestWrapper>
    );

    fireEvent.click(screen.getByRole('button', { name: /download/i }));
    expect(onDownload).toHaveBeenCalledWith('test-content-1');
  });

  it('does not show edit/download buttons when callbacks not provided', () => {
    render(
      <TestWrapper>
        <ContentViewerDialog {...defaultProps} onEdit={undefined} onDownload={undefined} />
      </TestWrapper>
    );

    expect(screen.queryByRole('button', { name: /edit/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /download/i })).not.toBeInTheDocument();
  });

  it('switches between preview and raw content tabs', () => {
    render(
      <TestWrapper>
        <ContentViewerDialog {...defaultProps} />
      </TestWrapper>
    );

    // Should start on preview tab
    expect(screen.getByRole('tab', { name: /preview/i })).toHaveAttribute('aria-selected', 'true');
    expect(screen.getByRole('tab', { name: /raw content/i })).toHaveAttribute('aria-selected', 'false');

    // Switch to raw content tab
    fireEvent.click(screen.getByRole('tab', { name: /raw content/i }));
    
    expect(screen.getByRole('tab', { name: /preview/i })).toHaveAttribute('aria-selected', 'false');
    expect(screen.getByRole('tab', { name: /raw content/i })).toHaveAttribute('aria-selected', 'true');
  });

  it('displays content in both preview and raw tabs', () => {
    render(
      <TestWrapper>
        <ContentViewerDialog {...defaultProps} />
      </TestWrapper>
    );

    // Content should be visible in preview tab
    expect(screen.getByText(/This is a test markdown document/)).toBeInTheDocument();

    // Switch to raw content tab
    fireEvent.click(screen.getByRole('tab', { name: /raw content/i }));
    
    // Raw content should include markdown syntax
    expect(screen.getByText(/# Test Document/)).toBeInTheDocument();
  });

  it('handles content without metadata', () => {
    const contentWithoutMetadata = {
      ...mockContent,
      metadata: undefined,
    };

    render(
      <TestWrapper>
        <ContentViewerDialog {...defaultProps} content={contentWithoutMetadata} />
      </TestWrapper>
    );

    expect(screen.queryByText(/source:/i)).not.toBeInTheDocument();
    expect(screen.queryByText('test')).not.toBeInTheDocument();
  });

  it('handles code files correctly', () => {
    const codeContent = {
      ...mockContent,
      name: 'test.js',
      type: 'code',
      content: 'console.log("Hello World");',
    };

    render(
      <TestWrapper>
        <ContentViewerDialog {...defaultProps} content={codeContent} />
      </TestWrapper>
    );

    expect(screen.getByText('test.js')).toBeInTheDocument();
    expect(screen.getByText('console.log("Hello World");')).toBeInTheDocument();
  });

  it('handles zero byte files', () => {
    const emptyContent = {
      ...mockContent,
      size: 0,
    };

    render(
      <TestWrapper>
        <ContentViewerDialog {...defaultProps} content={emptyContent} />
      </TestWrapper>
    );

    expect(screen.getByText('0 Bytes')).toBeInTheDocument();
  });

  it('truncates long filenames', () => {
    const longNameContent = {
      ...mockContent,
      name: 'this-is-a-very-long-filename-that-should-be-truncated-properly.md',
    };

    render(
      <TestWrapper>
        <ContentViewerDialog {...defaultProps} content={longNameContent} />
      </TestWrapper>
    );

    // The filename should be present but may be truncated with CSS
    expect(screen.getByText(/this-is-a-very-long-filename/)).toBeInTheDocument();
  });

  it('has proper accessibility attributes', () => {
    render(
      <TestWrapper>
        <ContentViewerDialog {...defaultProps} />
      </TestWrapper>
    );

    const dialog = screen.getByRole('dialog');
    expect(dialog).toHaveAttribute('aria-labelledby', 'content-viewer-dialog-title');
    
    expect(screen.getByRole('heading')).toHaveAttribute('id', 'content-viewer-dialog-title');
  });
});