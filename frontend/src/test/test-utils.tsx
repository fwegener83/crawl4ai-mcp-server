import React from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { vi } from 'vitest';
import type { ReactElement } from 'react';

// Mock Toast components and hooks
vi.mock('../components/ToastContainer', () => ({
  useToast: () => ({
    showToast: vi.fn(),
    hideToast: vi.fn(),
  }),
  ToastProvider: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="mock-toast-provider">{children}</div>
  ),
}));

const MockToastProvider = ({ children }: { children: React.ReactNode }) => {
  return <div data-testid="mock-toast-provider">{children}</div>;
};

// Custom render function with common providers
const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => {
  const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
    return (
      <MockToastProvider>
        {children}
      </MockToastProvider>
    );
  };

  return render(ui, { wrapper: AllTheProviders, ...options });
};

// Mock API responses for common test scenarios
export const mockAPIResponses = {
  successfulCrawl: {
    content: '# Test Page\n\nThis is test content from a crawled website.'
  },
  
  collections: [
    {
      name: 'default',
      document_count: 5,
      created_at: '2024-01-01T00:00:00Z',
      last_updated: '2024-01-02T00:00:00Z'
    },
    {
      name: 'test-collection',
      document_count: 3,
      created_at: '2024-01-01T00:00:00Z',
      last_updated: '2024-01-01T12:00:00Z'
    }
  ],

  searchResults: [
    {
      id: '1',
      content: 'This is a test search result',
      metadata: { source: 'https://example.com', title: 'Test Page' },
      score: 0.95
    }
  ],

  deepCrawlResults: [
    {
      url: 'https://example.com',
      title: 'Example Homepage',
      content: '# Welcome\n\nThis is the homepage.',
      links: ['https://example.com/about'],
      success: true,
      timestamp: '2024-01-01T00:00:00Z'
    }
  ]
};

// Common test scenarios for modals
export const modalTestHelpers = {
  // Wait for modal to appear
  waitForModal: async (getByTestId: any, modalTestId: string) => {
    const modal = await getByTestId(modalTestId);
    expect(modal).toBeInTheDocument();
    return modal;
  },

  // Check if modal is properly positioned
  checkModalPosition: (modal: HTMLElement) => {
    const styles = window.getComputedStyle(modal);
    expect(styles.position).toBe('fixed');
    expect(styles.zIndex).toBeTruthy();
  },

  // Mock escape key press
  mockEscapeKeyPress: () => {
    const escapeEvent = new KeyboardEvent('keydown', {
      key: 'Escape',
      code: 'Escape',
      keyCode: 27,
      which: 27,
      bubbles: true,
    });
    document.dispatchEvent(escapeEvent);
  },

  // Mock click outside modal
  mockClickOutside: (modal: HTMLElement) => {
    const backdrop = modal.closest('[data-testid*="backdrop"]') || document.body;
    backdrop.click();
  }
};

// Common assertions for form validation
export const formValidationHelpers = {
  expectValidationError: (container: HTMLElement, message: string) => {
    const error = container.querySelector('.text-red-500, .error-message, [role="alert"]');
    expect(error).toBeInTheDocument();
    expect(error).toHaveTextContent(message);
  },

  expectNoValidationError: (container: HTMLElement) => {
    const error = container.querySelector('.text-red-500, .error-message, [role="alert"]');
    expect(error).not.toBeInTheDocument();
  },

  expectFieldDisabled: (field: HTMLElement) => {
    expect(field).toBeDisabled();
  },

  expectFieldEnabled: (field: HTMLElement) => {
    expect(field).toBeEnabled();
  }
};

// Create mock functions for common hooks
export const createMockApiHook = (initialState = {}) => {
  return {
    data: undefined,
    error: undefined,
    loading: false,
    execute: vi.fn(),
    reset: vi.fn(),
    ...initialState
  };
};

export const createMockCollectionsHook = (initialState = {}) => {
  return {
    collections: mockAPIResponses.collections,
    selectedCollection: 'default',
    setSelectedCollection: vi.fn(),
    listLoading: false,
    deleteLoading: false,
    storeLoading: false,
    searchLoading: false,
    listError: undefined,
    deleteError: undefined,
    storeError: undefined,
    searchError: undefined,
    refreshCollections: vi.fn(),
    deleteCollection: vi.fn(),
    storeContent: vi.fn(),
    searchInCollection: vi.fn(),
    searchResults: undefined,
    ...initialState
  };
};

// Portal testing helper - creates a container for portal elements
export const createPortalContainer = () => {
  const portalRoot = document.createElement('div');
  portalRoot.setAttribute('id', 'portal-root');
  document.body.appendChild(portalRoot);
  
  return () => {
    document.body.removeChild(portalRoot);
  };
};

// Re-export everything from testing-library
export * from '@testing-library/react';
export { customRender as render };