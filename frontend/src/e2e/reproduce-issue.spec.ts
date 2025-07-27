import { test, expect, Page } from '@playwright/test';

test.describe('Deep Crawl Issue Reproduction', () => {
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

  test('reproduce deep crawl issue with axoniq.io', async ({ page }) => {
    console.log('=== Starting Deep Crawl Issue Reproduction ===');

    // Navigate to Deep Crawl page
    console.log('1. Clicking on Deep Crawl navigation');
    await page.click('text=Deep Crawl');
    
    // Wait for the Deep Crawl page to load (no URL change since it's SPA)
    await expect(page.locator('h1')).toContainText('Deep Website Crawling');

    // Fill in the domain URL
    console.log('2. Entering domain URL: https://docs.axoniq.io/home/');
    const urlInput = page.locator('input[placeholder*="https://example.com"]');
    await urlInput.fill('https://docs.axoniq.io/home/');

    // Set max_depth to 10
    console.log('3. Setting max_depth to 10');
    const depthInput = page.locator('input[type="number"]').first();
    await depthInput.fill('10');

    // Set max_pages to 100
    console.log('4. Setting max_pages to 100');
    const pagesInput = page.locator('input[type="number"]').nth(1);
    await pagesInput.fill('100');

    // Set crawl_strategy to "bfs"
    console.log('5. Setting crawl_strategy to bfs');
    const strategySelect = page.locator('select').first();
    await strategySelect.selectOption('bfs');

    // Wait a moment for the form to be ready
    await page.waitForTimeout(1000);

    // Take a screenshot before clicking
    await page.screenshot({ path: '/Users/florianwegener/Projects/crawl4ai-mcp-server/frontend/before-crawl.png' });

    // Click the Start Deep Crawl button
    console.log('6. Clicking Start Deep Crawl button');
    const startButton = page.locator('button:has-text("Start Deep Crawl")');
    await expect(startButton).toBeVisible();
    await expect(startButton).toBeEnabled();
    
    // Start monitoring for the API request
    const apiRequestPromise = page.waitForRequest(request => 
      request.url().includes('/api/deep-crawl') || 
      request.url().includes('deep-crawl')
    );

    await startButton.click();

    console.log('7. Monitoring for loading state and API calls');
    
    // Check if loading state appears
    try {
      await expect(page.locator('text=Crawling...')).toBeVisible({ timeout: 5000 });
      console.log('✓ Loading state appeared');
    } catch (error) {
      console.log('✗ Loading state did not appear:', error);
    }

    // Wait for API request and capture it
    try {
      const apiRequest = await apiRequestPromise;
      console.log('✓ API request detected:', apiRequest.url());
      console.log('Request method:', apiRequest.method());
      console.log('Request headers:', apiRequest.headers());
      console.log('Request body:', apiRequest.postData());
    } catch (error) {
      console.log('✗ No API request detected within timeout:', error);
    }

    // Wait for response or error for up to 30 seconds
    console.log('8. Waiting for response or error (up to 30 seconds)');
    
    const startTime = Date.now();
    let finalState = 'unknown';
    
    while (Date.now() - startTime < 30000) {
      // Check for success message
      if (await page.locator('text=Deep Crawl Complete').isVisible()) {
        finalState = 'success';
        console.log('✓ Deep Crawl completed successfully');
        break;
      }
      
      // Check for error messages
      const errorMessages = [
        'Error occurred',
        'Failed to crawl',
        'Something went wrong',
        'Network error',
        'Timeout',
        'Unable to crawl'
      ];
      
      for (const errorText of errorMessages) {
        if (await page.locator(`text=${errorText}`).isVisible()) {
          finalState = 'error';
          console.log(`✗ Error detected: ${errorText}`);
          break;
        }
      }
      
      if (finalState === 'error') break;
      
      // Check if still loading
      if (await page.locator('text=Crawling...').isVisible()) {
        console.log('Still crawling...');
      }
      
      await page.waitForTimeout(1000);
    }

    // Take a screenshot after the operation
    await page.screenshot({ path: '/Users/florianwegener/Projects/crawl4ai-mcp-server/frontend/after-crawl.png' });

    // Log final state
    console.log(`9. Final state: ${finalState}`);

    // Print all captured console logs
    console.log('\n=== CONSOLE LOGS ===');
    consoleLogs.forEach(log => console.log(log));

    // Print console errors specifically
    if (consoleErrors.length > 0) {
      console.log('\n=== CONSOLE ERRORS ===');
      consoleErrors.forEach(error => console.log(error));
    }

    // Print network requests
    console.log('\n=== NETWORK REQUESTS ===');
    networkRequests.forEach(req => {
      console.log(`${req.method} ${req.url} at ${req.timestamp}`);
      if (req.postData) {
        console.log(`  Body: ${req.postData}`);
      }
    });

    // Print network responses
    console.log('\n=== NETWORK RESPONSES ===');
    networkResponses.forEach(res => {
      console.log(`${res.status} ${res.statusText} - ${res.url} at ${res.timestamp}`);
    });

    // Check for specific API failures
    const apiResponses = networkResponses.filter(res => 
      res.url.includes('/api/deep-crawl') || res.url.includes('deep-crawl')
    );
    
    if (apiResponses.length > 0) {
      console.log('\n=== API RESPONSES ===');
      apiResponses.forEach(res => {
        console.log(`Status: ${res.status} ${res.statusText}`);
        console.log(`URL: ${res.url}`);
        console.log(`Headers:`, res.headers);
      });
    } else {
      console.log('\n=== NO API RESPONSES DETECTED ===');
    }

    // Final assertions and reporting
    console.log('\n=== SUMMARY ===');
    console.log(`Total console logs: ${consoleLogs.length}`);
    console.log(`Console errors: ${consoleErrors.length}`);
    console.log(`Network requests: ${networkRequests.length}`);
    console.log(`Network responses: ${networkResponses.length}`);
    console.log(`Final state: ${finalState}`);

    // Don't fail the test - we want to capture the behavior
    // Just report what happened
  });
});