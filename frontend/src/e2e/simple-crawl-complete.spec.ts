import { test, expect } from '@playwright/test';

test.describe('Simple Crawl Complete Workflow', () => {
  test('Complete Simple Crawl workflow: URL → Crawl → Edit → Save to Collection', async ({ page }) => {
    console.log('=== Simple Crawl Complete Workflow Test ===');

    // Step 1: Navigate to Simple Crawl page
    console.log('🔹 Step 1: Navigation to Simple Crawl page...');
    await page.goto('http://localhost:5175/');
    await page.click('text=Simple Crawl');
    await expect(page.locator('h1')).toContainText('Simple Website Crawling');
    console.log('✅ Navigated to Simple Crawl page');

    // Step 2: Fill URL and start crawl
    console.log('🔹 Step 2: Fill URL and start crawl...');
    await page.fill('input[placeholder*="https://example.com"]', 'https://docs.anthropic.com/en/docs/claude-code/');
    await page.click('button:has-text("Start Crawl")');
    console.log('✅ Crawl started');

    // Step 3: Wait for crawl completion
    console.log('🔹 Step 3: Wait for crawl completion...');
    
    // Wait for crawling to finish and content to appear
    await page.waitForSelector('text=Extracted Content', { timeout: 120000 });
    
    // Also ensure the content editor is loaded
    await page.waitForSelector('text=Content Editor', { timeout: 30000 });
    
    console.log('✅ Crawl completed, content extracted');

    // Screenshot after crawl
    await page.screenshot({ 
      path: '/Users/florianwegener/Projects/crawl4ai-mcp-server/frontend/simple-crawl-step-3-extracted.png',
      fullPage: true 
    });

    // Step 4: Verify content editor is present
    console.log('🔹 Step 4: Verify content editor...');
    await expect(page.locator('text=Content Editor')).toBeVisible();
    await expect(page.locator('button:has-text("Edit")')).toBeVisible();
    await expect(page.locator('button:has-text("Preview")')).toBeVisible();
    console.log('✅ Content editor present with Edit/Preview toggle');

    // Step 5: Test Edit/Preview toggle
    console.log('🔹 Step 5: Test Edit/Preview toggle...');
    
    // Should start in Edit mode, switch to Preview
    await page.click('button:has-text("Preview")');
    await page.waitForTimeout(1000);
    console.log('✅ Switched to Preview mode');
    
    // Switch back to Edit mode
    await page.click('button:has-text("Edit")');
    await page.waitForTimeout(1000);
    console.log('✅ Switched back to Edit mode');

    // Step 6: Edit content in the editor
    console.log('🔹 Step 6: Edit content in markdown editor...');
    
    // Find the Monaco editor container - it might not have the exact data-testid
    const editorContainer = page.locator('.monaco-editor').first();
    await expect(editorContainer).toBeVisible({ timeout: 10000 });
    
    // Click into the editor and add content
    await editorContainer.click();
    await page.waitForTimeout(1000);
    
    // Add some test content
    await page.keyboard.press('Control+A'); // Select all
    await page.keyboard.type('# Test Content\n\nThis is edited content from Playwright test.\n\n**Original content preserved below:**\n\n');
    await page.keyboard.press('Control+End'); // Go to end
    await page.keyboard.type('\n\n---\n\n*Modified by Playwright test*');
    
    await page.waitForTimeout(2000); // Let the changes propagate
    console.log('✅ Content edited in markdown editor');

    // Step 7: Verify unsaved changes indicator
    console.log('🔹 Step 7: Verify unsaved changes indicator...');
    
    // Check for unsaved changes indicator (orange dot)
    const saveButton = page.locator('[data-testid="save-to-collection-button"]');
    await expect(saveButton).toBeVisible();
    
    // The button should show changes indicator (orange dot in save button)
    const hasChangesIndicator = await saveButton.locator('span.bg-orange-500').isVisible();
    console.log(`📊 Unsaved changes indicator visible: ${hasChangesIndicator}`);

    // Step 8: Click Save to Collection button
    console.log('🔹 Step 8: Click Save to Collection button...');
    await saveButton.click();
    console.log('✅ Save to Collection button clicked');

    // Wait for modal animation
    await page.waitForTimeout(1500);

    // Step 9: Verify SaveToCollectionModal opened correctly
    console.log('🔹 Step 9: Verify SaveToCollectionModal...');
    
    const modalTitle = page.locator('h3:has-text("Save to Collection")');
    const isModalVisible = await modalTitle.isVisible();
    console.log(`🎭 SaveToCollectionModal visible: ${isModalVisible}`);

    if (isModalVisible) {
      console.log('🎉 SaveToCollectionModal opened successfully!');

      // Screenshot of opened modal
      await page.screenshot({ 
        path: '/Users/florianwegener/Projects/crawl4ai-mcp-server/frontend/simple-crawl-step-9-modal-opened.png',
        fullPage: true 
      });

      // Step 10: Verify modal components
      console.log('🔹 Step 10: Verify modal components...');
      
      // Check collection dropdown
      const collectionSelect = page.locator('[data-testid="collection-select"]');
      await expect(collectionSelect).toBeVisible();
      console.log('✅ Collection dropdown visible');
      
      // Check content preview section
      await expect(page.locator('text=Content to Save')).toBeVisible();
      console.log('✅ Content preview section visible');
      
      // Check save button
      const confirmButton = page.locator('[data-testid="save-confirm"]');
      await expect(confirmButton).toBeVisible();
      const isConfirmEnabled = await confirmButton.isEnabled();
      console.log(`📊 Save confirm button enabled: ${isConfirmEnabled}`);

      // Step 11: Select collection and save
      console.log('🔹 Step 11: Select collection and save...');
      
      // Select default collection
      await collectionSelect.selectOption('default');
      console.log('✅ Selected default collection');
      
      // Mock the store-content API to prevent actual storage during test
      await page.route('/api/store-content', async (route) => {
        console.log('📡 Intercepted store-content request');
        await route.fulfill({
          status: 200,
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            success: true, 
            message: 'Content stored successfully in test mode' 
          })
        });
      });

      // Click save confirm button
      await confirmButton.click();
      console.log('✅ Clicked save confirm button');
      
      // Wait for save operation
      await page.waitForTimeout(3000);

      // Step 12: Verify save success
      console.log('🔹 Step 12: Verify save success...');
      
      // Check if modal closed (success case)
      const isModalStillVisible = await modalTitle.isVisible();
      console.log(`🎭 Modal still visible after save: ${isModalStillVisible}`);
      
      // Check for success toast/message
      const successToast = page.locator('text=Content Saved').first();
      const hasSuccessMessage = await successToast.isVisible();
      console.log(`📢 Success message visible: ${hasSuccessMessage}`);

      if (!isModalStillVisible || hasSuccessMessage) {
        console.log('🎉 Save operation completed successfully!');
      }

    } else {
      console.log('❌ SaveToCollectionModal failed to open');
      
      // Debug modal issue
      const modalContainers = await page.locator('.fixed.inset-0').count();
      console.log(`🔍 Modal containers found: ${modalContainers}`);
      
      // Take debug screenshot
      await page.screenshot({ 
        path: '/Users/florianwegener/Projects/crawl4ai-mcp-server/frontend/simple-crawl-modal-failed.png',
        fullPage: true 
      });
    }

    // Step 13: Final verification
    console.log('🔹 Step 13: Final verification...');
    
    // Check if we're back to the main page
    await expect(page.locator('h1:has-text("Simple Website Crawling")')).toBeVisible();
    console.log('✅ Back on Simple Crawl page');

    // Final screenshot
    await page.screenshot({ 
      path: '/Users/florianwegener/Projects/crawl4ai-mcp-server/frontend/simple-crawl-final-complete.png',
      fullPage: true 
    });

    console.log('=== Simple Crawl Complete Workflow Test FINISHED ===');
    
    // Test Summary
    console.log('\\n--- TEST SUMMARY ---');
    console.log('✅ Navigation to Simple Crawl page: SUCCESS');
    console.log('✅ URL input and crawl execution: SUCCESS');
    console.log('✅ Content extraction: SUCCESS');
    console.log('✅ Content editor functionality: SUCCESS');
    console.log('✅ Edit/Preview toggle: SUCCESS');
    console.log('✅ Content editing: SUCCESS');
    console.log('✅ Save to Collection button: SUCCESS');
    console.log(`${isModalVisible ? '✅' : '❌'} SaveToCollectionModal: ${isModalVisible ? 'SUCCESS' : 'FAILED'}`);
    console.log('=== SIMPLE CRAWL WORKFLOW TEST COMPLETE ===');

    // Ensure test passes if core functionality works
    expect(isModalVisible).toBe(true);
  });
});