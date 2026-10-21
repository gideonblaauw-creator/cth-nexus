import { chromium } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';
import { mkdir } from 'fs/promises';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT = process.env.MOCK_ARTIFACT_DIR || '/opt/cursor/artifacts/peru-water-mock';
const BASE = (process.env.MOCK_BASE || 'http://127.0.0.1:8797/ecosystem/mock/peru-water/').replace(/\/?$/, '/');

const chapters = [
  { file: 'ch1-challenge.png', chapter: 0 },
  { file: 'ch2-policy.png', chapter: 1 },
  { file: 'ch3-hubs.png', chapter: 2 },
  { file: 'ch4-data.png', chapter: 3 },
  { file: 'ch5-coalition.png', chapter: 4 },
  { file: 'ch6-capital.png', chapter: 5 },
];

await mkdir(OUT, { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
let reports = null;

for (const ch of chapters) {
  await page.goto(`${BASE}?chapter=${ch.chapter}`, { waitUntil: 'domcontentloaded', timeout: 90000 });
  await page.waitForFunction(() => window.__mockPeruWaterReady === true, { timeout: 90000 });
  await page.waitForTimeout(1500);
  reports = await page.evaluate(() => window.__mockChapterReports);
  await page.screenshot({ path: path.join(OUT, ch.file) });
  console.log('saved', ch.file);
}

console.log('REPORTS', JSON.stringify(reports, null, 2));
await browser.close();
