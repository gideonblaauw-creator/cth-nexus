import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: '.',
  timeout: 90000,
  workers: 1,
  use: {
    headless: true,
    viewport: { width: 1280, height: 900 },
    // Test-only: Playwright waitForFunction needs eval; production CSP stays strict in index.html.
    bypassCSP: true,
  },
});
