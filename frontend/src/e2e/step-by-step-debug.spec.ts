import { test, expect } from '@playwright/test';

test.describe('Step-by-Step BulkSave Debug', () => {
  test('Debug bulk save modal step by step', async ({ page }) => {
    console.log('=== Schritt-für-Schritt BulkSave Debug ===');

    // Schritt 1: Zur Deep Crawl Seite navigieren
    console.log('🔹 Schritt 1: Navigation zur Deep Crawl Seite...');
    await page.goto('http://localhost:5175/');
    await page.click('text=Deep Crawl');
    await expect(page.locator('h1')).toContainText('Deep Website Crawling');
    console.log('✅ Auf Deep Crawl Seite angekommen');

    // Screenshot nach Navigation
    await page.screenshot({ 
      path: '/Users/florianwegener/Projects/crawl4ai-mcp-server/frontend/debug-step-1-navigation.png',
      fullPage: true 
    });

    // Schritt 2: Deep Crawl mit geringer Tiefe konfigurieren
    console.log('🔹 Schritt 2: Deep Crawl konfigurieren (geringe Tiefe)...');
    await page.fill('input[placeholder*="https://example.com"]', 'https://bpv-consult.de');
    await page.fill('input[type="number"]', '0'); // Max Depth = 0 (nur Startseite)
    await page.fill('input[type="number"] >> nth=1', '1'); // Max Pages = 1
    console.log('✅ Crawl Parameter gesetzt: Domain=bpv-consult.de, Depth=0, Pages=1');

    // Screenshot nach Konfiguration
    await page.screenshot({ 
      path: '/Users/florianwegener/Projects/crawl4ai-mcp-server/frontend/debug-step-2-config.png',
      fullPage: true 
    });

    // Schritt 3: Deep Crawl starten und auf Ergebnisse warten
    console.log('🔹 Schritt 3: Deep Crawl starten...');
    await page.click('button:has-text("Start Deep Crawl")');
    console.log('✅ Crawl gestartet, warte auf Ergebnisse...');

    // Warten auf Loading-State Ende
    await page.waitForSelector('text=Successful:', { timeout: 60000 });
    console.log('✅ Crawl abgeschlossen, Ergebnisse verfügbar');

    // Screenshot nach Crawl
    await page.screenshot({ 
      path: '/Users/florianwegener/Projects/crawl4ai-mcp-server/frontend/debug-step-3-results.png',
      fullPage: true 
    });

    // Schritt 4: Ergebnisse analysieren
    console.log('🔹 Schritt 4: Ergebnisse analysieren...');
    const resultsCount = await page.locator('text=Crawl Results').count();
    const successfulCount = await page.textContent('text=successful');
    console.log(`✅ Gefunden: ${resultsCount} Ergebnis-Container, Successful: ${successfulCount}`);

    // Überprüfung ob Bulk Save Button sichtbar ist
    const bulkSaveButton = page.locator('button:has-text("Bulk Save to Collection")');
    const isBulkSaveVisible = await bulkSaveButton.isVisible();
    const isBulkSaveDisabled = await bulkSaveButton.isDisabled();
    console.log(`📊 Bulk Save Button: sichtbar=${isBulkSaveVisible}, deaktiviert=${isBulkSaveDisabled}`);

    // Schritt 5: Ergebnisse selektieren
    console.log('🔹 Schritt 5: Ergebnisse selektieren...');
    
    // Finde alle Checkboxen in der Ergebnis-Liste
    const resultCheckboxes = page.locator('.divide-y input[type="checkbox"]');
    const checkboxCount = await resultCheckboxes.count();
    console.log(`📦 Gefunden: ${checkboxCount} Checkboxen in Ergebnissen`);

    if (checkboxCount > 0) {
      // Erste Checkbox selektieren
      await resultCheckboxes.first().check();
      console.log('✅ Erste Checkbox selektiert');

      // Kurz warten für State-Update
      await page.waitForTimeout(1000);

      // Button-Status nach Selektion prüfen
      const buttonEnabledAfterSelection = await bulkSaveButton.isEnabled();
      console.log(`📊 Bulk Save Button nach Selektion: aktiviert=${buttonEnabledAfterSelection}`);

      // Screenshot nach Selektion
      await page.screenshot({ 
        path: '/Users/florianwegener/Projects/crawl4ai-mcp-server/frontend/debug-step-5-selected.png',
        fullPage: true 
      });

      // Schritt 6: Bulk Save Button klicken
      if (buttonEnabledAfterSelection) {
        console.log('🔹 Schritt 6: Bulk Save Button klicken...');
        
        // Console-Ausgaben mitlesen
        page.on('console', msg => {
          console.log(`🖥️  Browser Console [${msg.type()}]: ${msg.text()}`);
        });

        await bulkSaveButton.click();
        console.log('✅ Bulk Save Button geklickt');

        // Kurz warten für Modal-Animation
        await page.waitForTimeout(2000);

        // Schritt 7: Modal-Status überprüfen
        console.log('🔹 Schritt 7: Modal-Status überprüfen...');
        
        // Nach Modal-Titel suchen
        const modalTitle = page.locator('h3:has-text("Bulk Save to Collection")');
        const isModalVisible = await modalTitle.isVisible();
        console.log(`🎭 Modal sichtbar: ${isModalVisible}`);

        // DOM nach Modal-Elementen durchsuchen
        const modalBackdrop = page.locator('.fixed.inset-0.bg-black.bg-opacity-50');
        const hasBackdrop = await modalBackdrop.count();
        console.log(`🎭 Modal Backdrop gefunden: ${hasBackdrop} Element(e)`);

        if (hasBackdrop > 0) {
          const backdropVisible = await modalBackdrop.isVisible();
          console.log(`🎭 Modal Backdrop sichtbar: ${backdropVisible}`);
        }

        // Screenshot nach Modal-Click
        await page.screenshot({ 
          path: '/Users/florianwegener/Projects/crawl4ai-mcp-server/frontend/debug-step-6-modal-attempt.png',
          fullPage: true 
        });

        // Dom-Struktur analysieren
        console.log('🔹 DOM-Analyse...');
        const domInfo = await page.evaluate(() => {
          const modals = document.querySelectorAll('[class*="fixed"], [class*="modal"], [class*="z-"]');
          return {
            totalFixedElements: modals.length,
            bodyChildren: document.body.children.length,
            documentPortals: Array.from(document.body.children).map(child => ({
              tagName: child.tagName,
              classes: child.className,
              visible: child.offsetParent !== null
            }))
          };
        });
        console.log('🔍 DOM-Info:', JSON.stringify(domInfo, null, 2));

        // React DevTools State (falls verfügbar)
        const reactState = await page.evaluate(() => {
          const reactFiber = (window as any).__REACT_DEVTOOLS_GLOBAL_HOOK__;
          return {
            reactDetected: !!reactFiber,
            errors: (window as any).__REACT_ERROR_OVERLAY_GLOBAL_HOOK__ || null
          };
        });
        console.log('⚛️  React-State:', JSON.stringify(reactState, null, 2));

      } else {
        console.log('❌ Bulk Save Button ist nicht aktiviert - kann nicht klicken');
      }
    } else {
      console.log('❌ Keine Checkboxen gefunden - kann nicht selektieren');
    }

    console.log('=== Debug-Session abgeschlossen ===');
    
    // Finaler Screenshot
    await page.screenshot({ 
      path: '/Users/florianwegener/Projects/crawl4ai-mcp-server/frontend/debug-final-state.png',
      fullPage: true 
    });
  });
});