import { test, expect } from '@playwright/test';

test.describe('Simple Collections Test', () => {
  test('File Collections laden korrekt', async ({ page }) => {
    // Navigate to the app
    await page.goto('http://localhost:5173/');
    
    // Wait for the app to load
    await page.waitForLoadState('networkidle');
    
    console.log('App geladen, suche nach File Collections Tab...');
    
    // Click on File Collections tab
    await page.click('[data-testid="file-collections-tab"]');
    
    // Wait for collections to load
    await page.waitForSelector('[data-testid="collections-list"]', { timeout: 10000 });
    
    // Check if we have collections now (should be > 15 from our tests)
    const allCollectionItems = page.locator('[data-testid="collection-item"]');
    const collectionCount = await allCollectionItems.count();
    console.log(`Anzahl Collections im DOM nach Fix: ${collectionCount}`);
    
    // Should have many collections now
    expect(collectionCount).toBeGreaterThan(15);
    
    console.log('✅ SUCCESS: Collections werden korrekt geladen!');
  });
});