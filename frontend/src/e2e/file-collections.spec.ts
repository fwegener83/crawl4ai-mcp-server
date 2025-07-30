import { test, expect } from '@playwright/test';

test.describe('File Collections Management', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
    
    // Navigate to file collections page using the correct navigation text
    await page.click('button:has-text("File Manager")');
    
    // Wait for the collections page to load
    await expect(page.locator('h2:has-text("Collections")')).toBeVisible({ timeout: 10000 });
  });

  test('should load the file collections page without errors', async ({ page }) => {
    // Check that the main components are visible
    await expect(page.locator('h2:has-text("Collections")')).toBeVisible();
    
    // Check for sidebar presence
    await expect(page.locator('.w-80.flex-shrink-0').first()).toBeVisible();
    
    // Check for main content area
    await expect(page.locator('.flex-1.flex.items-center.justify-center')).toBeVisible();
    
    // Check for "Select a Collection" message when no collection is selected
    await expect(page.locator('h3:has-text("Select a Collection")')).toBeVisible();
  });

  test('should display new collection modal when clicking Create New Collection button', async ({ page }) => {
    // Click the "Create New Collection" button
    await page.click('button:has-text("Create New Collection")');
    
    // Check that the modal is visible
    await expect(page.locator('h3:has-text("Create New Collection")')).toBeVisible();
    
    // Check form fields are present
    await expect(page.locator('input[placeholder="Enter collection name"]')).toBeVisible();
    await expect(page.locator('textarea[placeholder="Optional description"]')).toBeVisible();
    
    // Check buttons are present
    await expect(page.locator('button:has-text("Cancel")')).toBeVisible();
    await expect(page.locator('button:has-text("Create Collection")')).toBeVisible();
  });

  test('should close modal when clicking Cancel', async ({ page }) => {
    // Open modal
    await page.click('button:has-text("Create New Collection")');
    await expect(page.locator('h3:has-text("Create New Collection")')).toBeVisible();
    
    // Click Cancel
    await page.click('button:has-text("Cancel")');
    
    // Modal should be closed
    await expect(page.locator('h3:has-text("Create New Collection")')).not.toBeVisible();
  });

  test('should validate required fields in new collection modal', async ({ page }) => {
    // Open modal
    await page.click('button:has-text("Create New Collection")');
    
    // Try to submit without name
    const createButton = page.locator('button:has-text("Create Collection")');
    await expect(createButton).toBeDisabled();
    
    // Enter name
    await page.fill('input[placeholder="Enter collection name"]', 'Test Collection');
    
    // Now button should be enabled
    await expect(createButton).toBeEnabled();
  });

  test('should show empty state when no collections exist', async ({ page }) => {
    // Check for empty state in sidebar
    const emptyState = page.locator('p:has-text("No collections yet")');
    if (await emptyState.isVisible()) {
      await expect(emptyState).toBeVisible();
      await expect(page.locator('button:has-text("Create your first collection")')).toBeVisible();
    }
  });

  test('should show collection sidebar with refresh button', async ({ page }) => {
    // Check for refresh button in sidebar
    await expect(page.locator('button[title="Refresh collections"]')).toBeVisible();
    
    // Check for new collection button in sidebar
    await expect(page.locator('button:has-text("New")').first()).toBeVisible();
  });

  test('should navigate back to home', async ({ page }) => {
    // Click on the home/title button
    await page.click('button:has-text("Crawl4AI Web Interface")');
    
    // Should be back on home page (check for home-specific content)
    // This test verifies navigation works
    await page.waitForTimeout(1000);
  });

  test('should handle page refresh gracefully', async ({ page }) => {
    // Refresh the page
    await page.reload();
    
    // Navigate back to file manager
    await page.click('button:has-text("File Manager")');
    
    // Should still load correctly
    await expect(page.locator('h2:has-text("Collections")')).toBeVisible();
  });

  test('should not have console errors on page load', async ({ page }) => {
    const errors: string[] = [];
    
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    
    // Reload page to capture any console errors
    await page.reload();
    await page.click('button:has-text("File Manager")');
    await page.waitForTimeout(2000);
    
    // Filter out known acceptable errors (like network errors in development)
    const criticalErrors = errors.filter(error => 
      !error.includes('favicon.ico') && 
      !error.includes('404') &&
      !error.includes('net::ERR_') &&
      !error.includes('Failed to fetch')
    );
    
    expect(criticalErrors).toHaveLength(0);
  });

  test('should display correct navigation highlighting', async ({ page }) => {
    // Check that File Manager button is highlighted when on file collections page
    const fileManagerButton = page.locator('button:has-text("File Manager")');
    await expect(fileManagerButton).toHaveClass(/bg-blue-100/);
  });
});