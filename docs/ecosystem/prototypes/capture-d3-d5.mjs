import { chromium } from 'playwright';
import { mkdir } from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(__dirname, '../screenshots');
const BASE = 'http://127.0.0.1:8765';

const shots = [
  { file: 'd3-overview.png', url: `${BASE}/d3-hybrid-split/index.html?state=overview`, w: 1440, h: 900 },
  { file: 'd3-actor-selected.png', url: `${BASE}/d3-hybrid-split/index.html?state=selected&actor=pe-emprende-up-climatech-rein-hub-peru`, w: 1440, h: 900 },
  { file: 'd3-ego-2hop.png', url: `${BASE}/d3-hybrid-split/index.html?state=ego&actor=pe-emprende-up-climatech-rein-hub-peru&depth=2`, w: 1440, h: 900 },
  { file: 'd3-filters-country-type.png', url: `${BASE}/d3-hybrid-split/index.html?state=filters&country=PE&cats=accelerator,government,funder`, w: 1440, h: 900 },
  { file: 'd3-hub-emprende-up.png', url: `${BASE}/d3-hybrid-split/index.html?state=hub&hub=pe-emprende-up-climatech-rein-hub-peru&depth=2`, w: 1440, h: 900 },
  { file: 'd3-mobile-selected.png', url: `${BASE}/d3-hybrid-split/index.html?state=selected&mobile=1&actor=pe-cleantechhub`, w: 390, h: 844 },
  { file: 'd5-opening.png', url: `${BASE}/d5-story-explorer/index.html?chapter=0&year=2026`, w: 1440, h: 900 },
  { file: 'd5-chapter-clp26.png', url: `${BASE}/d5-story-explorer/index.html?chapter=1&year=2026`, w: 1440, h: 900 },
  { file: 'd5-chapter-hub-growth.png', url: `${BASE}/d5-story-explorer/index.html?chapter=2&year=2026`, w: 1440, h: 900 },
  { file: 'd5-chapter-funding.png', url: `${BASE}/d5-story-explorer/index.html?chapter=3&year=2026`, w: 1440, h: 900 },
  { file: 'd5-time-2022.png', url: `${BASE}/d5-story-explorer/index.html?chapter=2&year=2022`, w: 1440, h: 900 },
  { file: 'd5-time-2025.png', url: `${BASE}/d5-story-explorer/index.html?chapter=3&year=2025`, w: 1440, h: 900 },
  { file: 'd5-actor-detail.png', url: `${BASE}/d5-story-explorer/index.html?chapter=1&year=2026&actor=pe-emprende-up-climatech-rein-hub-peru`, w: 1440, h: 900 },
];

await mkdir(OUT, { recursive: true });
const browser = await chromium.launch({ headless: true });
for (const s of shots) {
  const page = await browser.newPage({ viewport: { width: s.w, height: s.h } });
  await page.goto(s.url, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForFunction(() => window.__ecoReady === true, { timeout: 70000 });
  await page.waitForTimeout(3500);
  await page.screenshot({ path: path.join(OUT, s.file), fullPage: false });
  console.log('OK', s.file);
  await page.close();
}
await browser.close();
