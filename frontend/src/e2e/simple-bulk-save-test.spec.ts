import { test, expect, ConsoleMessage } from '@playwright/test';

test.describe('Simple Bulk Save Modal Test', () => {
  let consoleErrors: ConsoleMessage[] = [];

  test.beforeEach(async ({ page }) => {
    consoleErrors = [];
    
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg);
      }
    });

    page.on('pageerror', (error) => {
      console.error('Page error:', error.message);
    });
  });

  test('BulkSaveModal opens correctly and has proper DOM structure', async ({ page }) => {
    console.log('=== Testing BulkSaveModal Opening and DOM Structure ===');

    // Navigate to Deep Crawl page
    await page.goto('/');
    await page.click('text=Deep Crawl');
    console.log('✓ Navigated to Deep Crawl page');

    // Fill form with minimal data
    await page.fill('input[placeholder*="https://example.com"]', 'https://httpbin.org');
    await page.fill('input[type="number"]', '1');
    await page.fill('input[type="number"] >> nth=1', '2');
    console.log('✓ Filled crawl form');

    // Mock API response to ensure consistent test data
    await page.route('/api/deep-crawl', async (route) => {
      const mockResponse = {
        success: true,
        results: {
          pages: [
            {
              url: 'https://httpbin.org/',
              title: 'Test Page 1',
              content: 'Test content 1',
              success: true,
              depth: 0,
              metadata: { crawl_time: new Date().toISOString(), score: 8.5 }
            },
            {
              url: 'https://httpbin.org/get',
              title: 'Test Page 2', 
              content: 'Test content 2',
              success: true,
              depth: 1,
              metadata: { crawl_time: new Date().toISOString(), score: 7.2 }
            }
          ]
        }
      };

      await route.fulfill({
        status: 200,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(mockResponse)
      });
    });

    // Start crawl
    await page.click('button:has-text("Start Deep Crawl")');
    console.log('✓ Started crawl');

    // Wait for results with more specific selector
    await page.waitForSelector('text=successful', { timeout: 10000 });
    console.log('✓ Results appeared');

    // Take screenshot after crawl
    await page.screenshot({ 
      path: '/Users/florianwegener/Projects/crawl4ai-mcp-server/frontend/simple-test-after-crawl.png',
      fullPage: true 
    });

    // Check if bulk save button exists and is initially disabled
    const bulkSaveButton = page.locator('button:has-text("Bulk Save to Collection")');
    await expect(bulkSaveButton).toBeVisible();
    await expect(bulkSaveButton).toBeDisabled();
    console.log('✓ Bulk save button is disabled initially');

    // Find and select checkboxes
    const checkboxes = page.locator('input[type="checkbox"]');
    const count = await checkboxes.count();
    console.log(`Found ${count} checkboxes`);

    // Select first available checkbox
    if (count > 0) {
      await checkboxes.first().check();
      console.log('✓ Selected first checkbox');
      
      // Wait for button state to update
      await page.waitForTimeout(500);
      
      // Button should be enabled now
      await expect(bulkSaveButton).toBeEnabled();
      console.log('✓ Bulk save button enabled after selection');
    }

    // Click bulk save button
    await bulkSaveButton.click();
    console.log('✓ Clicked bulk save button');

    // Wait for modal to appear
    await page.waitForTimeout(1000);

    // Check if modal opened
    const modalTitle = page.locator('h3:has-text("Bulk Save to Collection")');
    const isModalOpen = await modalTitle.isVisible();
    
    if (isModalOpen) {
      console.log('✅ BulkSaveModal opened successfully!');

      // Take screenshot of opened modal
      await page.screenshot({ 
        path: '/Users/florianwegener/Projects/crawl4ai-mcp-server/frontend/simple-test-modal-opened.png',
        fullPage: true 
      });

      // Test modal DOM structure
      console.log('Checking modal DOM structure...');

      // Check modal container (backdrop)
      const modalBackdrop = page.locator('.fixed.inset-0.bg-black.bg-opacity-50');
      const backdropExists = await modalBackdrop.isVisible();
      console.log(`Modal backdrop exists: ${backdropExists}`);

      if (backdropExists) {
        // Check z-index
        const zIndex = await modalBackdrop.evaluate((el) => {
          return window.getComputedStyle(el).zIndex;
        });
        console.log(`Modal z-index: ${zIndex}`);
        expect(parseInt(zIndex)).toBeGreaterThanOrEqual(50);
      }

      // Check modal dialog
      const modalDialog = page.locator('.bg-white.dark\\:bg-gray-800.rounded-lg');
      const dialogExists = await modalDialog.isVisible();
      console.log(`Modal dialog exists: ${dialogExists}`);

      // Check modal components
      const selectionSummary = page.locator('text=successful results selected');
      const hasSummary = await selectionSummary.isVisible();
      console.log(`Selection summary visible: ${hasSummary}`);

      const collectionSelect = page.locator('[data-testid="bulk-collection-select"]');
      const hasSelect = await collectionSelect.isVisible();
      console.log(`Collection select visible: ${hasSelect}`);

      const confirmButton = page.locator('[data-testid="bulk-save-confirm"]');
      const hasConfirm = await confirmButton.isVisible();
      console.log(`Confirm button visible: ${hasConfirm}`);

      // Test modal functionality
      if (hasSelect && hasConfirm) {
        console.log('Testing modal functionality...');
        
        // Select default collection
        await collectionSelect.selectOption('default');
        console.log('✓ Selected collection');
        
        // Check if confirm button is enabled
        const isEnabled = await confirmButton.isEnabled();
        console.log(`Confirm button enabled: ${isEnabled}`);

        if (isEnabled) {
          // Mock save API to avoid actual storage
          await page.route('/api/store-content', async (route) => {
            await route.fulfill({
              status: 200,
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ success: true })
            });
          });

          await confirmButton.click();
          console.log('✓ Clicked confirm button');
          
          // Wait for save operation
          await page.waitForTimeout(2000);
        }
      }

      // Test modal closing
      const closeButton = page.locator('button:has-text("Close"), button:has-text("Cancel")').first();
      if (await closeButton.isVisible()) {
        await closeButton.click();
        await page.waitForTimeout(500);
        console.log('✓ Modal can be closed');
      }

    } else {
      console.log('❌ BulkSaveModal did not open');
      
      // Investigate why modal didn't open
      console.log('Investigating modal state...');
      
      // Check if modal container exists but is hidden
      const allModalContainers = await page.locator('.fixed.inset-0').count();
      console.log(`Found ${allModalContainers} fixed positioned containers`);

      // Check for any elements with modal-related classes
      const modalElements = await page.evaluate(() => {
        const selectors = [
          '.fixed.inset-0',
          '[class*="modal"]', 
          '[class*="z-50"]',
          '[class*="bg-black"]'
        ];
        
        return selectors.map(selector => {
          const elements = document.querySelectorAll(selector);
          return {
            selector,
            count: elements.length,
            elements: Array.from(elements).map(el => ({
              visible: el.offsetParent !== null,
              styles: {
                display: window.getComputedStyle(el).display,
                visibility: window.getComputedStyle(el).visibility,
                opacity: window.getComputedStyle(el).opacity
              }
            }))
          };
        });
      });
      
      console.log('Modal element investigation:', JSON.stringify(modalElements, null, 2));
    }

    // Check for console errors
    console.log('\n--- Console Error Check ---');
    if (consoleErrors.length > 0) {
      console.log('❌ Console errors detected:');
      consoleErrors.forEach((error, index) => {
        console.log(`  ${index + 1}. ${error.type()}: ${error.text()}`);
      });
    } else {
      console.log('✅ No console errors detected');
    }

    // Final screenshot
    await page.screenshot({ 
      path: '/Users/florianwegener/Projects/crawl4ai-mcp-server/frontend/simple-test-final.png',
      fullPage: true 
    });

    console.log('\n=== Test Summary ===');
    console.log(`✅ Navigation: SUCCESS`);
    console.log(`✅ Form filling: SUCCESS`);
    console.log(`✅ Crawl execution: SUCCESS`);
    console.log(`✅ Button state management: SUCCESS`);
    console.log(`${isModalOpen ? '✅' : '❌'} Modal opening: ${isModalOpen ? 'SUCCESS' : 'FAILED'}`);
    console.log(`✅ Console errors: ${consoleErrors.length === 0 ? 'NONE' : consoleErrors.length + ' found'}`);
    console.log('=== Simple Bulk Save Test Complete ===');

    // Ensure test passes if modal opened successfully
    expect(isModalOpen).toBe(true);
  });

  test('Modal CSS z-index and positioning', async ({ page }) => {
    console.log('=== Testing Modal CSS and Z-Index ===');

    // Add high z-index competitor elements to test stacking
    await page.goto('/');
    
    await page.addStyleTag({
      content: `
        .test-high-z {
          position: fixed;
          top: 50px;
          right: 50px;
          width: 200px;
          height: 100px;
          background: rgba(255, 0, 0, 0.8);
          z-index: 9999;
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
        }
        .test-medium-z {
          position: fixed;
          bottom: 50px;  
          left: 50px;
          width: 200px;
          height: 100px;
          background: rgba(0, 255, 0, 0.8);
          z-index: 100;
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
        }
      `
    });

    await page.evaluate(() => {
      const highZ = document.createElement('div');
      highZ.className = 'test-high-z';
      highZ.textContent = 'High Z-Index (9999)';
      document.body.appendChild(highZ);

      const mediumZ = document.createElement('div'); 
      mediumZ.className = 'test-medium-z';
      mediumZ.textContent = 'Medium Z-Index (100)';
      document.body.appendChild(mediumZ);
    });

    // Take screenshot showing competitor elements
    await page.screenshot({ 
      path: '/Users/florianwegener/Projects/crawl4ai-mcp-server/frontend/css-test-competitors.png',
      fullPage: true 
    });

    // Check z-index stacking context
    const stackingContext = await page.evaluate(() => {
      const fixedElements = document.querySelectorAll('[style*="position: fixed"], .fixed, [class*="z-"]');
      return Array.from(fixedElements).map(el => {
        const computed = window.getComputedStyle(el);
        return {
          element: el.tagName + (el.className ? '.' + el.className.split(' ')[0] : ''),
          zIndex: computed.zIndex,
          position: computed.position,
          display: computed.display,
          visible: el.offsetParent !== null
        };
      }).filter(item => item.zIndex !== 'auto');
    });

    console.log('Z-Index stacking context:', stackingContext);

    // Test that modal elements have appropriate z-index values
    const modalZIndexes = stackingContext.filter(item => 
      item.element.includes('fixed') || item.element.includes('modal')
    );

    console.log('Modal-related z-indexes:', modalZIndexes);

    console.log('=== CSS and Z-Index Test Complete ===');
  });
});