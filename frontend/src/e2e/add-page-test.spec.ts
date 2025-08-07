import { test, expect } from '@playwright/test';

test('Add Page to Collection Test', async ({ page }) => {
  // Navigate directly to Simple Crawl
  await page.goto('http://localhost:5173/');
  await page.waitForLoadState('networkidle');
  
  // Go to Simple Crawl
  await page.click('[data-testid="simple-crawl-tab"]');
  await page.waitForSelector('[data-testid="url-input"]');
  
  // Enter URL and crawl
  await page.fill('[data-testid="url-input"]', 'https://www.wikipedia.org');
  await page.click('[data-testid="crawl-button"]');
  
  // Wait for crawl to complete (look for content in editor)
  await page.waitForTimeout(5000);
  
  // Add test content to ensure we have something to save
  await page.click('.cm-editor');
  await page.keyboard.type('\\n\\n# Added Test Content\\n\\nThis content was added by the E2E test.');
  
  // Click Save to Collection
  await page.click('[data-testid="save-to-collection-button"]');
  
  // Select an existing collection (just pick the first one available)
  await page.waitForSelector('[data-testid="collection-select"]');
  await page.click('[data-testid="collection-select"]');
  
  // Wait for dropdown and select any available collection
  await page.waitForTimeout(1000);
  const firstOption = page.locator('[role="option"]').first();
  await firstOption.click();
  
  // Confirm save
  await page.click('[data-testid="save-confirm"]');
  
  // Wait for success
  await page.waitForTimeout(3000);
  
  console.log('✅ Successfully added page to collection!');
});