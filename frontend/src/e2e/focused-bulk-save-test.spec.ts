import { test, expect, Page, ConsoleMessage } from '@playwright/test';

test.describe('Focused Bulk Save Modal Test', () => {
  let consoleMessages: ConsoleMessage[] = [];
  let consoleErrors: ConsoleMessage[] = [];

  test.beforeEach(async ({ page }) => {
    // Capture console messages and errors
    consoleMessages = [];
    consoleErrors = [];
    
    page.on('console', (msg) => {
      consoleMessages.push(msg);
      if (msg.type() === 'error') {
        consoleErrors.push(msg);
      }
    });

    page.on('pageerror', (error) => {
      console.error('Page error:', error.message);
    });
  });

  test('bulk save modal functionality and DOM inspection', async ({ page }) => {
    console.log('=== Focused Bulk Save Modal Test ===');

    // Step 1: Navigate and setup
    await page.goto('/');
    await page.click('text=Deep Crawl');
    await expect(page.locator('h1')).toContainText('Deep Website Crawling');
    console.log('✓ Navigated to Deep Crawl page');

    // Step 2: Fill form
    await page.locator('input[placeholder*="https://example.com"]').fill('https://httpbin.org');
    await page.locator('input[type="number"]').first().fill('1');
    await page.locator('input[type="number"]').nth(1).fill('2');
    await page.locator('select').first().selectOption('bfs');
    console.log('✓ Form filled');

    // Step 3: Mock API response with proper structure
    await page.route('/api/deep-crawl', async (route) => {
      const mockResponse = {
        success: true,
        results: {
          pages: [
            {
              url: 'https://httpbin.org/',
              title: 'HTTPBin Home',
              content: 'HTTPBin is a simple HTTP Request & Response Service',
              success: true,
              depth: 0,
              metadata: {
                crawl_time: new Date().toISOString(),
                score: 9.5
              }
            },
            {
              url: 'https://httpbin.org/get',
              title: 'HTTPBin GET',
              content: 'A simple GET endpoint for testing',
              success: true,
              depth: 1,
              metadata: {
                crawl_time: new Date().toISOString(),
                score: 8.2
              }
            }
          ],
          summary: {
            total_pages: 2,
            successful_pages: 2,
            failed_pages: 0
          }
        }
      };

      await route.fulfill({
        status: 200,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(mockResponse)
      });
    });

    // Step 4: Start crawl
    const startButton = page.locator('button:has-text("Start Deep Crawl")');
    await startButton.click();
    console.log('✓ Started crawl');

    // Wait for results
    await expect(page.locator('text=successful')).toBeVisible({ timeout: 10000 });
    console.log('✓ Results appeared');

    // Step 5: Test bulk save button states
    const bulkSaveButton = page.locator('button:has-text("Bulk Save to Collection")');
    await expect(bulkSaveButton).toBeVisible();
    await expect(bulkSaveButton).toBeDisabled();
    console.log('✓ Bulk save button is disabled when no items selected');

    // Step 6: Select checkboxes
    const checkboxes = page.locator('input[type="checkbox"]');
    const checkboxCount = await checkboxes.count();
    console.log(`Found ${checkboxCount} checkboxes`);

    // Select at least one checkbox (skip "Select All" if present)
    let selected = false;
    for (let i = 0; i < checkboxCount; i++) {
      try {
        const checkbox = checkboxes.nth(i);
        const isVisible = await checkbox.isVisible();
        const isChecked = await checkbox.isChecked();
        
        if (isVisible && !isChecked) {
          await checkbox.check();
          selected = true;
          console.log(`✓ Selected checkbox ${i}`);
          break;
        }
      } catch (error) {
        console.log(`Could not select checkbox ${i}: ${error}`);
      }
    }

    expect(selected).toBe(true);
    await page.waitForTimeout(500); // Wait for UI update

    // Button should be enabled now
    await expect(bulkSaveButton).toBeEnabled();
    console.log('✓ Bulk save button enabled after selection');

    // Step 7: Click bulk save button and check modal
    console.log('Testing modal opening...');
    await bulkSaveButton.click();
    await page.waitForTimeout(1000);

    // Check if modal opened
    const modalTitle = page.locator('h3:has-text("Bulk Save to Collection")');
    const isModalVisible = await modalTitle.isVisible();
    console.log(`Modal visible: ${isModalVisible}`);

    if (isModalVisible) {
      console.log('✓ Modal opened successfully');

      // Step 8: Check modal DOM structure
      console.log('Inspecting modal DOM...');
      
      // Check modal container
      const modalContainer = page.locator('.fixed.inset-0');
      await expect(modalContainer).toBeVisible();
      
      // Get modal container styles
      const containerStyles = await modalContainer.evaluate((el) => {
        const computed = window.getComputedStyle(el);
        return {
          position: computed.position,
          zIndex: computed.zIndex,
          background: computed.backgroundColor,
          display: computed.display
        };
      });
      console.log('Modal container styles:', containerStyles);

      // Check modal dialog
      const modalDialog = page.locator('.bg-white.dark\\:bg-gray-800.rounded-lg');
      const dialogExists = await modalDialog.isVisible();
      console.log(`Modal dialog exists: ${dialogExists}`);

      if (dialogExists) {
        const dialogStyles = await modalDialog.evaluate((el) => {
          const rect = el.getBoundingClientRect();
          const computed = window.getComputedStyle(el);
          return {
            position: rect,
            styles: {
              maxWidth: computed.maxWidth,
              width: computed.width,
              margin: computed.margin,
              transform: computed.transform
            }
          };
        });
        console.log('Modal dialog position and styles:', dialogStyles);
      }

      // Step 9: Test modal functionality
      console.log('Testing modal functionality...');
      
      // Check selection summary
      const selectionText = page.locator('text=successful results selected');
      const hasSelectionText = await selectionText.isVisible();
      console.log(`Selection summary visible: ${hasSelectionText}`);

      // Check collection dropdown
      const collectionSelect = page.locator('[data-testid="bulk-collection-select"]');
      const hasCollectionSelect = await collectionSelect.isVisible();
      console.log(`Collection select visible: ${hasCollectionSelect}`);

      if (hasCollectionSelect) {
        await collectionSelect.selectOption('default');
        console.log('✓ Selected default collection');
      }

      // Check confirm button
      const confirmButton = page.locator('[data-testid="bulk-save-confirm"]');
      const hasConfirmButton = await confirmButton.isVisible();
      console.log(`Confirm button visible: ${hasConfirmButton}`);

      if (hasConfirmButton) {
        const isEnabled = await confirmButton.isEnabled();
        console.log(`Confirm button enabled: ${isEnabled}`);
        
        if (isEnabled) {
          // Mock the save operation to avoid actual API calls
          await page.route('/api/store-content', async (route) => {
            await route.fulfill({
              status: 200,
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ success: true, message: 'Content stored successfully' })
            });
          });

          await confirmButton.click();
          console.log('✓ Clicked confirm button');
          
          // Wait for save operation
          await page.waitForTimeout(2000);
        }
      }

      // Step 10: Test modal closing
      const closeButton = page.locator('button:has-text("Close"), button:has-text("Cancel")').first();
      const hasCloseButton = await closeButton.isVisible();
      console.log(`Close button visible: ${hasCloseButton}`);

      if (hasCloseButton) {
        await closeButton.click();
        await page.waitForTimeout(500);
        console.log('✓ Clicked close button');
      }

    } else {
      console.log('✗ Modal did not open - investigating...');
      
      // Check if modal container exists but is hidden
      const hiddenModal = page.locator('.fixed.inset-0');
      const modalExists = await hiddenModal.count();
      console.log(`Modal containers found: ${modalExists}`);

      if (modalExists > 0) {
        for (let i = 0; i < modalExists; i++) {
          const modal = hiddenModal.nth(i);
          const styles = await modal.evaluate((el) => {
            const computed = window.getComputedStyle(el);
            return {
              display: computed.display,
              visibility: computed.visibility,
              opacity: computed.opacity,
              zIndex: computed.zIndex,
              classes: el.className
            };
          });
          console.log(`Modal ${i} styles:`, styles);
        }
      }

      // Check if there are any CSS issues
      const allModals = await page.evaluate(() => {
        const modals = document.querySelectorAll('[class*="modal"], [class*="fixed"], [class*="z-"]');
        return Array.from(modals).map((el, index) => ({
          index,
          tag: el.tagName,
          classes: el.className,
          id: el.id,
          visible: el.offsetParent !== null,
          innerHTML: el.innerHTML.substring(0, 100) + '...'
        }));
      });
      console.log('All potential modal elements:', allModals);
    }

    // Step 11: Check for console errors
    console.log('\nConsole error check:');
    if (consoleErrors.length > 0) {
      console.log('Console errors found:');
      consoleErrors.forEach((error, index) => {
        console.log(`  ${index + 1}. ${error.type()}: ${error.text()}`);
      });
    } else {
      console.log('✓ No console errors detected');
    }

    // Step 12: Take final screenshots
    await page.screenshot({ 
      path: '/Users/florianwegener/Projects/crawl4ai-mcp-server/frontend/focused-test-final.png',
      fullPage: true 
    });

    console.log('\n=== Test Summary ===');
    console.log(`Modal opened: ${isModalVisible ? 'SUCCESS' : 'FAILED'}`);
    console.log(`Console errors: ${consoleErrors.length === 0 ? 'NONE' : consoleErrors.length + ' found'}`);
    console.log(`Z-index: ${containerStyles?.zIndex || 'Not detected'}`);
    console.log('=== Focused Test Complete ===');
  });

  test('CSS and z-index isolation test', async ({ page }) => {
    console.log('=== CSS and Z-Index Isolation Test ===');

    // Add competing high z-index elements
    await page.goto('/');
    
    await page.addStyleTag({
      content: `
        .test-overlay-1 {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(255, 0, 0, 0.3);
          z-index: 40;
          pointer-events: none;
        }
        .test-overlay-2 {
          position: fixed;
          top: 100px;
          left: 100px;
          width: 300px;
          height: 200px;
          background: rgba(0, 255, 0, 0.5);
          z-index: 60;
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
        }
      `
    });

    await page.evaluate(() => {
      const overlay1 = document.createElement('div');
      overlay1.className = 'test-overlay-1';
      overlay1.textContent = 'Low Z-Index Overlay (40)';
      document.body.appendChild(overlay1);

      const overlay2 = document.createElement('div');
      overlay2.className = 'test-overlay-2';
      overlay2.textContent = 'High Z-Index Overlay (60)';
      document.body.appendChild(overlay2);
    });

    // Now test modal behavior with these overlays
    await page.click('text=Deep Crawl');
    
    // Take screenshot showing overlays
    await page.screenshot({ 
      path: '/Users/florianwegener/Projects/crawl4ai-mcp-server/frontend/css-test-overlays.png',
      fullPage: true 
    });

    // Test z-index stacking context
    const zIndexTest = await page.evaluate(() => {
      const elements = document.querySelectorAll('[class*="test-overlay"], [class*="fixed"], [class*="z-"]');
      return Array.from(elements).map(el => {
        const computed = window.getComputedStyle(el);
        return {
          classes: el.className,
          zIndex: computed.zIndex,
          position: computed.position,
          display: computed.display
        };
      }).filter(item => item.zIndex !== 'auto');
    });

    console.log('Z-Index stacking context:', zIndexTest);
    console.log('=== CSS Isolation Test Complete ===');
  });
});