import { test, expect, Page } from '@playwright/test';

test.describe('Debug Bulk Save Issue', () => {
  test('debug bulk save step by step with screenshots', async ({ page }) => {
    console.log('=== Debugging Bulk Save Issue ===');

    // Navigate to the application
    await page.goto('/');
    await page.screenshot({ path: '/Users/florianwegener/Projects/crawl4ai-mcp-server/frontend/debug-step-1-homepage.png', fullPage: true });

    // Navigate to Deep Crawl page
    console.log('1. Navigating to Deep Crawl page');
    await page.click('text=Deep Crawl');
    await expect(page.locator('h1')).toContainText('Deep Website Crawling');
    await page.screenshot({ path: '/Users/florianwegener/Projects/crawl4ai-mcp-server/frontend/debug-step-2-deep-crawl-page.png', fullPage: true });

    // Fill in a simple domain for quick testing
    console.log('2. Filling in domain URL for testing');
    const urlInput = page.locator('input[placeholder*="https://example.com"]');
    await urlInput.fill('https://httpbin.org'); // Use httpbin for reliable testing

    // Set basic crawl parameters for quick testing
    console.log('3. Setting crawl parameters');
    const depthInput = page.locator('input[type="number"]').first();
    await depthInput.fill('1');

    const pagesInput = page.locator('input[type="number"]').nth(1);
    await pagesInput.fill('2');

    const strategySelect = page.locator('select').first();
    await strategySelect.selectOption('bfs');

    await page.screenshot({ path: '/Users/florianwegener/Projects/crawl4ai-mcp-server/frontend/debug-step-3-form-filled.png', fullPage: true });

    // Start the crawl
    console.log('4. Starting deep crawl');
    const startButton = page.locator('button:has-text("Start Deep Crawl")');
    await expect(startButton).toBeVisible();
    await expect(startButton).toBeEnabled();
    
    await startButton.click();

    // Wait for loading state
    try {
      await expect(page.locator('text=Crawling...')).toBeVisible({ timeout: 5000 });
      console.log('✓ Loading state appeared');
    } catch (error) {
      console.log('✗ Loading state did not appear');
    }

    await page.screenshot({ path: '/Users/florianwegener/Projects/crawl4ai-mcp-server/frontend/debug-step-4-crawling.png', fullPage: true });

    // Wait for results with detailed monitoring
    console.log('5. Waiting for crawl results');
    let crawlCompleted = false;
    let attempts = 0;
    const maxAttempts = 30;

    while (attempts < maxAttempts && !crawlCompleted) {
      attempts++;
      
      // Check for various completion indicators
      const completionIndicators = [
        'text=Deep Crawl Complete',
        'h3:has-text("Crawl Results")',
        '.bg-white:has(h3:contains("Crawl Results"))',
        'text=successful',
        'button:has-text("Bulk Save to Collection")'
      ];

      for (const indicator of completionIndicators) {
        if (await page.locator(indicator).isVisible()) {
          crawlCompleted = true;
          console.log(`✓ Found completion indicator: ${indicator}`);
          break;
        }
      }

      if (!crawlCompleted) {
        console.log(`Attempt ${attempts}/${maxAttempts} - Still waiting for results...`);
        await page.waitForTimeout(1000);
      }
    }

    await page.screenshot({ path: '/Users/florianwegener/Projects/crawl4ai-mcp-server/frontend/debug-step-5-after-crawl.png', fullPage: true });

    if (crawlCompleted) {
      console.log('✓ Crawl completed');
      
      // Analyze the current page state
      console.log('6. Analyzing page state');
      
      // Check for results sections
      const resultsSections = await page.locator('div:has(h3)').all();
      console.log(`Found ${resultsSections.length} sections with h3 headers`);

      // Look for specific elements that should be present
      const elements = {
        'Results header': 'h3:has-text("Crawl Results")',
        'Success count': 'text=successful',
        'Failed count': 'text=failed',
        'Select all checkbox': 'input[type="checkbox"]:has-text("Select All")',
        'Individual checkboxes': 'input[type="checkbox"]',
        'Bulk save button': 'button:has-text("Bulk Save to Collection")',
        'Results summary': '.bg-white:has-text("successful")',
      };

      console.log('Element visibility check:');
      for (const [name, selector] of Object.entries(elements)) {
        const isVisible = await page.locator(selector).isVisible();
        const count = await page.locator(selector).count();
        console.log(`  ${name}: visible=${isVisible}, count=${count}`);
      }

      // Get page content for analysis
      const pageContent = await page.content();
      console.log('Page content analysis:');
      console.log(`  Contains "Crawl Results": ${pageContent.includes('Crawl Results')}`);
      console.log(`  Contains "successful": ${pageContent.includes('successful')}`);
      console.log(`  Contains "Bulk Save to Collection": ${pageContent.includes('Bulk Save to Collection')}`);
      console.log(`  Contains checkbox inputs: ${pageContent.includes('type="checkbox"')}`);

      // Check React component state
      const componentState = await page.evaluate(() => {
        // Find elements that might indicate the component state
        const resultsContainer = document.querySelector('div:has(h3)');
        const checkboxes = document.querySelectorAll('input[type="checkbox"]');
        const buttons = document.querySelectorAll('button');
        const bulkSaveBtn = Array.from(buttons).find(btn => 
          btn.textContent?.includes('Bulk Save to Collection')
        );

        return {
          hasResultsContainer: !!resultsContainer,
          checkboxCount: checkboxes.length,
          buttonCount: buttons.length,
          bulkSaveButtonExists: !!bulkSaveBtn,
          bulkSaveButtonDisabled: bulkSaveBtn?.disabled,
          bulkSaveButtonVisible: bulkSaveBtn ? 
            getComputedStyle(bulkSaveBtn).display !== 'none' : false,
          selectedCheckboxes: Array.from(checkboxes).filter(cb => cb.checked).length
        };
      });

      console.log('Component state:', JSON.stringify(componentState, null, 2));

      // If we found checkboxes, try to select them
      if (componentState.checkboxCount > 0) {
        console.log('7. Attempting to select checkboxes');
        
        const checkboxes = page.locator('input[type="checkbox"]');
        const checkboxCount = await checkboxes.count();
        
        // Skip the "Select All" checkbox (usually the first one)
        for (let i = 1; i < checkboxCount && i <= 2; i++) {
          try {
            await checkboxes.nth(i).check();
            console.log(`✓ Checked checkbox ${i}`);
            await page.waitForTimeout(500); // Wait for state update
          } catch (error) {
            console.log(`✗ Failed to check checkbox ${i}: ${error}`);
          }
        }

        await page.screenshot({ path: '/Users/florianwegener/Projects/crawl4ai-mcp-server/frontend/debug-step-6-checkboxes-selected.png', fullPage: true });

        // Check component state after selection
        const stateAfterSelection = await page.evaluate(() => {
          const checkboxes = document.querySelectorAll('input[type="checkbox"]');
          const buttons = document.querySelectorAll('button');
          const bulkSaveBtn = Array.from(buttons).find(btn => 
            btn.textContent?.includes('Bulk Save to Collection')
          );

          return {
            selectedCheckboxes: Array.from(checkboxes).filter(cb => cb.checked).length,
            bulkSaveButtonExists: !!bulkSaveBtn,
            bulkSaveButtonDisabled: bulkSaveBtn?.disabled,
            bulkSaveButtonText: bulkSaveBtn?.textContent
          };
        });

        console.log('State after checkbox selection:', JSON.stringify(stateAfterSelection, null, 2));

        // Now try to find and click the bulk save button
        const bulkSaveButton = page.locator('button:has-text("Bulk Save to Collection")');
        if (await bulkSaveButton.isVisible()) {
          console.log('8. Found bulk save button - attempting to click');
          
          const isEnabled = await bulkSaveButton.isEnabled();
          console.log(`Bulk save button enabled: ${isEnabled}`);
          
          if (isEnabled) {
            await bulkSaveButton.click();
            console.log('✓ Clicked bulk save button');
            
            // Wait for modal
            await page.waitForTimeout(1000);
            await page.screenshot({ path: '/Users/florianwegener/Projects/crawl4ai-mcp-server/frontend/debug-step-7-after-bulk-save-click.png', fullPage: true });
            
            // Check if modal appeared
            const modalVisible = await page.locator('h3:has-text("Bulk Save to Collection")').isVisible();
            console.log(`Modal visible: ${modalVisible}`);
            
            if (modalVisible) {
              console.log('✓ Bulk save modal appeared successfully!');
              
              // Test modal functionality
              const collectionSelect = page.locator('[data-testid="bulk-collection-select"]');
              if (await collectionSelect.isVisible()) {
                await collectionSelect.selectOption('default');
                console.log('✓ Selected collection');
                
                const saveButton = page.locator('[data-testid="bulk-save-confirm"]');
                if (await saveButton.isVisible()) {
                  await saveButton.click();
                  console.log('✓ Clicked save in modal');
                  
                  await page.waitForTimeout(2000);
                  await page.screenshot({ path: '/Users/florianwegener/Projects/crawl4ai-mcp-server/frontend/debug-step-8-final-result.png', fullPage: true });
                }
              }
            } else {
              console.log('✗ Modal did not appear');
            }
          } else {
            console.log('✗ Bulk save button is disabled');
          }
        } else {
          console.log('✗ Bulk save button not found');
        }
      } else {
        console.log('✗ No checkboxes found to select');
      }
    } else {
      console.log('✗ Crawl did not complete within timeout');
    }

    // Final page state
    await page.screenshot({ path: '/Users/florianwegener/Projects/crawl4ai-mcp-server/frontend/debug-final-state.png', fullPage: true });

    console.log('=== Debug session complete ===');
  });
});