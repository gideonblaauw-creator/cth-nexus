#!/usr/bin/env node
/**
 * Capture 1440×900 PNGs for story-direction mocks. Run from repo root:
 *   node static/ecosystem/mock/story-directions/capture-screenshots.mjs
 * Requires: static HTTP on :8765 (python -m http.server 8765 --directory static)
 */
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { chromium } = require('../../tests/node_modules/@playwright/test');
import { mkdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const outDir = path.join(__dirname, 'screenshots');
const base = process.env.MOCK_BASE_URL || 'http://127.0.0.1:8765';
const pages = [
  { id: 'a', url: `${base}/ecosystem/mock/story-directions/a/index.html`, file: 'direction-a-map-first.png' },
  { id: 'b', url: `${base}/ecosystem/mock/story-directions/b/index.html`, file: 'direction-b-network-first.png' },
  { id: 'c', url: `${base}/ecosystem/mock/story-directions/c/index.html`, file: 'direction-c-scrollytelling.png' },
  { id: 'd', url: `${base}/ecosystem/mock/story-directions/d/index.html`, file: 'direction-d-dashboard.png' },
];

await mkdir(outDir, { recursive: true });
const browser = await chromium.launch();
const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });

for (const p of pages) {
  const page = await context.newPage();
  await page.goto(p.url, { waitUntil: 'networkidle', timeout: 120000 });
  await page.waitForTimeout(3500);
  await page.screenshot({
    path: path.join(outDir, p.file),
    fullPage: false,
  });
  console.log('saved', p.file);
  await page.close();
}

await browser.close();
