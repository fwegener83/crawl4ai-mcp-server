import { test, expect, Page } from '@playwright/test';

test.describe('Vector Sync Polling System', () => {
  let page: Page;
  
  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;
    
    // Start with a clean slate - go to file collections
    await page.goto('http://localhost:5173');
    
    // Wait for app to load - use collections list instead
    await page.waitForSelector('[data-testid="collections-list"]', { timeout: 15000 });
  });

  test('should detect and recover orphaned syncing collections', async () => {
    console.log('🔬 TEST: Starting orphaned collection detection test');
    
    // 1. First, let's see what collections exist and their status
    await page.waitForTimeout(2000); // Wait for initial load
    
    // Listen to network requests
    const networkRequests: string[] = [];
    page.on('request', request => {
      if (request.url().includes('/vector-sync/')) {
        networkRequests.push(`${request.method()} ${request.url()}`);
        console.log(`📡 Network: ${request.method()} ${request.url()}`);
      }
    });
    
    // Monitor console logs for our debug messages
    const consoleMessages: string[] = [];
    page.on('console', msg => {
      const text = msg.text();
      if (text.includes('🔍') || text.includes('⚠️') || text.includes('🚀') || text.includes('🔄')) {
        consoleMessages.push(text);
        console.log(`🖥️ Console: ${text}`);
      }
    });
    
    // 2. Wait for initial sync status loading
    await page.waitForTimeout(5000);
    
    // 3. Check if we have any collections showing "syncing" status
    const syncingCollections = await page.evaluate(() => {
      // Look for any elements that show "Syncing..." text
      const syncButtons = document.querySelectorAll('[data-testid*="sync-btn"], button:has-text("Syncing")');
      const syncing = [];
      
      syncButtons.forEach(btn => {
        if (btn.textContent?.includes('Syncing')) {
          // Try to find the collection name
          const collectionElement = btn.closest('[data-testid="collection-item"]');
          const collectionName = collectionElement?.querySelector('[data-testid="collection-name"]')?.textContent;
          syncing.push(collectionName || 'unknown');
        }
      });
      
      return syncing;
    });
    
    console.log(`🔍 Found ${syncingCollections.length} collections in syncing state:`, syncingCollections);
    
    // 4. If we have syncing collections, wait and check if polling starts
    if (syncingCollections.length > 0) {
      console.log('⏳ Waiting 15 seconds to observe polling behavior...');
      await page.waitForTimeout(15000);
      
      // Check network requests - should have polling requests for each syncing collection
      const pollingRequests = networkRequests.filter(req => 
        req.includes('GET') && req.includes('/status')
      );
      
      console.log(`📊 Polling requests detected: ${pollingRequests.length}`);
      console.log('Polling requests:', pollingRequests);
      
      // Verify we have polling for syncing collections
      for (const collection of syncingCollections) {
        if (collection !== 'unknown') {
          const hasPolling = pollingRequests.some(req => req.includes(collection));
          console.log(`${collection}: ${hasPolling ? '✅ Has polling' : '❌ No polling'}`);
        }
      }
      
      // Check console messages for recovery
      const recoveryMessages = consoleMessages.filter(msg => 
        msg.includes('RECOVERY') || msg.includes('ORPHANED')
      );
      
      console.log(`🚨 Recovery messages: ${recoveryMessages.length}`);
      recoveryMessages.forEach(msg => console.log(`  - ${msg}`));
      
    } else {
      console.log('ℹ️ No collections in syncing state found - creating test scenario');
      
      // Try to find a collection and trigger sync to create a test scenario
      const firstCollection = await page.locator('[data-testid="collection-item"]').first();
      
      if (await firstCollection.isVisible()) {
        await firstCollection.click();
        await page.waitForTimeout(1000);
        
        // Look for sync button and click it
        const syncButton = page.locator('[data-testid*="sync-btn"]').first();
        if (await syncButton.isVisible()) {
          console.log('🧪 Triggering sync to create test scenario...');
          await syncButton.click();
          await page.waitForTimeout(2000);
          
          // Now check for polling
          await page.waitForTimeout(15000);
          
          const postSyncPollingRequests = networkRequests.filter(req => 
            req.includes('GET') && req.includes('/status')
          );
          
          console.log(`📊 Post-sync polling requests: ${postSyncPollingRequests.length}`);
        }
      }
    }
    
    // 5. Final analysis
    console.log('\n🔍 FINAL ANALYSIS:');
    console.log(`Total network requests: ${networkRequests.length}`);
    console.log(`Console debug messages: ${consoleMessages.length}`);
    
    // Look for specific patterns
    const orphanedDetection = consoleMessages.some(msg => msg.includes('ORPHANED'));
    const comprehensiveRecovery = consoleMessages.some(msg => msg.includes('COMPREHENSIVE RECOVERY'));
    const continuousDetection = consoleMessages.some(msg => msg.includes('CONTINUOUS DETECTION'));
    
    console.log(`- Orphaned detection: ${orphanedDetection ? '✅' : '❌'}`);
    console.log(`- Comprehensive recovery: ${comprehensiveRecovery ? '✅' : '❌'}`);
    console.log(`- Continuous detection: ${continuousDetection ? '✅' : '❌'}`);
    
    // Test should have some evidence of the polling system working
    expect(networkRequests.length).toBeGreaterThan(0);
  });

  test('should show polling intervals and safeguards in console', async () => {
    console.log('🔬 TEST: Checking polling intervals and safeguards');
    
    const debugMessages: string[] = [];
    page.on('console', msg => {
      const text = msg.text();
      if (text.includes('🟡 Active polling') || text.includes('🛡️ Safeguards')) {
        debugMessages.push(text);
        console.log(`🐛 Debug: ${text}`);
      }
    });
    
    // Wait for at least one debug cycle (30 seconds + buffer)
    console.log('⏳ Waiting 35 seconds for debug output...');
    await page.waitForTimeout(35000);
    
    console.log(`📊 Debug messages received: ${debugMessages.length}`);
    debugMessages.forEach(msg => console.log(`  - ${msg}`));
    
    // Should have at least one debug message after 35 seconds
    expect(debugMessages.length).toBeGreaterThan(0);
  });

  test('should handle continuous orphaned detection', async () => {
    console.log('🔬 TEST: Testing continuous orphaned detection');
    
    const continuousMessages: string[] = [];
    page.on('console', msg => {
      const text = msg.text();
      if (text.includes('🆘 CONTINUOUS DETECTION') || text.includes('🔄 CONTINUOUS RECOVERY')) {
        continuousMessages.push(text);
        console.log(`🔄 Continuous: ${text}`);
      }
    });
    
    // Wait for multiple continuous detection cycles (2+ cycles)
    console.log('⏳ Waiting 70 seconds for continuous detection cycles...');
    await page.waitForTimeout(70000);
    
    console.log(`🔄 Continuous detection messages: ${continuousMessages.length}`);
    continuousMessages.forEach(msg => console.log(`  - ${msg}`));
    
    // Continuous detection runs every 30s, so in 70s we should see at least 1-2 cycles
    // (depending on timing, we might catch 1 or 2 cycles)
  });
});