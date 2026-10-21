import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: '.',
  timeout: 90000,
  workers: 1,
  use: {
    headless: true,
    viewport: { width: 1280, height: 900 },
  },
});
