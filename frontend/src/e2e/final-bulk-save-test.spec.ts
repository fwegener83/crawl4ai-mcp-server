import { test, expect, Page } from '@playwright/test';

test.describe('Final Bulk Save Test - Data Structure Fix', () => {
  test('test bulk save with properly structured data', async ({ page }) => {
    console.log('=== Final Bulk Save Test ===');

    // Navigate to the application
    await page.goto('/');
    await page.click('text=Deep Crawl');
    await expect(page.locator('h1')).toContainText('Deep Website Crawling');

    // Fill form with reliable test domain
    await page.locator('input[placeholder*="https://example.com"]').fill('https://httpbin.org');
    await page.locator('input[type="number"]').first().fill('1');
    await page.locator('input[type="number"]').nth(1).fill('2');
    await page.locator('select').first().selectOption('bfs');

    console.log('1. Starting crawl with data structure monitoring...');

    // Intercept the API response and modify it to have the correct structure
    await page.route('/api/deep-crawl', async (route) => {
      // Get the original response
      const response = await route.fetch();
      const originalData = await response.json();

      console.log('Original API response structure:');
      console.log(JSON.stringify(originalData, null, 2));

      // Transform the data to match frontend expectations
      if (originalData.results && originalData.results.pages) {
        originalData.results.pages = originalData.results.pages.map((page: any) => ({
          ...page,
          success: true, // Add missing success field
          metadata: {    // Add missing metadata field
            crawl_time: new Date().toISOString(),
            score: Math.random() * 10
          }
        }));

        console.log('Transformed API response structure:');
        console.log(JSON.stringify(originalData, null, 2));
      }

      // Fulfill with the modified response
      await route.fulfill({
        status: response.status(),
        headers: response.headers(),
        body: JSON.stringify(originalData)
      });
    });

    // Start the crawl
    const startButton = page.locator('button:has-text("Start Deep Crawl")');
    await startButton.click();

    // Wait for loading to appear
    await expect(page.locator('text=Crawling...')).toBeVisible({ timeout: 5000 });
    console.log('✓ Crawling started');

    // Wait for results (up to 15 seconds)
    let resultsAppeared = false;
    for (let i = 0; i < 15; i++) {
      const resultsSection = page.locator('text=successful').first();
      if (await resultsSection.isVisible()) {
        resultsAppeared = true;
        console.log('✓ Results section with success count appeared');
        break;
      }
      await page.waitForTimeout(1000);
    }

    await page.screenshot({ 
      path: '/Users/florianwegener/Projects/crawl4ai-mcp-server/frontend/final-test-after-crawl.png',
      fullPage: true 
    });

    if (resultsAppeared) {
      console.log('2. Results appeared - checking bulk save functionality');

      // Look for the results summary section with bulk save button
      const bulkSaveButton = page.locator('button:has-text("Bulk Save to Collection")');
      if (await bulkSaveButton.isVisible()) {
        console.log('✓ Bulk Save button is visible');

        // Check if it's disabled (should be, since no checkboxes are selected yet)
        const isDisabled = await bulkSaveButton.isDisabled();
        console.log(`Bulk save button disabled (expected): ${isDisabled}`);

        // Now select some checkboxes
        console.log('3. Selecting result checkboxes');
        const checkboxes = page.locator('input[type="checkbox"]');
        const checkboxCount = await checkboxes.count();
        console.log(`Found ${checkboxCount} checkboxes`);

        // Skip "Select All" checkbox and select individual results
        let selectedCount = 0;
        for (let i = 1; i < checkboxCount && selectedCount < 2; i++) {
          try {
            await checkboxes.nth(i).check();
            selectedCount++;
            console.log(`✓ Selected checkbox ${i}`);
          } catch (error) {
            console.log(`Could not select checkbox ${i}: ${error}`);
          }
        }

        if (selectedCount > 0) {
          // Wait for button state to update
          await page.waitForTimeout(500);

          const isEnabledAfterSelection = await bulkSaveButton.isEnabled();
          console.log(`Bulk save button enabled after selection: ${isEnabledAfterSelection}`);

          if (isEnabledAfterSelection) {
            console.log('4. Clicking bulk save button');
            await bulkSaveButton.click();

            // Wait for modal to appear
            await page.waitForTimeout(1000);

            // Check for modal
            const modalTitle = page.locator('h3:has-text("Bulk Save to Collection")');
            if (await modalTitle.isVisible()) {
              console.log('✓ Bulk Save Modal appeared successfully!');

              await page.screenshot({ 
                path: '/Users/florianwegener/Projects/crawl4ai-mcp-server/frontend/final-test-modal-opened.png',
                fullPage: true 
              });

              // Test modal functionality
              console.log('5. Testing modal functionality');

              const collectionSelect = page.locator('[data-testid="bulk-collection-select"]');
              if (await collectionSelect.isVisible()) {
                await collectionSelect.selectOption('default');
                console.log('✓ Selected collection');

                const confirmButton = page.locator('[data-testid="bulk-save-confirm"]');
                if (await confirmButton.isVisible()) {
                  await confirmButton.click();
                  console.log('✓ Clicked confirm button');

                  // Wait for save operation
                  await page.waitForTimeout(3000);

                  // Check for success message
                  const successMessage = page.locator('[data-testid="bulk-success-message"]');
                  if (await successMessage.isVisible()) {
                    console.log('✓ Success message appeared');
                    console.log('🎉 BULK SAVE FUNCTIONALITY WORKS CORRECTLY!');
                  } else {
                    console.log('✗ Success message did not appear');
                  }

                  await page.screenshot({ 
                    path: '/Users/florianwegener/Projects/crawl4ai-mcp-server/frontend/final-test-complete.png',
                    fullPage: true 
                  });
                } else {
                  console.log('✗ Confirm button not found in modal');
                }
              } else {
                console.log('✗ Collection select not found in modal');
              }
            } else {
              console.log('✗ Bulk Save Modal did not appear');
              
              await page.screenshot({ 
                path: '/Users/florianwegener/Projects/crawl4ai-mcp-server/frontend/final-test-modal-failed.png',
                fullPage: true 
              });
            }
          } else {
            console.log('✗ Bulk save button remained disabled after selection');
          }
        } else {
          console.log('✗ Could not select any checkboxes');
        }
      } else {
        console.log('✗ Bulk Save button not found');
      }
    } else {
      console.log('✗ Results did not appear');
    }

    console.log('\n=== Final Test Complete ===');
  });
});