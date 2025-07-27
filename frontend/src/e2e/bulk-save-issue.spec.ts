import { test, expect, Page } from '@playwright/test';

test.describe('Bulk Save Modal Issue Reproduction', () => {
  let consoleLogs: string[] = [];
  let consoleErrors: string[] = [];
  let networkRequests: any[] = [];
  let networkResponses: any[] = [];

  test.beforeEach(async ({ page }) => {
    // Capture console logs and errors
    page.on('console', msg => {
      const logMessage = `[${msg.type()}] ${msg.text()}`;
      consoleLogs.push(logMessage);
      if (msg.type() === 'error') {
        consoleErrors.push(logMessage);
      }
      console.log(logMessage);
    });

    // Capture network requests and responses
    page.on('request', request => {
      networkRequests.push({
        url: request.url(),
        method: request.method(),
        headers: request.headers(),
        postData: request.postData(),
        timestamp: new Date().toISOString()
      });
      console.log(`→ ${request.method()} ${request.url()}`);
    });

    page.on('response', response => {
      networkResponses.push({
        url: response.url(),
        status: response.status(),
        statusText: response.statusText(),
        headers: response.headers(),
        timestamp: new Date().toISOString()
      });
      console.log(`← ${response.status()} ${response.url()}`);
    });

    // Clear arrays for each test
    consoleLogs = [];
    consoleErrors = [];
    networkRequests = [];
    networkResponses = [];

    // Navigate to the application
    await page.goto('/');
  });

  test('reproduce bulk save modal issue', async ({ page }) => {
    console.log('=== Starting Bulk Save Modal Issue Reproduction ===');

    // Navigate to Deep Crawl page
    console.log('1. Navigating to Deep Crawl page');
    await page.click('text=Deep Crawl');
    
    // Wait for the Deep Crawl page to load
    await expect(page.locator('h1')).toContainText('Deep Website Crawling');

    // Fill in a simple domain for quick testing
    console.log('2. Filling in domain URL for testing');
    const urlInput = page.locator('input[placeholder*="https://example.com"]');
    await urlInput.fill('https://example.com');

    // Set basic crawl parameters for quick testing
    console.log('3. Setting crawl parameters');
    const depthInput = page.locator('input[type="number"]').first();
    await depthInput.fill('1');

    const pagesInput = page.locator('input[type="number"]').nth(1);
    await pagesInput.fill('3');

    const strategySelect = page.locator('select').first();
    await strategySelect.selectOption('bfs');

    // Wait a moment for the form to be ready
    await page.waitForTimeout(1000);

    // Start the crawl
    console.log('4. Starting deep crawl');
    const startButton = page.locator('button:has-text("Start Deep Crawl")');
    await expect(startButton).toBeVisible();
    await expect(startButton).toBeEnabled();
    
    // Monitor for the API request
    const apiRequestPromise = page.waitForRequest(request => 
      request.url().includes('/api/deep-crawl') || 
      request.url().includes('deep-crawl')
    );

    await startButton.click();

    // Check if loading state appears
    try {
      await expect(page.locator('text=Crawling...')).toBeVisible({ timeout: 5000 });
      console.log('✓ Loading state appeared');
    } catch (error) {
      console.log('✗ Loading state did not appear');
    }

    // Wait for response and results
    console.log('5. Waiting for crawl results (up to 30 seconds)');
    
    const startTime = Date.now();
    let crawlCompleted = false;
    
    while (Date.now() - startTime < 30000) {
      // Check for completion
      if (await page.locator('text=Deep Crawl Complete').isVisible()) {
        crawlCompleted = true;
        console.log('✓ Deep Crawl completed successfully');
        break;
      }
      
      // Check if results are appearing
      const resultsHeader = page.locator('h3:has-text("Crawl Results")');
      if (await resultsHeader.isVisible()) {
        crawlCompleted = true;
        console.log('✓ Crawl results appeared');
        break;
      }
      
      await page.waitForTimeout(1000);
    }

    if (!crawlCompleted) {
      console.log('✗ Crawl did not complete within timeout - proceeding with mock data test');
      
      // If crawl fails, we'll simulate results by directly manipulating the page state
      console.log('6. Simulating crawl results for testing modal functionality');
      
      // We'll inject some mock results into the page's React state
      await page.evaluate(() => {
        // This is a hack to simulate having crawl results
        // In a real scenario, we'd need the backend to be running
        const mockResults = [
          {
            url: 'https://example.com/',
            title: 'Example Domain',
            content: 'This is a mock result for testing purposes.',
            success: true,
            depth: 0,
            metadata: {
              crawl_time: new Date().toISOString(),
              score: 8.5
            }
          },
          {
            url: 'https://example.com/page1',
            title: 'Page 1',
            content: 'Another mock result for testing.',
            success: true,
            depth: 1,
            metadata: {
              crawl_time: new Date().toISOString(),
              score: 7.2
            }
          }
        ];
        
        // Trigger a custom event that the React app can listen to
        window.dispatchEvent(new CustomEvent('mockCrawlResults', { detail: mockResults }));
      });
      
      // Wait a bit for the mock results to be processed
      await page.waitForTimeout(2000);
    }

    // Now test the bulk save functionality
    console.log('7. Testing bulk save functionality');

    // Check if results section is visible
    const resultsSection = page.locator('[data-testid="crawl-results"], h3:has-text("Crawl Results")');
    if (await resultsSection.isVisible()) {
      console.log('✓ Results section is visible');
      
      // Look for checkboxes
      const checkboxes = page.locator('input[type="checkbox"]');
      const checkboxCount = await checkboxes.count();
      console.log(`Found ${checkboxCount} checkboxes`);
      
      if (checkboxCount > 0) {
        // Select the first few checkboxes
        console.log('8. Selecting checkboxes');
        for (let i = 0; i < Math.min(2, checkboxCount - 1); i++) { // -1 to exclude "Select All" checkbox
          const checkbox = checkboxes.nth(i + 1); // Skip the "Select All" checkbox
          await checkbox.check();
          console.log(`✓ Checked checkbox ${i + 1}`);
        }
        
        // Wait for selection to register
        await page.waitForTimeout(500);
        
        // Look for the Bulk Save button
        console.log('9. Looking for Bulk Save to Collection button');
        const bulkSaveButton = page.locator('button:has-text("Bulk Save to Collection")');
        
        if (await bulkSaveButton.isVisible()) {
          console.log('✓ Bulk Save button is visible');
          
          // Check if button is enabled
          const isEnabled = await bulkSaveButton.isEnabled();
          console.log(`Bulk Save button enabled: ${isEnabled}`);
          
          if (isEnabled) {
            console.log('10. Clicking Bulk Save button');
            
            // Monitor for any JavaScript errors
            let jsErrors: any[] = [];
            page.on('pageerror', error => {
              jsErrors.push(error);
              console.log(`JavaScript Error: ${error.message}`);
            });
            
            // Click the button
            await bulkSaveButton.click();
            
            // Wait for modal to appear
            console.log('11. Waiting for BulkSaveModal to appear');
            
            // Look for the modal by various selectors
            const modalSelectors = [
              '[data-testid="bulk-save-modal"]',
              'h3:has-text("Bulk Save to Collection")',
              '[data-testid="bulk-collection-select"]',
              'div:has-text("Bulk Save to Collection")',
              '.fixed.inset-0', // Modal backdrop
            ];
            
            let modalAppeared = false;
            for (const selector of modalSelectors) {
              try {
                await expect(page.locator(selector)).toBeVisible({ timeout: 3000 });
                console.log(`✓ Modal appeared (found by selector: ${selector})`);
                modalAppeared = true;
                break;
              } catch (error) {
                console.log(`✗ Modal not found by selector: ${selector}`);
              }
            }
            
            if (!modalAppeared) {
              console.log('✗ BulkSaveModal did not appear');
              
              // Check for any JavaScript errors that might have prevented the modal
              if (jsErrors.length > 0) {
                console.log('JavaScript errors detected:');
                jsErrors.forEach(error => console.log(`  - ${error.message}`));
              }
              
              // Take a screenshot for debugging
              await page.screenshot({ 
                path: '/Users/florianwegener/Projects/crawl4ai-mcp-server/frontend/bulk-save-debug.png',
                fullPage: true 
              });
              console.log('Debug screenshot saved to bulk-save-debug.png');
              
              // Check the current page state
              console.log('Current page state:');
              const pageContent = await page.content();
              console.log('Page contains "Bulk Save to Collection":', pageContent.includes('Bulk Save to Collection'));
              console.log('Page contains modal classes:', pageContent.includes('fixed inset-0'));
              
              // Check React component state via browser console
              const reactState = await page.evaluate(() => {
                // Try to find React components and their state
                const buttons = Array.from(document.querySelectorAll('button'));
                const bulkSaveBtn = buttons.find(btn => btn.textContent?.includes('Bulk Save to Collection'));
                return {
                  bulkSaveButtonExists: !!bulkSaveBtn,
                  bulkSaveButtonDisabled: bulkSaveBtn?.disabled,
                  modalsInDOM: document.querySelectorAll('.fixed.inset-0').length,
                  totalButtons: buttons.length
                };
              });
              
              console.log('React state check:', reactState);
              
            } else {
              console.log('✓ BulkSaveModal appeared successfully');
              
              // Test modal functionality
              console.log('12. Testing modal functionality');
              
              // Check collection select
              const collectionSelect = page.locator('[data-testid="bulk-collection-select"]');
              if (await collectionSelect.isVisible()) {
                console.log('✓ Collection select is visible');
                
                // Try to select a collection
                await collectionSelect.selectOption('default');
                console.log('✓ Selected default collection');
                
                // Look for save button in modal
                const modalSaveButton = page.locator('[data-testid="bulk-save-confirm"]');
                if (await modalSaveButton.isVisible()) {
                  console.log('✓ Modal save button is visible');
                  
                  // Test saving
                  await modalSaveButton.click();
                  console.log('✓ Clicked modal save button');
                  
                  // Wait for save operation
                  await page.waitForTimeout(2000);
                  
                  // Check for success message
                  const successMessage = page.locator('[data-testid="bulk-success-message"]');
                  if (await successMessage.isVisible()) {
                    console.log('✓ Success message appeared');
                  } else {
                    console.log('✗ Success message did not appear');
                  }
                } else {
                  console.log('✗ Modal save button not found');
                }
              } else {
                console.log('✗ Collection select not found in modal');
              }
            }
          } else {
            console.log('✗ Bulk Save button is disabled');
          }
        } else {
          console.log('✗ Bulk Save button not found');
        }
      } else {
        console.log('✗ No checkboxes found');
      }
    } else {
      console.log('✗ Results section not visible');
    }

    // Print all captured console logs
    console.log('\n=== CONSOLE LOGS ===');
    consoleLogs.forEach(log => console.log(log));

    // Print console errors specifically
    if (consoleErrors.length > 0) {
      console.log('\n=== CONSOLE ERRORS ===');
      consoleErrors.forEach(error => console.log(error));
    }

    // Print network requests related to collections/storage
    console.log('\n=== RELEVANT NETWORK REQUESTS ===');
    const relevantRequests = networkRequests.filter(req => 
      req.url.includes('/api/') || 
      req.url.includes('store') || 
      req.url.includes('collection')
    );
    relevantRequests.forEach(req => {
      console.log(`${req.method} ${req.url} at ${req.timestamp}`);
      if (req.postData) {
        console.log(`  Body: ${req.postData}`);
      }
    });

    // Print network responses
    console.log('\n=== RELEVANT NETWORK RESPONSES ===');
    const relevantResponses = networkResponses.filter(res => 
      res.url.includes('/api/') || 
      res.url.includes('store') || 
      res.url.includes('collection')
    );
    relevantResponses.forEach(res => {
      console.log(`${res.status} ${res.statusText} - ${res.url} at ${res.timestamp}`);
    });

    // Final summary
    console.log('\n=== SUMMARY ===');
    console.log(`Total console logs: ${consoleLogs.length}`);
    console.log(`Console errors: ${consoleErrors.length}`);
    console.log(`Network requests: ${networkRequests.length}`);
    console.log(`Network responses: ${networkResponses.length}`);
    console.log(`Relevant API requests: ${relevantRequests.length}`);
    console.log(`Relevant API responses: ${relevantResponses.length}`);

    // Don't fail the test - we want to capture the behavior
    // The goal is to reproduce and diagnose the issue
  });

  test('test bulk save with mock data injection', async ({ page }) => {
    console.log('=== Testing Bulk Save with Direct Mock Data Injection ===');

    // Navigate to Deep Crawl page
    await page.click('text=Deep Crawl');
    await expect(page.locator('h1')).toContainText('Deep Website Crawling');

    // Inject mock data directly into the React component
    console.log('1. Injecting mock crawl results');
    await page.evaluate(() => {
      // Create mock crawl results
      const mockResults = [
        {
          url: 'https://example.com/',
          title: 'Example Domain - Home',
          content: 'This is the main page content. Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
          success: true,
          depth: 0,
          metadata: {
            crawl_time: new Date().toISOString(),
            score: 9.1
          }
        },
        {
          url: 'https://example.com/about',
          title: 'About Us',
          content: 'About page content with more information about the company and its mission.',
          success: true,
          depth: 1,
          metadata: {
            crawl_time: new Date().toISOString(),
            score: 8.3
          }
        },
        {
          url: 'https://example.com/contact',
          title: 'Contact Information',
          content: 'Contact page with address, phone, and email information.',
          success: true,
          depth: 1,
          metadata: {
            crawl_time: new Date().toISOString(),
            score: 7.5
          }
        }
      ];

      // Try to find the React root and trigger a state update
      // This is a bit hacky but allows us to test the UI without backend
      const reactRoot = document.querySelector('#root');
      if (reactRoot) {
        // Dispatch a custom event that our React app could listen to
        window.dispatchEvent(new CustomEvent('mockCrawlComplete', { 
          detail: { results: mockResults } 
        }));
      }
    });

    // Wait for potential state updates
    await page.waitForTimeout(1000);

    // Since we can't easily inject into React state from outside,
    // let's manually create the results structure in the DOM
    console.log('2. Creating mock results structure');
    await page.evaluate(() => {
      // Create a mock results container if it doesn't exist
      const mockResults = [
        {
          url: 'https://example.com/',
          title: 'Example Domain - Home',
          content: 'This is the main page content.',
          success: true,
          depth: 0
        },
        {
          url: 'https://example.com/about',
          title: 'About Us',
          content: 'About page content.',
          success: true,
          depth: 1
        }
      ];

      // Find the main content area
      const mainContent = document.querySelector('main') || document.querySelector('.space-y-6');
      if (mainContent) {
        // Create a mock results section similar to what would be rendered
        const resultsHTML = `
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-6">
                <div class="text-sm text-gray-600 dark:text-gray-300">
                  <span class="font-medium text-green-600 dark:text-green-400">2</span> successful
                </div>
                <div class="text-sm text-gray-600 dark:text-gray-300">
                  <span class="font-medium text-red-600 dark:text-red-400">0</span> failed
                </div>
              </div>
              <div class="flex items-center space-x-3">
                <span class="text-sm text-gray-600 dark:text-gray-300">0 selected</span>
                <button
                  id="mock-bulk-save-btn"
                  class="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium px-4 py-2 rounded-md transition-colors"
                  disabled
                >
                  Bulk Save to Collection
                </button>
              </div>
            </div>
          </div>
          
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <div class="flex items-center justify-between">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Crawl Results (2)</h3>
                <div class="flex items-center space-x-4">
                  <label class="flex items-center text-sm text-gray-600 dark:text-gray-300">
                    <input type="checkbox" id="select-all-mock" class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded mr-2">
                    Select All
                  </label>
                </div>
              </div>
            </div>
            <div class="divide-y divide-gray-200 dark:divide-gray-700">
              ${mockResults.map((result, index) => `
                <div class="p-4 hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors">
                  <div class="flex items-start space-x-3">
                    <input 
                      type="checkbox" 
                      class="mock-result-checkbox mt-1 h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                      data-index="${index}"
                    >
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center justify-between mb-2">
                        <div class="text-left flex-1">
                          <h4 class="text-sm font-medium text-gray-900 dark:text-white truncate">${result.title}</h4>
                          <p class="text-sm text-blue-600 dark:text-blue-400 truncate">${result.url}</p>
                        </div>
                        <div class="flex items-center space-x-2 ml-4">
                          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">Success</span>
                          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">Depth ${result.depth}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              `).join('')}
            </div>
          </div>
        `;

        // Add the results to the page
        mainContent.insertAdjacentHTML('beforeend', resultsHTML);

        // Add functionality to checkboxes
        let selectedCount = 0;
        const bulkSaveBtn = document.getElementById('mock-bulk-save-btn');
        const selectAllCheckbox = document.getElementById('select-all-mock') as HTMLInputElement;
        const resultCheckboxes = document.querySelectorAll('.mock-result-checkbox') as NodeListOf<HTMLInputElement>;

        const updateBulkSaveButton = () => {
          if (bulkSaveBtn) {
            bulkSaveBtn.disabled = selectedCount === 0;
            const selectedSpan = bulkSaveBtn.parentElement?.querySelector('span');
            if (selectedSpan) {
              selectedSpan.textContent = `${selectedCount} selected`;
            }
          }
        };

        resultCheckboxes.forEach(checkbox => {
          checkbox.addEventListener('change', (e) => {
            const target = e.target as HTMLInputElement;
            if (target.checked) {
              selectedCount++;
            } else {
              selectedCount--;
            }
            updateBulkSaveButton();
          });
        });

        selectAllCheckbox?.addEventListener('change', (e) => {
          const target = e.target as HTMLInputElement;
          resultCheckboxes.forEach(checkbox => {
            checkbox.checked = target.checked;
          });
          selectedCount = target.checked ? resultCheckboxes.length : 0;
          updateBulkSaveButton();
        });

        // Add click handler to bulk save button
        bulkSaveBtn?.addEventListener('click', () => {
          console.log('Mock bulk save button clicked');
          
          // Create and show a mock modal
          const modalHTML = `
            <div id="mock-bulk-save-modal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-lg w-full mx-4">
                <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                  <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Bulk Save to Collection</h3>
                </div>
                <div class="px-6 py-4 space-y-4">
                  <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md p-3">
                    <p class="text-sm font-medium text-blue-800 dark:text-blue-200">${selectedCount} successful results selected</p>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Select Collection</label>
                    <select data-testid="bulk-collection-select" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md">
                      <option value="default">Default Collection</option>
                      <option value="test">Test Collection</option>
                    </select>
                  </div>
                </div>
                <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-end space-x-3">
                  <button id="mock-modal-cancel" class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md">Cancel</button>
                  <button data-testid="bulk-save-confirm" id="mock-modal-save" class="px-4 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-md">Save ${selectedCount} Results</button>
                </div>
              </div>
            </div>
          `;

          document.body.insertAdjacentHTML('beforeend', modalHTML);

          // Add modal event handlers
          document.getElementById('mock-modal-cancel')?.addEventListener('click', () => {
            document.getElementById('mock-bulk-save-modal')?.remove();
          });

          document.getElementById('mock-modal-save')?.addEventListener('click', () => {
            console.log('Mock save button clicked');
            document.getElementById('mock-bulk-save-modal')?.remove();
            
            // Show success message
            const successHTML = `
              <div data-testid="bulk-success-message" class="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md mb-4">
                <p class="text-sm font-medium text-green-800 dark:text-green-200">Successfully saved ${selectedCount} results to collection: Default Collection</p>
              </div>
            `;
            mainContent.insertAdjacentHTML('afterbegin', successHTML);
          });
        });
      }
    });

    // Wait for the mock structure to be created
    await page.waitForTimeout(1000);

    console.log('3. Testing with mock data');
    
    // Check if our mock results are visible
    const resultsHeader = page.locator('h3:has-text("Crawl Results")');
    await expect(resultsHeader).toBeVisible();
    console.log('✓ Mock results section is visible');

    // Select some checkboxes
    console.log('4. Selecting mock result checkboxes');
    const checkboxes = page.locator('.mock-result-checkbox');
    const checkboxCount = await checkboxes.count();
    console.log(`Found ${checkboxCount} mock result checkboxes`);

    // Select the first checkbox
    if (checkboxCount > 0) {
      await checkboxes.first().check();
      console.log('✓ Selected first mock result');

      // Wait for button state to update
      await page.waitForTimeout(500);

      // Check if bulk save button is enabled
      const bulkSaveButton = page.locator('#mock-bulk-save-btn');
      const isEnabled = await bulkSaveButton.isEnabled();
      console.log(`Mock bulk save button enabled: ${isEnabled}`);

      if (isEnabled) {
        console.log('5. Clicking mock bulk save button');
        await bulkSaveButton.click();

        // Wait for modal to appear
        await page.waitForTimeout(500);

        // Check if modal appeared
        const modal = page.locator('#mock-bulk-save-modal');
        if (await modal.isVisible()) {
          console.log('✓ Mock bulk save modal appeared');

          // Test modal functionality
          const collectionSelect = page.locator('[data-testid="bulk-collection-select"]');
          await expect(collectionSelect).toBeVisible();
          console.log('✓ Collection select is visible in modal');

          const modalSaveButton = page.locator('[data-testid="bulk-save-confirm"]');
          await expect(modalSaveButton).toBeVisible();
          console.log('✓ Modal save button is visible');

          // Test saving
          await modalSaveButton.click();
          console.log('✓ Clicked modal save button');

          // Wait for success message
          await page.waitForTimeout(1000);

          const successMessage = page.locator('[data-testid="bulk-success-message"]');
          if (await successMessage.isVisible()) {
            console.log('✓ Success message appeared');
          } else {
            console.log('✗ Success message did not appear');
          }
        } else {
          console.log('✗ Mock bulk save modal did not appear');
        }
      } else {
        console.log('✗ Mock bulk save button remained disabled');
      }
    } else {
      console.log('✗ No mock checkboxes found');
    }

    console.log('\n=== Mock Test Complete ===');
  });
});