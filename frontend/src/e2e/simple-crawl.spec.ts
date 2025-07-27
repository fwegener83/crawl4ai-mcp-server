import { test, expect } from '@playwright/test';

test.describe('Simple Website Crawling Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should complete simple crawl workflow with real API', async ({ page }) => {
    // Navigate to Simple Crawl page
    await page.click('text=Simple Crawl');
    // SPA - check page content instead of URL
    
    // Verify page content
    await expect(page.locator('h1')).toContainText('Simple Website Crawling');
    await expect(page.locator('text=Extract clean content from any webpage')).toBeVisible();

    // Test URL input validation
    const urlInput = page.getByTestId('url-input');
    const crawlButton = page.getByTestId('crawl-button');
    
    // Should show validation error for invalid URL
    await urlInput.fill('invalid-url');
    await expect(page.locator('text=Please enter a valid URL')).toBeVisible();
    await expect(crawlButton).toBeDisabled();
    
    // Should accept valid URL
    await urlInput.fill('https://example.com');
    await expect(page.locator('text=Please enter a valid URL')).not.toBeVisible();
    await expect(crawlButton).toBeEnabled();

    // Start crawl with real API call (no mocking)
    await crawlButton.click();
    
    // Should show loading state
    await expect(page.locator('text=Crawling...')).toBeVisible();
    
    // Wait for the crawl to complete (increase timeout for real API calls)
    await page.waitForSelector('text=Content Extracted', { timeout: 30000 });
    
    // Should show success message
    await expect(page.locator('text=Content Extracted')).toBeVisible();
    await expect(page.locator('text=Website content has been successfully crawled')).toBeVisible();
    
    // Should show extracted content
    await expect(page.locator('h2:has-text("Extracted Content")')).toBeVisible();
    
    // Should show save button
    const saveButton = page.locator('button:has-text("Save to Collection")');
    await expect(saveButton).toBeVisible();
    await expect(saveButton).toBeEnabled();

    // Test content editing
    const editor = page.locator('.monaco-editor');
    await expect(editor).toBeVisible();
    
    // Click save button to open modal
    await saveButton.click();
    
    // Should open save modal
    await expect(page.locator('h3').filter({ hasText: 'Save to Collection' })).toBeVisible();
    await expect(page.locator('text=Select Collection')).toBeVisible();
  });

  test('should complete simple crawl workflow', async ({ page }) => {
    // Navigate to Simple Crawl page
    await page.click('text=Simple Crawl');
    
    // Verify page content (no URL change in SPA)
    await expect(page.locator('h1')).toContainText('Simple Website Crawling');
    await expect(page.locator('p').filter({ hasText: 'Extract clean content from any webpage and edit' })).toBeVisible();

    // Test URL input validation
    const urlInput = page.getByTestId('url-input');
    const crawlButton = page.getByTestId('crawl-button');
    
    // Should show validation error for invalid URL
    await urlInput.fill('invalid-url');
    await expect(page.locator('text=Please enter a valid URL')).toBeVisible();
    await expect(crawlButton).toBeDisabled();
    
    // Should accept valid URL
    await urlInput.fill('https://example.com');
    await expect(page.locator('text=Please enter a valid URL')).not.toBeVisible();
    await expect(crawlButton).toBeEnabled();

    // Mock API response for successful crawl
    await page.route('/api/extract', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          content: '# Example Website\n\nThis is example content from the crawled website.\n\n## Features\n- Clean content extraction\n- Markdown formatting\n- Easy to read'
        })
      });
    });

    // Start crawl
    await crawlButton.click();
    
    // Should show loading state
    await expect(page.locator('text=Crawling...')).toBeVisible();
    
    // Should show success message
    await expect(page.locator('text=Content Extracted')).toBeVisible();
    await expect(page.locator('text=Website content has been successfully crawled')).toBeVisible();
    
    // Should show extracted content
    await expect(page.locator('h2:has-text("Extracted Content")')).toBeVisible();
    await expect(page.locator('text=Example Website')).toBeVisible();
    
    // Should show save button
    const saveButton = page.locator('button:has-text("Save to Collection")');
    await expect(saveButton).toBeVisible();
    await expect(saveButton).toBeEnabled();

    // Test content editing
    const editor = page.locator('.monaco-editor');
    await expect(editor).toBeVisible();
    
    // Click save button to open modal
    await saveButton.click();
    
    // Should open save modal
    await expect(page.locator('h3').filter({ hasText: 'Save to Collection' })).toBeVisible();
    await expect(page.locator('text=Select Collection')).toBeVisible();
  });

  test('should handle crawl errors gracefully with real API', async ({ page }) => {
    await page.click('text=Simple Website Crawling');
    
    const urlInput = page.getByTestId('url-input');
    const crawlButton = page.getByTestId('crawl-button');
    
    // Use a URL that's likely to fail or be inaccessible
    await urlInput.fill('https://this-domain-definitely-does-not-exist-12345.com');
    
    await crawlButton.click();
    
    // Should show loading state
    await expect(page.locator('text=Crawling...')).toBeVisible();
    
    // Wait for error to appear (with increased timeout for real API)
    await page.waitForSelector('text=Crawl Failed', { timeout: 30000 });
    
    // Should show error message
    await expect(page.locator('text=Crawl Failed')).toBeVisible();
  });

  test('should handle crawl errors gracefully', async ({ page }) => {
    await page.click('text=Simple Website Crawling');
    
    const urlInput = page.getByTestId('url-input');
    const crawlButton = page.getByTestId('crawl-button');
    
    await urlInput.fill('https://nonexistent-website.com');
    
    // Mock API error response
    await page.route('/api/extract', async route => {
      await route.fulfill({
        status: 404,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Website not found or inaccessible'
        })
      });
    });

    await crawlButton.click();
    
    // Should show error message
    await expect(page.locator('text=Crawl Failed')).toBeVisible();
    await expect(page.locator('text=Website not found or inaccessible')).toBeVisible();
  });

  test('should navigate back to home', async ({ page }) => {
    await page.click('text=Simple Website Crawling');
    
    // Click home navigation
    await page.click('text=Home');
    await expect(page).toHaveURL('/');
    await expect(page.locator('h1:has-text("Web Crawling & RAG Platform")')).toBeVisible();
  });
});