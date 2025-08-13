import { test, expect } from '@playwright/test';

test.describe('File Manager - Add Page Feature', () => {
  test('Add Page to Collection IM File Manager', async ({ page }) => {
    console.log('🎯 SCHRITT 1: Navigate to File Collections...');
    
    // Navigate to the File Collections page
    await page.goto('http://localhost:5173/');
    await page.waitForLoadState('networkidle');
    
    // Go to File Collections tab
    await page.waitForSelector('[data-testid="collections-list"]', { timeout: 10000 });
    
    // Check that collections are loaded
    const collections = page.locator('[data-testid="collection-item"]');
    const collectionCount = await collections.count();
    console.log(`Found ${collectionCount} collections in File Manager`);
    expect(collectionCount).toBeGreaterThan(0);
    
    console.log('🎯 SCHRITT 2: Select a collection...');
    
    // Click on the first collection to select it
    await collections.first().click();
    console.log('✅ Collection selected');
    
    // Wait for collection details to load
    await page.waitForSelector('[data-testid="collection-details"]', { timeout: 5000 });
    
    console.log('🎯 SCHRITT 3: Click Add Page button IM File Manager...');
    
    // Look for the "Add Page" button in the File Manager
    await page.waitForSelector('[data-testid="add-page-btn"]', { timeout: 5000 });
    await page.click('[data-testid="add-page-btn"]');
    console.log('✅ Add Page button clicked');
    
    console.log('🎯 SCHRITT 4: Fill Add Page modal...');
    
    // Wait for the Add Page modal to open
    await page.waitForSelector('[data-testid="add-page-url-input"]', { timeout: 5000 });
    console.log('✅ Add Page Modal opened');
    
    // Enter a URL to crawl
    const testUrl = 'https://httpbin.org/html';
    await page.fill('[data-testid="add-page-url-input"]', testUrl);
    console.log(`✅ Entered URL: ${testUrl}`);
    
    console.log('🎯 SCHRITT 5: Submit Add Page request...');
    
    // Monitor API response for crawl completion
    let crawlCompleted = false;
    page.on('response', async response => {
      if (response.url().includes('/api/crawl/single/') && response.request().method() === 'POST') {
        if (response.status() === 200) {
          const data = await response.json();
          crawlCompleted = data.success === true;
          console.log('CRAWL Response:', data);
        }
      }
    });
    
    // Click Add Page submit button
    const submitButton = page.locator('[data-testid="add-page-submit"]');
    await expect(submitButton).toBeEnabled();
    await submitButton.click();
    console.log('✅ Add Page submitted');
    
    console.log('🎯 SCHRITT 6: Wait for crawl completion...');
    
    // Wait for crawl to complete
    await page.waitForFunction(() => {
      return window.crawlCompleted === true;
    }, { timeout: 30000 });
    
    // Set crawl completion status in browser context  
    await page.evaluate((completed) => { window.crawlCompleted = completed; }, crawlCompleted);
    
    console.log('✅ Page crawled and added to collection successfully!');
    
    // Verify modal closes after success
    await page.waitForTimeout(2000);
    const modalStillOpen = await page.locator('[data-testid="add-page-url-input"]').isVisible();
    expect(modalStillOpen).toBeFalsy();
    console.log('✅ Add Page Modal closed after success');
    
    console.log('🎉 SUCCESS: Add Page IM File Manager works perfectly!');
  });
});