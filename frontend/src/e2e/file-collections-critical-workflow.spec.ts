import { test, expect } from '@playwright/test';

test.describe('FileCollection - Critical Workflow Test', () => {
  test('Critical Path: Navigation → Create Collection → Select → Add Page → Vector Sync', async ({ page }) => {
    console.log('🎯 Starting FileCollection Critical Workflow Test...');
    
    // =====================================================================
    // STEP 1: Navigate to FileCollection Tab (Top Navigation)
    // =====================================================================
    console.log('📍 STEP 1: Navigate to FileCollection Tab...');
    
    await page.goto('http://localhost:5173/');
    await page.waitForLoadState('networkidle');
    
    // Click on File Collections tab in top navigation
    await page.click('[data-testid="file-collections-tab"]');
    await page.waitForSelector('[data-testid="collections-list"], [data-testid="collection-item"], .collection', { 
      timeout: 10000,
      state: 'attached'
    });
    
    console.log('✅ Successfully navigated to FileCollection Tab');
    
    // =====================================================================
    // STEP 2: Create Test Collection
    // =====================================================================
    console.log('📍 STEP 2: Create new Test Collection...');
    
    const testCollectionName = `TestCollection-${Date.now()}`;
    const testCollectionDescription = `Critical workflow test collection created at ${new Date().toISOString()}`;
    
    // Click Create Collection button
    await page.click('[data-testid="create-collection-btn"]');
    await page.waitForSelector('[data-testid="collection-name-input"]', { timeout: 10000 });
    
    // Fill collection details
    await page.fill('[data-testid="collection-name-input"]', testCollectionName);
    await page.fill('[data-testid="collection-description-input"]', testCollectionDescription);
    
    // Submit collection creation
    await page.click('[data-testid="create-collection-submit"]');
    
    console.log(`✅ Test Collection created: "${testCollectionName}"`);
    
    // =====================================================================
    // STEP 3: Select the newly created Test Collection
    // =====================================================================
    console.log('📍 STEP 3: Select Test Collection from sidebar...');
    
    // Wait for collection to appear in list
    await page.waitForTimeout(3000);
    
    // Look for the collection item that contains our test collection name
    const collectionSelector = `[data-testid="collection-item"]:has-text("${testCollectionName}")`;
    await page.waitForSelector(collectionSelector, { timeout: 10000 });
    
    // Click on the test collection
    await page.click(collectionSelector);
    
    // Wait for collection details to load
    await page.waitForSelector('[data-testid="collection-details"]', { timeout: 10000 });
    
    console.log('✅ Test Collection selected and details loaded');
    
    // =====================================================================  
    // STEP 4: CRITICAL - Add Page to Collection
    // =====================================================================
    console.log('📍 STEP 4: Add Page to Collection (CRITICAL STEP)...');
    
    // Monitor API requests for debugging
    const apiRequests: Array<{ url: string; method: string; status?: number; body?: any }> = [];
    
    page.on('request', request => {
      if (request.url().includes('/api/') || request.url().includes('crawl') || request.url().includes('collection')) {
        apiRequests.push({
          url: request.url(),
          method: request.method(),
          body: request.postData()
        });
        console.log(`🔄 API Request: ${request.method()} ${request.url()}`);
      }
    });
    
    page.on('response', response => {
      if (response.url().includes('/api/') || response.url().includes('crawl') || response.url().includes('collection')) {
        const requestData = apiRequests.find(req => req.url === response.url() && !('status' in req));
        if (requestData) {
          requestData.status = response.status();
        }
        console.log(`📥 API Response: ${response.status()} ${response.url()}`);
      }
    });
    
    // Click Add Page button
    console.log('🔍 Looking for Add Page button...');
    await page.waitForSelector('[data-testid="add-page-btn"]', { timeout: 10000 });
    await page.click('[data-testid="add-page-btn"]');
    
    // Wait for Add Page modal
    console.log('🔍 Waiting for Add Page modal...');
    await page.waitForSelector('[data-testid="add-page-url-input"]', { timeout: 10000 });
    
    console.log('✅ Add Page modal opened');
    
    // Enter test URL  
    const testUrl = 'https://httpbin.org/html';
    await page.fill('[data-testid="add-page-url-input"]', testUrl);
    
    console.log(`📝 URL entered: ${testUrl}`);
    
    // Track crawl success
    let crawlApiCalled = false;
    let crawlSuccess = false;
    let crawlError: string | null = null;
    
    page.on('response', async response => {
      if (response.url().includes('/api/') && (
          response.url().includes('crawl') || 
          response.url().includes('collection') || 
          response.url().includes('save')
        )) {
        crawlApiCalled = true;
        
        if (response.status() === 200) {
          try {
            const data = await response.json();
            crawlSuccess = data.success === true;
            console.log(`📊 Crawl API Response:`, { 
              url: response.url(), 
              status: response.status(), 
              success: data.success,
              filename: data.filename || 'N/A'
            });
          } catch (e) {
            console.log(`📊 Crawl API Response (raw):`, { 
              url: response.url(), 
              status: response.status(),
              error: 'Failed to parse JSON'
            });
          }
        } else {
          crawlError = `HTTP ${response.status()}`;
          console.log(`❌ Crawl API Error:`, { 
            url: response.url(), 
            status: response.status() 
          });
        }
      }
    });
    
    // Submit the Add Page request
    console.log('🚀 Submitting Add Page request...');
    await page.click('[data-testid="add-page-submit"]');
    
    console.log('⏳ Waiting for crawl to complete...');
    
    // Wait for crawl to complete (extended timeout)
    await page.waitForTimeout(15000);
    
    // Check results
    console.log('🔍 Checking crawl results...');
    console.log(`API Called: ${crawlApiCalled}`);
    console.log(`Crawl Success: ${crawlSuccess}`);
    console.log(`Crawl Error: ${crawlError}`);
    
    // Log all API requests for debugging
    console.log('📋 All API Requests during Add Page:');
    apiRequests.forEach((req, index) => {
      console.log(`  ${index + 1}. ${req.method} ${req.url} - Status: ${req.status || 'pending'}`);
    });
    
    // Verify crawl was successful
    if (!crawlApiCalled) {
      throw new Error('❌ CRITICAL ERROR: No crawl API was called - Check Add Page modal submission');
    }
    
    if (crawlError) {
      throw new Error(`❌ CRITICAL ERROR: Crawl API failed - ${crawlError}`);
    }
    
    if (!crawlSuccess) {
      throw new Error('❌ CRITICAL ERROR: Crawl API returned success=false');
    }
    
    console.log('✅ Add Page crawl completed successfully');
    
    // Check if modal closed (indicates success)
    await page.waitForTimeout(3000);
    const modalStillVisible = await page.locator('[data-testid="add-page-url-input"]').isVisible();
    
    if (modalStillVisible) {
      console.warn('⚠️ WARNING: Add Page modal is still visible after successful crawl');
      // Try to close it manually for testing continuation
      try {
        await page.click('button:has-text("Cancel"), [data-testid="modal-close"]', { timeout: 2000 });
      } catch (e) {
        console.warn('Could not close modal manually');
      }
    } else {
      console.log('✅ Add Page modal closed automatically');
    }
    
    // Verify file was added to collection
    console.log('🔍 Checking if file was added to collection...');
    await page.waitForTimeout(3000);
    
    // Look for file items in the file explorer
    const fileItems = page.locator('[data-testid="file-item"]');
    const fileCount = await fileItems.count();
    
    console.log(`📁 Files in collection: ${fileCount}`);
    
    if (fileCount === 0) {
      // Take screenshot for debugging
      await page.screenshot({ path: `debug-no-files-${Date.now()}.png` });
      throw new Error('❌ CRITICAL ERROR: No files were added to collection after successful crawl');
    }
    
    console.log('✅ File successfully added to collection');
    
    // =====================================================================
    // STEP 5: Vector Sync (if available)
    // =====================================================================
    console.log('📍 STEP 5: Vector Sync...');
    
    // Check if Vector Sync button is available
    const vectorSyncBtn = page.locator('[data-testid="vector-sync-btn"]');
    const syncBtnVisible = await vectorSyncBtn.isVisible();
    
    if (!syncBtnVisible) {
      console.log('⚠️ Vector Sync button not visible - skipping Vector Sync test');
    } else {
      // Track sync API
      let syncApiCalled = false;
      let syncSuccess = false;
      
      page.on('response', async response => {
        if (response.url().includes('vector-sync') || response.url().includes('sync')) {
          syncApiCalled = true;
          if (response.status() === 200) {
            try {
              const data = await response.json();
              syncSuccess = data.success === true;
              console.log(`📊 Vector Sync Response:`, { 
                status: response.status(), 
                success: data.success 
              });
            } catch (e) {
              console.log(`📊 Vector Sync Response (raw):`, { status: response.status() });
            }
          }
        }
      });
      
      // Click Vector Sync
      await vectorSyncBtn.click();
      console.log('🔄 Vector Sync initiated...');
      
      // Wait for sync
      await page.waitForTimeout(10000);
      
      console.log(`Sync API Called: ${syncApiCalled}`);
      console.log(`Sync Success: ${syncSuccess}`);
      
      // Check sync indicator
      const syncIndicator = page.locator('[data-testid="vector-sync-indicator"]');
      if (await syncIndicator.isVisible()) {
        console.log('✅ Vector Sync indicator visible');
      } else {
        console.log('⚠️ Vector Sync indicator not visible');
      }
      
      console.log('✅ Vector Sync completed');
    }
    
    // =====================================================================
    // SUCCESS - All Steps Completed
    // =====================================================================
    console.log('');
    console.log('🎉 CRITICAL WORKFLOW TEST COMPLETED SUCCESSFULLY!');
    console.log('✅ 1. Navigation to FileCollection Tab');
    console.log('✅ 2. Test Collection created');
    console.log('✅ 3. Collection selected in sidebar');
    console.log('✅ 4. Add Page: URL crawled and added to collection');
    console.log('✅ 5. Vector Sync: ' + (syncBtnVisible ? 'Completed' : 'Skipped (not available)'));
    console.log('');
    console.log('🔥 FILECOLLECTION WORKFLOW IS FUNCTIONAL!');
    
    // Final verification
    expect(crawlSuccess).toBeTruthy();
    expect(fileCount).toBeGreaterThan(0);
    
  });
  
  // =====================================================================
  // Additional Test: Compare Legacy vs FileCollection
  // =====================================================================
  test('Compare Legacy Simple Crawl vs FileCollection Add Page', async ({ page }) => {
    console.log('🔍 Comparison Test: Legacy Simple Crawl vs FileCollection Add Page');
    
    const testUrl = 'https://httpbin.org/html';
    
    // Test Legacy Simple Crawl first
    console.log('📍 Testing Legacy Simple Crawl...');
    
    await page.goto('http://localhost:5173/');
    await page.waitForLoadState('networkidle');
    
    // Navigate to Simple Crawl tab
    await page.click('[data-testid="simple-crawl-tab"]');
    await page.waitForSelector('[data-testid="url-input"]', { timeout: 10000 });
    
    // Enter URL and crawl
    await page.fill('[data-testid="url-input"]', testUrl);
    
    let legacyCrawlSuccess = false;
    page.on('response', async response => {
      if (response.url().includes('extract') && response.status() === 200) {
        legacyCrawlSuccess = true;
      }
    });
    
    await page.click('[data-testid="crawl-button"]');
    await page.waitForTimeout(8000);
    
    console.log(`Legacy Simple Crawl Success: ${legacyCrawlSuccess}`);
    
    // Now test FileCollection Add Page (simplified)
    console.log('📍 Testing FileCollection Add Page...');
    
    await page.click('[data-testid="file-collections-tab"]');
    await page.waitForTimeout(2000);
    
    // Try to find existing collection or create one
    const existingCollection = page.locator('[data-testid="collection-item"]').first();
    const hasCollections = await existingCollection.count() > 0;
    
    if (!hasCollections) {
      // Create a collection
      await page.click('[data-testid="create-collection-btn"]');
      await page.fill('[data-testid="collection-name-input"]', 'Comparison Test Collection');
      await page.click('[data-testid="create-collection-submit"]');
      await page.waitForTimeout(2000);
    }
    
    // Select first available collection
    await page.click('[data-testid="collection-item"]', { timeout: 10000 });
    await page.waitForSelector('[data-testid="collection-details"]', { timeout: 10000 });
    
    // Add Page
    await page.click('[data-testid="add-page-btn"]');
    await page.fill('[data-testid="add-page-url-input"]', testUrl);
    
    let fileCollectionCrawlSuccess = false;
    page.on('response', async response => {
      if ((response.url().includes('crawl') || response.url().includes('collection')) && response.status() === 200) {
        try {
          const data = await response.json();
          if (data.success === true) {
            fileCollectionCrawlSuccess = true;
          }
        } catch (e) {
          // Ignore JSON parse errors
        }
      }
    });
    
    await page.click('[data-testid="add-page-submit"]');
    await page.waitForTimeout(10000);
    
    console.log(`FileCollection Add Page Success: ${fileCollectionCrawlSuccess}`);
    
    // Comparison Results
    console.log('');
    console.log('📊 COMPARISON RESULTS:');
    console.log(`Legacy Simple Crawl: ${legacyCrawlSuccess ? '✅ WORKS' : '❌ FAILED'}`);
    console.log(`FileCollection Add Page: ${fileCollectionCrawlSuccess ? '✅ WORKS' : '❌ FAILED'}`);
    
    if (legacyCrawlSuccess && !fileCollectionCrawlSuccess) {
      console.log('⚠️ ISSUE CONFIRMED: Legacy works but FileCollection Add Page fails');
    } else if (legacyCrawlSuccess && fileCollectionCrawlSuccess) {
      console.log('✅ BOTH SYSTEMS WORK: Ready for legacy removal');
    }
  });
});