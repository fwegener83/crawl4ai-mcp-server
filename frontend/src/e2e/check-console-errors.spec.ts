import { test, expect } from '@playwright/test';

test('Check Frontend Console Errors', async ({ page }) => {
  const errors: string[] = [];
  
  // Listen for console errors
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(`Console ERROR: ${msg.text()}`);
    }
  });
  
  // Listen for page errors  
  page.on('pageerror', error => {
    errors.push(`Page ERROR: ${error.message}`);
  });
  
  // Navigate to the app
  await page.goto('http://localhost:5173/');
  
  // Wait for the app to load and check for errors
  await page.waitForTimeout(3000);
  
  console.log(`Fehler gefunden: ${errors.length}`);
  errors.forEach(error => console.log(error));
  
  // Take a screenshot to see what's displayed
  await page.screenshot({ path: 'debug-screenshot.png', fullPage: true });
  console.log('Screenshot gespeichert als debug-screenshot.png');
  
  // Try to get the page content to see what's actually displayed
  const bodyText = await page.locator('body').textContent();
  console.log('Page content:');
  console.log(bodyText?.substring(0, 500));
});