import { test, expect } from '@playwright/test';

test.describe('Deep Website Crawling Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should complete deep crawl workflow', async ({ page }) => {
    // Navigate to Deep Crawl page
    await page.click('text=Deep Crawl');
    // SPA - check page content instead of URL
    
    // Verify page content
    await expect(page.locator('h1')).toContainText('Deep Website Crawling');
    await expect(page.locator('text=Crawl entire domains with advanced strategies')).toBeVisible();

    // Test URL input
    const urlInput = page.locator('input[placeholder*="https://example.com"]');
    await urlInput.fill('https://example.com');

    // Test crawl strategy selection
    const strategySelect = page.locator('select').first();
    await strategySelect.selectOption('dfs');
    
    // Test max depth configuration
    const depthInput = page.locator('input[type="number"]').first();
    await depthInput.fill('3');
    
    // Test max pages configuration
    const pagesInput = page.locator('input[type="number"]').nth(1);
    await pagesInput.fill('20');

    // Test external links checkbox
    const externalLinksCheckbox = page.locator('input[type="checkbox"]').first();
    await externalLinksCheckbox.check();

    // Mock API response for successful deep crawl
    await page.route('/api/deep-crawl', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          results: [
            {
              url: 'https://example.com',
              title: 'Example Homepage',
              content: '# Welcome to Example\n\nThis is the homepage content.',
              links: ['https://example.com/about', 'https://example.com/contact'],
              success: true,
              timestamp: new Date().toISOString()
            },
            {
              url: 'https://example.com/about',
              title: 'About Us',
              content: '# About Example\n\nLearn more about our company.',
              links: ['https://example.com/team'],
              success: true,
              timestamp: new Date().toISOString()
            }
          ]
        })
      });
    });

    // Start deep crawl
    const startButton = page.locator('button:has-text("Start Deep Crawl")');
    await expect(startButton).toBeEnabled();
    await startButton.click();
    
    // Should show loading state
    await expect(page.locator('text=Crawling...')).toBeVisible();
    
    // Should show success message
    await expect(page.locator('text=Deep Crawl Complete')).toBeVisible();
    
    // Should show crawl results
    await expect(page.locator('h2:has-text("Crawl Results")')).toBeVisible();
    await expect(page.locator('text=2 pages crawled successfully')).toBeVisible();
    
    // Should show individual results
    await expect(page.locator('text=Example Homepage')).toBeVisible();
    await expect(page.locator('text=About Us')).toBeVisible();
    
    // Should show save all button
    const saveAllButton = page.locator('button:has-text("Save All to Collection")');
    await expect(saveAllButton).toBeVisible();
    await expect(saveAllButton).toBeEnabled();

    // Test individual result interaction
    const firstResult = page.locator('[data-testid="crawl-result"]').first();
    await expect(firstResult).toBeVisible();
    
    // Should show result details
    await expect(firstResult.locator('text=https://example.com')).toBeVisible();
    await expect(firstResult.locator('text=Welcome to Example')).toBeVisible();
  });

  test('should handle link preview functionality', async ({ page }) => {
    await page.click('text=Deep Website Crawling');
    
    const urlInput = page.locator('input[placeholder*="https://example.com"]');
    await urlInput.fill('https://example.com');

    // Mock link preview API
    await page.route('/api/link-preview', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          domain: 'example.com',
          total_links: 15,
          internal_links: 12,
          external_links: 3,
          links: [
            { url: 'https://example.com/home', title: 'Home', is_external: false },
            { url: 'https://example.com/about', title: 'About', is_external: false },
            { url: 'https://google.com', title: 'Google', is_external: true }
          ]
        })
      });
    });

    // Click preview links button
    const previewButton = page.locator('button:has-text("Preview Links")');
    await previewButton.click();
    
    // Should show loading state
    await expect(page.locator('text=Loading preview...')).toBeVisible();
    
    // Should show preview results
    await expect(page.locator('text=Found 15 links')).toBeVisible();
    await expect(page.locator('text=12 internal')).toBeVisible();
    await expect(page.locator('text=3 external')).toBeVisible();
    
    // Should show link list
    await expect(page.locator('text=Home')).toBeVisible();
    await expect(page.locator('text=About')).toBeVisible();
  });

  test('should validate configuration inputs', async ({ page }) => {
    await page.click('text=Deep Website Crawling');
    
    // Test invalid URL
    const urlInput = page.locator('input[placeholder*="https://example.com"]');
    await urlInput.fill('invalid-url');
    
    const startButton = page.locator('button:has-text("Start Deep Crawl")');
    await expect(startButton).toBeDisabled();
    
    // Test valid URL
    await urlInput.fill('https://example.com');
    await expect(startButton).toBeEnabled();
    
    // Test max depth bounds
    const depthInput = page.locator('input[type="number"]').first();
    await depthInput.fill('15'); // Above max of 10
    await expect(page.locator('text=Maximum depth is 10')).toBeVisible();
    
    await depthInput.fill('5');
    await expect(page.locator('text=Maximum depth is 10')).not.toBeVisible();
    
    // Test max pages bounds
    const pagesInput = page.locator('input[type="number"]').nth(1);
    await pagesInput.fill('1500'); // Above max of 1000
    await expect(page.locator('text=Maximum pages is 1000')).toBeVisible();
    
    await pagesInput.fill('50');
    await expect(page.locator('text=Maximum pages is 1000')).not.toBeVisible();
  });
});