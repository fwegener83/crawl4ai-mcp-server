import { test, expect } from '@playwright/test';

test('Debug verfügbare Tabs', async ({ page }) => {
  // Navigate to the app
  await page.goto('http://localhost:5173/');
  
  // Wait for the app to load
  await page.waitForLoadState('networkidle');
  
  console.log('App geladen, suche nach verfügbaren Tabs...');
  
  // List all elements with data-testid containing 'tab'
  const allTabs = page.locator('[data-testid*="tab"]');
  const tabCount = await allTabs.count();
  
  console.log(`Gefundene Tabs: ${tabCount}`);
  
  for (let i = 0; i < tabCount; i++) {
    const tab = allTabs.nth(i);
    const testId = await tab.getAttribute('data-testid');
    const text = await tab.textContent();
    console.log(`Tab ${i}: data-testid="${testId}", text="${text}"`);
  }
  
  // Also check for any buttons or links that might be tabs
  const allButtons = page.locator('button, [role="tab"]');
  const buttonCount = await allButtons.count();
  console.log(`\nGefundene Buttons/Tabs: ${buttonCount}`);
  
  for (let i = 0; i < Math.min(10, buttonCount); i++) {
    const button = allButtons.nth(i);
    const text = await button.textContent();
    const testId = await button.getAttribute('data-testid');
    console.log(`Button ${i}: text="${text}", data-testid="${testId}"`);
  }
});