import { test, expect, Page } from '@playwright/test';

test.describe('API Debug Test', () => {
  test('debug API communication and network issues', async ({ page }) => {
    console.log('=== API Debug Test ===');

    let networkRequests: any[] = [];
    let networkResponses: any[] = [];

    // Capture all network traffic
    page.on('request', request => {
      networkRequests.push({
        url: request.url(),
        method: request.method(),
        headers: request.headers(),
        postData: request.postData(),
        timestamp: new Date().toISOString()
      });
    });

    page.on('response', response => {
      networkResponses.push({
        url: response.url(),
        status: response.status(),
        statusText: response.statusText(),
        headers: response.headers(),
        timestamp: new Date().toISOString()
      });
    });

    // Navigate to the application
    await page.goto('/');

    // Navigate to Deep Crawl page
    await page.click('text=Deep Crawl');
    await expect(page.locator('h1')).toContainText('Deep Website Crawling');

    // Fill form with simple parameters
    await page.locator('input[placeholder*="https://example.com"]').fill('https://httpbin.org');
    await page.locator('input[type="number"]').first().fill('1');
    await page.locator('input[type="number"]').nth(1).fill('1');
    await page.locator('select').first().selectOption('bfs');

    console.log('Starting crawl and monitoring network traffic...');

    // Start the crawl and monitor the API request
    const startButton = page.locator('button:has-text("Start Deep Crawl")');
    
    // Wait for the API request promise
    const apiRequestPromise = page.waitForRequest(
      request => request.url().includes('deep-crawl'),
      { timeout: 10000 }
    );

    const apiResponsePromise = page.waitForResponse(
      response => response.url().includes('deep-crawl'),
      { timeout: 15000 }
    );

    await startButton.click();

    try {
      // Wait for API request
      const apiRequest = await apiRequestPromise;
      console.log('✓ API Request sent:');
      console.log(`  URL: ${apiRequest.url()}`);
      console.log(`  Method: ${apiRequest.method()}`);
      console.log(`  Headers:`, apiRequest.headers());
      if (apiRequest.postData()) {
        console.log(`  Body:`, apiRequest.postData());
      }

      try {
        // Wait for API response
        const apiResponse = await apiResponsePromise;
        console.log('✓ API Response received:');
        console.log(`  Status: ${apiResponse.status()} ${apiResponse.statusText()}`);
        console.log(`  Headers:`, apiResponse.headers());
        
        // Try to get response body
        try {
          const responseText = await apiResponse.text();
          console.log(`  Body: ${responseText.substring(0, 500)}${responseText.length > 500 ? '...' : ''}`);
        } catch (error) {
          console.log(`  Body: Could not read response body - ${error}`);
        }

        // Analyze the response
        if (apiResponse.status() >= 200 && apiResponse.status() < 300) {
          console.log('✓ API response indicates success');
        } else {
          console.log(`✗ API response indicates error: ${apiResponse.status()}`);
        }

      } catch (error) {
        console.log('✗ API Response timeout or error:');
        console.log(`  Error: ${error}`);
        
        // Check if there are any error responses
        const errorResponses = networkResponses.filter(res => 
          res.url.includes('deep-crawl') && (res.status >= 400 || res.status === 0)
        );
        
        if (errorResponses.length > 0) {
          console.log('Found error responses:');
          errorResponses.forEach(res => {
            console.log(`  ${res.status} ${res.statusText} - ${res.url}`);
          });
        }
      }

    } catch (error) {
      console.log('✗ API Request failed or timeout:');
      console.log(`  Error: ${error}`);
    }

    // Wait a bit more to see if anything happens
    console.log('Waiting additional 5 seconds to observe any delayed responses...');
    await page.waitForTimeout(5000);

    // Analyze all network traffic
    console.log('\n=== NETWORK ANALYSIS ===');
    
    const apiRequests = networkRequests.filter(req => 
      req.url.includes('api/') || req.url.includes('deep-crawl')
    );
    
    const apiResponses = networkResponses.filter(res => 
      res.url.includes('api/') || res.url.includes('deep-crawl')
    );

    console.log(`Total network requests: ${networkRequests.length}`);
    console.log(`Total network responses: ${networkResponses.length}`);
    console.log(`API requests: ${apiRequests.length}`);
    console.log(`API responses: ${apiResponses.length}`);

    if (apiRequests.length > 0) {
      console.log('\nAPI Requests:');
      apiRequests.forEach((req, i) => {
        console.log(`  ${i + 1}. ${req.method} ${req.url}`);
        console.log(`     Time: ${req.timestamp}`);
        if (req.postData) {
          console.log(`     Body: ${req.postData}`);
        }
      });
    }

    if (apiResponses.length > 0) {
      console.log('\nAPI Responses:');
      apiResponses.forEach((res, i) => {
        console.log(`  ${i + 1}. ${res.status} ${res.statusText} - ${res.url}`);
        console.log(`     Time: ${res.timestamp}`);
      });
    } else {
      console.log('\nNo API responses received - this indicates backend connectivity issues');
    }

    // Check for common network error patterns
    const networkErrors = networkResponses.filter(res => 
      res.status === 0 || res.status >= 500 || res.statusText.includes('ECONNREFUSED')
    );

    if (networkErrors.length > 0) {
      console.log('\nNetwork Errors Detected:');
      networkErrors.forEach(err => {
        console.log(`  ${err.status} ${err.statusText} - ${err.url}`);
      });
    }

    // Check if backend might be running on different port
    const possibleBackendPorts = [8000, 3000, 5000, 8080, 9000];
    console.log('\nBackend connectivity diagnosis:');
    console.log('Current frontend is running on: http://localhost:5174');
    console.log('API requests are being sent to: /api/deep-crawl (relative to frontend)');
    console.log('This resolves to: http://localhost:5174/api/deep-crawl');
    console.log('');
    console.log('Possible issues:');
    console.log('1. MCP server is not running');
    console.log('2. MCP server is running on different port than expected');
    console.log('3. Frontend proxy configuration is incorrect');
    console.log('4. CORS issues preventing API communication');
    console.log('');
    console.log('To fix:');
    console.log('1. Ensure crawl4ai-mcp-server is running: python -m crawl4ai_mcp_server');
    console.log('2. Check if frontend proxy in vite.config.ts points to correct backend port');
    console.log('3. Verify no firewall/network issues blocking connections');

    // Take final screenshot
    await page.screenshot({ 
      path: '/Users/florianwegener/Projects/crawl4ai-mcp-server/frontend/api-debug-final.png',
      fullPage: true 
    });

    console.log('\n=== API Debug Complete ===');
  });
});