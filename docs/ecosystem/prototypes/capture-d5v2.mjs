import { chromium } from 'playwright';
import { mkdir } from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(__dirname, '../screenshots');
const BASE = 'http://127.0.0.1:8765/d3-hybrid-split/index.html?mode=guide';

const shots = [
  { file: 'd5v2-ch1-challenges.png', q: 'chapter=0' },
  { file: 'd5v2-ch2-policy.png', q: 'chapter=1' },
  { file: 'd5v2-ch3-capital.png', q: 'chapter=2' },
  { file: 'd5v2-ch4-hubs.png', q: 'chapter=3' },
  { file: 'd5v2-ch5-partnerships.png', q: 'chapter=4' },
  { file: 'd5v2-ch5-constellation-agua-uqhu.png', q: 'chapter=4&constellation=agua-uqhu&closeup=1&actor=pe-uqhu' },
];

await mkdir(OUT, { recursive: true });
const browser = await chromium.launch({ headless: true });
for (const s of shots) {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto(`${BASE}&${s.q}`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForFunction(() => window.__ecoReady === true, { timeout: 70000 });
  await page.waitForTimeout(3500);
  await page.screenshot({ path: path.join(OUT, s.file) });
  console.log('OK', s.file);
  await page.close();
}
await browser.close();
