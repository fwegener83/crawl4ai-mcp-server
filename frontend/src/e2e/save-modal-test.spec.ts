import { test, expect } from '@playwright/test';

test('Save to Collection Modal Test', async ({ page }) => {
  // Navigate to Simple Crawl page
  await page.goto('http://localhost:5173/');
  await page.waitForLoadState('networkidle');
  
  // Go to Simple Crawl
  await page.click('[data-testid="simple-crawl-tab"]');
  await page.waitForSelector('[data-testid="url-input"]');
  
  // Enter some URL and crawl
  await page.fill('[data-testid="url-input"]', 'https://httpbin.org/html');
  await page.click('[data-testid="crawl-button"]');
  
  // Wait a moment for crawl to complete
  await page.waitForTimeout(8000);
  
  // Look for the Save to Collection button (should be enabled after crawl)
  const saveButton = page.locator('[data-testid="save-to-collection-button"]');
  await expect(saveButton).toBeVisible();
  
  // Click it to open the modal
  await saveButton.click();
  
  // Wait for modal to appear
  await page.waitForSelector('[data-testid="collection-select"]', { timeout: 10000 });
  console.log('✅ Save to Collection Modal opened successfully!');
  
  // Check that collections are loaded in the dropdown
  await page.click('[data-testid="collection-select"]');
  
  // Wait for options to appear
  await page.waitForTimeout(2000);
  
  // Look for any collection option
  const options = page.locator('[role="option"]');
  const optionCount = await options.count();
  console.log(`Found ${optionCount} collection options`);
  
  expect(optionCount).toBeGreaterThan(0);
  
  console.log('✅ Collections loaded in dropdown successfully!');
});