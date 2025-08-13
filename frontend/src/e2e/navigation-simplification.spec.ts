import { test, expect } from '@playwright/test';

test.describe('Navigation Simplification', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    // Wait for the app to be ready
    await page.waitForSelector('[data-testid="file-collections-page"]', { timeout: 10000 });
  });

  test('should only show File Collections tab in navigation', async ({ page }) => {
    // Check that only File Collections tab exists in navigation
    const tabs = page.locator('div[role="tablist"] .MuiTab-root');
    await expect(tabs).toHaveCount(1);
    
    // Verify the File Collections tab is present and active
    const fileCollectionsTab = page.locator('[data-testid="file-collections-tab"]');
    await expect(fileCollectionsTab).toBeVisible();
    await expect(fileCollectionsTab).toHaveAttribute('aria-selected', 'true');
  });

  test('should not show obsolete navigation tabs', async ({ page }) => {
    // These tabs should no longer exist
    const obsoleteTabs = [
      '[data-testid="home-tab"]',
      '[data-testid="simple-crawl-tab"]', 
      '[data-testid="deep-crawl-tab"]',
      '[data-testid="collections-tab"]',
      '[data-testid="settings-tab"]'
    ];

    for (const tabSelector of obsoleteTabs) {
      await expect(page.locator(tabSelector)).toHaveCount(0);
    }
  });

  test('should show File Collections page as default', async ({ page }) => {
    // The page should load directly to File Collections
    await expect(page.locator('[data-testid="file-collections-page"]')).toBeVisible();
    
    // Check for main components of File Collections page
    await expect(page.locator('text=Welcome to Crawl4AI File Manager')).toBeVisible();
  });

  test('should open Settings modal when Settings button is clicked', async ({ page }) => {
    // Find and click the Settings button in the top navigation
    const settingsButton = page.locator('button[title="Settings"]').first();
    await expect(settingsButton).toBeVisible();
    await settingsButton.click();
    
    // Wait for settings dropdown menu
    await page.waitForSelector('div[role="menu"]', { timeout: 5000 });
    
    // Click Settings menu item
    const settingsMenuItem = page.locator('div[role="menu"] >> text=Settings').first();
    await expect(settingsMenuItem).toBeVisible();
    await settingsMenuItem.click();
    
    // Verify Settings modal opens
    const settingsModal = page.locator('[role="dialog"] >> text=Settings').first();
    await expect(settingsModal).toBeVisible({ timeout: 5000 });
    
    // Verify modal contains expected content
    await expect(page.locator('[role="dialog"] >> text=Configure Crawl4AI application preferences')).toBeVisible();
  });

  test('should close Settings modal when close button is clicked', async ({ page }) => {
    // Open settings modal first
    const settingsButton = page.locator('button[title="Settings"]').first();
    await settingsButton.click();
    await page.waitForSelector('div[role="menu"]', { timeout: 5000 });
    const settingsMenuItem = page.locator('div[role="menu"] >> text=Settings').first();
    await settingsMenuItem.click();
    
    // Wait for modal to be visible
    const settingsModal = page.locator('[role="dialog"] >> text=Settings').first();
    await expect(settingsModal).toBeVisible({ timeout: 5000 });
    
    // Click close button
    const closeButton = page.locator('[role="dialog"] >> button[aria-label*="close"], [role="dialog"] >> button >> svg[data-testid="CloseIcon"]').first();
    await expect(closeButton).toBeVisible();
    await closeButton.click();
    
    // Verify modal is closed
    await expect(settingsModal).not.toBeVisible({ timeout: 5000 });
  });

  test('should show app title and File Collections in navigation', async ({ page }) => {
    // Check app title is visible
    await expect(page.locator('text=Crawl4AI File Manager')).toBeVisible();
    
    // Check beta badge is visible  
    await expect(page.locator('text=Beta')).toBeVisible();
    
    // Check File Collections tab is active and visible
    const fileCollectionsTab = page.locator('[data-testid="file-collections-tab"]');
    await expect(fileCollectionsTab).toBeVisible();
    await expect(fileCollectionsTab).toHaveText(/File Collections/);
  });

  test('should have functional theme toggle', async ({ page }) => {
    // Find theme toggle button
    const themeToggle = page.locator('button[title*="dark"], button[title*="light"]').first();
    await expect(themeToggle).toBeVisible();
    
    // Click theme toggle
    await themeToggle.click();
    
    // The button should still be visible after toggle (content may change)
    await expect(themeToggle).toBeVisible();
  });

  test('should have working info menu', async ({ page }) => {
    // Find info button
    const infoButton = page.locator('button[title="Information"]').first();
    await expect(infoButton).toBeVisible();
    await infoButton.click();
    
    // Info menu should appear
    await page.waitForSelector('div[role="menu"]', { timeout: 5000 });
    await expect(page.locator('div[role="menu"] >> text=Crawl4AI File Manager')).toBeVisible();
    await expect(page.locator('div[role="menu"] >> text=Version')).toBeVisible();
  });

  test('should maintain responsive layout', async ({ page }) => {
    // Test desktop layout
    await page.setViewportSize({ width: 1200, height: 800 });
    await expect(page.locator('[data-testid="file-collections-tab"]')).toBeVisible();
    
    // Test tablet layout
    await page.setViewportSize({ width: 768, height: 1024 });
    await expect(page.locator('[data-testid="file-collections-tab"]')).toBeVisible();
    
    // Test mobile layout (navigation may be collapsed)
    await page.setViewportSize({ width: 375, height: 667 });
    // Navigation should still be accessible (may be in hamburger menu)
    await expect(page.locator('text=Crawl4AI File Manager')).toBeVisible();
  });
});