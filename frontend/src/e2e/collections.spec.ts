import { test, expect } from '@playwright/test';

test.describe('Collections Management Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should complete collections management workflow', async ({ page }) => {
    // Navigate to Collections page
    await page.click('text=Collections');
    // SPA - check page content instead of URL
    
    // Verify page content
    await expect(page.locator('h1')).toContainText('RAG Collections');
    await expect(page.locator('text=Manage your knowledge base collections')).toBeVisible();

    // Mock API response for listing collections
    await page.route('/api/collections', async route => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            collections: [
              {
                name: 'default',
                document_count: 5,
                created_at: '2024-01-01T00:00:00Z',
                last_updated: '2024-01-02T00:00:00Z'
              },
              {
                name: 'research',
                document_count: 12,
                created_at: '2024-01-01T00:00:00Z',
                last_updated: '2024-01-03T00:00:00Z'
              }
            ]
          })
        });
      }
    });

    // Should show loading state first
    await expect(page.locator('text=Loading collections...')).toBeVisible();
    
    // Should show collections list
    await expect(page.locator('text=default')).toBeVisible();
    await expect(page.locator('text=research')).toBeVisible();
    await expect(page.locator('text=5 documents')).toBeVisible();
    await expect(page.locator('text=12 documents')).toBeVisible();

    // Test search functionality
    const searchInput = page.locator('input[placeholder*="Search collections"]');
    const searchButton = page.locator('button:has-text("Search")');
    
    await searchInput.fill('test query');
    
    // Mock search API
    await page.route('/api/search*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          results: [
            {
              id: '1',
              content: 'This is a matching document for the test query.',
              metadata: { source: 'https://example.com', title: 'Example Page' },
              score: 0.92
            },
            {
              id: '2',
              content: 'Another relevant document with test information.',
              metadata: { source: 'https://test.com', title: 'Test Documentation' },
              score: 0.87
            }
          ]
        })
      });
    });

    await searchButton.click();
    
    // Should show search results
    await expect(page.locator('h3:has-text("Search Results")')).toBeVisible();
    await expect(page.locator('text=2 results found')).toBeVisible();
    
    // Should show individual results with scores
    await expect(page.locator('text=Score: 0.92')).toBeVisible();
    await expect(page.locator('text=Score: 0.87')).toBeVisible();
    
    // Should show result content
    await expect(page.locator('text=This is a matching document')).toBeVisible();
    await expect(page.locator('text=Another relevant document')).toBeVisible();
    
    // Should show metadata
    await expect(page.locator('text=Source: https://example.com')).toBeVisible();
    await expect(page.locator('text=Example Page')).toBeVisible();
  });

  test('should handle collection creation workflow', async ({ page }) => {
    await page.click('text=Collections');
    
    // Mock initial empty collections
    await page.route('/api/collections', async route => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ collections: [] })
        });
      }
    });

    // Should show empty state
    await expect(page.locator('text=No collections found')).toBeVisible();
    await expect(page.locator('text=Create your first collection by crawling content')).toBeVisible();

    // Click create collection button
    const createButton = page.locator('button:has-text("Create Collection")');
    await createButton.click();
    
    // Should open create modal
    await expect(page.locator('text=Create New Collection')).toBeVisible();
    
    const nameInput = page.locator('input[placeholder*="collection name"]');
    await nameInput.fill('my-new-collection');
    
    // Mock collection creation
    await page.route('/api/collections', async route => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            collection_name: 'my-new-collection',
            documents_added: 0,
            message: 'Collection created successfully'
          })
        });
      }
    });

    const confirmButton = page.locator('button:has-text("Create")');
    await confirmButton.click();
    
    // Should show success message
    await expect(page.locator('text=Collection Created')).toBeVisible();
    await expect(page.locator('text=Successfully created my-new-collection')).toBeVisible();
  });

  test('should handle collection deletion', async ({ page }) => {
    await page.click('text=Collections');
    
    // Mock collections with delete option
    await page.route('/api/collections', async route => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            collections: [
              {
                name: 'test-collection',
                document_count: 3,
                created_at: '2024-01-01T00:00:00Z',
                last_updated: '2024-01-02T00:00:00Z'
              }
            ]
          })
        });
      }
    });

    // Find and click delete button
    const deleteButton = page.locator('button:has-text("Delete")').first();
    await deleteButton.click();
    
    // Should show confirmation modal
    await expect(page.locator('text=Delete Collection')).toBeVisible();
    await expect(page.locator('text=Are you sure you want to delete "test-collection"?')).toBeVisible();
    
    // Mock deletion API
    await page.route('/api/collections/test-collection', async route => {
      if (route.request().method() === 'DELETE') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            collection_name: 'test-collection',
            message: 'Collection deleted successfully'
          })
        });
      }
    });

    const confirmDeleteButton = page.locator('button:has-text("Delete Collection")');
    await confirmDeleteButton.click();
    
    // Should show success message
    await expect(page.locator('text=Collection Deleted')).toBeVisible();
    await expect(page.locator('text=Successfully deleted test-collection')).toBeVisible();
  });

  test('should handle search with no results', async ({ page }) => {
    await page.click('text=Collections');
    
    // Mock collections
    await page.route('/api/collections', async route => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            collections: [{ name: 'default', document_count: 0, created_at: '', last_updated: '' }]
          })
        });
      }
    });

    const searchInput = page.locator('input[placeholder*="Search collections"]');
    const searchButton = page.locator('button:has-text("Search")');
    
    await searchInput.fill('nonexistent query');
    
    // Mock empty search results
    await page.route('/api/search*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ results: [] })
      });
    });

    await searchButton.click();
    
    // Should show no results message
    await expect(page.locator('text=No results found')).toBeVisible();
    await expect(page.locator('text=Try different search terms')).toBeVisible();
  });

  test('should handle API errors gracefully', async ({ page }) => {
    await page.click('text=Collections');
    
    // Mock API error
    await page.route('/api/collections', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Internal server error'
        })
      });
    });

    // Should show error message
    await expect(page.locator('text=Failed to Load Collections')).toBeVisible();
    await expect(page.locator('text=Internal server error')).toBeVisible();
    
    // Should show retry button
    const retryButton = page.locator('button:has-text("Retry")');
    await expect(retryButton).toBeVisible();
  });
});