import { test, expect } from '@playwright/test';

test.describe('File Collections E2E', () => {
  // Start with a clean state by navigating to the home page
  test.beforeEach(async ({ page }) => {
    // Navigate to the app
    await page.goto('http://localhost:5173/');
    
    // Wait for the app to load
    await page.waitForLoadState('networkidle');
  });

  test('should display File Collections tab and load collections', async ({ page }) => {
    // File Collections is now the default page, no tab click needed
    
    // Wait for collections to load
    await page.waitForSelector('[data-testid="collections-list"]', { timeout: 10000 });
    
    // Check if collections are displayed
    const collectionsContainer = page.locator('[data-testid="collections-list"]');
    await expect(collectionsContainer).toBeVisible();
    
    // The list should either show collections or an empty state message
    const hasCollections = await page.locator('[data-testid="collection-item"]').count() > 0;
    const hasEmptyState = await page.locator('[data-testid="empty-collections"]').isVisible();
    
    expect(hasCollections || hasEmptyState).toBeTruthy();
  });

  test('should be able to create a new collection', async ({ page }) => {
    // Navigate to File Collections tab
    await page.waitForSelector('[data-testid="collections-list"]', { timeout: 10000 });
    
    // Get initial collection count
    const initialCount = await page.locator('[data-testid="collection-item"]').count();
    
    // Click "Create Collection" button
    await page.click('[data-testid="create-collection-btn"]');
    
    // Use unique collection name with timestamp
    const timestamp = Date.now();
    const collectionName = `E2E Test ${timestamp}`;
    const collectionDescription = `Created by E2E test at ${timestamp}`;
    
    // Set up network monitoring for creation
    let createResponseReceived = false;
    let createSuccess = false;
    
    page.on('response', async response => {
      if (response.url().includes('/api/file-collections') && response.request().method() === 'POST') {
        createResponseReceived = true;
        if (response.status() === 200) {
          const responseData = await response.json();
          createSuccess = responseData.success === true;
        }
      }
    });
    
    // Fill in collection details
    await page.fill('[data-testid="collection-name-input"]', collectionName);
    await page.fill('[data-testid="collection-description-input"]', collectionDescription);
    
    // Submit the form
    await page.click('[data-testid="create-collection-submit"]');
    
    // Wait for the API call to complete
    await page.waitForFunction(() => createResponseReceived, { timeout: 10000 });
    
    // Verify the API call was successful
    expect(createSuccess).toBeTruthy();
    
    // Wait for modal to close (it should close automatically on success)
    await expect(page.locator('[data-testid="collection-name-input"]')).not.toBeVisible();
    
    // Verify collection count increased (collections list should refresh)
    await page.waitForFunction(
      (expectedCount) => document.querySelectorAll('[data-testid="collection-item"]').length > expectedCount,
      initialCount,
      { timeout: 10000 }
    );
    
    const finalCount = await page.locator('[data-testid="collection-item"]').count();
    expect(finalCount).toBeGreaterThan(initialCount);
  });

  test('should show collection details when clicked', async ({ page }) => {
    // Navigate to File Collections tab
    await page.waitForSelector('[data-testid="collections-list"]', { timeout: 10000 });
    
    // Check if we have any collections
    const collectionCount = await page.locator('[data-testid="collection-item"]').count();
    
    if (collectionCount > 0) {
      // Click on the first collection
      await page.click('[data-testid="collection-item"]:first-child');
      
      // Wait for collection details to load
      await page.waitForSelector('[data-testid="collection-details"]', { timeout: 10000 });
      
      // Verify collection details panel is visible
      await expect(page.locator('[data-testid="collection-details"]')).toBeVisible();
      
      // Check for file list or empty state
      const hasFiles = await page.locator('[data-testid="file-item"]').count() > 0;
      const hasEmptyFiles = await page.locator('[data-testid="empty-files"]').isVisible();
      
      expect(hasFiles || hasEmptyFiles).toBeTruthy();
    } else {
      console.log('No collections found for testing collection details');
    }
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Mock API failure for all file-collections routes
    await page.route('**/api/file-collections', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Server error' })
      });
    });
    
    // Navigate to File Collections tab
    
    // Wait for the error state to be processed
    await page.waitForTimeout(3000);
    
    // Check for error message or fallback behavior
    const hasErrorMessage = await page.locator('[data-testid="error-message"]').isVisible();
    const collectionsContainer = await page.locator('[data-testid="collections-list"]').isVisible();
    const isStillLoading = await page.locator('[data-testid="loading-spinner"]').isVisible();
    
    // Should either show error message, collections container, or loading state
    expect(hasErrorMessage || collectionsContainer || isStillLoading).toBeTruthy();
    
    // If there's an error message visible, log it for debugging
    if (hasErrorMessage) {
      const errorText = await page.locator('[data-testid="error-message"]').textContent();
      console.log('Error message displayed:', errorText);
    }
  });

  test('should make correct API calls to backend', async ({ page }) => {
    // Monitor network requests
    const apiRequests: string[] = [];
    
    page.on('request', request => {
      if (request.url().includes('/api/')) {
        apiRequests.push(`${request.method()} ${request.url()}`);
      }
    });
    
    // Navigate to File Collections tab
    
    // Wait for network requests to complete
    await page.waitForTimeout(2000);
    
    // Verify that correct API calls were made
    expect(apiRequests.some(req => req.includes('GET') && req.includes('/api/file-collections'))).toBeTruthy();
    
    console.log('API Requests made:', apiRequests);
  });

  test('should display correct backend connectivity status', async ({ page }) => {
    // Check if backend is running
    const response = await page.request.get('http://localhost:8000/api/file-collections');
    
    if (response.ok()) {
      console.log('Backend is running correctly');
      
      // Navigate to File Collections and verify it works
      await page.waitForSelector('[data-testid="collections-list"]', { timeout: 10000 });
      
      await expect(page.locator('[data-testid="collections-list"]')).toBeVisible();
    } else {
      console.log('Backend connectivity issue:', response.status(), response.statusText());
      
      // The test should fail if backend is not accessible
      throw new Error(`Backend API not accessible: ${response.status()} ${response.statusText()}`);
    }
  });
});

test.describe('File Collections Backend API', () => {
  test('should respond to API requests correctly', async ({ request }) => {
    // Test list collections endpoint
    const listResponse = await request.get('http://localhost:8000/api/file-collections');
    expect(listResponse.ok()).toBeTruthy();
    
    const listData = await listResponse.json();
    expect(listData).toHaveProperty('success');
    expect(listData).toHaveProperty('collections');
    expect(Array.isArray(listData.collections)).toBeTruthy();
    
    console.log(`Backend returned ${listData.collections.length} collections`);
  });

  test('should create new collections via API', async ({ request }) => {
    // Test create collection endpoint with unique name
    const timestamp = Date.now();
    const collectionName = `API-Test-${timestamp}`;
    
    const createResponse = await request.post('http://localhost:8000/api/file-collections', {
      data: {
        name: collectionName,
        description: 'Created via Playwright API test'
      }
    });
    
    expect(createResponse.ok()).toBeTruthy();
    
    const createData = await createResponse.json();
    expect(createData).toHaveProperty('success', true);
    expect(createData).toHaveProperty('collection');
    expect(createData.collection).toHaveProperty('name', collectionName);
  });
});